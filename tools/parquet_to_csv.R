# Write a CSV copy of every Parquet file in data/. Run from the repo root:  Rscript tools/parquet_to_csv.R
# Needs the arrow package: install.packages("arrow")
library(arrow)
files <- list.files("data", pattern = "\\.parquet$", recursive = TRUE, full.names = TRUE)
for (f in files) {
  out <- sub("\\.parquet$", ".csv", f)
  if (file.exists(out) || file.exists(paste0(out, ".gz"))) { message("exists, skipped: ", out); next }
  write_csv_arrow(read_parquet(f), out)
  message("wrote ", out)
}
