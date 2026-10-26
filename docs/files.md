# Files and columns

All weather files run daily from 2100-01-01 to 2108-12-31. Day 0 is 2100-01-01. Week k covers days 7k to 7k+6.

## Participant data (HE²AT harmonised layout)

Laid out the way the real HE²AT RP1 data is harmonised, so code written here runs on the real thing with few changes.

- `long/<STUDY CODE>_long.csv.gz`: one file per study. Seven columns, in this order: `STUDY CODE | PT ID | DATE | VARIABLE | VALUE | RELATION | LOCATION ID`. 23 variables per pregnancy, 4,294,399 rows in all.
- `master_long.csv.gz`: the seven study files stacked, nothing else changed.
- `participants_wide.parquet` / `.csv.gz`: `master_long` pivoted to one row per pregnancy (186,713 rows). Same names and values. Use it if you would rather not pivot.
- `per_patient_exposures.csv.gz`: PM2.5 by trimester, keyed by `STUDY CODE` and `PT ID`. Columns `pm2p5_mean_t1`, `pm2p5_mean_t2`, `pm2p5_mean_t3`, `pm2p5_mean_pregnancy` (µg/m³), plus `LOCATION ID`.
- `locations.csv`: one row per `LOCATION ID` (160 health facilities) with its study, facility type, district and urban or rural setting. No names, no coordinates. Join on `LOCATION ID` to reach the district files below. Columns: `Loc_id` (the `LOCATION ID`), `Study_unique_ID` (the `STUDY CODE`), `Loc_type` (always `Health facility`), `District` (a `district_id`), `urban_rural`.

Variables and codes are in `data_dictionary.csv` and `codebook.md`. The mother and her child share one PT ID; `RELATION` says whose value it is. Read the long files with every column as text and blanks as blank, for example `pd.read_csv(f, dtype=str, keep_default_na=False)`.

## districts.csv, districts.geojson, district_cells_0p25deg.csv

80 invented districts in seven countries. `districts.geojson` has the boundaries (dissolved 0.25 degree cells). `district_cells_0p25deg.csv` lists every 0.25 degree cell with its district, centre and elevation. Use it to average any surface you build to districts.

- `districts.csv`: `district_id`, `country`, `n_cells` (0.25 degree cells), `centroid_lon`, `centroid_lat` and `mean_elev_m` (means over the district's cells), `area_km2`, `n_births` (released pregnancies booked in the district), `urban_share` (share of those booked at the urban facility).
- `districts.geojson`: one polygon per district, properties `district_id` and `country`.
- `district_cells_0p25deg.csv`: `cell_id`, `lon` and `lat` (cell centre, degrees), `elev_m`, `country`, `district_id`. The `cell_id` is the one the organisers use to score whole surfaces.

## stations.csv, weather_stations_daily.parquet (.csv.gz)

45 stations. `stations.csv` gives `station_id`, `country`, location (`lon`, `lat`, degrees) and elevation (`elev_m`). The daily file has `station_id`, `date` and:

| column | unit | notes |
|---|---|---|
| tmax, tmin | °C | measurement error and a fixed bias per station |
| rain_mm | mm | |
| rh_min_pct, rh_max_pct | % | afternoon and early-morning relative humidity |
| dewpoint_c | °C | |
| wind_speed_ms | m/s | 10 m wind speed |

Stations have gaps (runs of missing days, about 2 to 17 per cent of days once a station is open) and seven open late. Missing is missing for every variable on that day.

## weather_gridded/, gridded_0p5deg_cells.csv

A 0.5 degree gridded product, 1,728 cells, no gaps. Split into three files by year (2100-2102, 2103-2105, 2106-2108). `pd.read_parquet('data/weather_gridded')` or `arrow::open_dataset('data/weather_gridded')` reads all three as one table. Treat it like a reanalysis: complete, smooth, and wrong in ways you have to learn about. Its tmax has a spatially smooth bias, an error that drifts from day to day, and noise. It does not resolve features smaller than the grid.

`gridded_0p5deg_cells.csv` lists the boxes: `cell05_id`, `lon` and `lat` (box centre), `n_cells_0p25` (how many 0.25 degree district cells fall in the box). The daily files have `cell05_id`, `lon`, `lat`, `date` and:

| column | unit | notes |
|---|---|---|
| tmax, tmin | °C | grid-box mean, not at station height |
| rain_mm | mm | |
| wind_u_ms, wind_v_ms | m/s | steering wind, eastward and northward. This is the flow that carries temperature anomalies across the region |
| utci_c | °C | UTCI at the time of tmax |
| rh_min_pct, rh_max_pct | % | |
| dewpoint_c | °C | |
| wind_speed_ms | m/s | 10 m wind speed |

Grid-box tmax is for the box's mean elevation. A lapse rate of about 0.0055 °C per metre works for moving it to a station or cell height.

## district_week_exposure_gridded.csv

Weekly district means from the gridded product, one row per `district_id` and `week_start`: tmax, tmin, rain (weekly total), utci_max, rh_min_pct, dewpoint_c, wind_speed_ms. Each day's district value is the mean of the grid-box values over the district's 0.25 degree cells, with no elevation correction. `utci_max` is the weekly mean of the daily `utci_c` (UTCI at the time of tmax), not a weekly maximum. A ready-made exposure, and the baseline every better method should beat.

## district_week_births.csv

Weekly district counts by week of birth, one row per `district_id` and `week_start`: `births`, `preterm`, `very_preterm`, `stillbirths`, `mean_ga_weeks` (mean gestational age in days divided by 7), `mean_birth_weight_g` (all births). The two means are blank in weeks with no births. Whole weeks only, from the week starting 11 November 2101 to the week starting 22 June 2108: 186,125 births. The 588 births in the part weeks at either end of the birth window (6 November 2101 to 1 July 2108) are in the participant files but not here. For count models, the population at risk in a week is the number of ongoing pregnancies at 22 to 36 weeks, which you can build from the participant file.
