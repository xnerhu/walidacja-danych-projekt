from typing import Optional
import datasets as hf_datasets
import os
from steps.step_00_download import (
    get_owid_co2_dataset,
    get_sustainable_energy_dataset,
    get_countries_of_world_dataset,
)
from steps.step_01_quality_assessment import run_step_01
from steps.step_02_cleaning import run_step_02
from steps.step_03_merging import run_step_03
from steps.step_04_eda import run_step_04
from steps.step_05_feature_engineering import run_step_05
from steps.step_06_outliers import run_step_06
from steps.step_07_missing_data import run_step_07
from steps.step_08_final_selection import run_step_08
from steps.step_09_export import run_step_09


def step_00():
    """Pobieranie danych."""
    print("=" * 60)
    print("Krok 0: Pobieranie danych")
    print("=" * 60)

    ds_owid = get_owid_co2_dataset()
    print(f"  OWID CO2: {ds_owid}")

    ds_energy = get_sustainable_energy_dataset()
    print(f"  Sustainable Energy: {ds_energy}")

    ds_countries = get_countries_of_world_dataset()
    print(f"  Countries 2023: {ds_countries}")

    print("\n  Wszystkie zbiory danych pobrane!")

    return ds_owid, ds_energy, ds_countries


def main():
    """Glowna funkcja uruchamiajaca pipeline."""
    print("\n" + "=" * 60)
    print("PIPELINE PRZYGOTOWANIA DANYCH")
    print("Temat: Wplyw rozwoju gospodarczego na emisje CO2")
    print("=" * 60 + "\n")

    # Krok 0: Pobranie danych
    ds_owid, ds_energy, ds_countries = step_00()

    # Konwersja do pandas DataFrame
    df_owid = ds_owid.to_pandas()
    df_energy = ds_energy.to_pandas()
    df_countries = ds_countries.to_pandas()

    # Krok 1: Ocena jakosci danych
    print("\n")
    run_step_01(df_owid, df_energy, df_countries)

    # Krok 2: Czyszczenie i standaryzacja
    print("\n")
    df_owid_clean, df_energy_clean, df_countries_clean, _ = run_step_02(
        df_owid, df_energy, df_countries
    )

    # Krok 3: Laczenie zbiorow
    print("\n")
    df_merged, _ = run_step_03(df_owid_clean, df_energy_clean, df_countries_clean)

    # Krok 4: Eksploracyjna analiza danych
    print("\n")
    df_merged, _ = run_step_04(df_merged)

    # Krok 5: Feature engineering
    print("\n")
    df_features, _ = run_step_05(df_merged)

    # Krok 6: Analiza outlierow
    print("\n")
    df_features, _ = run_step_06(df_features)

    # Krok 7: Analiza brakow i imputacja
    print("\n")
    df_imputed, _ = run_step_07(df_features)

    # Krok 8: Selekcja zmiennych i rekordow
    print("\n")
    df_final, _ = run_step_08(df_imputed)

    # Krok 9: Eksport i dokumentacja
    print("\n")
    run_step_09(df_final)

    print("\n" + "=" * 60)
    print("PIPELINE ZAKONCZONY POMYSLNIE")
    print("=" * 60)
    print("\nWygenerowane raporty:")
    print("  - report/01_quality_assessment.md")
    print("  - report/02_cleaning.md")
    print("  - report/03_merging.md")
    print("  - report/04_eda.md")
    print("  - report/05_feature_engineering.md")
    print("  - report/06_outliers.md")
    print("  - report/07_missing_data.md")
    print("  - report/08_final_selection.md")
    print("  - report/09_export.md")
    print("\nFinalny zbior danych:")
    print("  - out/final/final_dataset.parquet")
    print("  - out/final/final_dataset.csv")
    print("  - out/final/codebook.md")


if __name__ == "__main__":
    main()
