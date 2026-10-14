"""Turn the station network into district exposure: the simplest possible surface (inverse distance weighting
on lapse-corrected station tmax), then compare it with the gridded product. Use this as the template for
plugging in SPDE, functional kriging, physics-informed regression or a CNN: anything that returns a daily
value per 0.25 degree cell can be averaged to districts the same way.

Run from the repo root:  python examples/03_station_surface.py
"""
import numpy as np
import pandas as pd
from common import DATA, DAY0

cells = pd.read_csv(DATA / 'district_cells_0p25deg.csv')
st = pd.read_csv(DATA / 'stations.csv')
obs = pd.read_parquet(DATA / 'weather_stations_daily.parquet')
Y = obs.pivot(index='date', columns='station_id', values='tmax')[st.station_id]          # days x stations
LAPSE = 0.0055                                                                            # degC per metre

def km(lon, lat):
    return np.c_[(np.asarray(lon) - 25) * 111.32 * np.cos(np.deg2rad(-20)), (np.asarray(lat) + 20) * 110.57]

D = np.linalg.norm(km(cells.lon, cells.lat)[:, None, :] - km(st.lon, st.lat)[None, :, :], axis=2)   # cells x stations
W0 = 1.0 / np.maximum(D, 5.0) ** 2
Ysl = Y.values + LAPSE * st.elev_m.values[None, :]                                        # reduce to sea level
ok = ~np.isnan(Ysl)
num = np.nan_to_num(Ysl) @ W0.T; den = ok.astype(float) @ W0.T
field = num / den - LAPSE * cells.elev_m.values[None, :]                                    # days x cells, back to cell height

# district daily means, then weekly
dist = cells.district_id.values
daily = pd.DataFrame(field, index=Y.index).T.groupby(dist).mean().T                        # days x districts
wk = ((pd.to_datetime(daily.index) - DAY0).days // 7)
weekly_idw = daily.groupby(wk).mean()

grid = pd.read_csv(DATA / 'district_week_exposure_gridded.csv', parse_dates=['week_start'])
grid['wk'] = (grid.week_start - DAY0).dt.days // 7
weekly_grid = grid.pivot(index='wk', columns='district_id', values='tmax')
diff = (weekly_idw - weekly_grid).stack()
print(f'IDW minus gridded product, district-week tmax: mean {diff.mean():.2f} degC, SD {diff.std():.2f} degC')
print('Which is closer to the truth? Score your surface at held-out stations: the organisers have 15 that are not in this release.')
weekly_idw.to_csv(DATA.parent / 'figures' / 'example_district_week_tmax_idw.csv')
