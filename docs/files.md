# Files and columns

All weather files run daily from 2100-01-01 to 2108-12-31. Day 0 is 2100-01-01. Week k covers days 7k to 7k+6.

## participants.parquet / participants.csv.gz

One row per pregnancy, 186,713 rows. Columns are in `data_dictionary.csv`. District only, no coordinates.

## districts.csv, districts.geojson, district_cells_0p25deg.csv

80 invented districts in seven countries. `districts.geojson` has the boundaries (dissolved 0.25 degree cells). `district_cells_0p25deg.csv` lists every 0.25 degree cell with its district, centre and elevation. Use it to average any surface you build to districts.

## stations.csv, weather_stations_daily.parquet (.csv.gz)

45 stations. `stations.csv` gives location and elevation.

| column | unit | notes |
|---|---|---|
| tmax, tmin | °C | measurement error and a fixed bias per station |
| rain_mm | mm | |
| rh_min_pct, rh_max_pct | % | afternoon and early-morning relative humidity |
| dewpoint_c | °C | |
| wind_speed_ms | m/s | 10 m wind speed |

Stations have gaps (runs of missing days, 3 to 20 per cent of days) and ten open late. Missing is missing for every variable on that day.

## weather_gridded/, gridded_0p5deg_cells.csv

A 0.5 degree gridded product, 1,728 cells, no gaps. Split into three files by year (2100-2102, 2103-2105, 2106-2108). `pd.read_parquet('data/weather_gridded')` or `arrow::open_dataset('data/weather_gridded')` reads all three as one table. Treat it like a reanalysis: complete, smooth, and wrong in ways you have to learn about. Its tmax has a spatially smooth bias, an error that drifts from day to day, and noise. It does not resolve features smaller than the grid.

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

Weekly district means from the gridded product: tmax, tmin, rain (weekly total), utci_max, rh_min_pct, dewpoint_c, wind_speed_ms. A ready-made exposure, and the baseline every better method should beat.

## district_week_births.csv

Weekly district counts by week of birth: births, preterm, very preterm, stillbirths, mean gestational age, mean birth weight. Restricted to the stable birth window (6 November 2101 to 1 July 2108). For count models, the population at risk in a week is the number of ongoing pregnancies at 22 to 36 weeks, which you can build from the participant file.
