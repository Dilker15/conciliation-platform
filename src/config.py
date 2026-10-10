import os


# =========================
# Processing configuration
# =========================



TMP_DIRECTORY = os.environ.get("TMP_DIRECTORY", "/tmp")

ATHENA_RESULTS_BUCKET = os.environ.get("ATHENA_RESULTS_PREFIX", "conciliation-parquet-files")
