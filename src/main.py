from typing import Optional
import datasets as hf_datasets
import pandas as pd
from utils.fs import create_dir, rimraf
from constants import WORKSPACE_PATH, OUT_DIR, REPORT_DIR
from dataset import get_nasa_power_dataset
from steps.step_00_download import get_us_wildfires_dataset

if __name__ == "__main__":
    create_dir(OUT_DIR)
    rimraf(REPORT_DIR)
    create_dir(REPORT_DIR)

    ds_nasa_power = get_nasa_power_dataset()
    print(ds_nasa_power)

    # ds_us_wildfires = get_us_wildfires_dataset()
    # print(ds_us_wildfires)
