# Method comparison: a floor to beat

Simple versions of each method family, run only on the released files and scored against the true field at 15 stations the organisers hold back. Weekly district RMSE is against the true district mean. Code is with the organisers.

| Method | Data | Daily RMSE at 15 held-out stations (°C) | Weekly district RMSE (°C) |
|---|---|---|---|
| Nearest station | stations only | 3.29 | 1.51 |
| Inverse distance (45 stations) | stations only | 2.46 | 1.23 |
| Universal kriging (elevation, latitude drift) | stations only | 2.43 | 1.19 |
| 0.5 degree product, lapse corrected | product | 1.32 | 0.99 |
| Product plus kriged station residuals | stations + product | 0.99 | 0.47 |
| SPDE (Matern GMRF) | stations only | 2.59 | 1.36 |
| Functional kriging (B-spline curves) | stations only | 2.65 | 1.42 |
| Physics-informed PDE regression, advection | stations only | 3.02 | 1.83 |
| Physics-informed PDE regression, no advection | stations only | 3.03 | 1.80 |
| SPDE on station minus product | stations + product | 0.99 | 0.49 |
| Functional kriging of station minus product | stations + product | 1.12 | 0.56 |
| Physics-informed PDE regression on station minus product | stations + product | 1.16 | 0.70 |
| CNN correction of the product | stations + product | 1.21 | 0.73 |

Stations alone get you to about 2.5 °C. The gridded product alone gets about 1.3 °C. Combining them gets about 1.0 °C. None of these used the steering wind well, and none was tuned hard. Beat them.

What these numbers do not tell you is how much a better surface changes the answer to the health question. That is the second half of the week.
