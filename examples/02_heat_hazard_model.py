"""Baseline analysis: discrete-time hazard of preterm delivery against weekly district temperature anomaly.

Exposure comes from the ready-made district weekly file (gridded product). The workshop question is what you
gain by replacing it with a better country-wide temperature surface (stations, SPDE, functional kriging,
physics-informed regression, CNN), averaged over each district.

Run from the repo root:  python examples/02_heat_hazard_model.py      (about 2 minutes, 2.8 million person-weeks)
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from common import participants, district_week_exposure, add_anomaly, person_weeks, attach_lags

df = participants()[['id', 'district_id', 'lmp_date', 'birth_date', 'ga_days', 'age_years', 'ses_grade', 'hiv_positive', 'anaemia',
                     'hypertensive_disorder', 'outdoor_work_pregnancy', 'infant_sex']]
ex = add_anomaly(district_week_exposure(), 'tmax')
ex['tmax_change'] = ex.tmax_anom - ex.groupby('district_id').tmax_anom.shift(1)      # week-on-week change
pw = person_weeks(df)
pw = attach_lags(pw, ex, 'tmax_anom')
pw = attach_lags(pw, ex, 'tmax_change')
pw = pw.dropna(subset=[c for c in pw if c.startswith('tmax_')])
print(f'{len(pw):,} person-weeks, {pw.event.sum():,} preterm births')

w = np.array([0.40, 0.28, 0.17, 0.10, 0.05])                                   # one sensible lag weighting; try your own
pw['heat'] = sum(w[l] * pw[f'tmax_anom_lag{l}'] for l in range(5))
pw['change'] = sum(w[l] * pw[f'tmax_change_lag{l}'] for l in range(5))
pw['rise'] = sum(w[l] * pw[f'tmax_change_lag{l}'].clip(lower=0) for l in range(5))     # warming only
X = pd.get_dummies(pw.gest_week, prefix='gw', drop_first=True, dtype=float)
X['age_35plus'] = (pw.age_years > 35).astype(float); X['age_under22'] = (pw.age_years < 22).astype(float)
X = X.join(pd.get_dummies(pw.ses_grade, prefix='ses', drop_first=True, dtype=float))
for c in ['hiv_positive', 'anaemia', 'hypertensive_disorder', 'outdoor_work_pregnancy']: X[c] = pw[c].astype(float)
X['male'] = (pw.infant_sex == 'male').astype(float)

def fit(cols, label):
    m = sm.Logit(pw.event, sm.add_constant(X.join(pw[cols]))).fit(disp=0)
    ci = np.exp(m.conf_int().loc[cols]); orr = np.exp(m.params[cols])
    print(label); print(pd.DataFrame({'OR': orr, 'lo': ci[0], 'hi': ci[1]}).round(3).to_string(), '\n')
    return m

fit(['heat'], 'Lag-weighted weekly tmax anomaly (per degC)')
fit(['heat', 'change'], 'Anomaly and week-on-week change together')
fit(['heat', 'rise'], 'Anomaly and week-on-week warming (rises only)')
fit([f'tmax_anom_lag{l}' for l in range(5)], 'Unconstrained lags 0 to 4 (a crude distributed lag model)')

# a simple non-linear check: anomaly in bands, reference -1 to +1 degC
bands = pd.cut(pw.heat, [-20, -3, -2, -1, 1, 2, 3, 20], labels=['<-3', '-3:-2', '-2:-1', 'ref', '1:2', '2:3', '>3'])
B = pd.get_dummies(bands, prefix='band', dtype=float).drop(columns='band_ref')
m = sm.Logit(pw.event, sm.add_constant(X.join(B))).fit(disp=0)
print('Exposure bands, OR against -1 to +1 degC'); print(np.exp(m.params[B.columns]).round(3).to_string())
