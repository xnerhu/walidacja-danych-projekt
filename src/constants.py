import os

WORKSPACE_PATH = os.getenv("BAZED_WORKSPACE_ROOT", os.getcwd())
OUT_DIR = os.path.join(WORKSPACE_PATH, "out")
REPORT_DIR = os.path.join(WORKSPACE_PATH, "report")
DATASET_DIR = os.path.join(OUT_DIR, "dataset")
