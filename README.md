# HE²AT synthetic pregnancies and weather, southern Africa (v4)

## Quick start

1. Download [he2at-synthetic-southern-africa-v4.0.2.zip](https://github.com/Wits-Planetary-Health-Research/he2at-synthetic-southern-africa/releases/download/v4.0.2/he2at-synthetic-southern-africa-v4.0.2.zip) (about 120 MB, no GitHub account needed), or clone the repo:
   `git clone https://github.com/Wits-Planetary-Health-Research/he2at-synthetic-southern-africa.git`
2. Unzip it and open a terminal in the unzipped folder, `he2at-synthetic-southern-africa-v4.0.2`. Every command below runs from there.
3. Python 3.10 or later:

   ```
   pip install -r requirements.txt
   python examples/01_explore.py              # sizes, studies and locations, preterm by group, district map
   python examples/03_station_surface.py      # stations to a district exposure (inverse distance), compared with the gridded product
   python examples/02_heat_hazard_model.py    # discrete-time hazard of preterm birth against weekly temperature (about 2 minutes, 4 GB RAM)
   ```

   `01_explore.py` takes under a minute. Its first two lines should read:

   ```
   186,713 pregnancies, 7 studies, 160 locations, 80 districts, births 2101-11-06 to 2108-07-01
   preterm 0.151, very preterm 0.029, stillbirth 0.020
   ```

   It then prints preterm rates by group and saves plots to `figures/`.
4. R 4.1 or later. Install once with `install.packages(c("arrow", "dplyr"))`, then in R:

   ```r
   library(arrow)
   p <- read_parquet("data/participants_wide.parquet")
   dim(p)                        # 186713 26
   mean(p$prem_birth == "yes")   # 0.151, the preterm rate
   ```

   `Rscript tools/parquet_to_csv.R` writes a CSV copy of every Parquet file. `dlnm` works directly on the person-week frame built in example 02. More R below, under "Opening the files".
5. How to cite: see `CITATION.cff` (GitHub's "Cite this repository" button gives APA and BibTeX). Licence: data under CC BY 4.0 (`LICENSE-DATA`), code under MIT (`LICENSE`). Read `DATA_USE.md` before you start.

## About the dataset

A fully synthetic teaching dataset for the ICMS workshop *From Data to Impact: Advancing Climate Resilience in Africa Through Statistics and Mathematical Modelling* (Edinburgh, November 2026). It is built for one question: estimate a temperature field over a whole region from imperfect data, link it to outcomes recorded by district, and test whether temperature, or a change in temperature, is related to preterm birth.

186,713 pregnancies in seven synthetic studies, one per country (South Africa, Mozambique, Zambia, Malawi, Zimbabwe, Botswana, Namibia), booked at 160 health facilities in 80 invented districts. Nine years of daily weather from 45 stations and a 0.5 degree gridded product.

## What changed in v4

The pregnancies and weather are the same draw as v3: the generator was re-run and every v3 file came back byte for byte. What changed is the layout of the participant data. It now follows the HE²AT harmonisation guidelines used for the real RP1 data:

- long format, `STUDY CODE | PT ID | DATE | VARIABLE | VALUE | RELATION | LOCATION ID`, one file per study plus `master_long`
- variable names and codes from the HEAT Master Codebook (`prem_birth`, `gest_age_delivery_days`, `hiv_status`, `yes`/`no` and so on)
- PT IDs are salted hashes. The mother's PT ID is used on her child's rows, and the same hash links the long files, the wide copy and the exposure file
- records carry a location code (`SYNZAF_17`), not a district name. The geolocation table with facility names and coordinates is held back, as it is for the real data
- PM2.5 moved to a separate exposure file

If you used v3: `examples/common.py` rebuilds the v3 column names from the new files, so the examples run unchanged. Results are identical.

## What this is and is not

Every value is simulated. Nothing was built from, fitted to or trained on any participant record, any HE²AT study or any real weather record. Country outlines are rough hand-drawn shapes, districts are invented and the years run 2100 to 2108 so no day can be matched to real weather. Effect sizes were set by hand with published meta-analyses in mind (see `docs/references.md`).

So results from this data are about methods, not about southern Africa. Please read `DATA_USE.md` before you start.

## Run it in Colab

Two walkthrough notebooks run the same first analysis cell by cell, with nothing to install on your own machine. The first cell clones the repo; no GitHub account is needed.

| | |
|---|---|
| Python | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Wits-Planetary-Health-Research/he2at-synthetic-southern-africa/blob/main/notebooks/01_python_walkthrough.ipynb) `notebooks/01_python_walkthrough.ipynb` |
| R (with `dlnm`) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Wits-Planetary-Health-Research/he2at-synthetic-southern-africa/blob/main/notebooks/02_r_walkthrough.ipynb) `notebooks/02_r_walkthrough.ipynb` |

## Opening the files (Parquet)

Most files are plain or gzipped CSV. Three are Parquet: the wide copy of the participant data, the station weather and the gridded weather. Parquet is a compressed table format, about a fifth the size of the same CSV and much faster to load. You cannot double-click it open in Excel, but one line in R or Python reads it.

You may not need Parquet at all. The wide participant file and the stations also come as `.csv.gz` (R and Python read these directly; for Stata or Excel, unzip first with 7-Zip or `gunzip`). For most health analyses the weekly district file `district_week_exposure_gridded.csv` is enough. Only the gridded daily weather is Parquet-only.

R (install once with `install.packages("arrow")`):

```r
library(arrow)
library(dplyr)
p    <- read_parquet("data/participants_wide.parquet")
loc  <- read.csv("data/locations.csv")                    # LOCATION ID to district
p    <- left_join(p, loc, by = c("LOCATION ID" = "Loc_id"))
st   <- read_parquet("data/weather_stations_daily.parquet")
grid <- open_dataset("data/weather_gridded") |>        # all three year files as one table
          filter(date >= as.Date("2104-01-01"), date < as.Date("2105-01-01")) |>
          collect()                                     # filter before collect to save memory
```

Python (`pip install pandas pyarrow`):

```python
import pandas as pd
p    = pd.read_parquet("data/participants_wide.parquet")
loc  = pd.read_csv("data/locations.csv")                  # LOCATION ID to district
p    = p.merge(loc, left_on="LOCATION ID", right_on="Loc_id")
grid = pd.read_parquet("data/weather_gridded")          # all three year files as one table
```

Stata has no built-in Parquet reader. Convert first, unzip, then `import delimited`:

```
python tools/parquet_to_csv.py        # or:  Rscript tools/parquet_to_csv.R
```

This writes a CSV copy next to every Parquet file, except the gridded weather, which goes to `data/weather_gridded_csv/` so the Parquet folder still reads as one table (about 3 minutes; the Python version writes gzipped `.csv.gz`, about 100 MB, the R version plain `.csv`). The gridded weather has 5.7 million rows, too many for Excel. Open it in R, Python or Stata.

## Files

All in `data/`. Variable definitions are in `docs/data_dictionary.csv` (participants) and `docs/files.md` (layout, weather and districts). What every code means is in `docs/codebook.md`, with R and Stata code.

| File | What it is |
|---|---|
| `long/<STUDY CODE>_long.csv.gz` | Participant data in the HE²AT long format, one file per study |
| `master_long.csv.gz` | The seven study files stacked |
| `participants_wide.parquet` / `.csv.gz` | `master_long` pivoted, one row per pregnancy |
| `per_patient_exposures.csv.gz` | PM2.5 by trimester, keyed by PT ID |
| `locations.csv` | Each LOCATION ID with its study, district and urban or rural setting. No names or coordinates |
| `districts.csv`, `districts.geojson` | District boundaries and summaries |
| `district_cells_0p25deg.csv` | Every 0.25 degree cell with its district and elevation. Use it to average any surface to districts |
| `stations.csv`, `weather_stations_daily.parquet` | 45 stations: tmax, tmin, rain, humidity, dew point, wind speed. Station bias, gaps, late openings |
| `weather_gridded/` (three files by year) | Gridded product: the same variables plus UTCI and steering wind (u, v). Complete, biased, smooth |
| `district_week_exposure_gridded.csv` | Weekly district means from the gridded product. The baseline exposure |
| `district_week_births.csv` | Weekly district counts of births, preterm, very preterm and stillbirths |

## Outcomes

`gest_age_delivery_days` gives gestational age at birth, 154 to 314 days (22 to 44 weeks). `prem_birth` is under 37 weeks (about 15 per cent), `very_prem_birth` under 32 weeks. Stillbirth, birth weight and low birth weight are there too.

## The weather

Temperature anomalies have three parts. A large, slow pattern. A mid-scale part that the steering wind carries across the region from day to day (west to east, stronger in winter and further south). And short-range local variation that 45 stations cannot see. Hot and cold spells sit on top. There is a warming trend, deliberately faster than the real one, so that change over the nine years is detectable.

Stations: accurate but sparse, roughly one per 100,000 km², with gaps. Gridded product: complete but carries a smooth bias and an error that drifts from day to day, about 1.3 °C overall. Neither is the truth. The organisers hold 15 stations back for scoring.

Humidity, dew point, wind speed and UTCI are derived from the same weather. Whether they add anything over tmax is a question for you.

## Things to watch

- `anc_visits` is counted over the whole pregnancy. Think about what that does to its link with gestational age before you adjust for it.
- Education and socio-economic grade are related. Check what each does with the other in the model.
- Exposure windows anchored on the birth date give biased answers. Anchor on the last menstrual period, or use the person-week set-up in example 02.
- Births at the very start and end of the period were removed because their pregnancies were only partly observed. The district weekly births file covers whole weeks only, so it also leaves out the 588 births in the part weeks at either end (see `docs/files.md`).
- There is no missing data in the participant files. Real data would have it, left blank.
- Each location is one urban or one rural facility in a district. Linking exposure at district level treats everyone at both facilities alike.

## Workshop tasks

1. Build a daily temperature surface for the whole region from the stations, the gridded product, or both. SPDE, functional kriging, physics-informed penalised regression and neural networks all fit here. The steering wind is released for methods that can use transport.
2. Score it. The organisers can score predictions at the 15 held-out stations, against the true temperature at each station's 0.25 degree cell. Report error as well as uncertainty, as in the Heaton et al. case study.
3. Average to districts and link to outcomes. Person-week hazard models, distributed lag models, or weekly district counts with an at-risk offset.
4. Ask the main question: is temperature, or week-on-week change in temperature, related to preterm birth? Does the answer depend on the surface you used?

Example results from simple versions of each method are in `docs/method_comparison.md`. Treat them as a floor to beat.

## Citation and contact

HE²AT Center, Wits Planetary Health Research. Synthetic southern Africa pregnancy and weather dataset, version 4, 2026. Data CC BY 4.0, code MIT.

Craig Parker, craig.parker@witsphr.org
