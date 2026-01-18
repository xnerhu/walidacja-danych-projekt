from typing import Optional
import datasets as hf_datasets
import os
import pandas as pd
import kagglehub
from functools import partial
from constants import WORKSPACE_PATH, DATASET_DIR
from utils.hf import load_hf_dataset
from utils.fs import create_dir
from utils.processing import get_worker_cpu


def get_nasa_power_dataset(samples: Optional[int] = None) -> hf_datasets.Dataset:
    """
    https://huggingface.co/datasets/notadib/NASA-Power-Daily-Weather
    """
    path = os.path.join(DATASET_DIR, f"nasa_power")
    if os.path.exists(path):
        dataset = hf_datasets.load_from_disk(path)
        return dataset

    dataset, _label = load_hf_dataset(
        "notadib/NASA-Power-Daily-Weather",
        split="train",
        streaming=False,
        num_proc=get_worker_cpu(),
    )

    if samples is not None:
        dataset = dataset.select(range(min(samples, len(dataset))))

    create_dir(path)
    dataset.save_to_disk(path)

    return dataset


def get_us_wildfires_dataset(samples: Optional[int] = None) -> pd.DataFrame:
    downloaded_path = kagglehub.dataset_download(
        "behroozsohrabi/us-wildfire-records-6th-edition"
    )
    print(downloaded_path)
