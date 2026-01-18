from typing import Optional
import datasets as hf_datasets
import pandas as pd
from utils.fs import create_dir, rimraf
from constants import WORKSPACE_PATH, OUT_DIR, REPORT_DIR
from steps.step_00_download import (
    get_owid_co2_dataset,
    get_sustainable_energy_dataset,
    get_countries_of_world_dataset,
)

if __name__ == "__main__":
    create_dir(OUT_DIR)
    rimraf(REPORT_DIR)
    create_dir(REPORT_DIR)

    ds_owid_co2 = get_owid_co2_dataset()
    print(ds_owid_co2)

    ds_sustainable_energy = get_sustainable_energy_dataset()
    print(ds_sustainable_energy)

    ds_countries = get_countries_of_world_dataset()
    print(ds_countries)
