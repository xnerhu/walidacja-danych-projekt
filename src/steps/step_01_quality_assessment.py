# src/steps/step_01_quality_assessment.py
"""
Krok 1: Ocena jakości danych źródłowych.

Funkcje:
- assess_source_credibility() - ocena wiarygodności źródeł
- assess_completeness() - kompletność czasowa i geograficzna
- assess_variable_coverage() - pokrycie zmiennych (% non-null)
- generate_quality_report() - raport jakości w markdown

Output:
- report/01_quality_assessment.md
- report/figures/quality/*.png
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

from constants import REPORT_DIR
from utils.report import ReportBuilder
from utils.df import df_info, df_missing_summary
from utils.plotting import plot_missing_bar, save_figure, FIGURES_DIR
from utils.country import is_aggregate, validate_countries


def assess_source_credibility(dataset_name: str) -> Dict:
    """
    Ocena wiarygodności źródła danych.

    Returns:
        Dict z oceną źródła
    """
    sources = {
        "OWID_CO2": {
            "name": "Our World in Data - CO2 and Greenhouse Gas Emissions",
            "organization": "Our World in Data (University of Oxford)",
            "url": "https://github.com/owid/co2-data",
            "license": "CC BY 4.0",
            "update_frequency": "Regularnie aktualizowany",
            "primary_sources": [
                "Global Carbon Project",
                "Climate Watch",
                "BP Statistical Review",
                "IEA",
                "World Bank"
            ],
            "data_type": "Dane wtórne (agregacja oficjalnych źródeł)",
            "credibility_score": 5,
            "credibility_note": "Bardzo wysoka wiarygodność - dane agregowane z oficjalnych źródeł, metodologia transparentna"
        },
        "Sustainable_Energy": {
            "name": "Global Data on Sustainable Energy",
            "organization": "Kaggle (dane zebrane przez społeczność)",
            "url": "https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy",
            "license": "CC0 Public Domain",
            "update_frequency": "Jednorazowy upload",
            "primary_sources": [
                "World Bank",
                "IEA",
                "UN Statistics Division"
            ],
            "data_type": "Dane wtórne (kompilacja)",
            "credibility_score": 3,
            "credibility_note": "Średnia wiarygodność - dane zebrane przez społeczność, wymaga weryfikacji"
        },
        "Countries_2023": {
            "name": "Countries of the World 2023",
            "organization": "Kaggle (dane zebrane przez społeczność)",
            "url": "https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023",
            "license": "CC0 Public Domain",
            "update_frequency": "Jednorazowy upload",
            "primary_sources": [
                "CIA World Factbook",
                "World Bank",
                "UN Statistics"
            ],
            "data_type": "Dane przekrojowe (cross-sectional)",
            "credibility_score": 3,
            "credibility_note": "Średnia wiarygodność - dane z wielu źródeł, brak pełnej dokumentacji metodologii"
        }
    }
    return sources.get(dataset_name, {})


def assess_completeness(df: pd.DataFrame, year_col: str = "year",
                        country_col: str = "country") -> Dict:
    """
    Ocena kompletności czasowej i geograficznej.

    Returns:
        Dict z metrykami kompletności
    """
    result = {}

    # Kompletność czasowa
    if year_col in df.columns:
        years = df[year_col].dropna()
        result["temporal"] = {
            "min_year": int(years.min()),
            "max_year": int(years.max()),
            "year_range": int(years.max() - years.min() + 1),
            "unique_years": int(years.nunique()),
            "missing_years": int(years.max() - years.min() + 1 - years.nunique())
        }

    # Kompletność geograficzna
    if country_col in df.columns:
        countries = df[country_col].dropna().unique().tolist()
        validation = validate_countries(countries)

        result["geographic"] = {
            "total_entities": len(countries),
            "valid_countries": validation["valid_count"],
            "aggregates": validation["aggregate_count"],
            "invalid": validation["invalid_count"],
            "aggregate_names": validation["aggregates"][:10]  # First 10
        }

    return result


def assess_variable_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ocena pokrycia zmiennych (% wartości niepustych).

    Returns:
        DataFrame z pokryciem dla każdej zmiennej
    """
    coverage = []

    for col in df.columns:
        non_null = df[col].notna().sum()
        total = len(df)

        coverage.append({
            "variable": col,
            "non_null_count": non_null,
            "total_count": total,
            "coverage_pct": round(non_null / total * 100, 2),
            "missing_pct": round((total - non_null) / total * 100, 2),
            "dtype": str(df[col].dtype)
        })

    return pd.DataFrame(coverage).sort_values("coverage_pct", ascending=True)


def generate_quality_report(
    df_owid: pd.DataFrame,
    df_energy: pd.DataFrame,
    df_countries: pd.DataFrame
) -> str:
    """
    Generuje raport oceny jakości danych.

    Returns:
        Ścieżka do zapisanego raportu
    """
    report = ReportBuilder(title="Ocena jakości danych źródłowych")

    # ==========================================================================
    # 1. Wprowadzenie
    # ==========================================================================
    report.add_heading("Wprowadzenie", level=2)
    report.add_paragraph(
        "Niniejszy raport przedstawia ocenę jakości trzech zbiorów danych "
        "wykorzystywanych w projekcie dotyczącym wpływu rozwoju gospodarczego "
        "na emisję CO2 i transformację energetyczną."
    )

    report.add_paragraph("**Analizowane zbiory danych:**")
    report.add_bullet("OWID CO2 Data - dane o emisjach CO2 i gazach cieplarnianych")
    report.add_bullet("Global Data on Sustainable Energy - dane o zrównoważonej energii")
    report.add_bullet("Countries of the World 2023 - dane przekrojowe o krajach")

    # ==========================================================================
    # 2. Ocena wiarygodności źródeł
    # ==========================================================================
    report.add_separator()
    report.add_heading("Ocena wiarygodności źródeł", level=2)

    datasets = [
        ("OWID_CO2", df_owid, "OWID CO2 Data"),
        ("Sustainable_Energy", df_energy, "Sustainable Energy"),
        ("Countries_2023", df_countries, "Countries 2023")
    ]

    for ds_key, df, ds_name in datasets:
        source_info = assess_source_credibility(ds_key)

        report.add_heading(f"{ds_name}", level=3)

        report.add_key_value_table({
            "Źródło": source_info.get("organization", "N/A"),
            "URL": source_info.get("url", "N/A"),
            "Licencja": source_info.get("license", "N/A"),
            "Typ danych": source_info.get("data_type", "N/A"),
            "Ocena wiarygodności": f"{source_info.get('credibility_score', 0)}/5"
        })

        report.add_paragraph(f"**Źródła pierwotne:** {', '.join(source_info.get('primary_sources', []))}")
        report.add_paragraph(f"**Uwagi:** {source_info.get('credibility_note', '')}")
        report.add_newline()

    # ==========================================================================
    # 3. Podstawowe charakterystyki zbiorów
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podstawowe charakterystyki zbiorów danych", level=2)

    for ds_key, df, ds_name in datasets:
        report.add_heading(f"{ds_name}", level=3)

        info = df_info(df)

        report.add_key_value_table({
            "Liczba wierszy": f"{info['rows']:,}",
            "Liczba kolumn": info['cols'],
            "Rozmiar w pamięci": f"{info['memory_mb']:.2f} MB",
            "Łączna liczba braków": f"{info['missing_total']:,}",
            "Procent braków": f"{info['missing_pct']:.2f}%"
        })

        report.add_newline()

    # ==========================================================================
    # 4. Kompletność czasowa i geograficzna
    # ==========================================================================
    report.add_separator()
    report.add_heading("Kompletność czasowa i geograficzna", level=2)

    # OWID CO2
    report.add_heading("OWID CO2 Data", level=3)
    completeness_owid = assess_completeness(df_owid)

    if "temporal" in completeness_owid:
        t = completeness_owid["temporal"]
        report.add_paragraph("**Zakres czasowy:**")
        report.add_key_value_table({
            "Lata": f"{t['min_year']} - {t['max_year']}",
            "Zakres": f"{t['year_range']} lat",
            "Unikalne lata": t['unique_years']
        })

    if "geographic" in completeness_owid:
        g = completeness_owid["geographic"]
        report.add_paragraph("**Pokrycie geograficzne:**")
        report.add_key_value_table({
            "Łączna liczba encji": g['total_entities'],
            "Kraje": g['valid_countries'],
            "Agregaty (regiony, grupy)": g['aggregates'],
            "Nierozpoznane": g['invalid']
        })
        if g['aggregate_names']:
            report.add_paragraph(f"Przykładowe agregaty: {', '.join(g['aggregate_names'][:5])}")

    # Sustainable Energy
    report.add_heading("Sustainable Energy", level=3)
    # Find the right column names
    year_col_energy = "Year" if "Year" in df_energy.columns else "year"
    country_col_energy = "Entity" if "Entity" in df_energy.columns else "country"
    completeness_energy = assess_completeness(df_energy, year_col_energy, country_col_energy)

    if "temporal" in completeness_energy:
        t = completeness_energy["temporal"]
        report.add_paragraph("**Zakres czasowy:**")
        report.add_key_value_table({
            "Lata": f"{t['min_year']} - {t['max_year']}",
            "Zakres": f"{t['year_range']} lat",
            "Unikalne lata": t['unique_years']
        })

    if "geographic" in completeness_energy:
        g = completeness_energy["geographic"]
        report.add_paragraph("**Pokrycie geograficzne:**")
        report.add_key_value_table({
            "Łączna liczba encji": g['total_entities'],
            "Kraje": g['valid_countries'],
            "Agregaty": g['aggregates']
        })

    # Countries 2023
    report.add_heading("Countries 2023", level=3)
    country_col_2023 = "Country" if "Country" in df_countries.columns else "country"
    report.add_paragraph("**Uwaga:** To są dane przekrojowe (cross-sectional) - pojedynczy rok.")

    countries_list = df_countries[country_col_2023].dropna().unique().tolist()
    validation = validate_countries(countries_list)
    report.add_key_value_table({
        "Liczba krajów": validation['valid_count'],
        "Agregaty": validation['aggregate_count'],
        "Nierozpoznane": validation['invalid_count']
    })

    # ==========================================================================
    # 5. Pokrycie zmiennych - analiza braków
    # ==========================================================================
    report.add_separator()
    report.add_heading("Analiza braków danych", level=2)

    figures_dir = os.path.join(FIGURES_DIR, "quality")
    os.makedirs(figures_dir, exist_ok=True)

    for ds_key, df, ds_name in datasets:
        report.add_heading(f"{ds_name}", level=3)

        # Coverage summary
        coverage = assess_variable_coverage(df)

        # Stats
        high_missing = coverage[coverage["missing_pct"] > 50]
        moderate_missing = coverage[(coverage["missing_pct"] > 10) & (coverage["missing_pct"] <= 50)]
        low_missing = coverage[coverage["missing_pct"] <= 10]

        report.add_key_value_table({
            "Zmienne z >50% braków": len(high_missing),
            "Zmienne z 10-50% braków": len(moderate_missing),
            "Zmienne z <10% braków": len(low_missing)
        })

        # Top missing variables
        if len(high_missing) > 0:
            report.add_paragraph("**Zmienne z największą liczbą braków (>50%):**")
            report.add_table(
                high_missing[["variable", "missing_pct", "coverage_pct"]].head(15),
                max_rows=15
            )

        # Generate and save plot
        fig = plot_missing_bar(df, title=f"Braki danych - {ds_name}", top_n=20)
        fig_path = save_figure(fig, f"missing_bar_{ds_key.replace(' ', '_')}", figures_dir=figures_dir)
        rel_path = os.path.relpath(fig_path, REPORT_DIR)
        report.add_figure(rel_path, f"Procent braków danych według zmiennych - {ds_name}")
        report.add_newline()

    # ==========================================================================
    # 6. Ocena przydatności do analizy
    # ==========================================================================
    report.add_separator()
    report.add_heading("Ocena przydatności do analizy", level=2)

    report.add_heading("OWID CO2 Data", level=3)
    report.add_paragraph(
        "**Ocena:** Bardzo dobra przydatność. Zbiór zawiera kompleksowe dane o emisjach CO2 "
        "dla większości krajów świata od 1750 roku. Kluczowe zmienne (co2, co2_per_capita, "
        "gdp, population) mają wysokie pokrycie dla lat 2000-2023."
    )
    report.add_bullet("Zalety: Długi zakres czasowy, duża liczba zmiennych, wiarygodne źródła")
    report.add_bullet("Wady: Duża liczba braków dla starszych lat i mniejszych krajów")

    report.add_heading("Sustainable Energy", level=3)
    report.add_paragraph(
        "**Ocena:** Dobra przydatność jako uzupełnienie. Zawiera dane o odnawialnych "
        "źródłach energii i dostępie do elektryczności, które uzupełniają dane OWID."
    )
    report.add_bullet("Zalety: Dane o OZE, dostępie do elektryczności")
    report.add_bullet("Wady: Krótszy zakres czasowy (2000-2020), wymaga standaryzacji nazw krajów")

    report.add_heading("Countries 2023", level=3)
    report.add_paragraph(
        "**Ocena:** Dobra jako dane uzupełniające (przekrojowe). Zawiera informacje "
        "o urbanizacji, strukturze gospodarczej, które nie są dostępne w pozostałych zbiorach."
    )
    report.add_bullet("Zalety: Dane o urbanizacji, strukturze gospodarczej")
    report.add_bullet("Wady: Dane przekrojowe (tylko jeden rok), wymaga standaryzacji nazw")

    # ==========================================================================
    # 7. Podsumowanie i rekomendacje
    # ==========================================================================
    report.add_separator()
    report.add_heading("Podsumowanie i rekomendacje", level=2)

    report.add_paragraph("**Kluczowe wnioski:**")
    report.add_numbered("OWID CO2 Data będzie głównym źródłem danych dla analizy", 1)
    report.add_numbered("Zakres czasowy analizy: 2000-2020 (wspólny dla wszystkich zbiorów)", 2)
    report.add_numbered("Konieczna standaryzacja nazw krajów przed łączeniem zbiorów", 3)
    report.add_numbered("Należy usunąć agregaty regionalne (World, Europe, itp.)", 4)
    report.add_numbered("Wymagana analiza i obsługa braków danych", 5)

    report.add_paragraph("**Rekomendacje dla kolejnych kroków:**")
    report.add_bullet("Standaryzacja nazw krajów we wszystkich zbiorach")
    report.add_bullet("Usunięcie agregatów i encji niebędących krajami")
    report.add_bullet("Filtrowanie do lat 2000-2020")
    report.add_bullet("Selekcja zmiennych z akceptowalnym poziomem braków (<30%)")

    # Save report
    report_path = report.save("01_quality_assessment.md")
    return report_path


def run_step_01(df_owid: pd.DataFrame, df_energy: pd.DataFrame,
                df_countries: pd.DataFrame) -> str:
    """
    Uruchamia krok 1: Ocena jakości danych.

    Returns:
        Ścieżka do raportu
    """
    print("=" * 60)
    print("Krok 1: Ocena jakości danych źródłowych")
    print("=" * 60)

    report_path = generate_quality_report(df_owid, df_energy, df_countries)

    print(f"\n✅ Raport zapisany: {report_path}")
    return report_path
