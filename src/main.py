from typing import Optional
import datasets as hf_datasets
import os
from steps.step_00_download import (
    get_owid_co2_dataset,
    get_sustainable_energy_dataset,
    get_countries_of_world_dataset,
)


def step_01():
    print("=" * 60)
    print("Step 00: Downloading datasets")
    print("=" * 60)

    ds_owid = get_owid_co2_dataset()
    print(f"  OWID CO2: {ds_owid}")

    ds_energy = get_sustainable_energy_dataset()
    print(f"  Sustainable Energy: {ds_energy}")

    ds_countries = get_countries_of_world_dataset()
    print(f"  Countries 2023: {ds_countries}")

    print("\n✅ All datasets downloaded successfully!")


if __name__ == "__main__":
    step_01()
