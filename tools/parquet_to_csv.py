"""Write a CSV copy of every Parquet file in data/. Run from the repo root:  python tools/parquet_to_csv.py
Needs pandas and pyarrow (pip install pandas pyarrow). Output goes next to each file as .csv.gz, except the gridded weather, which goes to data/weather_gridded_csv/
so that data/weather_gridded/ still reads as one Parquet dataset.
The gridded weather becomes three large CSVs (about 1.9 million rows each); open them in R, Python or Stata, not Excel."""
from pathlib import Path
import pandas as pd

data = Path(__file__).resolve().parents[1] / 'data'
for f in sorted(data.rglob('*.parquet')):
    out = f.with_suffix('.csv.gz')
    if f.parent.name == 'weather_gridded':
        out = data / 'weather_gridded_csv' / out.name; out.parent.mkdir(exist_ok=True)
    if out.exists():
        print('exists, skipped:', out.relative_to(data)); continue
    pd.read_parquet(f).to_csv(out, index=False)
    print('wrote', out.relative_to(data))
