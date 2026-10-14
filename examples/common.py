"""Shared loaders for the example scripts. Paths are relative to the repo root."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
DAY0 = pd.Timestamp('2100-01-01')          # day 0 of every weather file


def participants():
    return pd.read_parquet(DATA / 'participants.parquet')


def district_week_exposure():
    """Weekly district means from the 0.5 degree gridded product. Week k covers days 7k to 7k+6 after 2100-01-01."""
    ex = pd.read_csv(DATA / 'district_week_exposure_gridded.csv', parse_dates=['week_start'])
    ex['wk'] = (ex.week_start - DAY0).dt.days // 7
    return ex


def add_anomaly(ex, var='tmax'):
    """Anomaly against the district's own mean for that week of the year (all years pooled)."""
    ex = ex.copy()
    ex['woy'] = ex.wk % 52
    ex[f'{var}_anom'] = ex[var] - ex.groupby(['district_id', 'woy'])[var].transform('mean')
    return ex


def person_weeks(df, first_week=22, last_week=36):
    """One row per pregnancy per gestational week at risk of a preterm delivery.
    event = 1 in the week the baby is born (weeks 22 to 36 only)."""
    gw = np.floor(df.ga_days.values / 7).astype(int)
    rows = []
    for w in range(first_week, last_week + 1):
        at = gw >= w
        rows.append(pd.DataFrame({'id': df.id.values[at], 'gest_week': w, 'event': (gw[at] == w).astype(int),
                                  'week_start_day': ((df.lmp_date.values[at] - DAY0.to_datetime64()) // np.timedelta64(1, 'D')) + 7 * w}))
    pw = pd.concat(rows, ignore_index=True)
    return pw.merge(df.drop(columns=['lmp_date', 'birth_date']), on='id', how='left')


def attach_lags(pw, ex, var='tmax_anom', lags=range(5)):
    """Exposure in calendar week (start_day - 1 - 7*lag) // 7 for each lag, from the district weekly series."""
    key = ex.set_index(['district_id', 'wk'])[var]
    for l in lags:
        wk = (pw.week_start_day - 1 - 7 * l) // 7
        pw[f'{var}_lag{l}'] = key.reindex(pd.MultiIndex.from_arrays([pw.district_id, wk])).values
    return pw
