# Codebook: participants file

What every code means in `participants.parquet` / `participants.csv.gz`. Counts are for the released file (186,713 pregnancies). The same codes are in machine-readable form in `codebook.csv`.

## Yes/no variables (0/1)

All yes/no variables use **1 = yes, 0 = no**. There are no missing values.

| Variable | 1 means | 0 means | n with 1 (%) |
|---|---|---|---|
| `preterm` | Born before 37 completed weeks (`ga_days` under 259) | Born at 37 weeks or later | 28,208 (15.1) |
| `very_preterm` | Born before 32 completed weeks (`ga_days` under 224) | Born at 32 weeks or later | 5,350 (2.9) |
| `stillbirth` | Stillbirth | Live birth | 3,672 (2.0) |
| `low_birth_weight` | Birth weight under 2,500 g | 2,500 g or more | 11,795 (6.3) |
| `hiv_positive` | HIV positive at booking | HIV negative at booking | 30,804 (16.5) |
| `anaemia` | Haemoglobin under 11.0 g/dL at booking | 11.0 g/dL or more | 80,351 (43.0) |
| `hypertensive_disorder` | Hypertensive disorder of pregnancy | None recorded | 9,619 (5.2) |
| `outdoor_work_pregnancy` | Worked outdoors during the pregnancy | Did not | 34,039 (18.2) |
| `unimproved_water` | Household uses an unimproved water source | Improved source | 10,040 (5.4) |

`anaemia` was coded before haemoglobin was rounded to one decimal, so a woman shown as exactly 11.0 g/dL can carry either code.

## Socio-economic grade (`ses_grade`)

Five equal groups (quintiles) of a household wealth score. **1 is the least poor, 5 the poorest.** Each grade holds 20 per cent of women.

| Code | Label | n (%) |
|---|---|---|
| 1 | Least poor | 37,357 (20.0) |
| 2 | Second | 37,352 (20.0) |
| 3 | Middle | 37,347 (20.0) |
| 4 | Fourth | 37,298 (20.0) |
| 5 | Poorest | 37,359 (20.0) |

Treat it as categorical, or as ordered. Grade 1 is the natural reference.

## Education (`education`)

Highest level of schooling reached. **0 to 3, higher is more schooling.**

| Code | Label | n (%) |
|---|---|---|
| 0 | None | 21,316 (11.4) |
| 1 | Primary | 77,356 (41.4) |
| 2 | Secondary | 63,531 (34.0) |
| 3 | Tertiary | 24,510 (13.1) |

Education and socio-economic grade are related. Most women in grade 1 have secondary or tertiary schooling, and most in grade 5 have none or primary.

## Text variables

| Variable | Values |
|---|---|
| `country` | ZAF South Africa, MOZ Mozambique, ZMB Zambia, MWI Malawi, ZWE Zimbabwe, BWA Botswana, NAM Namibia |
| `district_id` | Country code plus district number, for example `ZAF_D07`. 80 districts, boundaries in `districts.geojson` |
| `urban_rural` | `urban` or `rural` (residence at booking) |
| `infant_sex` | `male` or `female` |

## Counts and continuous variables

| Variable | Unit | Range | Notes |
|---|---|---|---|
| `age_years` | years | 14 to 48 | Maternal age at booking, whole years |
| `parity` | count | 0 to 15 | Number of previous births |
| `anc_visits` | count | 0 to 14 | Antenatal visits over the whole pregnancy |
| `ga_days` | days | 154 to 314 | Gestational age at birth |
| `ga_weeks` | weeks | 22.0 to 44.9 | `ga_days` / 7, continuous |
| `birth_weight_g` | grams | 350 to 5,600 | |
| `haemoglobin_g_dl` | g/dL | 4.2 to 18.0 | At booking |
| `bmi_booking` | kg/m² | 11.2 to 55.3 | At booking |
| `pm25_t1`, `pm25_t2`, `pm25_t3`, `pm25_mean` | µg/m³ | | Mean PM2.5 in each trimester and over the pregnancy |
| `lmp_date`, `birth_date` | date | | Last menstrual period and date of delivery |
| `id` | | | Pregnancy identifier. Not renumbered after the edge births were trimmed, so there are gaps |

## Applying the labels

R:

```r
p$ses_grade <- factor(p$ses_grade, levels = 1:5,
                      labels = c("Least poor", "Second", "Middle", "Fourth", "Poorest"))
p$education <- factor(p$education, levels = 0:3,
                      labels = c("None", "Primary", "Secondary", "Tertiary"))
```

Stata:

```stata
label define ses 1 "Least poor" 2 "Second" 3 "Middle" 4 "Fourth" 5 "Poorest"
label values ses_grade ses
label define edu 0 "None" 1 "Primary" 2 "Secondary" 3 "Tertiary"
label values education edu
label define yesno 0 "No" 1 "Yes"
label values preterm very_preterm stillbirth low_birth_weight hiv_positive anaemia hypertensive_disorder outdoor_work_pregnancy unimproved_water yesno
```
