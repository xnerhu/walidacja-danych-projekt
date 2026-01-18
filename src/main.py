# src/main.py
"""
Main pipeline for CO2 emissions and economic development analysis.

Project: Impact of Economic Development on CO2 Emissions and Energy Transition
Categories: Economy + Environment

Research Questions:
1. Is there an Environmental Kuznets Curve (EKC)?
2. What structural factors differentiate countries with similar GDP in terms of CO2 emissions?
3. Does GDP growth rate affect the pace of energy transition?
4. How does geographic region moderate the relationship between development and emissions?
5. Which CO2 sources dominate at different levels of economic development?
"""

from typing import Optional
import datasets as hf_datasets
import pandas as pd
from utils.fs import create_dir, rimraf
from constants import WORKSPACE_PATH, OUT_DIR, REPORT_DIR

# Step imports
from steps.step_00_download import (
    get_owid_co2_dataset,
    get_sustainable_energy_dataset,
    get_countries_of_world_dataset,
)
from steps.step_01_quality_assessment import run_quality_assessment


def main():
    """Run the complete data preparation pipeline."""
    print("=" * 60)
    print("CO2 Emissions & Economic Development - Data Preparation")
    print("=" * 60)

    # Setup directories
    create_dir(OUT_DIR)
    rimraf(REPORT_DIR)
    create_dir(REPORT_DIR)

    # =========================================================================
    # Step 00: Download datasets
    # =========================================================================
    print("\n" + "=" * 60)
    print("STEP 00: Downloading datasets")
    print("=" * 60)

    ds_owid_co2 = get_owid_co2_dataset()
    print(f"  OWID CO2: {ds_owid_co2}")

    ds_sustainable_energy = get_sustainable_energy_dataset()
    print(f"  Sustainable Energy: {ds_sustainable_energy}")

    ds_countries = get_countries_of_world_dataset()
    print(f"  Countries 2023: {ds_countries}")

    # =========================================================================
    # Step 01: Quality Assessment
    # =========================================================================
    print("\n" + "=" * 60)
    print("STEP 01: Quality Assessment")
    print("=" * 60)

    report_path = run_quality_assessment(
        ds_owid_co2=ds_owid_co2,
        ds_sustainable_energy=ds_sustainable_energy,
        ds_countries=ds_countries,
    )

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Report: {report_path}")
    print(f"  - Data: {OUT_DIR}")


if __name__ == "__main__":
    main()
