# HE²AT synthetic pregnancies and weather, southern Africa (v3)

A fully synthetic teaching dataset for the ICMS workshop *From Data to Impact: Advancing Climate Resilience in Africa Through Statistics and Mathematical Modelling* (Edinburgh, November 2026). It is built for one question: estimate a temperature field over a whole region from imperfect data, link it to outcomes recorded by district, and test whether temperature, or a change in temperature, is related to preterm birth.

186,713 pregnancies in seven countries (South Africa, Mozambique, Zambia, Malawi, Zimbabwe, Botswana, Namibia) and 80 invented districts. Nine years of daily weather from 45 stations and a 0.5 degree gridded product.

## What this is and is not

Every value is simulated. Nothing was built from, fitted to or trained on any participant record, any HE²AT study or any real weather record. Country outlines are rough hand-drawn shapes, districts are invented and the years run 2100 to 2108 so no day can be matched to real weather. Effect sizes were set by hand with published meta-analyses in mind (see `docs/references.md`).

So results from this data are about methods, not about southern Africa. Please read `DATA_USE.md` before you start.

## Quick start

Python 3.10 or later.

```
pip install -r requirements.txt
python examples/01_explore.py              # sizes, preterm by group, district map
python examples/03_station_surface.py      # stations to a district exposure (inverse distance), compared with the gridded product
python examples/02_heat_hazard_model.py    # discrete-time hazard of preterm birth against weekly temperature (about 2 minutes, 4 GB RAM)
```

R users: the examples are short enough to port. `dlnm` works directly on the person-week frame built in example 02.

## Opening the files (Parquet)

Most files are plain CSV. Three kinds are Parquet: the participants, the station weather and the gridded weather. Parquet is a compressed table format, about a fifth the size of the same CSV and much faster to load. You cannot double-click it open in Excel, but one line in R or Python reads it.

You may not need Parquet at all. The participants and stations also come as `.csv.gz` (R and Python read these directly; for Stata or Excel, unzip first with 7-Zip or `gunzip`). For most health analyses the weekly district file `district_week_exposure_gridded.csv` is enough. Only the gridded daily weather is Parquet-only.

R (install once with `install.packages("arrow")`):

```r
library(arrow)
library(dplyr)
p    <- read_parquet("data/participants.parquet")
st   <- read_parquet("data/weather_stations_daily.parquet")
grid <- open_dataset("data/weather_gridded") |>        # all three year files as one table
          filter(date >= as.Date("2104-01-01"), date < as.Date("2105-01-01")) |>
          collect()                                     # filter before collect to save memory
```

Python (`pip install pandas pyarrow`):

```python
import pandas as pd
p    = pd.read_parquet("data/participants.parquet")
grid = pd.read_parquet("data/weather_gridded")          # all three year files as one table
```

Stata has no built-in Parquet reader. Convert first, unzip, then `import delimited`:

```
python tools/parquet_to_csv.py        # or:  Rscript tools/parquet_to_csv.R
```

This writes a CSV copy next to every Parquet file (about 3 minutes; the Python version writes gzipped `.csv.gz`, about 100 MB, the R version plain `.csv`). The gridded weather has 5.7 million rows, too many for Excel. Open it in R, Python or Stata.

## Files

All in `data/`. Column definitions are in `docs/data_dictionary.csv` (participants) and `docs/files.md` (weather and districts).

| File | What it is |
|---|---|
| `participants.parquet` / `.csv.gz` | One row per pregnancy. District only, no coordinates. |
| `districts.csv`, `districts.geojson` | District boundaries and summaries |
| `district_cells_0p25deg.csv` | Every 0.25 degree cell with its district and elevation. Use it to average any surface to districts |
| `stations.csv`, `weather_stations_daily.parquet` | 45 stations: tmax, tmin, rain, humidity, dew point, wind speed. Station bias, gaps, late openings |
| `weather_gridded/` (three files by year) | Gridded product: the same variables plus UTCI and steering wind (u, v). Complete, biased, smooth |
| `district_week_exposure_gridded.csv` | Weekly district means from the gridded product. The baseline exposure |
| `district_week_births.csv` | Weekly district counts of births, preterm, very preterm and stillbirths |

## Outcomes

`ga_days` and `ga_weeks` give gestational age at birth as a continuous quantity, 22 to 44 weeks. `preterm` is under 37 weeks (about 15 per cent), `very_preterm` under 32 weeks. Stillbirth, birth weight and low birth weight are there too.

## The weather

Temperature anomalies have three parts. A large, slow pattern. A mid-scale part that the steering wind carries across the region from day to day (west to east, stronger in winter and further south). And short-range local variation that 45 stations cannot see. Hot and cold spells sit on top. There is a warming trend, deliberately faster than the real one, so that change over the nine years is detectable.

Stations: accurate but sparse, roughly one per 100,000 km², with gaps. Gridded product: complete but carries a smooth bias and an error that drifts from day to day, about 1.3 °C overall. Neither is the truth. The organisers hold 15 stations back for scoring.

Humidity, dew point, wind speed and UTCI are derived from the same weather. Whether they add anything over tmax is a question for you.

## Things to watch

- `anc_visits` is counted over the whole pregnancy. Think about what that does to its link with gestational age before you adjust for it.
- Education and socio-economic grade are related. Check what each does with the other in the model.
- Exposure windows anchored on the birth date give biased answers. Anchor on the last menstrual period, or use the person-week set-up in example 02.
- Births at the very start and end of the period were removed because their pregnancies were only partly observed. The district weekly births file covers the same window.
- There is no missing data in the participant file. Real data would have it.

## Workshop tasks

1. Build a daily temperature surface for the whole region from the stations, the gridded product, or both. SPDE, functional kriging, physics-informed penalised regression and neural networks all fit here. The steering wind is released for methods that can use transport.
2. Score it. The organisers can score predictions at the 15 held-out stations. Report error as well as uncertainty, as in the Heaton et al. case study.
3. Average to districts and link to outcomes. Person-week hazard models, distributed lag models, or weekly district counts with an at-risk offset.
4. Ask the main question: is temperature, or week-on-week change in temperature, related to preterm birth? Does the answer depend on the surface you used?

Example results from simple versions of each method are in `docs/method_comparison.md`. Treat them as a floor to beat.

## Citation and contact

HE²AT Center, Wits Planetary Health Research. Synthetic southern Africa pregnancy and weather dataset, version 3, 2026.

Craig Parker, craig.parker@witsphr.org
