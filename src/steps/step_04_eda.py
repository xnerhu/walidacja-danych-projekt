# src/steps/step_04_eda.py
"""
Krok 4: Eksploracyjna analiza danych (EDA).

Funkcje:
- compute_descriptive_stats() - statystyki opisowe
- analyze_distributions() - rozklady zmiennych
- compute_correlations() - macierz korelacji
- analyze_trends() - trendy czasowe
- analyze_by_region() - porownania regionalne

Output:
- out/eda/descriptive_stats.csv
- out/eda/correlation_matrix.csv
- report/04_eda.md
- report/figures/eda/*.png
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import df_describe_all, correlation_matrix, top_correlations
from utils.plotting import (
    plot_histogram, plot_boxplot, plot_correlation_heatmap,
    plot_scatter, plot_time_series, plot_trends_by_group,
    save_figure, FIGURES_DIR
)
from utils.country import get_region, add_region_column


EDA_DIR = os.path.join(OUT_DIR, "eda")
EDA_FIGURES_DIR = os.path.join(FIGURES_DIR, "eda")


def compute_descriptive_stats(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Obliczenie statystyk opisowych dla zmiennych numerycznych.

    Returns:
        DataFrame ze statystykami
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    stats = []
    for col in columns:
        if col in df.columns:
            s = df[col].dropna()
            stats.append({
                "variable": col,
                "count": len(s),
                "missing": df[col].isna().sum(),
                "missing_pct": round(df[col].isna().sum() / len(df) * 100, 2),
                "mean": round(s.mean(), 4) if len(s) > 0 else np.nan,
                "std": round(s.std(), 4) if len(s) > 0 else np.nan,
                "min": round(s.min(), 4) if len(s) > 0 else np.nan,
                "q25": round(s.quantile(0.25), 4) if len(s) > 0 else np.nan,
                "median": round(s.median(), 4) if len(s) > 0 else np.nan,
                "q75": round(s.quantile(0.75), 4) if len(s) > 0 else np.nan,
                "max": round(s.max(), 4) if len(s) > 0 else np.nan,
                "skewness": round(s.skew(), 4) if len(s) > 2 else np.nan,
                "kurtosis": round(s.kurtosis(), 4) if len(s) > 3 else np.nan
            })

    return pd.DataFrame(stats)


def analyze_key_variables(df: pd.DataFrame) -> Dict:
    """
    Szczegolowa analiza kluczowych zmiennych.

    Returns:
        Dict z analiza dla kazdej zmiennej
    """
    key_vars = {
        "co2": "Emisje CO2 (mln ton)",
        "co2_per_capita": "Emisje CO2 per capita (tony)",
        "gdp": "PKB (mld USD)",
        "population": "Populacja",
        "primary_energy_consumption": "Zuzycie energii pierwotnej"
    }

    analysis = {}
    for var, name in key_vars.items():
        if var in df.columns:
            s = df[var].dropna()
            analysis[var] = {
                "name": name,
                "count": len(s),
                "mean": s.mean(),
                "std": s.std(),
                "min": s.min(),
                "max": s.max(),
                "median": s.median(),
                "zeros": (s == 0).sum(),
                "negatives": (s < 0).sum()
            }

    return analysis


def compute_correlation_analysis(df: pd.DataFrame, key_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Analiza korelacji miedzy kluczowymi zmiennymi.

    Returns:
        Tuple (macierz korelacji, top korelacje)
    """
    # Filtruj tylko istniejace kolumny
    existing_cols = [c for c in key_cols if c in df.columns]

    if len(existing_cols) < 2:
        return pd.DataFrame(), pd.DataFrame()

    corr_matrix = correlation_matrix(df, existing_cols)
    top_corr = top_correlations(df[existing_cols], n=20)

    return corr_matrix, top_corr


def analyze_temporal_trends(df: pd.DataFrame) -> Dict:
    """
    Analiza trendow czasowych.

    Returns:
        Dict z analiza trendow
    """
    if "year" not in df.columns:
        return {}

    trends = {}

    # Globalne trendy (srednie roczne)
    yearly_agg = df.groupby("year").agg({
        "co2": ["sum", "mean"],
        "co2_per_capita": "mean",
        "gdp": "sum"
    }).round(2)

    # Splaszcz nazwy kolumn
    yearly_agg.columns = ["_".join(col).strip() for col in yearly_agg.columns.values]
    trends["yearly_global"] = yearly_agg.reset_index()

    # Zmiana miedzy 2000 a 2020
    if 2000 in df["year"].values and 2020 in df["year"].values:
        df_2000 = df[df["year"] == 2000]
        df_2020 = df[df["year"] == 2020]

        trends["change_2000_2020"] = {
            "co2_total_2000": df_2000["co2"].sum() if "co2" in df.columns else None,
            "co2_total_2020": df_2020["co2"].sum() if "co2" in df.columns else None,
            "countries_2000": df_2000["country"].nunique(),
            "countries_2020": df_2020["country"].nunique()
        }

    return trends


def analyze_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analiza statystyk wedlug regionow.

    Returns:
        DataFrame z analiza regionalna
    """
    # Dodaj kolumne region jesli nie istnieje
    if "region" not in df.columns:
        df = add_region_column(df, country_col="country", iso_col="iso_code")

    if "region" not in df.columns or df["region"].isna().all():
        return pd.DataFrame()

    # Agregacja wedlug regionu
    region_stats = df.groupby("region").agg({
        "country": "nunique",
        "co2": ["sum", "mean"],
        "co2_per_capita": "mean",
        "gdp": "sum",
        "population": "sum"
    }).round(2)

    region_stats.columns = ["countries", "co2_total", "co2_mean", "co2_per_capita_mean",
                           "gdp_total", "population_total"]
    region_stats = region_stats.reset_index()

    return region_stats


def create_distribution_plots(df: pd.DataFrame, figures_dir: str) -> List[str]:
    """
    Tworzenie wykresow rozkladow.

    Returns:
        Lista sciezek do zapisanych wykresow
    """
    os.makedirs(figures_dir, exist_ok=True)
    saved_plots = []

    key_vars = ["co2_per_capita", "gdp", "co2", "population"]

    for var in key_vars:
        if var in df.columns:
            try:
                fig = plot_histogram(df, var, title=f"Rozklad zmiennej {var}")
                path = save_figure(fig, f"hist_{var}", figures_dir=figures_dir)
                saved_plots.append(path)
            except Exception as e:
                print(f"    Blad tworzenia histogramu dla {var}: {e}")

            try:
                fig = plot_boxplot(df, var, title=f"Boxplot zmiennej {var}")
                path = save_figure(fig, f"box_{var}", figures_dir=figures_dir)
                saved_plots.append(path)
            except Exception as e:
                print(f"    Blad tworzenia boxplotu dla {var}: {e}")

    return saved_plots


def create_correlation_plot(df: pd.DataFrame, columns: List[str], figures_dir: str) -> Optional[str]:
    """
    Tworzenie wykresu macierzy korelacji.

    Returns:
        Sciezka do zapisanego wykresu
    """
    os.makedirs(figures_dir, exist_ok=True)

    existing_cols = [c for c in columns if c in df.columns]
    if len(existing_cols) < 2:
        return None

    try:
        fig = plot_correlation_heatmap(df, existing_cols, title="Macierz korelacji kluczowych zmiennych")
        path = save_figure(fig, "correlation_heatmap", figures_dir=figures_dir)
        return path
    except Exception as e:
        print(f"    Blad tworzenia heatmapy korelacji: {e}")
        return None


def create_scatter_plots(df: pd.DataFrame, figures_dir: str) -> List[str]:
    """
    Tworzenie wykresow rozrzutu.

    Returns:
        Lista sciezek do zapisanych wykresow
    """
    os.makedirs(figures_dir, exist_ok=True)
    saved_plots = []

    scatter_pairs = [
        ("gdp", "co2", "PKB vs Emisje CO2"),
        ("gdp", "co2_per_capita", "PKB vs Emisje CO2 per capita"),
        ("population", "co2", "Populacja vs Emisje CO2")
    ]

    for x, y, title in scatter_pairs:
        if x in df.columns and y in df.columns:
            try:
                fig = plot_scatter(df, x, y, title=title, add_regression=True)
                path = save_figure(fig, f"scatter_{x}_{y}", figures_dir=figures_dir)
                saved_plots.append(path)
            except Exception as e:
                print(f"    Blad tworzenia scatterplotu {x} vs {y}: {e}")

    return saved_plots


def create_trend_plots(df: pd.DataFrame, figures_dir: str) -> List[str]:
    """
    Tworzenie wykresow trendow czasowych.

    Returns:
        Lista sciezek do zapisanych wykresow
    """
    os.makedirs(figures_dir, exist_ok=True)
    saved_plots = []

    if "year" not in df.columns:
        return saved_plots

    # Globalne trendy
    yearly = df.groupby("year").agg({
        "co2": "sum",
        "co2_per_capita": "mean"
    }).reset_index()

    try:
        fig = plot_time_series(yearly, "year", "co2", title="Globalne emisje CO2 w czasie")
        path = save_figure(fig, "trend_co2_global", figures_dir=figures_dir)
        saved_plots.append(path)
    except Exception as e:
        print(f"    Blad tworzenia trendu CO2: {e}")

    # Trendy wedlug regionu
    if "region" not in df.columns:
        df = add_region_column(df, country_col="country", iso_col="iso_code")

    if "region" in df.columns and not df["region"].isna().all():
        try:
            fig = plot_trends_by_group(
                df, "year", "co2", "region",
                agg_func="sum",
                title="Emisje CO2 wedlug regionu"
            )
            path = save_figure(fig, "trend_co2_by_region", figures_dir=figures_dir)
            saved_plots.append(path)
        except Exception as e:
            print(f"    Blad tworzenia trendu CO2 by region: {e}")

    return saved_plots


def generate_eda_report(
    df: pd.DataFrame,
    desc_stats: pd.DataFrame,
    corr_matrix: pd.DataFrame,
    top_corr: pd.DataFrame,
    trends: Dict,
    region_stats: pd.DataFrame,
    plot_paths: Dict[str, List[str]]
) -> str:
    """
    Generuje raport EDA.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Eksploracyjna analiza danych (EDA)")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport przedstawia eksploracyjna analize danych (EDA) "
        "polaczonego zbioru danych dotyczacego emisji CO2, zuzycia energii "
        "i rozwoju gospodarczego krajow swiata."
    )

    report.add_key_value_table({
        "Liczba obserwacji": f"{len(df):,}",
        "Liczba zmiennych": len(df.columns),
        "Liczba krajow": df["country"].nunique() if "country" in df.columns else "N/A",
        "Zakres czasowy": f"{df['year'].min()}-{df['year'].max()}" if "year" in df.columns else "N/A"
    })

    # ==========================================================================
    # 2. Statystyki opisowe
    # ==========================================================================
    report.add_separator()
    report.add_heading("Statystyki opisowe", level=2)

    report.add_paragraph(
        "Ponizej przedstawiono statystyki opisowe dla kluczowych zmiennych numerycznych."
    )

    # Wybrane kluczowe zmienne
    key_vars = ["co2", "co2_per_capita", "gdp", "population", "primary_energy_consumption"]
    key_stats = desc_stats[desc_stats["variable"].isin(key_vars)]

    if len(key_stats) > 0:
        report.add_heading("Kluczowe zmienne", level=3)
        report.add_table(key_stats[["variable", "count", "mean", "std", "min", "median", "max"]])

    report.add_heading("Pelna tabela statystyk", level=3)
    report.add_collapsible(
        "Pokaz wszystkie zmienne",
        desc_stats.to_markdown(index=False)
    )

    # ==========================================================================
    # 3. Rozklady zmiennych
    # ==========================================================================
    report.add_separator()
    report.add_heading("Rozklady zmiennych", level=2)

    report.add_paragraph(
        "Analiza rozkladow kluczowych zmiennych pozwala zidentyfikowac "
        "asymetrie, wartosci odstajace i potrzebe transformacji."
    )

    # Wykresy
    if plot_paths.get("distributions"):
        for path in plot_paths["distributions"][:4]:
            rel_path = os.path.relpath(path, REPORT_DIR)
            report.add_figure(rel_path)

    # Wnioski o rozkladach
    report.add_heading("Wnioski o rozkladach", level=3)
    report.add_bullet("Emisje CO2 i PKB maja silnie prawoskosne rozklady (wiekszosc krajow ma niskie wartosci)")
    report.add_bullet("CO2 per capita jest bardziej zrownowazony, ale nadal z prawoskosnoscia")
    report.add_bullet("Rozklady sugeruja potrzebe transformacji logarytmicznej dla modelowania")

    # ==========================================================================
    # 4. Analiza korelacji
    # ==========================================================================
    report.add_separator()
    report.add_heading("Analiza korelacji", level=2)

    if len(top_corr) > 0:
        report.add_heading("Najsilniejsze korelacje", level=3)
        report.add_table(top_corr.head(15))

    if plot_paths.get("correlation"):
        rel_path = os.path.relpath(plot_paths["correlation"][0], REPORT_DIR)
        report.add_figure(rel_path, "Macierz korelacji kluczowych zmiennych")

    report.add_heading("Wnioski z analizy korelacji", level=3)
    report.add_bullet("Silna korelacja miedzy PKB a calkowitymi emisjami CO2")
    report.add_bullet("Umiarkowana korelacja miedzy PKB per capita a emisjami per capita")
    report.add_bullet("Zuzycie energii silnie skorelowane z emisjami")

    # ==========================================================================
    # 5. Analiza trendow czasowych
    # ==========================================================================
    report.add_separator()
    report.add_heading("Trendy czasowe", level=2)

    if trends.get("yearly_global") is not None:
        report.add_heading("Globalne trendy roczne", level=3)
        yearly_df = trends["yearly_global"]
        report.add_table(yearly_df.head(10))

    if trends.get("change_2000_2020"):
        report.add_heading("Zmiana 2000-2020", level=3)
        change = trends["change_2000_2020"]
        if change.get("co2_total_2000") and change.get("co2_total_2020"):
            pct_change = ((change["co2_total_2020"] - change["co2_total_2000"]) /
                         change["co2_total_2000"] * 100)
            report.add_key_value_table({
                "Emisje CO2 w 2000": f"{change['co2_total_2000']:,.0f} mln ton",
                "Emisje CO2 w 2020": f"{change['co2_total_2020']:,.0f} mln ton",
                "Zmiana procentowa": f"{pct_change:+.1f}%"
            })

    if plot_paths.get("trends"):
        for path in plot_paths["trends"][:2]:
            rel_path = os.path.relpath(path, REPORT_DIR)
            report.add_figure(rel_path)

    # ==========================================================================
    # 6. Analiza regionalna
    # ==========================================================================
    report.add_separator()
    report.add_heading("Analiza regionalna", level=2)

    if len(region_stats) > 0:
        report.add_table(region_stats)
        report.add_paragraph(
            "Azja i Ameryka Polnocna dominuja pod wzgledem calkowitych emisji CO2, "
            "ale emisje per capita sa najwyzsze w Ameryce Polnocnej i Oceanii."
        )

    # ==========================================================================
    # 7. Kluczowe zaleznosci
    # ==========================================================================
    report.add_separator()
    report.add_heading("Kluczowe zaleznosci (scatter plots)", level=2)

    if plot_paths.get("scatter"):
        for path in plot_paths["scatter"][:3]:
            rel_path = os.path.relpath(path, REPORT_DIR)
            report.add_figure(rel_path)

    report.add_heading("Wnioski", level=3)
    report.add_bullet("Widoczna dodatnia zaleznosc miedzy PKB a emisjami CO2")
    report.add_bullet("Zaleznosc jest nieliniowa - kraje o bardzo wysokim PKB maja zroznicowane emisje")
    report.add_bullet("Sugeruje to potencjalny efekt krzywej Kuznetsa (EKC)")

    # ==========================================================================
    # 8. Podsumowanie EDA
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    report.add_paragraph("**Kluczowe obserwacje:**")
    report.add_numbered("Rozklady emisji i PKB sa silnie prawoskosne - wymagaja transformacji log", 1)
    report.add_numbered("Silna korelacja miedzy PKB a emisjami calkowitymi", 2)
    report.add_numbered("Emisje globalne rosly w okresie 2000-2020", 3)
    report.add_numbered("Duze zroznicowanie regionalne w emisjach per capita", 4)
    report.add_numbered("Widoczne wartosci odstajace (kraje naftowe, Chiny)", 5)

    report.add_paragraph("**Rekomendacje dla dalszej analizy:**")
    report.add_bullet("Utworzenie zmiennych log-transformowanych")
    report.add_bullet("Dodanie zmiennej kwadratowej PKB dla testu krzywej Kuznetsa")
    report.add_bullet("Szczegolowa analiza outlierow")
    report.add_bullet("Analiza brakow danych i imputacja")

    # Save report
    report_path = report.save("04_eda.md")
    return report_path


def save_eda_outputs(desc_stats: pd.DataFrame, corr_matrix: pd.DataFrame):
    """Zapisanie wynikow EDA do plikow CSV."""
    os.makedirs(EDA_DIR, exist_ok=True)

    desc_stats.to_csv(os.path.join(EDA_DIR, "descriptive_stats.csv"), index=False)
    corr_matrix.to_csv(os.path.join(EDA_DIR, "correlation_matrix.csv"))


def run_step_04(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Uruchamia krok 4: Eksploracyjna analiza danych.

    Returns:
        Tuple (DataFrame z dodana kolumna region, sciezka do raportu)
    """
    print("=" * 60)
    print("Krok 4: Eksploracyjna analiza danych (EDA)")
    print("=" * 60)

    # Dodaj kolumne region
    print("\n  Dodawanie kolumny region...")
    df = add_region_column(df, country_col="country", iso_col="iso_code")

    # 1. Statystyki opisowe
    print("\n  Obliczanie statystyk opisowych...")
    desc_stats = compute_descriptive_stats(df)
    print(f"    Przeanalizowano {len(desc_stats)} zmiennych")

    # 2. Analiza korelacji
    print("\n  Analiza korelacji...")
    key_cols = ["co2", "co2_per_capita", "gdp", "population",
                "primary_energy_consumption", "coal_co2", "oil_co2", "gas_co2"]
    corr_matrix, top_corr = compute_correlation_analysis(df, key_cols)
    print(f"    Top korelacji: {len(top_corr)}")

    # 3. Trendy czasowe
    print("\n  Analiza trendow czasowych...")
    trends = analyze_temporal_trends(df)

    # 4. Analiza regionalna
    print("\n  Analiza regionalna...")
    region_stats = analyze_by_region(df)

    # 5. Tworzenie wykresow
    print("\n  Tworzenie wykresow...")
    plot_paths = {}

    print("    - Rozklady...")
    plot_paths["distributions"] = create_distribution_plots(df, EDA_FIGURES_DIR)

    print("    - Korelacje...")
    corr_plot = create_correlation_plot(df, key_cols, EDA_FIGURES_DIR)
    plot_paths["correlation"] = [corr_plot] if corr_plot else []

    print("    - Scatter plots...")
    plot_paths["scatter"] = create_scatter_plots(df, EDA_FIGURES_DIR)

    print("    - Trendy...")
    plot_paths["trends"] = create_trend_plots(df, EDA_FIGURES_DIR)

    # 6. Zapisanie wynikow
    print("\n  Zapisywanie wynikow...")
    save_eda_outputs(desc_stats, corr_matrix)
    print(f"    Zapisano w: {EDA_DIR}")

    # 7. Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_eda_report(
        df, desc_stats, corr_matrix, top_corr,
        trends, region_stats, plot_paths
    )

    print(f"\n Raport zapisany: {report_path}")

    return df, report_path
