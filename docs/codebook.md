# Codebook: participant data

What every value means in `master_long.csv.gz`, the per-study long files and `participants_wide`. Names, units and category spellings follow the HEAT Master Codebook used for the real HE²AT harmonised data. Five variables are not in that codebook and are marked below. Counts are for the full release (186,713 pregnancies). The same counts are in `codebook.csv`.

There are no missing values. Real data would have them, left blank.

## Identifiers

| Column | What it is |
|---|---|
| `STUDY CODE` | One synthetic study per country: SYNBWA, SYNMOZ, SYNMWI, SYNNAM, SYNZAF, SYNZMB, SYNZWE |
| `PT ID` | Salted hash, 16 characters. One per pregnancy. The child's rows carry the mother's PT ID, with `RELATION = Child` |
| `LOCATION ID` | `STUDYCODE_xx`, the health facility where the woman booked. 160 facilities, one urban and one rural per district. `locations.csv` gives each one's district |
| `RELATION` | `Mother` or `Child` |
| `DATE` | Birth date on delivery outcomes, LMP date on `lnmp`, blank on booking variables |

Location names and coordinates are not released. The geolocation table that holds them stays with the organisers, the same way it stays with the geolocation team for the real data.

## Yes/no variables

Coded `yes` / `no` as in the master codebook. `common.participants()` in the examples converts them to 1/0.

| Variable | Relation | yes means | n yes (%) |
|---|---|---|---|
| `prem_birth` | Child | Born before 37 completed weeks (`gest_age_delivery_days` under 259) | 28,208 (15.1) |
| `very_prem_birth` | Child | Born before 32 completed weeks (under 224 days) | 5,350 (2.9) |
| `stillbirth` | Child | Stillbirth | 3,672 (2.0) |
| `low_birth_weight` | Child | Birth weight under 2,500 g | 11,795 (6.3) |
| `hypertension_preg` | Mother | Hypertensive disorder of pregnancy | 9,619 (5.2) |
| `anaemia` * | Mother | Haemoglobin under 11.0 g/dL at booking | 80,351 (43.0) |
| `outdoor_work_preg` * | Mother | Worked outdoors during the pregnancy | 34,039 (18.2) |
| `water_source_unimproved` * | Mother | Household uses an unimproved water source | 10,040 (5.4) |

`hiv_status` (Mother) is `positive` (30,804, 16.5%) or `negative`. `sex` (Child) is `Male` (95,511) or `Female` (91,202).

`anaemia` was coded before haemoglobin was rounded to one decimal, so a woman shown as exactly 11.0 g/dL can carry either value.

\* Not in the HEAT Master Codebook. Kept because the workshop tasks use them.

## Socio-economic grade (`ses_quintile`) *

Five equal groups of a household wealth score. **1 is the least poor, 5 the poorest.** Each holds 20 per cent of women (37,298 to 37,359). Treat it as categorical, or as ordered. Grade 1 is the natural reference.

## Education (`education_cat`)

Highest level of schooling reached: `none` 21,316 (11.4%), `primary` 77,356 (41.4%), `secondary` 63,531 (34.0%), `tertiary` 24,510 (13.1%).

Education and socio-economic grade are related. Most women in grade 1 have secondary or tertiary schooling, and most in grade 5 have none or primary.

## Counts and continuous variables

| Variable | Relation | Unit | Range | Notes |
|---|---|---|---|---|
| `age_years` | Mother | years | 14 to 48 | At booking, whole years |
| `parity` | Mother | count | 0 to 15 | Previous births |
| `anc_visits` * | Mother | count | 0 to 14 | Antenatal visits over the whole pregnancy |
| `haemoglobin` | Mother | g/dL | 4.2 to 18.0 | At booking |
| `bmi` | Mother | kg/m² | 11.2 to 55.3 | At booking, one decimal |
| `gest_age_delivery_days` | Child | days | 154 to 314 | Gestational age at birth |
| `gest_age_delivery_weeks` | Child | weeks | 22 to 44 | Completed weeks. Divide days by 7 for a continuous value |
| `birth_weight` | Child | g | 350 to 5,600 | |
| `lnmp`, `dob` | Mother, Child | date | | Last normal menstrual period, date of delivery |

PM2.5 is in the exposure file (`per_patient_exposures.csv.gz`), keyed by the same PT ID: `pm2p5_mean_t1`, `_t2`, `_t3` and `_pregnancy`, in µg/m³.

## Applying labels

R:

```r
p$ses_quintile  <- factor(p$ses_quintile, levels = 1:5,
                          labels = c("Least poor", "Second", "Middle", "Fourth", "Poorest"))
p$education_cat <- factor(p$education_cat, levels = c("none", "primary", "secondary", "tertiary"))
yn <- c("prem_birth", "very_prem_birth", "stillbirth", "low_birth_weight", "hypertension_preg",
        "anaemia", "outdoor_work_preg", "water_source_unimproved")
p[yn] <- lapply(p[yn], function(x) as.integer(x == "yes"))
```

Stata:

```stata
foreach v in prem_birth very_prem_birth stillbirth low_birth_weight hypertension_preg anaemia outdoor_work_preg water_source_unimproved {
    gen byte `v'_n = (`v' == "yes")
}
label define ses 1 "Least poor" 2 "Second" 3 "Middle" 4 "Fourth" 5 "Poorest"
label values ses_quintile ses
```
