import sys
from typing import Optional
import datasets as hf_datasets
import os
from constants import WORKSPACE_PATH, DATASET_DIR
from utils.hf import load_hf_dataset, huggingface_from_sqlite
from utils.fs import create_dir
from functools import partial
import pandas as pd
import kagglehub
from utils.kaggle import find_sqlite_file
import sqlite3
from pathlib import Path


import sys
from typing import Optional
import datasets as hf_datasets
import os
from constants import WORKSPACE_PATH, DATASET_DIR
from utils.hf import load_hf_dataset, huggingface_from_sqlite
from utils.fs import create_dir
from functools import partial
import pandas as pd
import kagglehub
from utils.kaggle import find_sqlite_file
import sqlite3
from pathlib import Path


def get_owid_co2_dataset(samples: Optional[int] = None) -> hf_datasets.Dataset:
    """
    Our World in Data - CO2 and Greenhouse Gas Emissions Dataset

    Source: https://github.com/owid/co2-data
    Direct CSV: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv

    Time range: 1750-2023 (most data from 1900+)

    Key variables:
    - country, year, iso_code — identifiers
    - population, gdp — demographic and economic data
    - co2, co2_per_capita, co2_per_gdp — CO2 emissions
    - coal_co2, oil_co2, gas_co2, cement_co2 — emissions by source
    - primary_energy_consumption, energy_per_capita — energy consumption
    - methane, nitrous_oxide — other greenhouse gases
    """
    cache_path = os.path.join(DATASET_DIR, "owid_co2")

    if os.path.exists(cache_path):
        return hf_datasets.load_from_disk(cache_path)

    print("Downloading OWID CO2 dataset from GitHub...")

    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"

    df = pd.read_csv(url)
    print(f"Downloaded {len(df)} rows, {len(df.columns)} columns")

    if samples is not None:
        df = df.head(samples)

    ds = hf_datasets.Dataset.from_pandas(df, preserve_index=False)

    create_dir(cache_path)
    ds.save_to_disk(cache_path)
    print(f"Saved OWID CO2 dataset to {cache_path}")

    return ds


def get_sustainable_energy_dataset(
    samples: Optional[int] = None,
) -> hf_datasets.Dataset:
    """
    Global Data on Sustainable Energy (2000-2020)

    Source: https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy

    Key variables:
    - Entity, Year — identifiers
    - Access to electricity (% of population) — electricity access
    - Renewable energy share in total final energy consumption (%) — OZE share
    - Electricity from renewables (TWh) — renewable production
    - gdp_per_capita, gdp_growth — economic data
    - Density, Land Area — geographic data
    """
    cache_path = os.path.join(DATASET_DIR, "sustainable_energy")

    if os.path.exists(cache_path):
        return hf_datasets.load_from_disk(cache_path)

    print("Downloading Global Data on Sustainable Energy from Kaggle...")

    downloaded_path = kagglehub.dataset_download(
        "anshtanwar/global-data-on-sustainable-energy"
    )

    csv_files = list(Path(downloaded_path).rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {downloaded_path}")

    csv_files.sort(key=lambda p: p.stat().st_size, reverse=True)
    csv_path = csv_files[0]

    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    if samples is not None:
        df = df.head(samples)

    ds = hf_datasets.Dataset.from_pandas(df, preserve_index=False)

    ds.save_to_disk(cache_path)
    print(f"Saved Sustainable Energy dataset to {cache_path}")

    return ds


def get_countries_of_world_dataset(
    samples: Optional[int] = None,
) -> hf_datasets.Dataset:
    """
    Countries of the World 2023 - Cross-sectional country data

    Source: https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023

    Key variables:
    - Country — identifier
    - Urban_population — % of urban population
    - Agricultural Land (%) — economic structure
    - Unemployment Rate, Tax Revenue (%) — economic indicators
    - Population, Density — demographic data
    - GDP, GDP per capita — economic data
    - CO2 Emissions, CPI — additional indicators

    Note: This is cross-sectional data (single snapshot, ~2023),
    not time-series like the other two datasets.
    """
    cache_path = os.path.join(DATASET_DIR, "countries_of_world_2023")

    if os.path.exists(cache_path):
        return hf_datasets.load_from_disk(cache_path)

    print("Downloading Countries of the World 2023 from Kaggle...")

    downloaded_path = kagglehub.dataset_download(
        "nelgiriyewithana/countries-of-the-world-2023"
    )

    csv_files = list(Path(downloaded_path).rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {downloaded_path}")

    csv_files.sort(key=lambda p: p.stat().st_size, reverse=True)
    csv_path = csv_files[0]

    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    if samples is not None:
        df = df.head(samples)

    ds = hf_datasets.Dataset.from_pandas(df, preserve_index=False)

    create_dir(cache_path)
    ds.save_to_disk(cache_path)
    print(f"Saved Countries of the World 2023 dataset to {cache_path}")

    return ds


if __name__ == "__main__":
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
