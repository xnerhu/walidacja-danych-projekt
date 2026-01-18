# src/steps/step_02_cleaning.py
"""
Krok 2: Czyszczenie i standaryzacja danych.

Funkcje:
- standardize_country_names() - mapowanie nazw krajów
- standardize_column_names() - ujednolicenie nazw kolumn
- filter_aggregates() - usunięcie agregatów (World, Europe, etc.)
- fix_data_types() - konwersja typów
- validate_ranges() - walidacja zakresów

Output:
- out/cleaned/owid_co2_cleaned.parquet
- out/cleaned/sustainable_energy_cleaned.parquet
- out/cleaned/countries_cleaned.parquet
- report/02_cleaning.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import re

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import df_info, standardize_column_names as std_col_names
from utils.country import (
    is_aggregate,
    standardize_country_name,
    get_country_iso,
    COUNTRY_ALIASES
)


CLEANED_DIR = os.path.join(OUT_DIR, "cleaned")


def standardize_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standaryzacja nazw kolumn do formatu snake_case.

    Returns:
        Tuple (DataFrame ze zmienionymi nazwami, słownik mapowań stare -> nowe)
    """
    df = df.copy()
    old_names = df.columns.tolist()
    df = std_col_names(df)
    new_names = df.columns.tolist()

    mapping = {old: new for old, new in zip(old_names, new_names) if old != new}
    return df, mapping


def filter_aggregates(df: pd.DataFrame, country_col: str = "country") -> Tuple[pd.DataFrame, List[str]]:
    """
    Usunięcie agregatów regionalnych (World, Europe, itp.).

    Returns:
        Tuple (przefiltrowany DataFrame, lista usuniętych agregatów)
    """
    if country_col not in df.columns:
        return df, []

    aggregates_found = df[df[country_col].apply(is_aggregate)][country_col].unique().tolist()
    df_filtered = df[~df[country_col].apply(is_aggregate)].copy()

    return df_filtered, aggregates_found


def filter_year_range(df: pd.DataFrame, year_col: str = "year",
                      min_year: int = 2000, max_year: int = 2020) -> pd.DataFrame:
    """
    Filtrowanie do wybranego zakresu lat.
    """
    if year_col not in df.columns:
        return df

    return df[(df[year_col] >= min_year) & (df[year_col] <= max_year)].copy()


def standardize_country_names_in_df(df: pd.DataFrame, country_col: str = "country") -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standaryzacja nazw krajów w DataFrame.

    Returns:
        Tuple (DataFrame ze standaryzowanymi nazwami, słownik mapowań)
    """
    if country_col not in df.columns:
        return df, {}

    df = df.copy()
    original_names = df[country_col].unique().tolist()
    name_mapping = {}

    for name in original_names:
        if pd.isna(name):
            continue
        standardized = standardize_country_name(str(name))
        if standardized != name:
            name_mapping[name] = standardized

    if name_mapping:
        df[country_col] = df[country_col].replace(name_mapping)

    return df, name_mapping


def add_iso_codes(df: pd.DataFrame, country_col: str = "country",
                  iso_col: str = "iso_code") -> pd.DataFrame:
    """
    Dodanie/uzupełnienie kodów ISO dla krajów.
    """
    df = df.copy()

    if iso_col not in df.columns:
        df[iso_col] = None

    # Uzupełnij brakujące kody ISO
    mask = df[iso_col].isna()
    if mask.any():
        df.loc[mask, iso_col] = df.loc[mask, country_col].apply(get_country_iso)

    return df


def validate_percentage_columns(df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
    """
    Walidacja kolumn procentowych (0-100).

    Returns:
        Dict z liczbą wartości poza zakresem dla każdej kolumny
    """
    issues = {}
    for col in columns:
        if col in df.columns:
            invalid_count = ((df[col] < 0) | (df[col] > 100)).sum()
            if invalid_count > 0:
                issues[col] = int(invalid_count)
    return issues


def validate_positive_columns(df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
    """
    Walidacja kolumn, które powinny być nieujemne.

    Returns:
        Dict z liczbą ujemnych wartości dla każdej kolumny
    """
    issues = {}
    for col in columns:
        if col in df.columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                issues[col] = int(negative_count)
    return issues


def clean_owid_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Czyszczenie zbioru OWID CO2.

    Returns:
        Tuple (oczyszczony DataFrame, słownik z informacjami o czyszczeniu)
    """
    cleaning_info = {
        "original_rows": len(df),
        "original_cols": len(df.columns)
    }

    # 1. Standaryzacja nazw kolumn
    df, col_mapping = standardize_column_names(df)
    cleaning_info["column_renames"] = len(col_mapping)

    # 2. Usunięcie agregatów
    df, aggregates = filter_aggregates(df, "country")
    cleaning_info["aggregates_removed"] = len(aggregates)
    cleaning_info["aggregates_list"] = aggregates[:20]

    # 3. Filtrowanie lat (2000-2020)
    df = filter_year_range(df, "year", 2000, 2020)
    cleaning_info["year_range"] = "2000-2020"

    # 4. Standaryzacja nazw krajów
    df, name_mapping = standardize_country_names_in_df(df, "country")
    cleaning_info["country_renames"] = len(name_mapping)
    cleaning_info["country_mapping"] = dict(list(name_mapping.items())[:10])

    # 5. Walidacja
    positive_cols = ["co2", "co2_per_capita", "gdp", "population",
                     "primary_energy_consumption", "coal_co2", "oil_co2", "gas_co2"]
    cleaning_info["validation_positive"] = validate_positive_columns(df, positive_cols)

    # 6. Usunięcie wierszy bez kodu ISO (nie są to prawdziwe kraje)
    if "iso_code" in df.columns:
        rows_before = len(df)
        df = df[df["iso_code"].notna()].copy()
        cleaning_info["rows_without_iso_removed"] = rows_before - len(df)
    else:
        cleaning_info["rows_without_iso_removed"] = 0

    cleaning_info["final_rows"] = len(df)
    cleaning_info["final_cols"] = len(df.columns)
    cleaning_info["unique_countries"] = df["country"].nunique()
    cleaning_info["unique_years"] = df["year"].nunique()

    return df, cleaning_info


def clean_sustainable_energy_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Czyszczenie zbioru Sustainable Energy.

    Returns:
        Tuple (oczyszczony DataFrame, słownik z informacjami o czyszczeniu)
    """
    cleaning_info = {
        "original_rows": len(df),
        "original_cols": len(df.columns)
    }

    # 1. Standaryzacja nazw kolumn
    df, col_mapping = standardize_column_names(df)
    cleaning_info["column_renames"] = len(col_mapping)
    cleaning_info["column_mapping"] = col_mapping

    # 2. Rename Entity to country, Year to year
    renames = {}
    if "entity" in df.columns:
        renames["entity"] = "country"
    if "Entity" in df.columns:
        renames["Entity"] = "country"

    df = df.rename(columns=renames)
    cleaning_info["key_renames"] = renames

    # 3. Usunięcie agregatów
    df, aggregates = filter_aggregates(df, "country")
    cleaning_info["aggregates_removed"] = len(aggregates)

    # 4. Standaryzacja nazw krajów
    df, name_mapping = standardize_country_names_in_df(df, "country")
    cleaning_info["country_renames"] = len(name_mapping)

    # 5. Dodanie kodów ISO
    df = add_iso_codes(df, "country", "iso_code")

    # 6. Walidacja kolumn procentowych
    pct_cols = [col for col in df.columns if "%" in col or "share" in col.lower()]
    cleaning_info["validation_percentage"] = validate_percentage_columns(df, pct_cols)

    cleaning_info["final_rows"] = len(df)
    cleaning_info["final_cols"] = len(df.columns)
    cleaning_info["unique_countries"] = df["country"].nunique()

    return df, cleaning_info


def clean_countries_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Czyszczenie zbioru Countries 2023.

    Returns:
        Tuple (oczyszczony DataFrame, słownik z informacjami o czyszczeniu)
    """
    cleaning_info = {
        "original_rows": len(df),
        "original_cols": len(df.columns)
    }

    # 1. Standaryzacja nazw kolumn
    df, col_mapping = standardize_column_names(df)
    cleaning_info["column_renames"] = len(col_mapping)

    # 2. Rename Country to country
    if "country" not in df.columns and "Country" in df.columns:
        df = df.rename(columns={"Country": "country"})

    # 3. Usunięcie agregatów
    df, aggregates = filter_aggregates(df, "country")
    cleaning_info["aggregates_removed"] = len(aggregates)

    # 4. Standaryzacja nazw krajów
    df, name_mapping = standardize_country_names_in_df(df, "country")
    cleaning_info["country_renames"] = len(name_mapping)

    # 5. Dodanie kodów ISO
    df = add_iso_codes(df, "country", "iso_code")

    # 6. Konwersja kolumn numerycznych (usunięcie separatorów tysięcy, znaków $, % etc.)
    for col in df.columns:
        if df[col].dtype == object:
            # Sprawdź czy wygląda na liczbę z formatowaniem
            sample = df[col].dropna().head(10)
            if len(sample) > 0:
                sample_str = str(sample.iloc[0])
                if any(c.isdigit() for c in sample_str):
                    try:
                        # Usuń $, %, , i spróbuj przekonwertować
                        df[col] = df[col].replace(r'[\$,%]', '', regex=True)
                        df[col] = df[col].replace(r',', '', regex=True)
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except:
                        pass

    cleaning_info["final_rows"] = len(df)
    cleaning_info["final_cols"] = len(df.columns)
    cleaning_info["unique_countries"] = df["country"].nunique()

    return df, cleaning_info


def save_cleaned_data(df: pd.DataFrame, name: str) -> str:
    """
    Zapisanie oczyszczonego zbioru danych.

    Returns:
        Ścieżka do zapisanego pliku
    """
    os.makedirs(CLEANED_DIR, exist_ok=True)
    path = os.path.join(CLEANED_DIR, f"{name}.parquet")
    df.to_parquet(path, index=False)
    return path


def generate_cleaning_report(
    info_owid: Dict,
    info_energy: Dict,
    info_countries: Dict,
    df_owid: pd.DataFrame,
    df_energy: pd.DataFrame,
    df_countries: pd.DataFrame
) -> str:
    """
    Generuje raport czyszczenia danych.

    Returns:
        Ścieżka do zapisanego raportu
    """
    report = ReportBuilder(title="Czyszczenie i standaryzacja danych")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport dokumentuje proces czyszczenia i standaryzacji trzech "
        "zbiorów danych. Celem było przygotowanie danych do łączenia i analizy."
    )

    report.add_paragraph("**Wykonane operacje:**")
    report.add_bullet("Standaryzacja nazw kolumn (snake_case)")
    report.add_bullet("Usunięcie agregatów regionalnych (World, Europe, itp.)")
    report.add_bullet("Filtrowanie do zakresu lat 2000-2020")
    report.add_bullet("Standaryzacja nazw krajów")
    report.add_bullet("Dodanie/weryfikacja kodów ISO")
    report.add_bullet("Walidacja zakresów wartości")

    # ==========================================================================
    # 2. OWID CO2 Data
    # ==========================================================================
    report.add_separator()
    report.add_heading("OWID CO2 Data", level=2)

    report.add_heading("Podsumowanie zmian", level=3)
    report.add_key_value_table({
        "Wiersze (przed)": f"{info_owid['original_rows']:,}",
        "Wiersze (po)": f"{info_owid['final_rows']:,}",
        "Usunięte wiersze": f"{info_owid['original_rows'] - info_owid['final_rows']:,}",
        "Kolumny": info_owid['final_cols'],
        "Unikalne kraje": info_owid['unique_countries'],
        "Unikalne lata": info_owid['unique_years'],
        "Zakres lat": info_owid['year_range']
    })

    report.add_heading("Usunięte agregaty", level=3)
    report.add_paragraph(f"Usunięto {info_owid['aggregates_removed']} agregatów regionalnych:")
    for agg in info_owid['aggregates_list'][:10]:
        report.add_bullet(agg)
    if len(info_owid['aggregates_list']) > 10:
        report.add_paragraph(f"*... i {len(info_owid['aggregates_list']) - 10} więcej*")

    if info_owid['country_mapping']:
        report.add_heading("Przykłady standaryzacji nazw krajów", level=3)
        for old, new in list(info_owid['country_mapping'].items())[:5]:
            report.add_bullet(f"{old} → {new}")

    report.add_heading("Walidacja danych", level=3)
    if info_owid['validation_positive']:
        report.add_paragraph("Znaleziono ujemne wartości w kolumnach, które powinny być nieujemne:")
        for col, count in info_owid['validation_positive'].items():
            report.add_bullet(f"{col}: {count} wartości ujemnych")
    else:
        report.add_paragraph("Brak problemów z walidacją wartości nieujemnych.")

    # ==========================================================================
    # 3. Sustainable Energy
    # ==========================================================================
    report.add_separator()
    report.add_heading("Sustainable Energy", level=2)

    report.add_heading("Podsumowanie zmian", level=3)
    report.add_key_value_table({
        "Wiersze (przed)": f"{info_energy['original_rows']:,}",
        "Wiersze (po)": f"{info_energy['final_rows']:,}",
        "Kolumny (przed)": info_energy['original_cols'],
        "Kolumny (po)": info_energy['final_cols'],
        "Unikalne kraje": info_energy['unique_countries']
    })

    if info_energy.get('column_mapping'):
        report.add_heading("Przykłady zmian nazw kolumn", level=3)
        for old, new in list(info_energy['column_mapping'].items())[:10]:
            report.add_bullet(f"`{old}` → `{new}`")

    # ==========================================================================
    # 4. Countries 2023
    # ==========================================================================
    report.add_separator()
    report.add_heading("Countries 2023", level=2)

    report.add_heading("Podsumowanie zmian", level=3)
    report.add_key_value_table({
        "Wiersze (przed)": f"{info_countries['original_rows']:,}",
        "Wiersze (po)": f"{info_countries['final_rows']:,}",
        "Kolumny (przed)": info_countries['original_cols'],
        "Kolumny (po)": info_countries['final_cols'],
        "Unikalne kraje": info_countries['unique_countries']
    })

    # ==========================================================================
    # 5. Porównanie krajów między zbiorami
    # ==========================================================================
    report.add_separator()
    report.add_heading("Porównanie krajów między zbiorami", level=2)

    countries_owid = set(df_owid["country"].unique())
    countries_energy = set(df_energy["country"].unique())
    countries_2023 = set(df_countries["country"].unique())

    common_all = countries_owid & countries_energy & countries_2023
    common_owid_energy = countries_owid & countries_energy

    report.add_key_value_table({
        "Kraje w OWID CO2": len(countries_owid),
        "Kraje w Sustainable Energy": len(countries_energy),
        "Kraje w Countries 2023": len(countries_2023),
        "Wspólne (wszystkie 3)": len(common_all),
        "Wspólne (OWID + Energy)": len(common_owid_energy)
    })

    # Kraje tylko w jednym zbiorze
    only_owid = countries_owid - countries_energy - countries_2023
    only_energy = countries_energy - countries_owid - countries_2023
    only_2023 = countries_2023 - countries_owid - countries_energy

    if only_owid:
        report.add_paragraph(f"**Kraje tylko w OWID ({len(only_owid)}):** {', '.join(sorted(only_owid)[:10])}...")
    if only_energy:
        report.add_paragraph(f"**Kraje tylko w Sustainable Energy ({len(only_energy)}):** {', '.join(sorted(only_energy)[:10])}...")

    # ==========================================================================
    # 6. Struktura oczyszczonych zbiorów
    # ==========================================================================
    report.add_separator()
    report.add_heading("Struktura oczyszczonych zbiorów", level=2)

    report.add_heading("OWID CO2 - kolumny", level=3)
    report.add_paragraph(f"Liczba kolumn: {len(df_owid.columns)}")
    report.add_paragraph("Kluczowe zmienne:")
    key_cols_owid = ["country", "year", "iso_code", "population", "gdp",
                     "co2", "co2_per_capita", "co2_per_gdp"]
    for col in key_cols_owid:
        if col in df_owid.columns:
            report.add_bullet(f"`{col}` - {df_owid[col].dtype}")

    report.add_heading("Sustainable Energy - kolumny", level=3)
    report.add_code(", ".join(df_energy.columns.tolist()), language="")

    report.add_heading("Countries 2023 - kolumny", level=3)
    report.add_code(", ".join(df_countries.columns.tolist()), language="")

    # ==========================================================================
    # 7. Podsumowanie
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    report.add_paragraph("**Wykonane operacje:**")
    report.add_numbered("Standaryzacja nazw kolumn we wszystkich zbiorach", 1)
    report.add_numbered("Usunięcie agregatów regionalnych", 2)
    report.add_numbered("Filtrowanie OWID do lat 2000-2020", 3)
    report.add_numbered("Standaryzacja nazw krajów (mapowanie aliasów)", 4)
    report.add_numbered("Dodanie kodów ISO do zbiorów, które ich nie miały", 5)

    report.add_paragraph("**Zapisane pliki:**")
    report.add_bullet(f"`out/cleaned/owid_co2_cleaned.parquet` ({info_owid['final_rows']:,} wierszy)")
    report.add_bullet(f"`out/cleaned/sustainable_energy_cleaned.parquet` ({info_energy['final_rows']:,} wierszy)")
    report.add_bullet(f"`out/cleaned/countries_cleaned.parquet` ({info_countries['final_rows']:,} wierszy)")

    report.add_paragraph("**Gotowość do łączenia:**")
    report.add_paragraph(
        f"Po standaryzacji {len(common_owid_energy)} krajów można połączyć między OWID a Sustainable Energy. "
        f"Łączenie będzie wykonane po kluczach `(country, year)` dla danych panelowych."
    )

    # Save report
    report_path = report.save("02_cleaning.md")
    return report_path


def run_step_02(df_owid: pd.DataFrame, df_energy: pd.DataFrame,
                df_countries: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    """
    Uruchamia krok 2: Czyszczenie danych.

    Returns:
        Tuple (df_owid_cleaned, df_energy_cleaned, df_countries_cleaned, report_path)
    """
    print("=" * 60)
    print("Krok 2: Czyszczenie i standaryzacja danych")
    print("=" * 60)

    # Czyszczenie zbiorów
    print("\n  Czyszczenie OWID CO2...")
    df_owid_clean, info_owid = clean_owid_dataset(df_owid)
    print(f"    {info_owid['original_rows']:,} -> {info_owid['final_rows']:,} wierszy")

    print("\n  Czyszczenie Sustainable Energy...")
    df_energy_clean, info_energy = clean_sustainable_energy_dataset(df_energy)
    print(f"    {info_energy['original_rows']:,} -> {info_energy['final_rows']:,} wierszy")

    print("\n  Czyszczenie Countries 2023...")
    df_countries_clean, info_countries = clean_countries_dataset(df_countries)
    print(f"    {info_countries['original_rows']:,} -> {info_countries['final_rows']:,} wierszy")

    # Zapisanie oczyszczonych danych
    print("\n  Zapisywanie oczyszczonych zbiorów...")
    save_cleaned_data(df_owid_clean, "owid_co2_cleaned")
    save_cleaned_data(df_energy_clean, "sustainable_energy_cleaned")
    save_cleaned_data(df_countries_clean, "countries_cleaned")
    print(f"    Zapisano w: {CLEANED_DIR}")

    # Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_cleaning_report(
        info_owid, info_energy, info_countries,
        df_owid_clean, df_energy_clean, df_countries_clean
    )

    print(f"\n✅ Raport zapisany: {report_path}")

    return df_owid_clean, df_energy_clean, df_countries_clean, report_path
