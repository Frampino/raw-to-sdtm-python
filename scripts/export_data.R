# Esporta in CSV i dati grezzi e i domini SDTM di riferimento usati dai test
dir.create("data/raw", recursive = TRUE, showWarnings = FALSE)
dir.create("data/reference", recursive = TRUE, showWarnings = FALSE)

for (d in c("dm_raw", "ds_raw", "ec_raw", "ae_raw")) {
  write.csv(getExportedValue("pharmaverseraw", d), file.path("data/raw", paste0(d, ".csv")), row.names = FALSE, na = "")
}
for (d in c("dm", "ds", "ex", "ae")) {
  write.csv(getExportedValue("pharmaversesdtm", d), file.path("data/reference", paste0(d, ".csv")), row.names = FALSE, na = "")
}
