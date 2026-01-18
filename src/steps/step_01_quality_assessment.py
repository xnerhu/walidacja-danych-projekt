# src/steps/step_01_quality_assessment.py
"""
Step 01: Quality Assessment of Source Data

This step evaluates the quality of downloaded datasets:
- Source credibility assessment
- Completeness analysis (temporal and geographical)
- Variable coverage analysis
- Data type validation
- Generates quality report in markdown

Output:
- report/01_quality_assessment.md
- out/quality/coverage_stats.csv
- out/figures/quality/*.png
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import datasets as hf_datasets

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import OUT_DIR, REPORT_DIR
from utils.fs import create_dir
from utils.df import df_info, df_missing_summary, df_describe_all
from utils.report import ReportBuilder
from utils.plotting import (
    plot_missing_bar,
    plot_missing_heatmap,
    save_figure,
    setup_plotting_style,
)
from utils.country import is_aggregate

# Output directories
QUALITY_DIR = os.path.join(OUT_DIR, "quality")
FIGURES_DIR = os.path.join(REPORT_DIR, "figures", "quality")


# =============================================================================
# Polish Pluralization Helper
# =============================================================================


def pluralize_polish(count: int, singular: str, plural_2_4: str, plural_5: str) -> str:
    """
    Polish pluralization for nouns.

    Args:
        count: Number
        singular: Form for 1 (e.g., "zmienna")
        plural_2_4: Form for 2-4 (e.g., "zmienne")
        plural_5: Form for 5+ and 0 (e.g., "zmiennych")
    """
    if count == 1:
        return f"{count} {singular}"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return f"{count} {plural_2_4}"
    else:
        return f"{count} {plural_5}"


# =============================================================================
# Source Credibility Assessment
# =============================================================================

DATASET_METADATA = {
    "owid_co2": {
        "name": "Our World in Data - CO2 and Greenhouse Gas Emissions",
        "source": "Our World in Data (OWID)",
        "url": "https://github.com/owid/co2-data",
        "original_sources": [
            "Global Carbon Project",
            "Climate Watch",
            "BP Statistical Review",
            "CDIAC",
            "World Bank",
            "UN Population Division",
        ],
        "license": "CC BY 4.0",
        "update_frequency": "Annual",
        "credibility": "HIGH",
        "credibility_notes": (
            "OWID aggregates data from reputable primary sources. "
            "Data is peer-reviewed and regularly updated. "
            "Methodology is transparent and well-documented."
        ),
        "time_range": "1750-2023 (most data from 1900+)",
        "geographic_coverage": "~200 countries and regions",
    },
    "sustainable_energy": {
        "name": "Global Data on Sustainable Energy",
        "source": "Kaggle (anshtanwar)",
        "url": "https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy",
        "original_sources": [
            "World Bank",
            "International Energy Agency (IEA)",
            "UN Statistics",
        ],
        "license": "CC0 (Public Domain)",
        "update_frequency": "Unknown",
        "credibility": "MEDIUM",
        "credibility_notes": (
            "Secondary dataset compiled from official sources. "
            "Aggregation methodology not fully documented. "
            "Data appears consistent with primary sources but requires validation."
        ),
        "time_range": "2000-2020",
        "geographic_coverage": "~170 countries",
    },
    "countries_2023": {
        "name": "Countries of the World 2023",
        "source": "Kaggle (nelgiriyewithana)",
        "url": "https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023",
        "original_sources": [
            "World Bank",
            "CIA World Factbook",
            "UN Data",
        ],
        "license": "CC0 (Public Domain)",
        "update_frequency": "Snapshot (~2023)",
        "credibility": "MEDIUM",
        "credibility_notes": (
            "Cross-sectional country data from various years. "
            "Some variables may not be from 2023 exactly. "
            "Useful for supplementary analysis but not primary source."
        ),
        "time_range": "Cross-sectional (~2023)",
        "geographic_coverage": "~195 countries",
    },
}


def assess_source_credibility(report: ReportBuilder) -> ReportBuilder:
    """Add source credibility assessment to report."""
    report.add_heading("Ocena wiarygodności źródeł danych", level=2)

    report.add_paragraph(
        "Poniżej przedstawiono ocenę wiarygodności każdego z wykorzystywanych zbiorów danych. "
        "Ocena uwzględnia: pochodzenie danych, częstotliwość aktualizacji, transparentność metodologii "
        "oraz zgodność z pierwotnymi źródłami."
    )

    for ds_key, meta in DATASET_METADATA.items():
        report.add_heading(meta["name"], level=3)

        report.add_key_value_table(
            {
                "Źródło": meta["source"],
                "URL": meta["url"],
                "Licencja": meta["license"],
                "Częstotliwość aktualizacji": meta["update_frequency"],
                "Zakres czasowy": meta["time_range"],
                "Pokrycie geograficzne": meta["geographic_coverage"],
                "Ocena wiarygodności": f"**{meta['credibility']}**",
            }
        )

        report.add_paragraph(
            f"**Źródła pierwotne:** {', '.join(meta['original_sources'])}"
        )
        report.add_paragraph(f"**Uwagi:** {meta['credibility_notes']}")
        report.add_newline()

    return report


# =============================================================================
# Completeness Analysis
# =============================================================================


def analyze_temporal_coverage(df: pd.DataFrame, year_col: str = "year") -> Dict:
    """Analyze temporal coverage of dataset."""
    # Try different possible column names (case-insensitive search)
    possible_cols = [year_col, "Year", "YEAR", "year"]
    found_col = None

    for col in possible_cols:
        if col in df.columns:
            found_col = col
            break

    if found_col is None:
        return {"has_temporal": False}

    years = df[found_col].dropna()

    # Handle non-numeric year columns
    try:
        years = pd.to_numeric(years, errors="coerce").dropna()
    except Exception:
        return {"has_temporal": False}

    if len(years) == 0:
        return {"has_temporal": False}

    return {
        "has_temporal": True,
        "column_used": found_col,
        "min_year": int(years.min()),
        "max_year": int(years.max()),
        "year_range": int(years.max() - years.min()),
        "unique_years": int(years.nunique()),
        "year_counts": years.value_counts().sort_index().to_dict(),
    }


def analyze_geographic_coverage(df: pd.DataFrame, country_col: str = "country") -> Dict:
    """Analyze geographic coverage of dataset."""
    # Try different possible column names
    possible_cols = [country_col, "Entity", "Country", "country_name", "iso_code"]
    found_col = None

    for col in possible_cols:
        if col in df.columns:
            found_col = col
            break

    if found_col is None:
        return {"has_geographic": False}

    countries = df[found_col].dropna()

    # Filter out aggregates for real country count
    try:
        real_countries = countries[~countries.apply(is_aggregate)]
        real_country_count = int(real_countries.nunique())
        top_countries = real_countries.value_counts().head(10).to_dict()
    except Exception:
        # Fallback if is_aggregate fails
        real_country_count = int(countries.nunique())
        top_countries = countries.value_counts().head(10).to_dict()

    return {
        "has_geographic": True,
        "column_used": found_col,
        "unique_countries": real_country_count,
        "unique_total": int(countries.nunique()),  # including aggregates
        "total_records": len(countries),
        "top_countries": top_countries,
    }


def analyze_variable_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze coverage (non-null percentage) for each variable."""
    coverage = []

    for col in df.columns:
        non_null = df[col].notna().sum()
        total = len(df)
        pct = non_null / total * 100

        dtype = str(df[col].dtype)
        unique = df[col].nunique()

        coverage.append(
            {
                "column": col,
                "dtype": dtype,
                "non_null": non_null,
                "null_count": total - non_null,
                "coverage_pct": round(pct, 2),
                "unique_values": unique,
            }
        )

    return pd.DataFrame(coverage).sort_values("coverage_pct", ascending=True)


def categorize_coverage(pct: float) -> str:
    """Categorize coverage percentage."""
    if pct >= 95:
        return "Excellent (≥95%)"
    elif pct >= 80:
        return "Good (80-95%)"
    elif pct >= 50:
        return "Moderate (50-80%)"
    elif pct >= 20:
        return "Poor (20-50%)"
    else:
        return "Very Poor (<20%)"


# =============================================================================
# Dataset Quality Assessment
# =============================================================================


def assess_dataset_quality(
    ds: hf_datasets.Dataset, name: str, report: ReportBuilder, figures_dir: str
) -> Tuple[ReportBuilder, pd.DataFrame]:
    """
    Comprehensive quality assessment for a single dataset.

    Returns:
        Tuple of (report, coverage_df)
    """
    df = ds.to_pandas()
    info = df_info(df)

    # Create safe filename (no spaces)
    safe_name = name.replace(" ", "_")

    report.add_heading(f"Dataset: {name}", level=2)

    # Basic info
    report.add_heading("Podstawowe informacje", level=3)
    report.add_key_value_table(
        {
            "Liczba wierszy": f"{info['rows']:,}",
            "Liczba kolumn": info["cols"],
            "Pamięć": f"{info['memory_mb']:.2f} MB",
            "Całkowita liczba braków": f"{info['missing_total']:,}",
            "Procent braków": f"{info['missing_pct']:.2f}%",
        }
    )

    # Data types distribution
    report.add_heading("Rozkład typów danych", level=3)
    dtype_df = pd.DataFrame(
        [(str(k), v) for k, v in info["dtypes"].items()], columns=["Typ", "Liczba"]
    )
    report.add_table(dtype_df)

    # Temporal coverage
    temporal = analyze_temporal_coverage(df)
    if temporal.get("has_temporal"):
        report.add_heading("Pokrycie czasowe", level=3)
        temporal_info = {
            "Minimalny rok": temporal["min_year"],
            "Maksymalny rok": temporal["max_year"],
            "Zakres lat": temporal["year_range"],
            "Unikalne lata": temporal["unique_years"],
        }
        if "column_used" in temporal and temporal["column_used"] != "year":
            temporal_info["Kolumna roku"] = temporal["column_used"]
        report.add_key_value_table(temporal_info)

    # Geographic coverage
    geographic = analyze_geographic_coverage(df)
    if geographic.get("has_geographic"):
        report.add_heading("Pokrycie geograficzne", level=3)
        geo_info = {
            "Kolumna identyfikująca": geographic["column_used"],
            "Unikalne kraje": geographic["unique_countries"],
            "Całkowita liczba rekordów": f"{geographic['total_records']:,}",
        }
        # Show total including aggregates if different
        if (
            geographic.get("unique_total")
            and geographic["unique_total"] != geographic["unique_countries"]
        ):
            geo_info["Łącznie z agregatami"] = geographic["unique_total"]
        report.add_key_value_table(geo_info)

        # Top countries
        report.add_heading("Top 10 krajów (wg liczby rekordów)", level=4)
        top_countries_df = pd.DataFrame(
            list(geographic["top_countries"].items()),
            columns=["Kraj", "Liczba rekordów"],
        )
        report.add_table(top_countries_df)

    # Variable coverage analysis
    report.add_heading("Pokrycie zmiennych (kompletność danych)", level=3)
    coverage_df = analyze_variable_coverage(df)

    # Summary by coverage category
    coverage_df["category"] = coverage_df["coverage_pct"].apply(categorize_coverage)
    category_summary = coverage_df["category"].value_counts().to_dict()

    report.add_paragraph("**Podsumowanie kompletności zmiennych:**")
    for cat in [
        "Excellent (≥95%)",
        "Good (80-95%)",
        "Moderate (50-80%)",
        "Poor (20-50%)",
        "Very Poor (<20%)",
    ]:
        if cat in category_summary:
            count = category_summary[cat]
            var_text = pluralize_polish(count, "zmienna", "zmienne", "zmiennych")
            report.add_bullet(f"{cat}: {var_text}")

    # Variables with low coverage (potential issues)
    low_coverage = coverage_df[coverage_df["coverage_pct"] < 50]
    if len(low_coverage) > 0:
        low_count = len(low_coverage)
        var_word = pluralize_polish(low_count, "zmienną", "zmienne", "zmiennych")
        report.add_warning_box(
            f"Znaleziono {var_word} z pokryciem <50%. "
            "Te zmienne mogą wymagać szczególnej uwagi podczas analizy."
        )

        report.add_heading("Zmienne z niskim pokryciem (<50%)", level=4)
        report.add_table(
            low_coverage[["column", "dtype", "coverage_pct", "null_count"]].head(20),
            max_rows=20,
        )

    # Generate missing data plot
    if info["missing_total"] > 0:
        fig = plot_missing_bar(df, title=f"Braki danych - {name}", top_n=30)
        fig_path = save_figure(fig, f"missing_bar_{safe_name}", figures_dir=figures_dir)
        # Use forward slashes for cross-platform compatibility
        rel_path = os.path.relpath(fig_path, REPORT_DIR).replace("\\", "/")
        report.add_figure(
            rel_path,
            caption=f"Braki danych według zmiennych - {name}",
        )

    return report, coverage_df


# =============================================================================
# Helper: Find similar column name
# =============================================================================


def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """
    Find a column from a list of candidate names.
    Returns the first match found, or None.
    """
    for col in candidates:
        if col in df.columns:
            return col

    # Try case-insensitive and partial match
    df_cols_lower = {c.lower().replace(" ", "").replace("_", ""): c for c in df.columns}
    for candidate in candidates:
        candidate_normalized = candidate.lower().replace(" ", "").replace("_", "")
        # Exact normalized match
        if candidate_normalized in df_cols_lower:
            return df_cols_lower[candidate_normalized]
        # Partial match
        for col_normalized, col_original in df_cols_lower.items():
            if (
                candidate_normalized in col_normalized
                or col_normalized in candidate_normalized
            ):
                return col_original

    return None


# =============================================================================
# Helper: Try to get numeric stats from potentially string column
# =============================================================================


def try_get_numeric_stats(series: pd.Series) -> Optional[Dict]:
    """
    Try to extract numeric statistics from a series that might be
    stored as strings with formatting (e.g., "1,234,567" or "$1,234").

    Returns dict with min, median, max or None if not possible.
    """
    if pd.api.types.is_numeric_dtype(series):
        desc = series.describe()
        return {
            "min": desc.get("min"),
            "median": desc.get("50%"),
            "max": desc.get("max"),
            "converted_from_string": False,
        }

    # Try to convert string to numeric
    try:
        # Remove common formatting characters
        cleaned = series.astype(str).str.replace(r"[\$,\s%]", "", regex=True)
        cleaned = cleaned.str.replace(r"[^\d.\-eE]", "", regex=True)
        numeric = pd.to_numeric(cleaned, errors="coerce")

        # If at least 50% converted successfully, use those stats
        valid_count = numeric.notna().sum()
        if valid_count >= 0.5 * len(numeric) and valid_count > 0:
            desc = numeric.describe()
            return {
                "min": desc.get("min"),
                "median": desc.get("50%"),
                "max": desc.get("max"),
                "converted_from_string": True,
            }
    except Exception:
        pass

    return None


# =============================================================================
# Key Variables Assessment
# =============================================================================


def assess_key_variables(
    df: pd.DataFrame, key_vars: List[str], report: ReportBuilder, dataset_name: str = ""
) -> ReportBuilder:
    """Assess quality of key variables for analysis."""
    title = "Ocena kluczowych zmiennych"
    if dataset_name:
        title += f" ({dataset_name})"
    report.add_heading(title, level=3)

    # Try to find each variable (with fuzzy matching)
    found_vars = []
    missing_vars = []
    var_mapping = {}  # requested name -> actual column name

    for var in key_vars:
        # First try exact match
        if var in df.columns:
            found_vars.append(var)
            var_mapping[var] = var
        else:
            # Try to find similar column
            actual_col = find_column(df, [var])
            if actual_col:
                found_vars.append(var)
                var_mapping[var] = actual_col
            else:
                missing_vars.append(var)

    if missing_vars:
        report.add_warning_box(
            f"Brak następujących zmiennych: {', '.join(missing_vars)}"
        )

    if found_vars:
        stats = []
        any_converted = False

        for var in found_vars:
            actual_col = var_mapping[var]
            col_data = df[actual_col]

            non_null = col_data.notna().sum()
            coverage = non_null / len(df) * 100
            unique = col_data.nunique()

            # Try to get numeric stats
            numeric_stats = try_get_numeric_stats(col_data)

            if numeric_stats and numeric_stats.get("min") is not None:
                # Format the stats
                def fmt_num(val):
                    if val is None or pd.isna(val):
                        return "N/A"
                    if abs(val) >= 1_000_000:
                        return f"{val:.2e}"
                    elif abs(val) >= 1:
                        return f"{val:,.2f}"
                    else:
                        return f"{val:.4f}"

                type_note = ""
                if numeric_stats.get("converted_from_string"):
                    type_note = " *"
                    any_converted = True

                stats.append(
                    {
                        "Zmienna": var + type_note,
                        "Pokrycie %": f"{coverage:.1f}%",
                        "Unikalne": unique,
                        "Min": fmt_num(numeric_stats["min"]),
                        "Mediana": fmt_num(numeric_stats["median"]),
                        "Max": fmt_num(numeric_stats["max"]),
                    }
                )
            else:
                # Categorical or unable to parse
                # Show top value instead
                top_val = "N/A"
                if col_data.notna().any():
                    top_val_raw = str(col_data.value_counts().index[0])
                    top_val = top_val_raw[:30]
                    if len(top_val_raw) > 30:
                        top_val += "..."

                stats.append(
                    {
                        "Zmienna": var,
                        "Pokrycie %": f"{coverage:.1f}%",
                        "Unikalne": unique,
                        "Min": "(tekst)",
                        "Mediana": f"Top: {top_val}",
                        "Max": "(tekst)",
                    }
                )

        report.add_table(pd.DataFrame(stats))

        # Add footnote if any columns were converted from string
        if any_converted:
            report.add_paragraph("*\\* Wartości skonwertowane z formatu tekstowego*")

    return report


# =============================================================================
# Data Usability Assessment
# =============================================================================


def assess_data_usability(report: ReportBuilder) -> ReportBuilder:
    """Add data usability and generalizability assessment."""
    report.add_heading("Ocena przydatności danych i możliwości uogólnienia", level=2)

    report.add_heading("Przydatność do celów badawczych", level=3)
    report.add_paragraph(
        "Zebrane dane pozwalają na analizę związku między rozwojem gospodarczym "
        "(mierzonym PKB per capita) a emisjami CO2 oraz transformacją energetyczną. "
        "Kluczowe pytania badawcze możliwe do zbadania:"
    )
    report.add_bullet("Weryfikacja hipotezy krzywej środowiskowej Kuznetsa (EKC)")
    report.add_bullet("Analiza czynników wpływających na emisje CO2 per capita")
    report.add_bullet("Badanie tempa transformacji energetycznej w różnych krajach")
    report.add_bullet("Porównania regionalne i grupowe")

    report.add_heading("Ograniczenia i zastrzeżenia", level=3)
    report.add_bullet(
        "**Agregaty regionalne**: Dane OWID zawierają agregaty (World, Europe, etc.) "
        "które należy wykluczyć z analizy na poziomie krajów"
    )
    report.add_bullet(
        "**Braki danych historycznych**: Dane przed 1960 r. są niekompletne dla wielu krajów"
    )
    report.add_bullet(
        "**Różne definicje**: Nazwy krajów mogą się różnić między datasetami "
        "(np. 'USA' vs 'United States')"
    )
    report.add_bullet(
        "**Dane przekrojowe vs panelowe**: Dataset 'Countries 2023' jest przekrojowy "
        "i może nie być w pełni kompatybilny z danymi panelowymi"
    )
    report.add_bullet(
        "**Typy danych**: Niektóre kolumny numeryczne są zapisane jako tekst "
        "(np. z separatorami tysięcy) i wymagają konwersji"
    )

    report.add_heading("Możliwości uogólnienia wyników", level=3)
    report.add_paragraph(
        "Dane obejmują większość krajów świata (>150 krajów) i okres 2000-2020, "
        "co pozwala na:"
    )
    report.add_bullet(
        "Wnioskowanie globalne o trendach emisji i transformacji energetycznej"
    )
    report.add_bullet(
        "Porównania między grupami krajów (rozwinięte vs rozwijające się)"
    )
    report.add_bullet("Analizę trendów czasowych")
    report.add_newline()
    report.add_paragraph(
        "**Ograniczenia uogólnienia:** Wyniki mogą nie być w pełni reprezentatywne dla "
        "małych państw wyspiarskich i terytoriów zależnych ze względu na braki danych."
    )

    return report


# =============================================================================
# Main Function
# =============================================================================


def run_quality_assessment(
    ds_owid_co2: hf_datasets.Dataset,
    ds_sustainable_energy: hf_datasets.Dataset,
    ds_countries: hf_datasets.Dataset,
) -> str:
    """
    Run complete quality assessment for all datasets.

    Args:
        ds_owid_co2: OWID CO2 dataset
        ds_sustainable_energy: Sustainable Energy dataset
        ds_countries: Countries of the World 2023 dataset

    Returns:
        Path to generated report
    """
    # Setup
    setup_plotting_style()
    create_dir(QUALITY_DIR)
    create_dir(FIGURES_DIR)

    # Initialize report
    report = ReportBuilder(title="Ocena jakości danych źródłowych")

    report.add_paragraph(
        "Niniejszy raport przedstawia kompleksową ocenę jakości trzech zbiorów danych "
        "wykorzystywanych w projekcie analizy wpływu rozwoju gospodarczego na emisje CO2 "
        "i transformację energetyczną."
    )

    # 1. Source credibility
    report = assess_source_credibility(report)
    report.add_separator()

    # 2. Dataset quality assessment
    report.add_heading("Szczegółowa ocena jakości datasetów", level=2)

    # =========================================================================
    # OWID CO2
    # =========================================================================
    report, coverage_owid = assess_dataset_quality(
        ds_owid_co2, "OWID CO2", report, FIGURES_DIR
    )

    # Key variables for OWID
    owid_key_vars = [
        "country",
        "year",
        "iso_code",
        "population",
        "gdp",
        "co2",
        "co2_per_capita",
        "co2_per_gdp",
        "primary_energy_consumption",
        "energy_per_capita",
    ]
    report = assess_key_variables(
        ds_owid_co2.to_pandas(), owid_key_vars, report, "OWID CO2"
    )
    report.add_separator()

    # =========================================================================
    # Sustainable Energy
    # =========================================================================
    report, coverage_energy = assess_dataset_quality(
        ds_sustainable_energy, "Sustainable Energy", report, FIGURES_DIR
    )

    # Key variables for Sustainable Energy
    energy_key_vars = [
        "Entity",
        "Year",
        "Access to electricity (% of population)",
        "Renewable energy share in the total final energy consumption (%)",
        "Electricity from renewables (TWh)",
        "gdp_per_capita",
        "gdp_growth",
        "Energy intensity level of primary energy (MJ/$2017 PPP GDP)",
    ]
    report = assess_key_variables(
        ds_sustainable_energy.to_pandas(), energy_key_vars, report, "Sustainable Energy"
    )
    report.add_separator()

    # =========================================================================
    # Countries 2023
    # =========================================================================
    report, coverage_countries = assess_dataset_quality(
        ds_countries, "Countries 2023", report, FIGURES_DIR
    )

    # Key variables for Countries 2023
    # Use multiple candidate names for fuzzy matching
    countries_key_vars = [
        "Country",
        "Population",
        "GDP",
        "Urban_population",
        "Agricultural Land(%)",  # Will fuzzy match "Agricultural Land (%)" etc.
        "CO2 Emissions",
        "Unemployment rate",
        "Density",  # Will fuzzy match "Density\n(P/Km2)" etc.
    ]
    report = assess_key_variables(
        ds_countries.to_pandas(), countries_key_vars, report, "Countries 2023"
    )

    # 3. Data usability assessment
    report.add_separator()
    report = assess_data_usability(report)

    # 4. Summary and recommendations
    report.add_separator()
    report.add_heading("Podsumowanie i rekomendacje", level=2)

    report.add_heading("Główne wnioski", level=3)
    report.add_bullet(
        "**OWID CO2** - wysokiej jakości, dobrze udokumentowany zbiór danych, "
        "odpowiedni jako główne źródło do analizy emisji"
    )
    report.add_bullet(
        "**Sustainable Energy** - uzupełniający zbiór z danymi o OZE, "
        "wymaga walidacji z pierwotnymi źródłami"
    )
    report.add_bullet(
        "**Countries 2023** - przydatny do analizy przekrojowej, "
        "ale ograniczony dla analizy panelowej; wymaga konwersji typów danych"
    )

    # Save coverage stats
    all_coverage = pd.concat(
        [
            coverage_owid.assign(dataset="owid_co2"),
            coverage_energy.assign(dataset="sustainable_energy"),
            coverage_countries.assign(dataset="countries_2023"),
        ]
    )
    coverage_path = os.path.join(QUALITY_DIR, "coverage_stats.csv")
    all_coverage.to_csv(coverage_path, index=False)

    # Use relative path in report
    rel_coverage_path = os.path.relpath(coverage_path, REPORT_DIR).replace("\\", "/")
    report.add_paragraph(
        f"\n*Szczegółowe statystyki pokrycia zapisano do: `{rel_coverage_path}`*"
    )

    # Save report
    report_path = report.save("01_quality_assessment.md")

    print(f"\n✅ Quality assessment complete!")
    print(f"   Report: {report_path}")
    print(f"   Coverage stats: {coverage_path}")

    return report_path


if __name__ == "__main__":
    from steps.step_00_download import (
        get_owid_co2_dataset,
        get_sustainable_energy_dataset,
        get_countries_of_world_dataset,
    )

    print("=" * 60)
    print("Step 01: Quality Assessment")
    print("=" * 60)

    ds_owid = get_owid_co2_dataset()
    ds_energy = get_sustainable_energy_dataset()
    ds_countries = get_countries_of_world_dataset()

    run_quality_assessment(ds_owid, ds_energy, ds_countries)
