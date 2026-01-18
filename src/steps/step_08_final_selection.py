# src/steps/step_08_final_selection.py
"""
Krok 8: Wybor zmiennych i rekordow do finalnego zbioru.

Kryteria wykluczenia:
- Kraje z >30% brakujacych danych
- Lata spoza 2000-2020
- Agregaty regionalne

Output:
- out/final/final_panel.parquet
- report/08_final_selection.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import df_info


FINAL_DIR = os.path.join(OUT_DIR, "final")


def select_countries(df: pd.DataFrame, max_missing_pct: float = 30.0) -> Tuple[pd.DataFrame, Dict]:
    """
    Selekcja krajow na podstawie kompletnosci danych.

    Args:
        max_missing_pct: Maksymalny dopuszczalny procent brakow

    Returns:
        Tuple (przefiltrowany DataFrame, statystyki selekcji)
    """
    stats = {"countries_before": df["country"].nunique()}

    # Oblicz procent brakow dla kazdego kraju
    key_cols = ["co2", "co2_per_capita", "gdp", "population"]
    existing_cols = [c for c in key_cols if c in df.columns]

    country_missing = df.groupby("country")[existing_cols].apply(
        lambda x: x.isna().sum().sum() / x.size * 100
    )

    # Kraje do zachowania
    valid_countries = country_missing[country_missing <= max_missing_pct].index.tolist()
    excluded_countries = country_missing[country_missing > max_missing_pct].index.tolist()

    df_filtered = df[df["country"].isin(valid_countries)].copy()

    stats["countries_after"] = df_filtered["country"].nunique()
    stats["countries_excluded"] = len(excluded_countries)
    stats["excluded_list"] = excluded_countries[:20]

    return df_filtered, stats


def select_years(df: pd.DataFrame, min_year: int = 2000, max_year: int = 2020) -> Tuple[pd.DataFrame, Dict]:
    """
    Selekcja lat.

    Returns:
        Tuple (przefiltrowany DataFrame, statystyki)
    """
    stats = {
        "years_before": df["year"].nunique() if "year" in df.columns else 0,
        "year_range_before": f"{df['year'].min()}-{df['year'].max()}" if "year" in df.columns else "N/A"
    }

    if "year" in df.columns:
        df_filtered = df[(df["year"] >= min_year) & (df["year"] <= max_year)].copy()
    else:
        df_filtered = df.copy()

    stats["years_after"] = df_filtered["year"].nunique() if "year" in df_filtered.columns else 0
    stats["year_range_after"] = f"{min_year}-{max_year}"

    return df_filtered, stats


def select_variables(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Selekcja zmiennych do finalnego zbioru.

    Returns:
        Tuple (DataFrame z wybranymi zmiennymi, statystyki)
    """
    # Definicja grup zmiennych
    variable_groups = {
        "identifiers": ["country", "year", "iso_code", "region"],
        "dependent": ["co2", "co2_per_capita", "co2_per_capita_log"],
        "main_predictors": [
            "gdp", "gdp_per_capita", "gdp_per_capita_log",
            "gdp_per_capita_sq", "gdp_per_capita_cu",
            "population", "population_log"
        ],
        "energy": [
            "primary_energy_consumption", "primary_energy_consumption_log",
            "coal_co2", "oil_co2", "gas_co2",
            "fossil_co2", "fossil_share", "coal_share", "oil_share", "gas_share",
            "emission_intensity", "energy_intensity"
        ],
        "renewable": [
            "access_to_electricity_of_population",
            "renewable_energy_share_in_the_total_final_energy_consumption",
            "electricity_from_renewables_twh",
            "renewable_share_change"
        ],
        "dynamics": [
            "co2_change", "co2_pct_change",
            "co2_per_capita_change", "co2_per_capita_pct_change",
            "gdp_change", "gdp_pct_change"
        ],
        "categorical": [
            "development_level"
        ],
        "lagged": [
            "co2_per_capita_lag1", "co2_per_capita_lag5",
            "gdp_lag1", "gdp_lag5"
        ],
        "country_metadata": [
            "urban_population", "agricultural_land",
            "latitude", "longitude"
        ]
    }

    # Zbierz wszystkie zmienne do zachowania (bez duplikatow)
    vars_to_keep = []
    seen = set()
    for group_vars in variable_groups.values():
        for v in group_vars:
            if v not in seen:
                vars_to_keep.append(v)
                seen.add(v)

    # Filtruj tylko istniejace kolumny
    existing_vars = [v for v in vars_to_keep if v in df.columns]

    # Dodaj zmienne ktore moga miec rozne nazwy (bez duplikatow)
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ["renewable", "electricity", "access"]):
            if col not in existing_vars:
                existing_vars.append(col)

    # Usun ewentualne duplikaty
    existing_vars = list(dict.fromkeys(existing_vars))

    df_selected = df[existing_vars].copy()

    stats = {
        "vars_before": len(df.columns),
        "vars_after": len(df_selected.columns),
        "vars_by_group": {
            group: len([v for v in vars if v in df_selected.columns])
            for group, vars in variable_groups.items()
        }
    }

    return df_selected, stats


def validate_final_dataset(df: pd.DataFrame) -> Dict:
    """
    Walidacja finalnego zbioru danych.

    Returns:
        Dict z wynikami walidacji
    """
    validation = {
        "rows": len(df),
        "columns": len(df.columns),
        "countries": df["country"].nunique() if "country" in df.columns else 0,
        "years": df["year"].nunique() if "year" in df.columns else 0,
        "year_range": f"{df['year'].min()}-{df['year'].max()}" if "year" in df.columns else "N/A"
    }

    # Sprawdz kompletnosc kluczowych zmiennych
    key_vars = ["co2", "co2_per_capita", "gdp", "population"]
    for var in key_vars:
        if var in df.columns:
            validation[f"{var}_coverage"] = round(df[var].notna().sum() / len(df) * 100, 2)

    # Sprawdz duplikaty
    if "country" in df.columns and "year" in df.columns:
        duplicates = df.duplicated(subset=["country", "year"]).sum()
        validation["duplicates"] = duplicates

    # Sprawdz regiony
    if "region" in df.columns:
        validation["regions"] = df["region"].nunique()
        validation["region_coverage"] = round(df["region"].notna().sum() / len(df) * 100, 2)

    return validation


def generate_selection_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    country_stats: Dict,
    year_stats: Dict,
    var_stats: Dict,
    validation: Dict
) -> str:
    """
    Generuje raport selekcji.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Wybor zmiennych i rekordow")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport dokumentuje proces selekcji zmiennych i rekordow "
        "do finalnego zbioru danych przeznaczonego do modelowania."
    )

    report.add_key_value_table({
        "Wiersze przed selekcja": f"{len(df_before):,}",
        "Wiersze po selekcji": f"{len(df_after):,}",
        "Kolumny przed selekcja": len(df_before.columns),
        "Kolumny po selekcji": len(df_after.columns)
    })

    # ==========================================================================
    # 2. Selekcja krajow
    # ==========================================================================
    report.add_separator()
    report.add_heading("Selekcja krajow", level=2)

    report.add_paragraph(
        f"**Kryterium:** Wykluczenie krajow z >30% brakujacych danych "
        f"w kluczowych zmiennych (co2, gdp, population)."
    )

    report.add_key_value_table({
        "Kraje przed": country_stats["countries_before"],
        "Kraje po": country_stats["countries_after"],
        "Wykluczone": country_stats["countries_excluded"]
    })

    if country_stats.get("excluded_list"):
        report.add_paragraph("**Przykladowe wykluczone kraje:**")
        for country in country_stats["excluded_list"][:10]:
            report.add_bullet(country)

    # ==========================================================================
    # 3. Selekcja lat
    # ==========================================================================
    report.add_separator()
    report.add_heading("Selekcja lat", level=2)

    report.add_paragraph(
        f"**Kryterium:** Zakres czasowy 2000-2020 (wspolny dla wszystkich zbiorow)."
    )

    report.add_key_value_table({
        "Zakres przed": year_stats["year_range_before"],
        "Zakres po": year_stats["year_range_after"],
        "Liczba lat": year_stats["years_after"]
    })

    # ==========================================================================
    # 4. Selekcja zmiennych
    # ==========================================================================
    report.add_separator()
    report.add_heading("Selekcja zmiennych", level=2)

    report.add_paragraph(
        "**Kryteria:** Wybrano zmienne istotne dla pytan badawczych oraz "
        "zmienne kontrolne niezbedne do modelowania."
    )

    report.add_key_value_table({
        "Zmienne przed": var_stats["vars_before"],
        "Zmienne po": var_stats["vars_after"]
    })

    report.add_heading("Zmienne wedlug kategorii", level=3)
    for group, count in var_stats["vars_by_group"].items():
        report.add_bullet(f"{group}: {count} zmiennych")

    # ==========================================================================
    # 5. Walidacja finalnego zbioru
    # ==========================================================================
    report.add_separator()
    report.add_heading("Walidacja finalnego zbioru", level=2)

    report.add_heading("Ogolne statystyki", level=3)
    report.add_key_value_table({
        "Liczba obserwacji": f"{validation['rows']:,}",
        "Liczba zmiennych": validation['columns'],
        "Liczba krajow": validation['countries'],
        "Zakres czasowy": validation['year_range'],
        "Duplikaty (country, year)": validation.get('duplicates', 0)
    })

    report.add_heading("Pokrycie kluczowych zmiennych", level=3)
    coverage = {k: f"{v}%" for k, v in validation.items() if k.endswith('_coverage')}
    if coverage:
        report.add_key_value_table(coverage)

    # ==========================================================================
    # 6. Lista finalnych zmiennych
    # ==========================================================================
    report.add_separator()
    report.add_heading("Lista zmiennych w finalnym zbiorze", level=2)

    report.add_code(", ".join(df_after.columns.tolist()))

    # ==========================================================================
    # 7. Podsumowanie
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    report.add_paragraph(
        f"Finalny zbior danych zawiera **{validation['rows']:,} obserwacji** "
        f"dla **{validation['countries']} krajow** w okresie **{validation['year_range']}**."
    )

    report.add_paragraph("**Zapisany plik:**")
    report.add_bullet("`out/final/final_panel.parquet`")

    report.add_paragraph("**Zbiór jest gotowy do:**")
    report.add_bullet("Modelowania regresyjnego (krzywa Kuznetsa)")
    report.add_bullet("Analizy panelowej")
    report.add_bullet("Analizy skupien (clustering)")
    report.add_bullet("Wizualizacji i raportowania")

    # Save report
    report_path = report.save("08_final_selection.md")
    return report_path


def save_final_data(df: pd.DataFrame) -> str:
    """Zapisanie finalnego zbioru danych."""
    os.makedirs(FINAL_DIR, exist_ok=True)
    path = os.path.join(FINAL_DIR, "final_panel.parquet")
    df.to_parquet(path, index=False)
    return path


def run_step_08(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Uruchamia krok 8: Selekcja zmiennych i rekordow.

    Returns:
        Tuple (finalny DataFrame, sciezka do raportu)
    """
    print("=" * 60)
    print("Krok 8: Wybor zmiennych i rekordow")
    print("=" * 60)

    df_before = df.copy()

    # 1. Selekcja krajow
    print("\n  Selekcja krajow (max 30% brakow)...")
    df, country_stats = select_countries(df, max_missing_pct=30.0)
    print(f"    {country_stats['countries_before']} -> {country_stats['countries_after']} krajow")

    # 2. Selekcja lat
    print("\n  Selekcja lat (2000-2020)...")
    df, year_stats = select_years(df, 2000, 2020)
    print(f"    Zakres: {year_stats['year_range_after']}")

    # 3. Selekcja zmiennych
    print("\n  Selekcja zmiennych...")
    df, var_stats = select_variables(df)
    print(f"    {var_stats['vars_before']} -> {var_stats['vars_after']} zmiennych")

    # 4. Walidacja
    print("\n  Walidacja finalnego zbioru...")
    validation = validate_final_dataset(df)
    print(f"    {validation['rows']:,} obserwacji, {validation['columns']} zmiennych")

    # 5. Zapisanie danych
    print("\n  Zapisywanie finalnego zbioru...")
    save_final_data(df)
    print(f"    Zapisano w: {FINAL_DIR}")

    # 6. Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_selection_report(
        df_before, df, country_stats, year_stats, var_stats, validation
    )

    print(f"\n Raport zapisany: {report_path}")

    return df, report_path
