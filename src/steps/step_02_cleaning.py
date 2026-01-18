# src/steps/step_02_cleaning.py
"""
Step 02: Data Cleaning and Standardization

This step cleans and standardizes the downloaded datasets:
- Standardizes country names (USA vs United States, etc.)
- Standardizes column names (snake_case)
- Filters out aggregates (World, Europe, etc.)
- Fixes data types (string -> numeric)
- Validates value ranges (percentages 0-100)
- Generates cleaning report in markdown

Output:
- out/cleaned/owid_co2_cleaned.parquet
- out/cleaned/sustainable_energy_cleaned.parquet
- out/cleaned/countries_cleaned.parquet
- report/02_cleaning.md
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import datasets as hf_datasets
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import OUT_DIR, REPORT_DIR
from utils.fs import create_dir, write_parquet
from utils.df import standardize_column_names
from utils.report import ReportBuilder
from utils.plotting import save_figure, setup_plotting_style
from utils.country import (
    is_aggregate,
    get_aggregates_list,
    standardize_country_name,
    get_country_iso,
    COUNTRY_ALIASES,
)

# Output directories
CLEANED_DIR = os.path.join(OUT_DIR, "cleaned")
FIGURES_DIR = os.path.join(REPORT_DIR, "figures", "cleaning")


# =============================================================================
# Polish Pluralization Helper
# =============================================================================


def pluralize_polish(count: int, singular: str, plural_2_4: str, plural_5: str) -> str:
    """
    Polish pluralization for nouns.

    Args:
        count: Number
        singular: Form for 1 (e.g., "rekord")
        plural_2_4: Form for 2-4 (e.g., "rekordy")
        plural_5: Form for 5+ and 0 (e.g., "rekordów")
    """
    if count == 1:
        return f"{count} {singular}"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return f"{count} {plural_2_4}"
    else:
        return f"{count} {plural_5}"


# =============================================================================
# Country Name Standardization
# =============================================================================

# Countries/territories that should NOT be fuzzy-matched (keep original names)
# These are either disputed territories, special regions, or have problematic fuzzy matches
KEEP_ORIGINAL_NAMES = {
    "Kosovo",
    "Curacao",
    "Curaçao",
    "Taiwan",
    "Hong Kong",
    "Macao",
    "Macau",
    "Palestine",
    "Western Sahara",
    "Puerto Rico",
    "Guam",
    "American Samoa",
    "British Virgin Islands",
    "U.S. Virgin Islands",
    "Faroe Islands",
    "Greenland",
    "New Caledonia",
    "French Polynesia",
    "Gibraltar",
    "Bermuda",
    "Cayman Islands",
    "Aruba",
    "Sint Maarten",
    "Bonaire",
    "Channel Islands",
    "Isle of Man",
    "Falkland Islands",
    "Montserrat",
    "Turks and Caicos Islands",
    "Anguilla",
    "Saint Helena",
    "Wallis and Futuna",
    "Saint Pierre and Miquelon",
    "Cook Islands",
    "Niue",
    "Tokelau",
    "Nauru",  # Sometimes mismatched
}

# Simple aliases that should be mapped (without fuzzy matching)
SIMPLE_COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "U.S.": "United States",
    "U.S.A.": "United States",
    "United States of America": "United States",
    "UK": "United Kingdom",
    "U.K.": "United Kingdom",
    "Great Britain": "United Kingdom",
    "Britain": "United Kingdom",
    "Russia": "Russia",  # Keep as Russia, not "Russian Federation"
    "South Korea": "South Korea",  # Keep simple name
    "North Korea": "North Korea",  # Keep simple name
    "Iran": "Iran",  # Keep simple name
    "Syria": "Syria",
    "Venezuela": "Venezuela",
    "Bolivia": "Bolivia",
    "Tanzania": "Tanzania",
    "Vietnam": "Vietnam",
    "Laos": "Laos",
    "Brunei": "Brunei",
    "Moldova": "Moldova",
    "Czech Republic": "Czechia",
    "Czechia": "Czechia",
    "Ivory Coast": "Cote d'Ivoire",
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Cape Verde": "Cabo Verde",
    "Swaziland": "Eswatini",
    "Macedonia": "North Macedonia",
    "Burma": "Myanmar",
    "East Timor": "Timor-Leste",
    "Democratic Republic of Congo": "DR Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "Congo, The Democratic Republic of the": "DR Congo",
    "DRC": "DR Congo",
    "Congo-Kinshasa": "DR Congo",
    "Republic of Congo": "Congo",
    "Congo-Brazzaville": "Congo",
    "Republic of the Congo": "Congo",
    "Vatican": "Vatican City",
    "Vatican City State": "Vatican City",
    "Holy See": "Vatican City",
    "Holy See (Vatican City State)": "Vatican City",
    "The Bahamas": "Bahamas",
    "The Gambia": "Gambia",
    "Federated States of Micronesia": "Micronesia",
    "Micronesia, Federated States of": "Micronesia",
}


def safe_standardize_country_name(name: str) -> str:
    """
    Safely standardize country name without problematic fuzzy matching.

    Returns original name if:
    - It's in the keep-original list
    - It's an aggregate
    - Fuzzy matching might give wrong results
    """
    if not name or pd.isna(name):
        return name

    name = str(name).strip()

    # Check if should keep original
    if name in KEEP_ORIGINAL_NAMES:
        return name

    # Check if it's an aggregate (don't standardize aggregates)
    if is_aggregate(name):
        return name

    # Check simple aliases
    if name in SIMPLE_COUNTRY_ALIASES:
        return SIMPLE_COUNTRY_ALIASES[name]

    # For other names, only use exact match from pycountry, not fuzzy
    try:
        import pycountry

        # Try exact match only
        country = pycountry.countries.get(name=name)
        if country:
            # Return common name if available, otherwise official name
            return getattr(country, "common_name", country.name)
    except (LookupError, KeyError):
        pass

    # Return original if no exact match
    return name


def standardize_country_column(
    df: pd.DataFrame, country_col: str = "country"
) -> Tuple[pd.DataFrame, Dict]:
    """
    Standardize country names in a DataFrame.

    Returns:
        Tuple of (cleaned DataFrame, mapping stats dict)
    """
    df = df.copy()

    # Find the country column (case-insensitive)
    actual_col = None
    for col in df.columns:
        if col.lower() in ["country", "entity", "country_name"]:
            actual_col = col
            break

    if actual_col is None:
        return df, {"standardized": False, "reason": "No country column found"}

    original_values = df[actual_col].unique().tolist()

    # Track mappings
    mappings = {}
    for val in original_values:
        if pd.isna(val):
            continue
        standardized = safe_standardize_country_name(str(val))
        if standardized != val:
            mappings[val] = standardized

    # Apply mappings
    df[actual_col] = df[actual_col].apply(
        lambda x: safe_standardize_country_name(str(x)) if pd.notna(x) else x
    )

    stats = {
        "standardized": True,
        "column": actual_col,
        "original_unique": len(original_values),
        "mapped_count": len(mappings),
        "mappings": mappings,
    }

    return df, stats


# =============================================================================
# Aggregate Filtering
# =============================================================================


def filter_aggregate_entities(
    df: pd.DataFrame, country_col: str = "country"
) -> Tuple[pd.DataFrame, Dict]:
    """
    Remove aggregate entities (World, Europe, etc.) from DataFrame.

    Returns:
        Tuple of (filtered DataFrame, filter stats dict)
    """
    df = df.copy()

    # Find the country column
    actual_col = None
    for col in df.columns:
        if col.lower() in ["country", "entity", "country_name"]:
            actual_col = col
            break

    if actual_col is None:
        return df, {"filtered": False, "reason": "No country column found"}

    # Identify aggregates
    original_count = len(df)
    aggregate_mask = df[actual_col].apply(
        lambda x: is_aggregate(str(x)) if pd.notna(x) else False
    )
    removed_entities = df.loc[aggregate_mask, actual_col].unique().tolist()

    # Filter out aggregates
    df_filtered = df[~aggregate_mask].copy()

    stats = {
        "filtered": True,
        "column": actual_col,
        "original_rows": original_count,
        "filtered_rows": len(df_filtered),
        "removed_rows": original_count - len(df_filtered),
        "removed_entities": sorted(removed_entities),
        "removed_count": len(removed_entities),
    }

    return df_filtered, stats


# =============================================================================
# Data Type Fixing
# =============================================================================


def parse_numeric_string(value) -> Optional[float]:
    """
    Parse numeric value from string, handling various formats.

    Handles:
    - Comma separators: "1,234,567" -> 1234567
    - Dollar signs: "$1,234" -> 1234
    - Percentages: "45%" -> 45
    - Scientific notation: "1.23e6" -> 1230000
    - Spaces as separators: "1 234 567" -> 1234567
    """
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return np.nan

    # Clean the string
    s = value.strip()

    if s == "" or s.lower() in ["nan", "na", "n/a", "-", "--", "..."]:
        return np.nan

    # Remove common prefixes/suffixes
    s = s.replace("$", "").replace("€", "").replace("£", "")
    s = s.replace("%", "")

    # Remove thousand separators (but be careful with decimal points)
    # If there's a comma followed by 3 digits, it's likely a thousand separator
    s = re.sub(r",(\d{3})", r"\1", s)

    # Handle space as thousand separator
    s = re.sub(r"\s+", "", s)

    try:
        return float(s)
    except ValueError:
        return np.nan


def fix_data_types(
    df: pd.DataFrame, numeric_hints: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Fix data types, converting string columns to numeric where appropriate.

    Args:
        df: Input DataFrame
        numeric_hints: List of column name patterns that should be numeric

    Returns:
        Tuple of (cleaned DataFrame, conversion stats dict)
    """
    df = df.copy()

    if numeric_hints is None:
        numeric_hints = [
            "gdp",
            "population",
            "co2",
            "energy",
            "emission",
            "per_capita",
            "share",
            "rate",
            "percent",
            "density",
            "area",
            "land",
            "urban",
            "tax",
            "unemployment",
            "birth",
            "death",
            "life",
            "fertility",
            "infant",
            "latitude",
            "longitude",
        ]

    conversions = {}

    for col in df.columns:
        # Skip already numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Check if column name suggests it should be numeric
        col_lower = col.lower()
        should_convert = any(hint in col_lower for hint in numeric_hints)

        if not should_convert:
            # Check if the column contains mostly numeric-looking values
            sample = df[col].dropna().head(100)
            if len(sample) > 0:
                numeric_count = sum(
                    1
                    for v in sample
                    if isinstance(v, str)
                    and re.match(r"^[\$€£]?[\d,\s]+\.?\d*%?$", v.strip())
                )
                if numeric_count / len(sample) > 0.5:
                    should_convert = True

        if should_convert:
            original_dtype = str(df[col].dtype)
            original_non_null = df[col].notna().sum()

            # Convert
            df[col] = df[col].apply(parse_numeric_string)

            new_non_null = df[col].notna().sum()

            conversions[col] = {
                "original_dtype": original_dtype,
                "new_dtype": str(df[col].dtype),
                "original_non_null": original_non_null,
                "new_non_null": new_non_null,
                "lost_values": original_non_null - new_non_null,
            }

    stats = {
        "converted_columns": list(conversions.keys()),
        "conversion_count": len(conversions),
        "details": conversions,
    }

    return df, stats


# =============================================================================
# Value Range Validation
# =============================================================================


def validate_ranges(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Validate and fix value ranges (e.g., percentages should be 0-100).

    Note: Some "share" columns can have negative values (e.g., land use change
    can be negative = carbon sink), so we only validate true percentage columns.

    Returns:
        Tuple of (validated DataFrame, validation stats dict)
    """
    df = df.copy()
    validations = {}

    # Define expected ranges for common column patterns
    # Note: 'share' is NOT included here because emission shares can be negative
    range_rules = {
        "percent": (0, 100),
        "access": (0, 100),  # Access to electricity etc.
        "_of_population": (0, 100),
        "year": (1750, 2100),  # Reasonable year range for historical data
    }

    # Columns that should NOT be validated even if they match patterns
    # (because they can legitimately have negative values or exceed 100%)
    skip_patterns = [
        "share_global",  # Can be negative for land use change
        "share_of_temperature",  # Can be negative
        "trade_co2_share",  # Can exceed 100% (net exporters)
        "luc",  # Land use change - can be negative
        "change",  # Rate of change can be negative
        "growth",  # Growth can be negative
    ]

    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        col_lower = col.lower()

        # Skip columns that can legitimately have out-of-range values
        if any(skip in col_lower for skip in skip_patterns):
            continue

        for pattern, (min_val, max_val) in range_rules.items():
            if pattern in col_lower:
                original_values = df[col].copy()

                # Count out-of-range values
                below_min = (df[col] < min_val).sum()
                above_max = (df[col] > max_val).sum()

                if below_min > 0 or above_max > 0:
                    validations[col] = {
                        "expected_range": f"[{min_val}, {max_val}]",
                        "below_min": int(below_min),
                        "above_max": int(above_max),
                        "min_value": (
                            float(df[col].min()) if df[col].notna().any() else None
                        ),
                        "max_value": (
                            float(df[col].max()) if df[col].notna().any() else None
                        ),
                    }

                    # For percentages, if values are in 0-1 range, multiply by 100
                    if pattern in ["percent", "access", "_of_population"]:
                        if df[col].max() <= 1 and df[col].min() >= 0:
                            df[col] = df[col] * 100
                            validations[col][
                                "action"
                            ] = "Multiplied by 100 (was in 0-1 range)"

                break

    stats = {
        "validated_columns": list(validations.keys()),
        "validation_count": len(validations),
        "details": validations,
    }

    return df, stats


# =============================================================================
# Column Name Standardization
# =============================================================================


def standardize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Standardize column names to snake_case.

    Returns:
        Tuple of (DataFrame with standardized names, mapping dict)
    """
    original_names = df.columns.tolist()
    df_clean = standardize_column_names(df)
    new_names = df_clean.columns.tolist()

    mappings = {
        orig: new for orig, new in zip(original_names, new_names) if orig != new
    }

    stats = {
        "original_columns": original_names,
        "new_columns": new_names,
        "renamed_count": len(mappings),
        "mappings": mappings,
    }

    return df_clean, stats


# =============================================================================
# Dataset-Specific Cleaning Functions
# =============================================================================


def clean_owid_co2(ds: hf_datasets.Dataset) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean OWID CO2 dataset.

    Specific cleaning:
    - Remove aggregate entities
    - Standardize country names
    - Validate year range
    - Keep only relevant columns for analysis
    """
    df = ds.to_pandas()
    all_stats = {"dataset": "OWID CO2", "original_shape": df.shape}

    # 1. Standardize column names
    df, col_stats = standardize_columns(df)
    all_stats["column_standardization"] = col_stats

    # 2. Filter aggregates
    df, filter_stats = filter_aggregate_entities(df)
    all_stats["aggregate_filtering"] = filter_stats

    # 3. Standardize country names
    df, country_stats = standardize_country_column(df)
    all_stats["country_standardization"] = country_stats

    # 4. Fix data types (most should already be correct in OWID)
    df, dtype_stats = fix_data_types(df)
    all_stats["dtype_conversion"] = dtype_stats

    # 5. Validate ranges
    df, range_stats = validate_ranges(df)
    all_stats["range_validation"] = range_stats

    # 6. Filter year range (focus on 1990-2023 for most complete data)
    if "year" in df.columns:
        original_years = df["year"].nunique()
        df = df[(df["year"] >= 1990) & (df["year"] <= 2023)]
        all_stats["year_filter"] = {
            "original_years": original_years,
            "filtered_years": df["year"].nunique(),
            "range": "1990-2023",
        }

    all_stats["final_shape"] = df.shape

    return df, all_stats


def clean_sustainable_energy(ds: hf_datasets.Dataset) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean Sustainable Energy dataset.

    Specific cleaning:
    - Rename Entity -> country
    - Rename Year -> year
    - Remove aggregates
    - Standardize country names
    - Fix percentage columns
    """
    df = ds.to_pandas()
    all_stats = {"dataset": "Sustainable Energy", "original_shape": df.shape}

    # 1. First rename Entity/Year BEFORE standardizing column names
    # (so we can find the country column later)
    pre_rename = {}
    if "Entity" in df.columns:
        pre_rename["Entity"] = "country"
    if "Year" in df.columns:
        pre_rename["Year"] = "year"

    if pre_rename:
        df = df.rename(columns=pre_rename)
        all_stats["entity_year_rename"] = pre_rename

    # 2. Standardize column names (snake_case)
    df, col_stats = standardize_columns(df)
    all_stats["column_standardization"] = col_stats

    # 3. Filter aggregates - this dataset DOES have aggregates
    df, filter_stats = filter_aggregate_entities(df)
    all_stats["aggregate_filtering"] = filter_stats

    # 4. Standardize country names
    df, country_stats = standardize_country_column(df)
    all_stats["country_standardization"] = country_stats

    # 5. Fix data types
    df, dtype_stats = fix_data_types(df)
    all_stats["dtype_conversion"] = dtype_stats

    # 6. Validate ranges
    df, range_stats = validate_ranges(df)
    all_stats["range_validation"] = range_stats

    all_stats["final_shape"] = df.shape

    return df, all_stats


def clean_countries_2023(ds: hf_datasets.Dataset) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean Countries of the World 2023 dataset.

    Specific cleaning:
    - Standardize column names
    - Convert string numeric columns (GDP, Population, etc.)
    - Standardize country names
    - Remove aggregates if any
    """
    df = ds.to_pandas()
    all_stats = {"dataset": "Countries 2023", "original_shape": df.shape}

    # 1. Standardize column names
    df, col_stats = standardize_columns(df)
    all_stats["column_standardization"] = col_stats

    # 2. Filter aggregates (if any)
    df, filter_stats = filter_aggregate_entities(df)
    all_stats["aggregate_filtering"] = filter_stats

    # 3. Standardize country names
    df, country_stats = standardize_country_column(df)
    all_stats["country_standardization"] = country_stats

    # 4. Fix data types - this dataset has many string-formatted numbers
    df, dtype_stats = fix_data_types(df)
    all_stats["dtype_conversion"] = dtype_stats

    # 5. Validate ranges
    df, range_stats = validate_ranges(df)
    all_stats["range_validation"] = range_stats

    all_stats["final_shape"] = df.shape

    return df, all_stats


# =============================================================================
# Report Generation
# =============================================================================


def generate_cleaning_report(
    owid_stats: Dict,
    energy_stats: Dict,
    countries_stats: Dict,
) -> ReportBuilder:
    """Generate markdown report for cleaning step."""
    report = ReportBuilder(title="Czyszczenie i standaryzacja danych")

    report.add_paragraph(
        "Niniejszy raport dokumentuje proces czyszczenia i standaryzacji trzech "
        "zbiorów danych wykorzystywanych w projekcie. Proces obejmuje: standaryzację "
        "nazw krajów, ujednolicenie nazw kolumn, usunięcie agregatów regionalnych, "
        "konwersję typów danych oraz walidację zakresów wartości."
    )

    # =========================================================================
    # Summary Table
    # =========================================================================
    report.add_heading("Podsumowanie czyszczenia", level=2)

    summary_data = []
    for stats in [owid_stats, energy_stats, countries_stats]:
        orig_rows, orig_cols = stats["original_shape"]
        final_rows, final_cols = stats["final_shape"]
        removed_rows = orig_rows - final_rows

        summary_data.append(
            {
                "Dataset": stats["dataset"],
                "Wiersze (przed)": f"{orig_rows:,}",
                "Wiersze (po)": f"{final_rows:,}",
                "Usunięte wiersze": f"{removed_rows:,}",
                "Kolumny (przed)": orig_cols,
                "Kolumny (po)": final_cols,
            }
        )

    report.add_table(pd.DataFrame(summary_data))

    # =========================================================================
    # Dataset-specific details
    # =========================================================================
    for stats in [owid_stats, energy_stats, countries_stats]:
        report.add_separator()
        report.add_heading(f"Dataset: {stats['dataset']}", level=2)

        # Column standardization
        col_stats = stats.get("column_standardization", {})
        if col_stats.get("renamed_count", 0) > 0:
            report.add_heading("Standaryzacja nazw kolumn", level=3)
            report.add_paragraph(
                f"Zmieniono nazwy {col_stats['renamed_count']} kolumn na format snake_case."
            )

            # Show sample mappings (not all if there are many)
            mappings = col_stats.get("mappings", {})
            if mappings:
                sample_mappings = dict(list(mappings.items())[:10])
                mapping_df = pd.DataFrame(
                    [(k, v) for k, v in sample_mappings.items()],
                    columns=["Oryginalna nazwa", "Nowa nazwa"],
                )
                report.add_table(mapping_df)

                if len(mappings) > 10:
                    report.add_paragraph(
                        f"*... oraz {len(mappings) - 10} innych zmian*"
                    )

        # Aggregate filtering
        filter_stats = stats.get("aggregate_filtering", {})
        if filter_stats.get("filtered", False):
            report.add_heading("Filtrowanie agregatów", level=3)

            removed = filter_stats.get("removed_count", 0)
            removed_rows = filter_stats.get("removed_rows", 0)

            if removed > 0:
                report.add_paragraph(
                    f"Usunięto **{removed}** encji agregujących "
                    f"({removed_rows:,} wierszy)."
                )

                # List removed entities
                removed_entities = filter_stats.get("removed_entities", [])
                if removed_entities:
                    report.add_paragraph("**Usunięte encje:**")
                    # Show first 20
                    for entity in removed_entities[:20]:
                        report.add_bullet(entity)
                    if len(removed_entities) > 20:
                        report.add_paragraph(
                            f"*... oraz {len(removed_entities) - 20} innych*"
                        )
            else:
                report.add_paragraph("Nie znaleziono agregatów do usunięcia.")

        # Country name standardization
        country_stats = stats.get("country_standardization", {})
        if country_stats.get("standardized", False):
            report.add_heading("Standaryzacja nazw krajów", level=3)

            mapped = country_stats.get("mapped_count", 0)
            if mapped > 0:
                report.add_paragraph(
                    f"Znormalizowano nazwy **{mapped}** krajów do standardowego formatu."
                )

                mappings = country_stats.get("mappings", {})
                if mappings:
                    sample_mappings = dict(list(mappings.items())[:15])
                    mapping_df = pd.DataFrame(
                        [(k, v) for k, v in sample_mappings.items()],
                        columns=["Nazwa oryginalna", "Nazwa znormalizowana"],
                    )
                    report.add_table(mapping_df)

                    if len(mappings) > 15:
                        report.add_paragraph(
                            f"*... oraz {len(mappings) - 15} innych zmian*"
                        )
            else:
                report.add_paragraph(
                    "Wszystkie nazwy krajów były już w standardowym formacie."
                )

        # Data type conversion
        dtype_stats = stats.get("dtype_conversion", {})
        if dtype_stats.get("conversion_count", 0) > 0:
            report.add_heading("Konwersja typów danych", level=3)

            conversions = dtype_stats.get("details", {})
            conv_data = []
            for col, details in list(conversions.items())[:10]:
                conv_data.append(
                    {
                        "Kolumna": col,
                        "Typ (przed)": details["original_dtype"],
                        "Typ (po)": details["new_dtype"],
                        "Utracone wartości": details["lost_values"],
                    }
                )

            if conv_data:
                report.add_table(pd.DataFrame(conv_data))

            if len(conversions) > 10:
                report.add_paragraph(
                    f"*... oraz {len(conversions) - 10} innych konwersji*"
                )

        # Range validation
        range_stats = stats.get("range_validation", {})
        if range_stats.get("validation_count", 0) > 0:
            report.add_heading("Walidacja zakresów wartości", level=3)

            validations = range_stats.get("details", {})
            val_data = []
            for col, details in validations.items():
                val_data.append(
                    {
                        "Kolumna": col,
                        "Oczekiwany zakres": details["expected_range"],
                        "Poniżej min": details["below_min"],
                        "Powyżej max": details["above_max"],
                        "Działanie": details.get("action", "Brak"),
                    }
                )

            if val_data:
                report.add_table(pd.DataFrame(val_data))

        # Year filter (OWID specific)
        year_filter = stats.get("year_filter", {})
        if year_filter:
            report.add_heading("Filtrowanie zakresu czasowego", level=3)
            report.add_paragraph(
                f"Ograniczono dane do zakresu lat **{year_filter['range']}** "
                f"(z {year_filter['original_years']} do {year_filter['filtered_years']} unikalnych lat)."
            )

    # =========================================================================
    # Final Summary
    # =========================================================================
    report.add_separator()
    report.add_heading("Wnioski i następne kroki", level=2)

    report.add_paragraph(
        "Wszystkie trzy datasety zostały wyczyszczone i przygotowane do etapu "
        "łączenia (merging). Kluczowe zmiany:"
    )

    report.add_bullet(
        "Nazwy krajów zostały znormalizowane, co umożliwi łączenie po kluczu `country`"
    )
    report.add_bullet(
        "Usunięto agregaty regionalne (World, Europe, etc.), pozostawiając tylko kraje"
    )
    report.add_bullet("Nazwy kolumn zostały ujednolicone do formatu snake_case")
    report.add_bullet("Kolumny numeryczne zapisane jako tekst zostały skonwertowane")

    report.add_newline()
    report.add_paragraph(
        "**Następny krok:** Łączenie datasetów po kluczu `(country, year)` "
        "w celu utworzenia zintegrowanego zbioru danych panelowych."
    )

    return report


# =============================================================================
# Main Function
# =============================================================================


def run_cleaning(
    ds_owid_co2: hf_datasets.Dataset,
    ds_sustainable_energy: hf_datasets.Dataset,
    ds_countries: hf_datasets.Dataset,
) -> Tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run complete data cleaning for all datasets.

    Args:
        ds_owid_co2: OWID CO2 dataset
        ds_sustainable_energy: Sustainable Energy dataset
        ds_countries: Countries of the World 2023 dataset

    Returns:
        Tuple of (report_path, df_owid_cleaned, df_energy_cleaned, df_countries_cleaned)
    """
    # Setup
    setup_plotting_style()
    create_dir(CLEANED_DIR)
    create_dir(FIGURES_DIR)

    print("Cleaning datasets...")

    # =========================================================================
    # Clean OWID CO2
    # =========================================================================
    print("  Cleaning OWID CO2...")
    df_owid, owid_stats = clean_owid_co2(ds_owid_co2)
    print(
        f"    {owid_stats['original_shape'][0]:,} -> {owid_stats['final_shape'][0]:,} rows"
    )

    # Save cleaned dataset
    owid_path = os.path.join(CLEANED_DIR, "owid_co2_cleaned.parquet")
    write_parquet(df_owid, owid_path)
    print(f"    Saved: {owid_path}")

    # =========================================================================
    # Clean Sustainable Energy
    # =========================================================================
    print("  Cleaning Sustainable Energy...")
    df_energy, energy_stats = clean_sustainable_energy(ds_sustainable_energy)
    print(
        f"    {energy_stats['original_shape'][0]:,} -> {energy_stats['final_shape'][0]:,} rows"
    )

    # Save cleaned dataset
    energy_path = os.path.join(CLEANED_DIR, "sustainable_energy_cleaned.parquet")
    write_parquet(df_energy, energy_path)
    print(f"    Saved: {energy_path}")

    # =========================================================================
    # Clean Countries 2023
    # =========================================================================
    print("  Cleaning Countries 2023...")
    df_countries, countries_stats = clean_countries_2023(ds_countries)
    print(
        f"    {countries_stats['original_shape'][0]:,} -> {countries_stats['final_shape'][0]:,} rows"
    )

    # Save cleaned dataset
    countries_path = os.path.join(CLEANED_DIR, "countries_cleaned.parquet")
    write_parquet(df_countries, countries_path)
    print(f"    Saved: {countries_path}")

    # =========================================================================
    # Generate Report
    # =========================================================================
    print("  Generating report...")
    report = generate_cleaning_report(owid_stats, energy_stats, countries_stats)

    # Add output paths to report
    report.add_separator()
    report.add_heading("Pliki wyjściowe", level=2)

    rel_owid = os.path.relpath(owid_path, REPORT_DIR).replace("\\", "/")
    rel_energy = os.path.relpath(energy_path, REPORT_DIR).replace("\\", "/")
    rel_countries = os.path.relpath(countries_path, REPORT_DIR).replace("\\", "/")

    report.add_bullet(f"OWID CO2: `{rel_owid}`")
    report.add_bullet(f"Sustainable Energy: `{rel_energy}`")
    report.add_bullet(f"Countries 2023: `{rel_countries}`")

    # Save report
    report_path = report.save("02_cleaning.md")

    print(f"\n✅ Cleaning complete!")
    print(f"   Report: {report_path}")
    print(f"   Cleaned data: {CLEANED_DIR}")

    return report_path, df_owid, df_energy, df_countries


# =============================================================================
# Standalone execution
# =============================================================================

if __name__ == "__main__":
    # For standalone testing - load datasets from cache
    from steps.step_00_download import (
        get_owid_co2_dataset,
        get_sustainable_energy_dataset,
        get_countries_of_world_dataset,
    )

    ds_owid = get_owid_co2_dataset()
    ds_energy = get_sustainable_energy_dataset()
    ds_countries = get_countries_of_world_dataset()

    run_cleaning(ds_owid, ds_energy, ds_countries)
