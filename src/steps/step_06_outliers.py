# src/steps/step_06_outliers.py
"""
Krok 6: Analiza danych nietypowych (outliers).

Funkcje:
- detect_outliers_iqr() - metoda IQR
- detect_outliers_zscore() - metoda Z-score
- analyze_extreme_cases() - analiza przypadkow ekstremalnych
- decide_outlier_treatment() - strategia obslugi

Output:
- out/outliers/outliers_summary.csv
- out/outliers/extreme_cases.csv
- report/06_outliers.md
- report/figures/outliers/*.png
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import detect_outliers_iqr, detect_outliers_zscore, get_outlier_bounds_iqr
from utils.plotting import (
    plot_boxplot_with_outliers, plot_outliers_scatter,
    save_figure, FIGURES_DIR
)


OUTLIERS_DIR = os.path.join(OUT_DIR, "outliers")
OUTLIERS_FIGURES_DIR = os.path.join(FIGURES_DIR, "outliers")


def detect_outliers_multiple_methods(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Wykrywanie outlierow wieloma metodami.

    Returns:
        DataFrame z informacja o outlierach dla kazdej zmiennej
    """
    results = []

    for col in columns:
        if col not in df.columns:
            continue

        s = df[col].dropna()
        if len(s) == 0:
            continue

        # IQR method
        outliers_iqr = detect_outliers_iqr(df, col)
        lower_iqr, upper_iqr = get_outlier_bounds_iqr(df, col)

        # Z-score method
        outliers_zscore = detect_outliers_zscore(df, col, threshold=3.0)

        results.append({
            "variable": col,
            "n_total": len(s),
            "n_outliers_iqr": outliers_iqr.sum(),
            "pct_outliers_iqr": round(outliers_iqr.sum() / len(df) * 100, 2),
            "n_outliers_zscore": outliers_zscore.sum(),
            "pct_outliers_zscore": round(outliers_zscore.sum() / len(df) * 100, 2),
            "lower_bound_iqr": round(lower_iqr, 4),
            "upper_bound_iqr": round(upper_iqr, 4),
            "min": round(s.min(), 4),
            "max": round(s.max(), 4)
        })

    return pd.DataFrame(results)


def identify_extreme_cases(df: pd.DataFrame, var: str, n_top: int = 10) -> pd.DataFrame:
    """
    Identyfikacja ekstremalnych przypadkow dla danej zmiennej.

    Returns:
        DataFrame z top N ekstremalnych przypadkow
    """
    if var not in df.columns:
        return pd.DataFrame()

    # Top high values
    top_high = df.nlargest(n_top, var)[["country", "year", var]].copy()
    top_high["type"] = "high"

    # Top low values (excluding zeros/negatives for some vars)
    df_positive = df[df[var] > 0] if var in ["co2_per_capita", "gdp"] else df
    top_low = df_positive.nsmallest(n_top, var)[["country", "year", var]].copy()
    top_low["type"] = "low"

    return pd.concat([top_high, top_low]).reset_index(drop=True)


def analyze_known_outliers(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analiza znanych przypadkow outlierow (kraje naftowe, Chiny, itp.).

    Returns:
        Dict z analiza dla roznych kategorii outlierow
    """
    analyses = {}

    # Kraje naftowe (wysokie emisje per capita)
    oil_countries = ["Qatar", "Kuwait", "United Arab Emirates", "Bahrain", "Saudi Arabia"]
    oil_mask = df["country"].isin(oil_countries)
    if oil_mask.any():
        analyses["oil_countries"] = df[oil_mask][["country", "year", "co2_per_capita", "gdp", "population"]].copy()

    # Duze gospodarki (Chiny, USA, Indie)
    big_economies = ["China", "United States", "India", "Russia", "Japan"]
    big_mask = df["country"].isin(big_economies)
    if big_mask.any():
        analyses["big_economies"] = df[big_mask][["country", "year", "co2", "co2_per_capita", "gdp"]].copy()

    # Kraje skandynawskie (niskie emisje per capita przy wysokim PKB)
    nordic = ["Norway", "Sweden", "Denmark", "Finland", "Iceland"]
    nordic_mask = df["country"].isin(nordic)
    if nordic_mask.any():
        analyses["nordic_countries"] = df[nordic_mask][["country", "year", "co2_per_capita", "gdp"]].copy()

    return analyses


def create_outlier_plots(df: pd.DataFrame, figures_dir: str) -> List[str]:
    """
    Tworzenie wykresow outlierow.

    Returns:
        Lista sciezek do zapisanych wykresow
    """
    os.makedirs(figures_dir, exist_ok=True)
    saved_plots = []

    key_vars = ["co2_per_capita", "co2", "gdp"]

    for var in key_vars:
        if var in df.columns:
            try:
                fig = plot_boxplot_with_outliers(
                    df, var, label_col="country", n_labels=5,
                    title=f"Boxplot z outlierami: {var}"
                )
                path = save_figure(fig, f"outliers_box_{var}", figures_dir=figures_dir)
                saved_plots.append(path)
            except Exception as e:
                print(f"    Blad tworzenia boxplotu dla {var}: {e}")

    # Scatter plot: gdp vs co2 z zaznaczonymi outlierami
    if "gdp" in df.columns and "co2" in df.columns:
        try:
            outlier_mask = detect_outliers_iqr(df, "co2")
            fig = plot_outliers_scatter(
                df, "gdp", "co2", outlier_mask, label_col="country",
                title="PKB vs Emisje CO2 (outliery zaznaczone)"
            )
            path = save_figure(fig, "outliers_scatter_gdp_co2", figures_dir=figures_dir)
            saved_plots.append(path)
        except Exception as e:
            print(f"    Blad tworzenia scatter plotu: {e}")

    return saved_plots


def generate_outliers_report(
    outliers_summary: pd.DataFrame,
    extreme_cases: Dict[str, pd.DataFrame],
    known_outliers: Dict[str, pd.DataFrame],
    plot_paths: List[str]
) -> str:
    """
    Generuje raport analizy outlierow.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Analiza danych nietypowych (outliers)")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport przedstawia analize wartosci odstajacych (outlierow) "
        "w zbiorze danych. Outliery moga byc bledy pomiaru lub prawdziwe, "
        "ale ekstremalne wartosci wymagajace interpretacji."
    )

    report.add_paragraph("**Metody wykrywania outlierow:**")
    report.add_bullet("IQR (Interquartile Range): wartosci < Q1-1.5*IQR lub > Q3+1.5*IQR")
    report.add_bullet("Z-score: wartosci z |z| > 3")

    # ==========================================================================
    # 2. Podsumowanie outlierow
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie outlierow wedlug zmiennych", level=2)

    if len(outliers_summary) > 0:
        report.add_table(outliers_summary[["variable", "n_total", "n_outliers_iqr",
                                          "pct_outliers_iqr", "n_outliers_zscore"]])

    # ==========================================================================
    # 3. Ekstremalne przypadki
    # ==========================================================================
    report.add_separator()
    report.add_heading("Ekstremalne przypadki", level=2)

    for var, cases_df in extreme_cases.items():
        if len(cases_df) > 0:
            report.add_heading(f"Ekstrema dla: {var}", level=3)

            high_cases = cases_df[cases_df["type"] == "high"]
            low_cases = cases_df[cases_df["type"] == "low"]

            if len(high_cases) > 0:
                report.add_paragraph("**Najwyzsze wartosci:**")
                report.add_table(high_cases.head(5))

            if len(low_cases) > 0:
                report.add_paragraph("**Najnizsze wartosci:**")
                report.add_table(low_cases.head(5))

    # ==========================================================================
    # 4. Analiza znanych outlierow
    # ==========================================================================
    report.add_separator()
    report.add_heading("Analiza znanych kategorii outlierow", level=2)

    if "oil_countries" in known_outliers and len(known_outliers["oil_countries"]) > 0:
        report.add_heading("Kraje naftowe (wysokie emisje per capita)", level=3)
        report.add_paragraph(
            "Kraje takie jak Katar, Kuwejt czy ZEA maja bardzo wysokie emisje CO2 "
            "per capita ze wzgledu na przemysl naftowy i niewielka populacje."
        )
        summary = known_outliers["oil_countries"].groupby("country").agg({
            "co2_per_capita": "mean",
            "gdp": "mean"
        }).round(2)
        report.add_table(summary.reset_index())

    if "nordic_countries" in known_outliers and len(known_outliers["nordic_countries"]) > 0:
        report.add_heading("Kraje nordyckie (niskie emisje przy wysokim PKB)", level=3)
        report.add_paragraph(
            "Norwegia, Szwecja i inne kraje nordyckie maja relatywnie niskie emisje "
            "pomimo wysokiego PKB - dzieki energii odnawialnej (hydro, wiatr)."
        )
        summary = known_outliers["nordic_countries"].groupby("country").agg({
            "co2_per_capita": "mean",
            "gdp": "mean"
        }).round(2)
        report.add_table(summary.reset_index())

    # ==========================================================================
    # 5. Wykresy
    # ==========================================================================
    report.add_separator()
    report.add_heading("Wizualizacje", level=2)

    for path in plot_paths[:4]:
        rel_path = os.path.relpath(path, REPORT_DIR)
        report.add_figure(rel_path)

    # ==========================================================================
    # 6. Rekomendacje
    # ==========================================================================
    report.add_separator()
    report.add_heading("Rekomendacje dotyczace obslugi outlierow", level=2)

    report.add_paragraph("**Strategia:**")
    report.add_numbered("**Zachowaj** outliery bedace prawdziwymi ekstremalnym wartosciami (kraje naftowe, duze gospodarki)", 1)
    report.add_numbered("**Rozważ winsoryzacje** dla skrajnych wartosci w analizie regresyjnej", 2)
    report.add_numbered("**Dodaj zmienne kontrolne** (region, poziom rozwoju) aby wyjasnic zroznicowanie", 3)
    report.add_numbered("**Przeprowadź analize wrazliwosci** - modele z i bez outlierow", 4)

    report.add_paragraph(
        "**Wniosek:** Wiekszosc outlierow to prawdziwe wartosci odzwierciedlajace "
        "specyfike krajow (kraje naftowe, duze gospodarki). Nie nalezy ich usuwac, "
        "ale uwzglednic w interpretacji wynikow."
    )

    # Save report
    report_path = report.save("06_outliers.md")
    return report_path


def save_outliers_outputs(outliers_summary: pd.DataFrame, extreme_cases: Dict[str, pd.DataFrame]):
    """Zapisanie wynikow analizy outlierow."""
    os.makedirs(OUTLIERS_DIR, exist_ok=True)

    outliers_summary.to_csv(os.path.join(OUTLIERS_DIR, "outliers_summary.csv"), index=False)

    # Polacz ekstremalne przypadki
    all_extreme = []
    for var, df in extreme_cases.items():
        df_copy = df.copy()
        df_copy["source_variable"] = var
        all_extreme.append(df_copy)

    if all_extreme:
        pd.concat(all_extreme).to_csv(os.path.join(OUTLIERS_DIR, "extreme_cases.csv"), index=False)


def run_step_06(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Uruchamia krok 6: Analiza outlierow.

    Returns:
        Tuple (DataFrame bez zmian, sciezka do raportu)
    """
    print("=" * 60)
    print("Krok 6: Analiza danych nietypowych (outliers)")
    print("=" * 60)

    # 1. Wykrywanie outlierow
    print("\n  Wykrywanie outlierow...")
    key_vars = ["co2", "co2_per_capita", "gdp", "population",
                "primary_energy_consumption", "coal_co2", "oil_co2"]
    outliers_summary = detect_outliers_multiple_methods(df, key_vars)
    print(f"    Przeanalizowano {len(outliers_summary)} zmiennych")

    # 2. Ekstremalne przypadki
    print("\n  Identyfikacja ekstremalnych przypadkow...")
    extreme_cases = {}
    for var in ["co2_per_capita", "co2", "gdp"]:
        if var in df.columns:
            extreme_cases[var] = identify_extreme_cases(df, var)

    # 3. Analiza znanych outlierow
    print("\n  Analiza znanych kategorii outlierow...")
    known_outliers = analyze_known_outliers(df)

    # 4. Tworzenie wykresow
    print("\n  Tworzenie wykresow...")
    plot_paths = create_outlier_plots(df, OUTLIERS_FIGURES_DIR)

    # 5. Zapisanie wynikow
    print("\n  Zapisywanie wynikow...")
    save_outliers_outputs(outliers_summary, extreme_cases)
    print(f"    Zapisano w: {OUTLIERS_DIR}")

    # 6. Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_outliers_report(
        outliers_summary, extreme_cases, known_outliers, plot_paths
    )

    print(f"\n Raport zapisany: {report_path}")

    return df, report_path
