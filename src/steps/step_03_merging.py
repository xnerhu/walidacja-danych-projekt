# src/steps/step_03_merging.py
"""
Krok 3: Laczenie datasetow.

Funkcje:
- merge_owid_sustainable() - laczenie po (country, year)
- add_country_metadata() - dodanie danych przekrojowych
- validate_merge() - walidacja jakosci laczenia
- report_merge_stats() - statystyki laczenia

Output:
- out/merged/merged_panel.parquet (dane panelowe 2000-2020)
- report/03_merging.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import df_info


MERGED_DIR = os.path.join(OUT_DIR, "merged")


def merge_owid_sustainable(
    df_owid: pd.DataFrame,
    df_energy: pd.DataFrame,
    on: List[str] = ["country", "year"]
) -> Tuple[pd.DataFrame, Dict]:
    """
    Laczenie OWID CO2 z Sustainable Energy po (country, year).

    Returns:
        Tuple (polaczony DataFrame, statystyki laczenia)
    """
    stats = {
        "owid_rows": len(df_owid),
        "energy_rows": len(df_energy),
        "owid_countries": df_owid["country"].nunique(),
        "energy_countries": df_energy["country"].nunique()
    }

    # Upewnij sie, ze kolumna year jest typu int
    df_owid = df_owid.copy()
    df_energy = df_energy.copy()

    if "year" in df_owid.columns:
        df_owid["year"] = df_owid["year"].astype(int)
    if "year" in df_energy.columns:
        df_energy["year"] = df_energy["year"].astype(int)

    # Identyfikuj kolumny do usuniecia z energy (duplikaty)
    common_cols = set(df_owid.columns) & set(df_energy.columns) - set(on)
    energy_cols_to_drop = list(common_cols)

    if energy_cols_to_drop:
        df_energy = df_energy.drop(columns=energy_cols_to_drop)

    # Laczenie - left join, aby zachowac wszystkie wiersze z OWID
    df_merged = pd.merge(
        df_owid,
        df_energy,
        on=on,
        how="left",
        suffixes=("", "_energy")
    )

    # Statystyki
    stats["merged_rows"] = len(df_merged)
    stats["merged_countries"] = df_merged["country"].nunique()
    stats["matched_rows"] = df_merged[df_energy.columns.difference(on).tolist()[0] if len(df_energy.columns) > len(on) else "country"].notna().sum() if len(df_energy.columns) > len(on) else 0
    stats["dropped_energy_cols"] = energy_cols_to_drop
    stats["new_cols_from_energy"] = [c for c in df_merged.columns if c not in df_owid.columns]

    return df_merged, stats


def add_country_metadata(
    df_panel: pd.DataFrame,
    df_countries: pd.DataFrame,
    on: str = "country"
) -> Tuple[pd.DataFrame, Dict]:
    """
    Dodanie danych przekrojowych (Countries 2023) do danych panelowych.

    Returns:
        Tuple (DataFrame z metadanymi, statystyki)
    """
    stats = {
        "panel_rows": len(df_panel),
        "countries_rows": len(df_countries),
        "panel_countries": df_panel[on].nunique()
    }

    # Wybor kolumn z Countries 2023 do dodania
    # Unikamy duplikatow z istniejacymi kolumnami
    existing_cols = set(df_panel.columns)
    new_cols = [c for c in df_countries.columns if c not in existing_cols or c == on]

    # Jesli sa kolumny do dodania
    if len(new_cols) > 1:  # wiecej niz tylko 'country'
        df_countries_subset = df_countries[new_cols].copy()

        df_merged = pd.merge(
            df_panel,
            df_countries_subset,
            on=on,
            how="left"
        )
    else:
        df_merged = df_panel.copy()

    stats["final_rows"] = len(df_merged)
    stats["final_cols"] = len(df_merged.columns)
    stats["new_cols"] = [c for c in new_cols if c != on]

    return df_merged, stats


def validate_merge(df: pd.DataFrame, key_cols: List[str]) -> Dict:
    """
    Walidacja jakosci polaczonego zbioru.

    Returns:
        Dict z wynikami walidacji
    """
    validation = {}

    # Sprawdz duplikaty klucza
    duplicates = df.duplicated(subset=key_cols, keep=False)
    validation["duplicate_keys"] = duplicates.sum()

    # Sprawdz kompletnosc kluczowych zmiennych
    key_vars = ["co2", "co2_per_capita", "gdp", "population"]
    for var in key_vars:
        if var in df.columns:
            validation[f"{var}_coverage"] = round(df[var].notna().sum() / len(df) * 100, 2)

    # Zakres czasowy
    if "year" in df.columns:
        validation["year_min"] = int(df["year"].min())
        validation["year_max"] = int(df["year"].max())
        validation["unique_years"] = int(df["year"].nunique())

    # Liczba krajow
    if "country" in df.columns:
        validation["unique_countries"] = int(df["country"].nunique())

    return validation


def analyze_merge_coverage(
    df_owid: pd.DataFrame,
    df_energy: pd.DataFrame,
    df_merged: pd.DataFrame
) -> pd.DataFrame:
    """
    Analiza pokrycia krajow i lat miedzy zbiorami.

    Returns:
        DataFrame z analiza pokrycia
    """
    # Kraje
    owid_countries = set(df_owid["country"].unique())
    energy_countries = set(df_energy["country"].unique())

    # Lata w energy
    energy_years = set(df_energy["year"].unique()) if "year" in df_energy.columns else set()
    owid_years = set(df_owid["year"].unique()) if "year" in df_owid.columns else set()

    coverage_data = []

    for country in sorted(owid_countries):
        in_owid = country in owid_countries
        in_energy = country in energy_countries

        if "year" in df_merged.columns:
            merged_years = df_merged[df_merged["country"] == country]["year"].nunique()
        else:
            merged_years = 0

        coverage_data.append({
            "country": country,
            "in_owid": in_owid,
            "in_energy": in_energy,
            "years_in_merged": merged_years
        })

    return pd.DataFrame(coverage_data)


def generate_merging_report(
    merge_stats: Dict,
    metadata_stats: Dict,
    validation: Dict,
    df_merged: pd.DataFrame,
    coverage_df: pd.DataFrame
) -> str:
    """
    Generuje raport laczenia danych.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Laczenie zbiorow danych")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport dokumentuje proces laczenia trzech zbiorow danych "
        "w jeden spojny zbior panelowy. Laczenie odbywa sie po kluczach "
        "`country` i `year` dla danych czasowych oraz `country` dla danych przekrojowych."
    )

    report.add_paragraph("**Schemat laczenia:**")
    report.add_code("""
OWID CO2 Data                    Sustainable Energy Data
     |                                    |
     | (country, year)                    | (country, year)
     |                                    |
     +----------------+-------------------+
                      |
                      v
              +---------------+
              |  MERGED DATA  |
              |  (2000-2020)  |
              +-------+-------+
                      |
                      | (country)
                      v
              +---------------+
              | Country Info  |
              | (urbanizacja) |
              +---------------+
    """)

    # ==========================================================================
    # 2. Laczenie OWID + Sustainable Energy
    # ==========================================================================
    report.add_separator()
    report.add_heading("Laczenie OWID CO2 z Sustainable Energy", level=2)

    report.add_heading("Statystyki przed laczeniem", level=3)
    report.add_key_value_table({
        "OWID CO2 - wiersze": f"{merge_stats['owid_rows']:,}",
        "OWID CO2 - kraje": merge_stats['owid_countries'],
        "Sustainable Energy - wiersze": f"{merge_stats['energy_rows']:,}",
        "Sustainable Energy - kraje": merge_stats['energy_countries']
    })

    report.add_heading("Wynik laczenia", level=3)
    report.add_key_value_table({
        "Polaczony zbior - wiersze": f"{merge_stats['merged_rows']:,}",
        "Polaczony zbior - kraje": merge_stats['merged_countries'],
        "Nowe kolumny z Energy": len(merge_stats.get('new_cols_from_energy', []))
    })

    if merge_stats.get('dropped_energy_cols'):
        report.add_paragraph("**Usuniete duplikaty kolumn z Energy:**")
        for col in merge_stats['dropped_energy_cols'][:10]:
            report.add_bullet(f"`{col}`")

    if merge_stats.get('new_cols_from_energy'):
        report.add_paragraph("**Nowe kolumny dodane z Sustainable Energy:**")
        for col in merge_stats['new_cols_from_energy'][:15]:
            report.add_bullet(f"`{col}`")

    # ==========================================================================
    # 3. Dodanie metadanych krajow
    # ==========================================================================
    report.add_separator()
    report.add_heading("Dodanie metadanych krajow (Countries 2023)", level=2)

    report.add_key_value_table({
        "Wiersze przed": f"{metadata_stats['panel_rows']:,}",
        "Wiersze po": f"{metadata_stats['final_rows']:,}",
        "Kolumny przed": metadata_stats['panel_rows'],
        "Kolumny po": metadata_stats['final_cols'],
        "Nowe kolumny": len(metadata_stats.get('new_cols', []))
    })

    if metadata_stats.get('new_cols'):
        report.add_paragraph("**Dodane kolumny z Countries 2023:**")
        for col in metadata_stats['new_cols'][:15]:
            report.add_bullet(f"`{col}`")

    # ==========================================================================
    # 4. Walidacja polaczonego zbioru
    # ==========================================================================
    report.add_separator()
    report.add_heading("Walidacja polaczonego zbioru", level=2)

    report.add_heading("Ogolne statystyki", level=3)
    report.add_key_value_table({
        "Liczba wierszy": f"{len(df_merged):,}",
        "Liczba kolumn": len(df_merged.columns),
        "Unikalne kraje": validation['unique_countries'],
        "Zakres lat": f"{validation['year_min']} - {validation['year_max']}",
        "Unikalne lata": validation['unique_years']
    })

    report.add_heading("Pokrycie kluczowych zmiennych", level=3)
    coverage_vars = {k: v for k, v in validation.items() if k.endswith('_coverage')}
    if coverage_vars:
        report.add_key_value_table({
            k.replace('_coverage', ''): f"{v}%"
            for k, v in coverage_vars.items()
        })

    if validation['duplicate_keys'] > 0:
        report.add_warning_box(
            f"Znaleziono {validation['duplicate_keys']} zduplikowanych kluczy (country, year)!"
        )
    else:
        report.add_success_box("Brak zduplikowanych kluczy (country, year).")

    # ==========================================================================
    # 5. Analiza pokrycia krajow
    # ==========================================================================
    report.add_separator()
    report.add_heading("Analiza pokrycia krajow", level=2)

    # Statystyki pokrycia
    in_both = coverage_df[(coverage_df["in_owid"]) & (coverage_df["in_energy"])]
    only_owid = coverage_df[(coverage_df["in_owid"]) & (~coverage_df["in_energy"])]
    only_energy = coverage_df[(~coverage_df["in_owid"]) & (coverage_df["in_energy"])]

    report.add_key_value_table({
        "Kraje w obu zbiorach": len(in_both),
        "Kraje tylko w OWID": len(only_owid),
        "Kraje tylko w Energy": len(only_energy)
    })

    if len(only_owid) > 0:
        report.add_paragraph("**Przykladowe kraje tylko w OWID:**")
        for country in only_owid["country"].head(10).tolist():
            report.add_bullet(country)

    # ==========================================================================
    # 6. Struktura finalnego zbioru
    # ==========================================================================
    report.add_separator()
    report.add_heading("Struktura finalnego zbioru", level=2)

    # Pogrupuj kolumny wedlug kategorii
    id_cols = ["country", "year", "iso_code"]
    emission_cols = [c for c in df_merged.columns if "co2" in c.lower() or "ghg" in c.lower() or "emission" in c.lower()]
    energy_cols = [c for c in df_merged.columns if "energy" in c.lower() or "electricity" in c.lower() or "renewable" in c.lower()]
    economic_cols = [c for c in df_merged.columns if "gdp" in c.lower() or "population" in c.lower()]

    report.add_heading("Kolumny identyfikujace", level=3)
    report.add_paragraph(", ".join([f"`{c}`" for c in id_cols if c in df_merged.columns]))

    report.add_heading("Kolumny emisji (wybrane)", level=3)
    report.add_paragraph(", ".join([f"`{c}`" for c in emission_cols[:10]]))

    report.add_heading("Kolumny energetyczne (wybrane)", level=3)
    report.add_paragraph(", ".join([f"`{c}`" for c in energy_cols[:10]]))

    report.add_heading("Kolumny ekonomiczne", level=3)
    report.add_paragraph(", ".join([f"`{c}`" for c in economic_cols[:10]]))

    # ==========================================================================
    # 7. Podsumowanie
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    report.add_paragraph("**Wynik laczenia:**")
    report.add_numbered(f"Polaczony zbior panelowy: {len(df_merged):,} obserwacji", 1)
    report.add_numbered(f"Liczba krajow: {validation['unique_countries']}", 2)
    report.add_numbered(f"Zakres czasowy: {validation['year_min']}-{validation['year_max']}", 3)
    report.add_numbered(f"Liczba zmiennych: {len(df_merged.columns)}", 4)

    report.add_paragraph("**Zapisany plik:**")
    report.add_bullet("`out/merged/merged_panel.parquet`")

    report.add_paragraph("**Nastepne kroki:**")
    report.add_bullet("Eksploracyjna analiza danych (EDA)")
    report.add_bullet("Tworzenie nowych zmiennych")
    report.add_bullet("Analiza outlierow i brakow danych")

    # Save report
    report_path = report.save("03_merging.md")
    return report_path


def save_merged_data(df: pd.DataFrame, name: str) -> str:
    """
    Zapisanie polaczonego zbioru danych.

    Returns:
        Sciezka do zapisanego pliku
    """
    os.makedirs(MERGED_DIR, exist_ok=True)
    path = os.path.join(MERGED_DIR, f"{name}.parquet")
    df.to_parquet(path, index=False)
    return path


def run_step_03(
    df_owid: pd.DataFrame,
    df_energy: pd.DataFrame,
    df_countries: pd.DataFrame
) -> Tuple[pd.DataFrame, str]:
    """
    Uruchamia krok 3: Laczenie danych.

    Returns:
        Tuple (polaczony DataFrame, sciezka do raportu)
    """
    print("=" * 60)
    print("Krok 3: Laczenie zbiorow danych")
    print("=" * 60)

    # 1. Laczenie OWID z Sustainable Energy
    print("\n  Laczenie OWID CO2 z Sustainable Energy...")
    df_merged, merge_stats = merge_owid_sustainable(df_owid, df_energy)
    print(f"    Wynik: {len(df_merged):,} wierszy, {len(df_merged.columns)} kolumn")

    # 2. Dodanie metadanych krajow
    print("\n  Dodawanie metadanych krajow (Countries 2023)...")
    df_merged, metadata_stats = add_country_metadata(df_merged, df_countries)
    print(f"    Wynik: {len(df_merged):,} wierszy, {len(df_merged.columns)} kolumn")

    # 3. Walidacja
    print("\n  Walidacja polaczonego zbioru...")
    validation = validate_merge(df_merged, ["country", "year"])
    print(f"    Unikalne kraje: {validation['unique_countries']}")
    print(f"    Zakres lat: {validation['year_min']}-{validation['year_max']}")

    # 4. Analiza pokrycia
    coverage_df = analyze_merge_coverage(df_owid, df_energy, df_merged)

    # 5. Zapisanie danych
    print("\n  Zapisywanie polaczonego zbioru...")
    save_merged_data(df_merged, "merged_panel")
    print(f"    Zapisano w: {MERGED_DIR}")

    # 6. Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_merging_report(
        merge_stats, metadata_stats, validation,
        df_merged, coverage_df
    )

    print(f"\n Raport zapisany: {report_path}")

    return df_merged, report_path
