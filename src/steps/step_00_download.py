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


def get_nasa_power_dataset(samples: Optional[int] = None) -> hf_datasets.Dataset:
    """
    https://huggingface.co/datasets/notadib/NASA-Power-Daily-Weather
    """
    path = os.path.join(DATASET_DIR, f"nasa_power")
    if os.path.exists(path):
        return hf_datasets.load_from_disk(path)

    print(f"Downloading NASA Power dataset to {path}")

    # Load in streaming mode to avoid schema conflicts
    dataset = hf_datasets.load_dataset(
        "notadib/NASA-Power-Daily-Weather",
        data_files={"train": "csvs/usa/*_regional_daily.csv"},
        split="train",
        streaming=True,
    )

    dataset = hf_datasets.Dataset.from_generator(
        lambda: (ex for ex in dataset),
        features=dataset.features,
    )

    if samples is not None:
        dataset = dataset.select(range(min(samples, len(dataset))))

    create_dir(path)
    dataset.save_to_disk(path)

    return dataset


def get_us_wildfires_dataset(samples: Optional[int] = None) -> pd.DataFrame:
    """
    https://www.kaggle.com/datasets/behroozsohrabi/us-wildfire-records-6th-edition?select=data.csv
    """

    cache_path = os.path.join(DATASET_DIR, "us_wildfires")
    if os.path.exists(cache_path):
        return hf_datasets.load_from_disk(cache_path)

    downloaded_path = kagglehub.dataset_download(
        "behroozsohrabi/us-wildfire-records-6th-edition"
    )
    sqlite_path = find_sqlite_file(downloaded_path)

    cols = [
        "FOD_ID",
        "FIRE_YEAR",
        "DISCOVERY_DATE",
        "DISCOVERY_DOY",
        "DISCOVERY_TIME",
        "CONT_DATE",
        "CONT_DOY",
        "CONT_TIME",
        "FIRE_SIZE",
        "FIRE_SIZE_CLASS",
        "LATITUDE",
        "LONGITUDE",
        "STATE",
        "COUNTY",
        "FIPS_CODE",
        "FIPS_NAME",
        "NWCG_CAUSE_CLASSIFICATION",
        "NWCG_GENERAL_CAUSE",
        "NWCG_CAUSE_AGE_CATEGORY",
        "FIRE_NAME",
    ]

    ds = huggingface_from_sqlite(
        sqlite_path=sqlite_path,
        out_dir=cache_path,
        table="Fires",
        columns=cols,
        computed_columns={
            "DISCOVERY_DATE_ISO": "date(DISCOVERY_DATE)",
            "CONT_DATE_ISO": "date(CONT_DATE)",
        },
        limit=samples,
        chunk_size=250_000,
    )

    return ds
