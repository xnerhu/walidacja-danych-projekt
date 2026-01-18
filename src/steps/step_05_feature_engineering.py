# src/steps/step_05_feature_engineering.py
"""
Krok 5: Przeksztalcanie i tworzenie nowych zmiennych.

Nowe zmienne:
- co2_per_capita_log - log(co2_per_capita)
- gdp_per_capita_log - log(gdp_per_capita)
- gdp_per_capita_sq - gdp_per_capita^2 (dla krzywej Kuznetsa)
- renewable_share_change - delta renewable_share (YoY)
- co2_change_rate - delta co2 / co2 (%)
- development_level - kwartyle PKB (Low/Medium/High/Very High)
- fossil_share - (coal + oil + gas) / total CO2

Output:
- out/features/panel_with_features.parquet
- report/05_feature_engineering.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder
from utils.df import (
    add_log_column, add_squared_column, add_pct_change,
    add_diff, add_quantile_bins
)
from utils.country import add_region_column


FEATURES_DIR = os.path.join(OUT_DIR, "features")


def add_log_transforms(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Dodanie transformacji logarytmicznych.

    Returns:
        Tuple (DataFrame z nowymi kolumnami, lista dodanych kolumn)
    """
    df = df.copy()
    new_cols = []

    log_vars = ["co2_per_capita", "gdp", "population", "co2",
                "primary_energy_consumption"]

    for var in log_vars:
        if var in df.columns:
            new_col = f"{var}_log"
            # Dodaj maly offset dla wartosci zerowych/ujemnych
            df[new_col] = np.log1p(df[var].clip(lower=0))
            new_cols.append(new_col)

    return df, new_cols


def add_polynomial_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Dodanie cech wielomianowych (dla testu krzywej Kuznetsa).

    Returns:
        Tuple (DataFrame z nowymi kolumnami, lista dodanych kolumn)
    """
    df = df.copy()
    new_cols = []

    # PKB per capita do kwadratu
    if "gdp" in df.columns and "population" in df.columns:
        # Najpierw oblicz gdp_per_capita jesli nie istnieje
        if "gdp_per_capita" not in df.columns:
            df["gdp_per_capita"] = df["gdp"] / df["population"]
            new_cols.append("gdp_per_capita")

    if "gdp_per_capita" in df.columns:
        df["gdp_per_capita_sq"] = df["gdp_per_capita"] ** 2
        new_cols.append("gdp_per_capita_sq")

        # Opcjonalnie: szescian dla lepszego dopasowania
        df["gdp_per_capita_cu"] = df["gdp_per_capita"] ** 3
        new_cols.append("gdp_per_capita_cu")

    return df, new_cols


def add_change_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Dodanie cech zmiany (rok do roku).

    Returns:
        Tuple (DataFrame z nowymi kolumnami, lista dodanych kolumn)
    """
    df = df.copy()
    new_cols = []

    # Sortuj po kraju i roku
    df = df.sort_values(["country", "year"])

    change_vars = {
        "co2": "co2_change",
        "co2_per_capita": "co2_per_capita_change",
        "gdp": "gdp_change"
    }

    for var, new_col in change_vars.items():
        if var in df.columns:
            df[new_col] = df.groupby("country")[var].diff()
            new_cols.append(new_col)

            # Procentowa zmiana
            pct_col = f"{var}_pct_change"
            df[pct_col] = df.groupby("country")[var].pct_change() * 100
            new_cols.append(pct_col)

    # Zmiana udzialu OZE
    oze_cols = [c for c in df.columns if "renewable" in c.lower() and "share" in c.lower()]
    if oze_cols:
        oze_col = oze_cols[0]
        df["renewable_share_change"] = df.groupby("country")[oze_col].diff()
        new_cols.append("renewable_share_change")

    return df, new_cols


def add_categorical_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Dodanie cech kategorycznych.

    Returns:
        Tuple (DataFrame z nowymi kolumnami, lista dodanych kolumn)
    """
    df = df.copy()
    new_cols = []

    # Poziom rozwoju (kwartyle PKB per capita)
    if "gdp_per_capita" in df.columns:
        # Oblicz kwartyle na podstawie sredniej per capita dla kazdego kraju
        country_gdp = df.groupby("country")["gdp_per_capita"].mean()

        labels = ["Low", "Medium", "High", "Very High"]
        country_level = pd.qcut(country_gdp, q=4, labels=labels, duplicates="drop")
        country_level_map = country_level.to_dict()

        df["development_level"] = df["country"].map(country_level_map)
        new_cols.append("development_level")

    # Dodaj region jesli nie istnieje
    if "region" not in df.columns:
        df = add_region_column(df, country_col="country", iso_col="iso_code")
        if "region" in df.columns:
            new_cols.append("region")

    return df, new_cols


def add_ratio_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Dodanie cech stosunkowych.

    Returns:
        Tuple (DataFrame z nowymi kolumnami, lista dodanych kolumn)
    """
    df = df.copy()
    new_cols = []

    # Udzial paliw kopalnych w emisjach CO2
    fossil_cols = ["coal_co2", "oil_co2", "gas_co2"]
    if all(c in df.columns for c in fossil_cols) and "co2" in df.columns:
        df["fossil_co2"] = df["coal_co2"].fillna(0) + df["oil_co2"].fillna(0) + df["gas_co2"].fillna(0)
        df["fossil_share"] = df["fossil_co2"] / df["co2"].replace(0, np.nan)
        new_cols.extend(["fossil_co2", "fossil_share"])

        # Udzial poszczegolnych paliw
        for fuel in ["coal", "oil", "gas"]:
            col = f"{fuel}_co2"
            if col in df.columns:
                share_col = f"{fuel}_share"
                df[share_col] = df[col] / df["co2"].replace(0, np.nan)
                new_cols.append(share_col)

    # Intensywnosc emisji (CO2 per unit GDP)
    if "co2" in df.columns and "gdp" in df.columns:
        df["emission_intensity"] = df["co2"] / df["gdp"].replace(0, np.nan)
        new_cols.append("emission_intensity")

    # Intensywnosc energetyczna
    if "primary_energy_consumption" in df.columns and "gdp" in df.columns:
        df["energy_intensity"] = df["primary_energy_consumption"] / df["gdp"].replace(0, np.nan)
        new_cols.append("energy_intensity")

    return df, new_cols


def add_lag_features(df: pd.DataFrame, lags: List[int] = [1, 5]) -> Tuple[pd.DataFrame, List[str]]:
    """
    Dodanie cech opoznionych (lagged features).

    Returns:
        Tuple (DataFrame z nowymi kolumnami, lista dodanych kolumn)
    """
    df = df.copy()
    new_cols = []

    df = df.sort_values(["country", "year"])

    lag_vars = ["co2_per_capita", "gdp"]

    for var in lag_vars:
        if var in df.columns:
            for lag in lags:
                new_col = f"{var}_lag{lag}"
                df[new_col] = df.groupby("country")[var].shift(lag)
                new_cols.append(new_col)

    return df, new_cols


def generate_feature_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    features_added: Dict[str, List[str]]
) -> str:
    """
    Generuje raport feature engineering.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Przeksztalcanie zmiennych (Feature Engineering)")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport dokumentuje proces tworzenia nowych zmiennych "
        "(feature engineering) na potrzeby dalszej analizy. "
        "Nowe zmienne maja na celu uchycenie nieliniowych zaleznosci, "
        "dynamiki zmian i kategoryzacji krajow."
    )

    report.add_key_value_table({
        "Kolumny przed": len(df_before.columns),
        "Kolumny po": len(df_after.columns),
        "Nowe kolumny": len(df_after.columns) - len(df_before.columns)
    })

    # ==========================================================================
    # 2. Transformacje logarytmiczne
    # ==========================================================================
    report.add_separator()
    report.add_heading("Transformacje logarytmiczne", level=2)

    report.add_paragraph(
        "Transformacje logarytmiczne zastosowano dla zmiennych o silnie "
        "prawoskosnych rozkladach. Uzyto transformacji log1p(x) = log(1+x) "
        "dla obslugi wartosci zerowych."
    )

    if features_added.get("log"):
        report.add_paragraph("**Dodane zmienne:**")
        for col in features_added["log"]:
            report.add_bullet(f"`{col}`")

    report.add_paragraph(
        "**Uzasadnienie:** Transformacja logarytmiczna normalizuje rozklady "
        "i stabilizuje wariancje, co jest istotne dla modelowania regresyjnego."
    )

    # ==========================================================================
    # 3. Cechy wielomianowe
    # ==========================================================================
    report.add_separator()
    report.add_heading("Cechy wielomianowe (dla krzywej Kuznetsa)", level=2)

    report.add_paragraph(
        "Dodano cechy wielomianowe PKB per capita do testowania "
        "hipotezy krzywej srodowiskowej Kuznetsa (EKC), ktora zaklada "
        "odwrocona zaleznosc U miedzy rozwojem a emisjami."
    )

    if features_added.get("polynomial"):
        report.add_paragraph("**Dodane zmienne:**")
        for col in features_added["polynomial"]:
            report.add_bullet(f"`{col}`")

    report.add_paragraph(
        "**Model EKC:** CO2_per_capita = b0 + b1*GDP_pc + b2*GDP_pc^2 + e"
    )
    report.add_paragraph(
        "Jesli b1 > 0 i b2 < 0, to istnieje punkt zwrotny (peak) emisji."
    )

    # ==========================================================================
    # 4. Cechy zmiany (dynamika)
    # ==========================================================================
    report.add_separator()
    report.add_heading("Cechy zmiany (dynamika rok-do-roku)", level=2)

    report.add_paragraph(
        "Dodano cechy uchycujace dynamike zmian w czasie, "
        "co pozwala analizowac tempo transformacji energetycznej."
    )

    if features_added.get("change"):
        report.add_paragraph("**Dodane zmienne:**")
        for col in features_added["change"][:10]:
            report.add_bullet(f"`{col}`")
        if len(features_added["change"]) > 10:
            report.add_paragraph(f"*... i {len(features_added['change']) - 10} wiecej*")

    # ==========================================================================
    # 5. Cechy kategoryczne
    # ==========================================================================
    report.add_separator()
    report.add_heading("Cechy kategoryczne", level=2)

    report.add_paragraph(
        "Dodano zmienne kategoryczne do analizy grupowej i porownawczej."
    )

    if features_added.get("categorical"):
        report.add_paragraph("**Dodane zmienne:**")
        for col in features_added["categorical"]:
            report.add_bullet(f"`{col}`")

    # Rozklad poziomow rozwoju
    if "development_level" in df_after.columns:
        report.add_heading("Rozklad poziomu rozwoju", level=3)
        dev_counts = df_after.groupby("development_level")["country"].nunique()
        report.add_key_value_table(dev_counts.to_dict())

    # ==========================================================================
    # 6. Cechy stosunkowe
    # ==========================================================================
    report.add_separator()
    report.add_heading("Cechy stosunkowe (ratios)", level=2)

    report.add_paragraph(
        "Dodano cechy wyrazajace udzialy i intensywnosci, "
        "co normalizuje porownania miedzy krajami o roznych wielkosciach."
    )

    if features_added.get("ratio"):
        report.add_paragraph("**Dodane zmienne:**")
        for col in features_added["ratio"]:
            report.add_bullet(f"`{col}`")

    # ==========================================================================
    # 7. Cechy opoznione
    # ==========================================================================
    report.add_separator()
    report.add_heading("Cechy opoznione (lagged)", level=2)

    report.add_paragraph(
        "Dodano zmienne opoznione o 1 i 5 lat, co pozwala "
        "modelowac efekty opoznione i przyczynowe."
    )

    if features_added.get("lag"):
        report.add_paragraph("**Dodane zmienne:**")
        for col in features_added["lag"]:
            report.add_bullet(f"`{col}`")

    # ==========================================================================
    # 8. Podsumowanie
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    total_new = sum(len(v) for v in features_added.values())

    report.add_key_value_table({
        "Transformacje log": len(features_added.get("log", [])),
        "Cechy wielomianowe": len(features_added.get("polynomial", [])),
        "Cechy zmiany": len(features_added.get("change", [])),
        "Cechy kategoryczne": len(features_added.get("categorical", [])),
        "Cechy stosunkowe": len(features_added.get("ratio", [])),
        "Cechy opoznione": len(features_added.get("lag", [])),
        "LACZNIE": total_new
    })

    report.add_paragraph("**Zapisany plik:**")
    report.add_bullet("`out/features/panel_with_features.parquet`")

    report.add_paragraph("**Kluczowe zmienne dla modelowania:**")
    report.add_bullet("`co2_per_capita_log` - zmienna zalezna (log)")
    report.add_bullet("`gdp_per_capita_log` - glowny predyktor (log)")
    report.add_bullet("`gdp_per_capita_sq` - test krzywej Kuznetsa")
    report.add_bullet("`development_level` - kategoryzacja krajow")
    report.add_bullet("`region` - analiza regionalna")
    report.add_bullet("`renewable_share_change` - tempo transformacji")

    # Save report
    report_path = report.save("05_feature_engineering.md")
    return report_path


def save_features_data(df: pd.DataFrame) -> str:
    """Zapisanie danych z nowymi cechami."""
    os.makedirs(FEATURES_DIR, exist_ok=True)
    path = os.path.join(FEATURES_DIR, "panel_with_features.parquet")
    df.to_parquet(path, index=False)
    return path


def run_step_05(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Uruchamia krok 5: Feature Engineering.

    Returns:
        Tuple (DataFrame z nowymi cechami, sciezka do raportu)
    """
    print("=" * 60)
    print("Krok 5: Przeksztalcanie zmiennych (Feature Engineering)")
    print("=" * 60)

    df_before = df.copy()
    features_added = {}

    # 1. Transformacje logarytmiczne
    print("\n  Dodawanie transformacji logarytmicznych...")
    df, new_cols = add_log_transforms(df)
    features_added["log"] = new_cols
    print(f"    Dodano {len(new_cols)} zmiennych")

    # 2. Cechy wielomianowe
    print("\n  Dodawanie cech wielomianowych...")
    df, new_cols = add_polynomial_features(df)
    features_added["polynomial"] = new_cols
    print(f"    Dodano {len(new_cols)} zmiennych")

    # 3. Cechy zmiany
    print("\n  Dodawanie cech zmiany (YoY)...")
    df, new_cols = add_change_features(df)
    features_added["change"] = new_cols
    print(f"    Dodano {len(new_cols)} zmiennych")

    # 4. Cechy kategoryczne
    print("\n  Dodawanie cech kategorycznych...")
    df, new_cols = add_categorical_features(df)
    features_added["categorical"] = new_cols
    print(f"    Dodano {len(new_cols)} zmiennych")

    # 5. Cechy stosunkowe
    print("\n  Dodawanie cech stosunkowych...")
    df, new_cols = add_ratio_features(df)
    features_added["ratio"] = new_cols
    print(f"    Dodano {len(new_cols)} zmiennych")

    # 6. Cechy opoznione
    print("\n  Dodawanie cech opoznionych...")
    df, new_cols = add_lag_features(df)
    features_added["lag"] = new_cols
    print(f"    Dodano {len(new_cols)} zmiennych")

    # Podsumowanie
    total_new = sum(len(v) for v in features_added.values())
    print(f"\n  Lacznie dodano {total_new} nowych zmiennych")
    print(f"  Kolumny: {len(df_before.columns)} -> {len(df.columns)}")

    # Zapisanie danych
    print("\n  Zapisywanie danych...")
    save_features_data(df)
    print(f"    Zapisano w: {FEATURES_DIR}")

    # Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_feature_report(df_before, df, features_added)

    print(f"\n Raport zapisany: {report_path}")

    return df, report_path
