# src/steps/step_09_export.py
"""
Krok 9: Eksport finalnego zbioru i dokumentacji.

Funkcje:
- export_to_csv() - eksport do CSV
- export_to_parquet() - eksport do Parquet
- generate_codebook() - generowanie codebooka
- generate_summary_stats() - podsumowanie statystyk
- compile_final_report() - kompilacja raportu koncowego

Output:
- out/final/final_dataset.csv
- out/final/final_dataset.parquet
- out/final/codebook.md
- out/final/codebook.csv
- report/09_export.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
from datetime import datetime

from constants import REPORT_DIR, OUT_DIR
from utils.report import ReportBuilder, create_codebook
from utils.df import df_info, df_describe_all


FINAL_DIR = os.path.join(OUT_DIR, "final")


def export_to_csv(df: pd.DataFrame, filename: str = "final_dataset.csv") -> str:
    """Eksport do formatu CSV."""
    os.makedirs(FINAL_DIR, exist_ok=True)
    path = os.path.join(FINAL_DIR, filename)
    df.to_csv(path, index=False)
    return path


def export_to_parquet(df: pd.DataFrame, filename: str = "final_dataset.parquet") -> str:
    """Eksport do formatu Parquet."""
    os.makedirs(FINAL_DIR, exist_ok=True)
    path = os.path.join(FINAL_DIR, filename)
    df.to_parquet(path, index=False)
    return path


def generate_codebook(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Generowanie codebooka (slownika danych).

    Returns:
        Tuple (sciezka do codebook.md, sciezka do codebook.csv)
    """
    os.makedirs(FINAL_DIR, exist_ok=True)

    # Opisy zmiennych
    descriptions = {
        "country": "Nazwa kraju",
        "year": "Rok obserwacji",
        "iso_code": "Kod ISO-3166-1 alpha-3",
        "region": "Region geograficzny (kontynent)",
        "co2": "Emisje CO2 (mln ton)",
        "co2_per_capita": "Emisje CO2 per capita (tony/osobe)",
        "co2_per_capita_log": "Log(1 + CO2 per capita)",
        "gdp": "PKB (mld USD, PPP)",
        "gdp_per_capita": "PKB per capita (USD)",
        "gdp_per_capita_log": "Log(1 + PKB per capita)",
        "gdp_per_capita_sq": "PKB per capita do kwadratu (dla krzywej Kuznetsa)",
        "gdp_per_capita_cu": "PKB per capita do szescianu",
        "population": "Populacja",
        "population_log": "Log(1 + populacja)",
        "primary_energy_consumption": "Zuzycie energii pierwotnej (TWh)",
        "coal_co2": "Emisje CO2 z wegla",
        "oil_co2": "Emisje CO2 z ropy",
        "gas_co2": "Emisje CO2 z gazu",
        "fossil_co2": "Laczone emisje z paliw kopalnych",
        "fossil_share": "Udzial paliw kopalnych w emisjach",
        "coal_share": "Udzial wegla w emisjach",
        "oil_share": "Udzial ropy w emisjach",
        "gas_share": "Udzial gazu w emisjach",
        "emission_intensity": "Intensywnosc emisji (CO2/PKB)",
        "energy_intensity": "Intensywnosc energetyczna (energia/PKB)",
        "development_level": "Poziom rozwoju (Low/Medium/High/Very High)",
        "co2_change": "Zmiana CO2 rok-do-roku",
        "co2_pct_change": "Procentowa zmiana CO2 rok-do-roku",
        "co2_per_capita_change": "Zmiana CO2 per capita rok-do-roku",
        "gdp_change": "Zmiana PKB rok-do-roku",
        "gdp_pct_change": "Procentowa zmiana PKB rok-do-roku",
        "renewable_share_change": "Zmiana udzialu OZE rok-do-roku",
        "urban_population": "Populacja miejska",
        "latitude": "Szerokosc geograficzna stolicy",
        "longitude": "Dlugosc geograficzna stolicy"
    }

    # Generuj codebook jako markdown
    codebook_md = create_codebook(df, descriptions, title="Codebook - Zbior danych")
    md_path = os.path.join(FINAL_DIR, "codebook.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(codebook_md)

    # Generuj codebook jako CSV
    rows = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_pct = df[col].isna().sum() / len(df) * 100
        unique = df[col].nunique()

        # Statystyki dla zmiennych numerycznych
        if pd.api.types.is_numeric_dtype(df[col]):
            stats = df[col].describe()
            rows.append({
                "variable": col,
                "type": dtype,
                "description": descriptions.get(col, ""),
                "non_null": non_null,
                "missing_pct": round(null_pct, 2),
                "unique": unique,
                "mean": round(stats.get("mean", np.nan), 4),
                "std": round(stats.get("std", np.nan), 4),
                "min": round(stats.get("min", np.nan), 4),
                "max": round(stats.get("max", np.nan), 4)
            })
        else:
            rows.append({
                "variable": col,
                "type": dtype,
                "description": descriptions.get(col, ""),
                "non_null": non_null,
                "missing_pct": round(null_pct, 2),
                "unique": unique,
                "mean": np.nan,
                "std": np.nan,
                "min": np.nan,
                "max": np.nan
            })

    codebook_df = pd.DataFrame(rows)
    csv_path = os.path.join(FINAL_DIR, "codebook.csv")
    codebook_df.to_csv(csv_path, index=False)

    return md_path, csv_path


def generate_summary_stats(df: pd.DataFrame) -> str:
    """
    Generowanie podsumowania statystyk.

    Returns:
        Sciezka do pliku ze statystykami
    """
    os.makedirs(FINAL_DIR, exist_ok=True)

    # Pelne statystyki opisowe
    stats = df_describe_all(df)
    path = os.path.join(FINAL_DIR, "summary_stats.csv")
    stats.to_csv(path, index=False)

    return path


def generate_export_report(
    df: pd.DataFrame,
    export_paths: Dict[str, str]
) -> str:
    """
    Generuje raport eksportu.

    Returns:
        Sciezka do zapisanego raportu
    """
    report = ReportBuilder(title="Eksport finalnego zbioru danych")

    # ==========================================================================
    # 1. Podsumowanie zbioru
    # ==========================================================================
    report.add_heading("Podsumowanie finalnego zbioru danych", level=2)

    info = df_info(df)
    report.add_key_value_table({
        "Liczba obserwacji": f"{info['rows']:,}",
        "Liczba zmiennych": info['cols'],
        "Rozmiar w pamieci": f"{info['memory_mb']:.2f} MB",
        "Braki danych": f"{info['missing_pct']:.2f}%",
        "Liczba krajow": df["country"].nunique() if "country" in df.columns else "N/A",
        "Zakres czasowy": f"{df['year'].min()}-{df['year'].max()}" if "year" in df.columns else "N/A"
    })

    # ==========================================================================
    # 2. Struktura danych
    # ==========================================================================
    report.add_separator()
    report.add_heading("Struktura danych", level=2)

    report.add_paragraph("**Typ zbioru:** Dane panelowe (panel data)")
    report.add_paragraph("**Klucze:** `country`, `year`")
    report.add_paragraph("**Format czasu:** Roczny (2000-2020)")

    # Typy zmiennych
    report.add_heading("Typy zmiennych", level=3)
    dtype_counts = df.dtypes.astype(str).value_counts()
    report.add_key_value_table(dtype_counts.to_dict())

    # ==========================================================================
    # 3. Pokrycie geograficzne
    # ==========================================================================
    report.add_separator()
    report.add_heading("Pokrycie geograficzne", level=2)

    if "region" in df.columns:
        region_counts = df.groupby("region")["country"].nunique()
        report.add_table(region_counts.reset_index().rename(columns={
            "region": "Region",
            "country": "Liczba krajow"
        }))

    # ==========================================================================
    # 4. Eksportowane pliki
    # ==========================================================================
    report.add_separator()
    report.add_heading("Eksportowane pliki", level=2)

    report.add_paragraph("**Pliki danych:**")
    for name, path in export_paths.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / 1024 / 1024
            report.add_bullet(f"`{os.path.basename(path)}` ({size_mb:.2f} MB)")
        else:
            report.add_bullet(f"`{os.path.basename(path)}`")

    # ==========================================================================
    # 5. Instrukcja uzycia
    # ==========================================================================
    report.add_separator()
    report.add_heading("Instrukcja uzycia", level=2)

    report.add_heading("Python (pandas)", level=3)
    report.add_code("""
import pandas as pd

# Wczytanie danych
df = pd.read_parquet("out/final/final_dataset.parquet")

# Lub z CSV
df = pd.read_csv("out/final/final_dataset.csv")

# Podstawowe operacje
print(df.shape)
print(df.columns.tolist())
print(df.describe())
    """, language="python")

    report.add_heading("R", level=3)
    report.add_code("""
library(arrow)
library(dplyr)

# Wczytanie danych
df <- read_parquet("out/final/final_dataset.parquet")

# Lub z CSV
df <- read.csv("out/final/final_dataset.csv")

# Podstawowe operacje
dim(df)
names(df)
summary(df)
    """, language="r")

    # ==========================================================================
    # 6. Pytania badawcze
    # ==========================================================================
    report.add_separator()
    report.add_heading("Przygotowane pytania badawcze", level=2)

    report.add_paragraph(
        "Zbior danych zostal przygotowany do odpowiedzi na nastepujace pytania:"
    )

    report.add_numbered("Czy istnieje krzywa srodowiskowa Kuznetsa (EKC)?", 1)
    report.add_paragraph(
        "  - Zmienne: `co2_per_capita`, `gdp_per_capita`, `gdp_per_capita_sq`"
    )

    report.add_numbered("Jakie czynniki strukturalne roznicuja emisje?", 2)
    report.add_paragraph(
        "  - Zmienne: `fossil_share`, `emission_intensity`, `energy_intensity`, `development_level`"
    )

    report.add_numbered("Czy tempo wzrostu PKB wplywa na transformacje energetyczna?", 3)
    report.add_paragraph(
        "  - Zmienne: `gdp_pct_change`, `renewable_share_change`"
    )

    report.add_numbered("Jak region moderuje zwiazek rozwoj-emisje?", 4)
    report.add_paragraph(
        "  - Zmienne: `region`, interakcje z `gdp_per_capita`"
    )

    # ==========================================================================
    # 7. Podsumowanie
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie", level=2)

    report.add_paragraph(
        f"Finalny zbior danych zawiera **{info['rows']:,} obserwacji** "
        f"dla **{df['country'].nunique()} krajow** w okresie **2000-2020**."
    )

    report.add_paragraph("**Pipeline przetwarzania obejmowal:**")
    report.add_numbered("Pobranie danych z 3 zrodel (OWID, Kaggle)", 1)
    report.add_numbered("Ocene jakosci danych zrodlowych", 2)
    report.add_numbered("Czyszczenie i standaryzacje nazw", 3)
    report.add_numbered("Laczenie zbiorow po (country, year)", 4)
    report.add_numbered("Eksploracyjna analize danych (EDA)", 5)
    report.add_numbered("Tworzenie nowych zmiennych (feature engineering)", 6)
    report.add_numbered("Analize outlierow", 7)
    report.add_numbered("Analize i imputacje brakow danych", 8)
    report.add_numbered("Selekcje zmiennych i rekordow", 9)
    report.add_numbered("Eksport i dokumentacje", 10)

    report.add_paragraph(
        f"**Data eksportu:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # Save report
    report_path = report.save("09_export.md")
    return report_path


def run_step_09(df: pd.DataFrame) -> str:
    """
    Uruchamia krok 9: Eksport i dokumentacja.

    Returns:
        Sciezka do raportu
    """
    print("=" * 60)
    print("Krok 9: Eksport finalnego zbioru i dokumentacji")
    print("=" * 60)

    export_paths = {}

    # 1. Eksport do CSV
    print("\n  Eksport do CSV...")
    export_paths["csv"] = export_to_csv(df)
    print(f"    Zapisano: {export_paths['csv']}")

    # 2. Eksport do Parquet
    print("\n  Eksport do Parquet...")
    export_paths["parquet"] = export_to_parquet(df)
    print(f"    Zapisano: {export_paths['parquet']}")

    # 3. Generowanie codebooka
    print("\n  Generowanie codebooka...")
    md_path, csv_path = generate_codebook(df)
    export_paths["codebook_md"] = md_path
    export_paths["codebook_csv"] = csv_path
    print(f"    Zapisano: {md_path}")
    print(f"    Zapisano: {csv_path}")

    # 4. Statystyki podsumowujace
    print("\n  Generowanie statystyk...")
    export_paths["stats"] = generate_summary_stats(df)
    print(f"    Zapisano: {export_paths['stats']}")

    # 5. Generowanie raportu
    print("\n  Generowanie raportu...")
    report_path = generate_export_report(df, export_paths)

    print(f"\n Raport zapisany: {report_path}")

    # Podsumowanie
    print("\n" + "=" * 60)
    print("EKSPORT ZAKONCZONY")
    print("=" * 60)
    print(f"\nWyeksportowane pliki:")
    for name, path in export_paths.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / 1024 / 1024
            print(f"  - {os.path.basename(path)}: {size_mb:.2f} MB")

    return report_path
