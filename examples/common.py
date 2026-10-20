"""Shared loaders for the example scripts. Paths are relative to the repo root."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
DAY0 = pd.Timestamp('2100-01-01')          # day 0 of every weather file


YES = lambda s: (s == 'yes').astype(int)


def participants():
    """One row per pregnancy in analysis-ready form.

    Reads the wide copy of master_long (HEAT Master Codebook names and codes), joins each LOCATION ID to its
    district through locations.csv, and adds 0/1 versions of the yes/no variables. `id` is the PT ID.
    The same frame can be built from data/master_long.csv.gz with a pivot, see long_to_wide()."""
    w = pd.read_parquet(DATA / 'participants_wide.parquet')
    loc = pd.read_csv(DATA / 'locations.csv')
    df = w.merge(loc[['Loc_id', 'District', 'urban_rural']], left_on='LOCATION ID', right_on='Loc_id', how='left')
    assert df.District.notna().all(), 'every LOCATION ID should be in locations.csv'
    return pd.DataFrame({
        'id': df['PT ID'], 'study': df['STUDY CODE'], 'location_id': df['LOCATION ID'],
        'district_id': df.District, 'urban_rural': df.urban_rural, 'country': df.country,
        'lmp_date': pd.to_datetime(df.lnmp), 'birth_date': pd.to_datetime(df.dob),
        'ga_days': df.gest_age_delivery_days.astype(int), 'ga_weeks': df.gest_age_delivery_days / 7,
        'preterm': YES(df.prem_birth), 'very_preterm': YES(df.very_prem_birth), 'stillbirth': YES(df.stillbirth),
        'birth_weight_g': df.birth_weight, 'low_birth_weight': YES(df.low_birth_weight),
        'infant_sex': df.sex.str.lower(), 'age_years': df.age_years, 'parity': df.parity,
        'ses_grade': df.ses_quintile, 'education': df.education_cat.map({'none': 0, 'primary': 1, 'secondary': 2, 'tertiary': 3}),
        'hiv_positive': (df.hiv_status == 'positive').astype(int), 'haemoglobin_g_dl': df.haemoglobin,
        'anaemia': YES(df.anaemia), 'bmi_booking': df.bmi, 'hypertensive_disorder': YES(df.hypertension_preg),
        'outdoor_work_pregnancy': YES(df.outdoor_work_preg), 'unimproved_water': YES(df.water_source_unimproved),
        'anc_visits': df.anc_visits})


def long_to_wide(path=None):
    """Pivot master_long (STUDY CODE | PT ID | DATE | VARIABLE | VALUE | RELATION | LOCATION ID) to one row per
    pregnancy. Mother and child share the mother's PT ID, so the key is STUDY CODE + PT ID."""
    ml = pd.read_csv(path or DATA / 'master_long.csv.gz', dtype=str, keep_default_na=False)
    w = ml.pivot_table(index=['STUDY CODE', 'PT ID', 'LOCATION ID'], columns='VARIABLE', values='VALUE', aggfunc='first')
    return w.reset_index().rename_axis(columns=None)


def exposures():
    """Per-pregnancy PM2.5 by trimester, keyed by the same PT ID."""
    return pd.read_csv(DATA / 'per_patient_exposures.csv.gz').rename(columns={'PT ID': 'id'})


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
