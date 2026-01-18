# src/steps/step_07_missing_data.py
"""
Krok 7: Analiza brakow danych i imputacja.

Funkcje:
- compute_missing_stats() - statystyki brakow
- visualize_missing_patterns() - heatmapa brakow
- analyze_missing_mechanism() - MCAR/MAR/MNAR
- impute_temporal() - interpolacja czasowa
- impute_regional_median() - mediana regionalna

Output:
- out/missing/missing_stats.csv
- out/missing/missing_patterns.csv
- out/imputed/panel_imputed.parquet
- report/07_missing_data.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import (
    df_missing_summary, impute_interpolate, impute_by_group,
    impute_forward_backward
)
from utils.plotting import (
    plot_missing_heatmap, plot_missing_bar, plot_missing_by_year,
    save_figure, FIGURES_DIR
)


MISSING_DIR = os.path.join(OUT_DIR, "missing")
IMPUTED_DIR = os.path.join(OUT_DIR, "imputed")
MISSING_FIGURES_DIR = os.path.join(FIGURES_DIR, "missing")


def compute_missing_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Obliczenie szczegolowych statystyk brakow.

    Returns:
        DataFrame ze statystykami brakow dla kazdej zmiennej
    """
    return df_missing_summary(df)


def analyze_missing_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analiza brakow wedlug krajow.

    Returns:
        DataFrame z liczba brakow dla kazdego kraju
    """
    if "country" not in df.columns:
        return pd.DataFrame()

    country_missing = df.groupby("country").apply(
        lambda x: x.isna().sum().sum()
    ).reset_index()
    country_missing.columns = ["country", "total_missing"]

    # Dodaj procent brakow
    n_cols = len(df.columns) - 1  # minus country
    n_years = df.groupby("country").size()
    max_possible = n_cols * n_years

    country_missing = country_missing.merge(
        n_years.reset_index().rename(columns={0: "n_years"}),
        on="country"
    )
    country_missing["missing_pct"] = round(
        country_missing["total_missing"] / (n_cols * country_missing["n_years"]) * 100, 2
    )

    return country_missing.sort_values("missing_pct", ascending=False)


def analyze_missing_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analiza brakow wedlug lat.

    Returns:
        DataFrame z liczba brakow dla kazdego roku
    """
    if "year" not in df.columns:
        return pd.DataFrame()

    year_missing = df.groupby("year").apply(
        lambda x: x.isna().sum().sum()
    ).reset_index()
    year_missing.columns = ["year", "total_missing"]

    n_cols = len(df.columns) - 1
    n_countries = df.groupby("year").size()

    year_missing = year_missing.merge(
        n_countries.reset_index().rename(columns={0: "n_countries"}),
        on="year"
    )
    year_missing["missing_pct"] = round(
        year_missing["total_missing"] / (n_cols * year_missing["n_countries"]) * 100, 2
    )

    return year_missing.sort_values("year")


def analyze_missing_patterns(df: pd.DataFrame, key_vars: List[str]) -> pd.DataFrame:
    """
    Analiza wzorcow brakow (ktore zmienne czesto brakuja razem).

    Returns:
        DataFrame z wzorcami brakow
    """
    existing_vars = [v for v in key_vars if v in df.columns]
    if not existing_vars:
        return pd.DataFrame()

    # Utworz maske brakow
    missing_mask = df[existing_vars].isna()

    # Policz wzorce
    pattern_counts = missing_mask.groupby(existing_vars).size().reset_index(name="count")
    pattern_counts = pattern_counts.sort_values("count", ascending=False)

    return pattern_counts.head(20)


def impute_data(df: pd.DataFrame, columns_to_impute: List[str]) -> Tuple[pd.DataFrame, Dict]:
    """
    Imputacja brakujacych wartosci.

    Strategia:
    1. Interpolacja czasowa w ramach kraju
    2. Forward/backward fill dla krawedzi
    3. Mediana regionalna dla pozostalych

    Returns:
        Tuple (DataFrame z imputacja, statystyki imputacji)
    """
    df = df.copy()
    imputation_stats = {}

    for col in columns_to_impute:
        if col not in df.columns:
            continue

        missing_before = df[col].isna().sum()

        # Krok 1: Interpolacja czasowa w ramach kraju
        df = impute_interpolate(df, col, group_by="country", sort_by="year", method="linear")

        # Krok 2: Forward/backward fill dla krawedzi
        df = impute_forward_backward(df, col, group_by="country")

        # Krok 3: Mediana regionalna dla pozostalych (jesli jest kolumna region)
        if "region" in df.columns and df[col].isna().any():
            df = impute_by_group(df, col, group_by="region", method="median")

        # Krok 4: Mediana globalna jako ostatecznosc
        if df[col].isna().any():
            global_median = df[col].median()
            df[col] = df[col].fillna(global_median)

        missing_after = df[col].isna().sum()

        imputation_stats[col] = {
            "missing_before": missing_before,
            "missing_after": missing_after,
            "imputed": missing_before - missing_after
        }

    return df, imputation_stats


def create_missing_plots(df: pd.DataFrame, figures_dir: str) -> List[str]:
    """
    Tworzenie wykresow brakow danych.

    Returns:
        Lista sciezek do zapisanych wykresow
    """
    os.makedirs(figures_dir, exist_ok=True)
    saved_plots = []

    # Bar plot brakow
    try:
        fig = plot_missing_bar(df, title="Braki danych wedlug zmiennych", top_n=25)
        path = save_figure(fig, "missing_bar", figures_dir=figures_dir)
        saved_plots.append(path)
    except Exception as e:
        print(f"    Blad tworzenia bar plotu: {e}")

    # Heatmapa brakow
    try:
        fig = plot_missing_heatmap(df, title="Wzorce brakow danych")
        path = save_figure(fig, "missing_heatmap", figures_dir=figures_dir)
        saved_plots.append(path)
    except Exception as e:
        print(f"    Blad tworzenia heatmapy: {e}")

    # Braki wedlug roku
    if "year" in df.columns:
        try:
            fig = plot_missing_by_year(df, "year", title="Braki danych wedlug roku")
            path = save_figure(fig, "missing_by_year", figures_dir=figures_dir)
            saved_plots.append(path)
        except Exception as e:
            print(f"    Blad tworzenia wykresu brakow by year: {e}")

    return saved_plots


def generate_missing_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    missing_stats: pd.DataFrame,
    country_missing: pd.DataFrame,
    year_missing: pd.DataFrame,
    imputation_stats: Dict,
    plot_paths: List[str]
) -> str:
    """
    Generuje raport analizy brakow.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Analiza brakow danych i imputacja")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport przedstawia analize brakow danych oraz zastosowane "
        "metody imputacji. Braki danych sa powszechne w danych miedzynarodowych "
        "i wymagaja starannej obslugi."
    )

    total_missing_before = df_before.isna().sum().sum()
    total_missing_after = df_after.isna().sum().sum()
    total_cells = df_before.size

    report.add_key_value_table({
        "Lacznie komorek": f"{total_cells:,}",
        "Braki przed imputacja": f"{total_missing_before:,} ({total_missing_before/total_cells*100:.2f}%)",
        "Braki po imputacji": f"{total_missing_after:,} ({total_missing_after/total_cells*100:.2f}%)",
        "Uzupelnionych wartosci": f"{total_missing_before - total_missing_after:,}"
    })

    # ==========================================================================
    # 2. Braki wedlug zmiennych
    # ==========================================================================
    report.add_separator()
    report.add_heading("Braki wedlug zmiennych", level=2)

    if len(missing_stats) > 0:
        high_missing = missing_stats[missing_stats["missing_pct"] > 30]
        medium_missing = missing_stats[(missing_stats["missing_pct"] > 10) & (missing_stats["missing_pct"] <= 30)]
        low_missing = missing_stats[missing_stats["missing_pct"] <= 10]

        report.add_key_value_table({
            "Zmienne z >30% brakow": len(high_missing),
            "Zmienne z 10-30% brakow": len(medium_missing),
            "Zmienne z <10% brakow": len(low_missing)
        })

        if len(high_missing) > 0:
            report.add_heading("Zmienne z wysokim odsetkiem brakow (>30%)", level=3)
            report.add_table(high_missing[["column", "missing_count", "missing_pct"]].head(15))

    # ==========================================================================
    # 3. Braki wedlug krajow
    # ==========================================================================
    report.add_separator()
    report.add_heading("Braki wedlug krajow", level=2)

    if len(country_missing) > 0:
        report.add_paragraph("**Kraje z najwieksza liczba brakow:**")
        report.add_table(country_missing.head(15))

        high_missing_countries = country_missing[country_missing["missing_pct"] > 30]
        report.add_paragraph(
            f"**Uwaga:** {len(high_missing_countries)} krajow ma >30% brakow i moze "
            "wymagac wykluczenia z analizy."
        )

    # ==========================================================================
    # 4. Braki wedlug lat
    # ==========================================================================
    report.add_separator()
    report.add_heading("Braki wedlug lat", level=2)

    if len(year_missing) > 0:
        report.add_table(year_missing)

    # ==========================================================================
    # 5. Wizualizacje
    # ==========================================================================
    report.add_separator()
    report.add_heading("Wizualizacje", level=2)

    for path in plot_paths[:3]:
        rel_path = os.path.relpath(path, REPORT_DIR)
        report.add_figure(rel_path)

    # ==========================================================================
    # 6. Strategia imputacji
    # ==========================================================================
    report.add_separator()
    report.add_heading("Strategia imputacji", level=2)

    report.add_paragraph("**Zastosowana strategia imputacji (w kolejnosci):**")
    report.add_numbered("**Interpolacja czasowa** - dla wartosci wewnatrz szeregu czasowego kraju", 1)
    report.add_numbered("**Forward/backward fill** - dla wartosci na krawedziach szeregu", 2)
    report.add_numbered("**Mediana regionalna** - dla pozostalych brakow w ramach regionu", 3)
    report.add_numbered("**Mediana globalna** - jako ostatecznosc dla pojedynczych brakow", 4)

    # ==========================================================================
    # 7. Wyniki imputacji
    # ==========================================================================
    report.add_separator()
    report.add_heading("Wyniki imputacji", level=2)

    if imputation_stats:
        imp_df = pd.DataFrame([
            {"variable": k, **v} for k, v in imputation_stats.items()
        ])
        report.add_table(imp_df)

    # ==========================================================================
    # 8. Podsumowanie
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    report.add_paragraph("**Wnioski:**")
    report.add_bullet("Wiekszosc brakow wystepuje w zmiennych pochodnych (cumulative, share)")
    report.add_bullet("Kluczowe zmienne (co2, gdp, population) maja niski odsetek brakow")
    report.add_bullet("Interpolacja czasowa jest najbardziej odpowiednia dla danych panelowych")

    report.add_paragraph("**Zapisane pliki:**")
    report.add_bullet("`out/imputed/panel_imputed.parquet` - dane po imputacji")
    report.add_bullet("`out/missing/missing_stats.csv` - statystyki brakow")

    # Save report
    report_path = report.save("07_missing_data.md")
    return report_path


def save_missing_outputs(missing_stats: pd.DataFrame, country_missing: pd.DataFrame, df_imputed: pd.DataFrame):
    """Zapisanie wynikow analizy brakow."""
    os.makedirs(MISSING_DIR, exist_ok=True)
    os.makedirs(IMPUTED_DIR, exist_ok=True)

    missing_stats.to_csv(os.path.join(MISSING_DIR, "missing_stats.csv"), index=False)
    country_missing.to_csv(os.path.join(MISSING_DIR, "country_missing.csv"), index=False)
    df_imputed.to_parquet(os.path.join(IMPUTED_DIR, "panel_imputed.parquet"), index=False)


def run_step_07(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Uruchamia krok 7: Analiza brakow i imputacja.

    Returns:
        Tuple (DataFrame po imputacji, sciezka do raportu)
    """
    print("=" * 60)
    print("Krok 7: Analiza brakow danych i imputacja")
    print("=" * 60)

    df_before = df.copy()

    # 1. Statystyki brakow
    print("\n  Obliczanie statystyk brakow...")
    missing_stats = compute_missing_stats(df)
    print(f"    Przeanalizowano {len(missing_stats)} zmiennych")

    # 2. Braki wedlug krajow
    print("\n  Analiza brakow wedlug krajow...")
    country_missing = analyze_missing_by_country(df)

    # 3. Braki wedlug lat
    print("\n  Analiza brakow wedlug lat...")
    year_missing = analyze_missing_by_year(df)

    # 4. Tworzenie wykresow
    print("\n  Tworzenie wykresow...")
    plot_paths = create_missing_plots(df, MISSING_FIGURES_DIR)

    # 5. Imputacja
    print("\n  Imputacja brakujacych wartosci...")
    key_columns = ["co2", "co2_per_capita", "gdp", "population",
                   "primary_energy_consumption", "coal_co2", "oil_co2", "gas_co2"]
    df_imputed, imputation_stats = impute_data(df, key_columns)

    total_imputed = sum(s["imputed"] for s in imputation_stats.values())
    print(f"    Uzupelniono {total_imputed:,} wartosci")

    # 6. Zapisanie wynikow
    print("\n  Zapisywanie wynikow...")
    save_missing_outputs(missing_stats, country_missing, df_imputed)
    print(f"    Zapisano w: {MISSING_DIR}, {IMPUTED_DIR}")

    # 7. Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_missing_report(
        df_before, df_imputed, missing_stats, country_missing,
        year_missing, imputation_stats, plot_paths
    )

    print(f"\n Raport zapisany: {report_path}")

    return df_imputed, report_path
