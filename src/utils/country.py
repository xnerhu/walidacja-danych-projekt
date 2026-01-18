# src/utils/country.py
"""
Country utilities - complements pycountry with project-specific helpers.

Uses pycountry for standard lookups, adds:
- Aggregate detection (World, Europe, etc.)
- Region mapping
- Common name aliases
"""

import pycountry
from typing import Optional, List, Set


# =============================================================================
# Aggregate Entities (not real countries)
# =============================================================================

# Common aggregates found in OWID and other datasets
AGGREGATES: Set[str] = {
    # Global
    "World",
    "Global",
    # Continents
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Oceania",
    "Antarctica",
    # Regions
    "European Union",
    "European Union (27)",
    "European Union (28)",
    "EU-27",
    "EU-28",
    "EU",
    "OECD",
    "G7",
    "G20",
    "BRICS",
    "OPEC",
    "NATO",
    # Income groups
    "High income",
    "High-income countries",
    "Upper middle income",
    "Upper-middle-income countries",
    "Lower middle income",
    "Lower-middle-income countries",
    "Low income",
    "Low-income countries",
    # Other groupings
    "Africa (GCP)",
    "Asia (GCP)",
    "Central America (GCP)",
    "Europe (GCP)",
    "Middle East (GCP)",
    "North America (GCP)",
    "Oceania (GCP)",
    "South America (GCP)",
    "Asia (excl. China and India)",
    "Europe (excl. EU-27)",
    "Europe (excl. EU-28)",
    "European Union (27) (GCP)",
    "International transport",
    "International aviation",
    "International shipping",
    "Kuwaiti Oil Fires",
    "Non-OECD",
    "OECD (GCP)",
    # Historical
    "USSR",
    "Czechoslovakia",
    "Yugoslavia",
    "East Germany",
    "West Germany",
}


def is_aggregate(name: str) -> bool:
    """
    Check if name is an aggregate/grouping rather than a real country.

    Args:
        name: Country/entity name

    Returns:
        True if it's an aggregate
    """
    if name in AGGREGATES:
        return True

    # Check patterns
    name_lower = name.lower()
    aggregate_patterns = [
        "(gcp)",
        "(excl.",
        "income countries",
        "income ",
        "international ",
    ]

    return any(pattern in name_lower for pattern in aggregate_patterns)


def get_aggregates_list() -> List[str]:
    """Return list of known aggregate names."""
    return sorted(AGGREGATES)


def filter_aggregates(names: List[str]) -> List[str]:
    """Filter out aggregates from a list of names."""
    return [name for name in names if not is_aggregate(name)]


# =============================================================================
# Country Name Standardization
# =============================================================================

# Common aliases/variations -> standard name
COUNTRY_ALIASES: dict = {
    # USA variations
    "USA": "United States",
    "US": "United States",
    "U.S.": "United States",
    "U.S.A.": "United States",
    "United States of America": "United States",
    "America": "United States",
    # UK variations
    "UK": "United Kingdom",
    "U.K.": "United Kingdom",
    "Great Britain": "United Kingdom",
    "Britain": "United Kingdom",
    "England": "United Kingdom",  # Note: technically incorrect but common
    # Russia variations
    "Russia": "Russian Federation",
    # Korea variations
    "South Korea": "Korea, Republic of",
    "Korea, South": "Korea, Republic of",
    "Republic of Korea": "Korea, Republic of",
    "North Korea": "Korea, Democratic People's Republic of",
    "Korea, North": "Korea, Democratic People's Republic of",
    # China variations
    "China": "China",
    "Mainland China": "China",
    "People's Republic of China": "China",
    "Taiwan": "Taiwan, Province of China",
    # Iran
    "Iran": "Iran, Islamic Republic of",
    # Syria
    "Syria": "Syrian Arab Republic",
    # Venezuela
    "Venezuela": "Venezuela, Bolivarian Republic of",
    # Bolivia
    "Bolivia": "Bolivia, Plurinational State of",
    # Tanzania
    "Tanzania": "Tanzania, United Republic of",
    # Vietnam
    "Vietnam": "Viet Nam",
    # Laos
    "Laos": "Lao People's Democratic Republic",
    # Brunei
    "Brunei": "Brunei Darussalam",
    # Moldova
    "Moldova": "Moldova, Republic of",
    # Czechia / Czech Republic
    "Czech Republic": "Czechia",
    # Other common
    "Ivory Coast": "Côte d'Ivoire",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Cape Verde": "Cabo Verde",
    "Swaziland": "Eswatini",
    "Macedonia": "North Macedonia",
    "Burma": "Myanmar",
    "East Timor": "Timor-Leste",
    "Democratic Republic of Congo": "Congo, The Democratic Republic of the",
    "DR Congo": "Congo, The Democratic Republic of the",
    "DRC": "Congo, The Democratic Republic of the",
    "Congo-Kinshasa": "Congo, The Democratic Republic of the",
    "Republic of Congo": "Congo",
    "Congo-Brazzaville": "Congo",
    "Micronesia": "Micronesia, Federated States of",
    "Palestine": "Palestine, State of",
    "Vatican": "Holy See (Vatican City State)",
    "Vatican City": "Holy See (Vatican City State)",
}


def standardize_country_name(name: str) -> str:
    """
    Standardize country name to pycountry standard form.

    Args:
        name: Input country name (any common variation)

    Returns:
        Standardized name (or original if not found)
    """
    if not name or is_aggregate(name):
        return name

    # Check aliases first
    if name in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[name]

    # Try pycountry lookup
    try:
        # Try exact match
        country = pycountry.countries.get(name=name)
        if country:
            return country.name

        # Try fuzzy search
        results = pycountry.countries.search_fuzzy(name)
        if results:
            return results[0].name
    except LookupError:
        pass

    return name


def get_country_iso(name: str) -> Optional[str]:
    """
    Get ISO 3166-1 alpha-3 code for country name.

    Args:
        name: Country name

    Returns:
        ISO alpha-3 code or None
    """
    if not name or is_aggregate(name):
        return None

    # Standardize first
    std_name = standardize_country_name(name)

    try:
        country = pycountry.countries.get(name=std_name)
        if country:
            return country.alpha_3

        # Try fuzzy search
        results = pycountry.countries.search_fuzzy(std_name)
        if results:
            return results[0].alpha_3
    except LookupError:
        pass

    return None


def get_country_from_iso(iso_code: str) -> Optional[str]:
    """
    Get country name from ISO code.

    Args:
        iso_code: ISO alpha-2 or alpha-3 code

    Returns:
        Country name or None
    """
    if not iso_code:
        return None

    try:
        if len(iso_code) == 2:
            country = pycountry.countries.get(alpha_2=iso_code)
        else:
            country = pycountry.countries.get(alpha_3=iso_code)

        return country.name if country else None
    except (LookupError, KeyError):
        return None


# =============================================================================
# Region Mapping
# =============================================================================

# ISO alpha-3 to region mapping
REGION_MAPPING: dict = {
    # Africa
    "DZA": "Africa",
    "AGO": "Africa",
    "BEN": "Africa",
    "BWA": "Africa",
    "BFA": "Africa",
    "BDI": "Africa",
    "CPV": "Africa",
    "CMR": "Africa",
    "CAF": "Africa",
    "TCD": "Africa",
    "COM": "Africa",
    "COG": "Africa",
    "COD": "Africa",
    "CIV": "Africa",
    "DJI": "Africa",
    "EGY": "Africa",
    "GNQ": "Africa",
    "ERI": "Africa",
    "SWZ": "Africa",
    "ETH": "Africa",
    "GAB": "Africa",
    "GMB": "Africa",
    "GHA": "Africa",
    "GIN": "Africa",
    "GNB": "Africa",
    "KEN": "Africa",
    "LSO": "Africa",
    "LBR": "Africa",
    "LBY": "Africa",
    "MDG": "Africa",
    "MWI": "Africa",
    "MLI": "Africa",
    "MRT": "Africa",
    "MUS": "Africa",
    "MAR": "Africa",
    "MOZ": "Africa",
    "NAM": "Africa",
    "NER": "Africa",
    "NGA": "Africa",
    "RWA": "Africa",
    "STP": "Africa",
    "SEN": "Africa",
    "SYC": "Africa",
    "SLE": "Africa",
    "SOM": "Africa",
    "ZAF": "Africa",
    "SSD": "Africa",
    "SDN": "Africa",
    "TZA": "Africa",
    "TGO": "Africa",
    "TUN": "Africa",
    "UGA": "Africa",
    "ZMB": "Africa",
    "ZWE": "Africa",
    # Asia
    "AFG": "Asia",
    "ARM": "Asia",
    "AZE": "Asia",
    "BHR": "Asia",
    "BGD": "Asia",
    "BTN": "Asia",
    "BRN": "Asia",
    "KHM": "Asia",
    "CHN": "Asia",
    "CYP": "Asia",
    "GEO": "Asia",
    "IND": "Asia",
    "IDN": "Asia",
    "IRN": "Asia",
    "IRQ": "Asia",
    "ISR": "Asia",
    "JPN": "Asia",
    "JOR": "Asia",
    "KAZ": "Asia",
    "KWT": "Asia",
    "KGZ": "Asia",
    "LAO": "Asia",
    "LBN": "Asia",
    "MYS": "Asia",
    "MDV": "Asia",
    "MNG": "Asia",
    "MMR": "Asia",
    "NPL": "Asia",
    "PRK": "Asia",
    "OMN": "Asia",
    "PAK": "Asia",
    "PSE": "Asia",
    "PHL": "Asia",
    "QAT": "Asia",
    "SAU": "Asia",
    "SGP": "Asia",
    "KOR": "Asia",
    "LKA": "Asia",
    "SYR": "Asia",
    "TWN": "Asia",
    "TJK": "Asia",
    "THA": "Asia",
    "TLS": "Asia",
    "TUR": "Asia",
    "TKM": "Asia",
    "ARE": "Asia",
    "UZB": "Asia",
    "VNM": "Asia",
    "YEM": "Asia",
    # Europe
    "ALB": "Europe",
    "AND": "Europe",
    "AUT": "Europe",
    "BLR": "Europe",
    "BEL": "Europe",
    "BIH": "Europe",
    "BGR": "Europe",
    "HRV": "Europe",
    "CZE": "Europe",
    "DNK": "Europe",
    "EST": "Europe",
    "FIN": "Europe",
    "FRA": "Europe",
    "DEU": "Europe",
    "GRC": "Europe",
    "HUN": "Europe",
    "ISL": "Europe",
    "IRL": "Europe",
    "ITA": "Europe",
    "XKX": "Europe",
    "LVA": "Europe",
    "LIE": "Europe",
    "LTU": "Europe",
    "LUX": "Europe",
    "MLT": "Europe",
    "MDA": "Europe",
    "MCO": "Europe",
    "MNE": "Europe",
    "NLD": "Europe",
    "MKD": "Europe",
    "NOR": "Europe",
    "POL": "Europe",
    "PRT": "Europe",
    "ROU": "Europe",
    "RUS": "Europe",
    "SMR": "Europe",
    "SRB": "Europe",
    "SVK": "Europe",
    "SVN": "Europe",
    "ESP": "Europe",
    "SWE": "Europe",
    "CHE": "Europe",
    "UKR": "Europe",
    "GBR": "Europe",
    "VAT": "Europe",
    # North America
    "ATG": "North America",
    "BHS": "North America",
    "BRB": "North America",
    "BLZ": "North America",
    "CAN": "North America",
    "CRI": "North America",
    "CUB": "North America",
    "DMA": "North America",
    "DOM": "North America",
    "SLV": "North America",
    "GRD": "North America",
    "GTM": "North America",
    "HTI": "North America",
    "HND": "North America",
    "JAM": "North America",
    "MEX": "North America",
    "NIC": "North America",
    "PAN": "North America",
    "KNA": "North America",
    "LCA": "North America",
    "VCT": "North America",
    "TTO": "North America",
    "USA": "North America",
    # South America
    "ARG": "South America",
    "BOL": "South America",
    "BRA": "South America",
    "CHL": "South America",
    "COL": "South America",
    "ECU": "South America",
    "GUY": "South America",
    "PRY": "South America",
    "PER": "South America",
    "SUR": "South America",
    "URY": "South America",
    "VEN": "South America",
    # Oceania
    "AUS": "Oceania",
    "FJI": "Oceania",
    "KIR": "Oceania",
    "MHL": "Oceania",
    "FSM": "Oceania",
    "NRU": "Oceania",
    "NZL": "Oceania",
    "PLW": "Oceania",
    "PNG": "Oceania",
    "WSM": "Oceania",
    "SLB": "Oceania",
    "TON": "Oceania",
    "TUV": "Oceania",
    "VUT": "Oceania",
}


def get_region(iso_code: str) -> Optional[str]:
    """
    Get region/continent for a country ISO code.

    Args:
        iso_code: ISO alpha-3 code

    Returns:
        Region name or None
    """
    if not iso_code:
        return None
    return REGION_MAPPING.get(iso_code.upper())


def get_region_by_name(country_name: str) -> Optional[str]:
    """
    Get region/continent for a country name.

    Args:
        country_name: Country name

    Returns:
        Region name or None
    """
    iso = get_country_iso(country_name)
    return get_region(iso) if iso else None


def add_region_column(df, country_col: str = "country", iso_col: Optional[str] = None):
    """
    Add region column to DataFrame.

    Args:
        df: DataFrame
        country_col: Column with country names
        iso_col: Column with ISO codes (optional, faster if available)

    Returns:
        DataFrame with 'region' column added
    """
    import pandas as pd

    df = df.copy()

    if iso_col and iso_col in df.columns:
        df["region"] = df[iso_col].apply(get_region)
    else:
        df["region"] = df[country_col].apply(get_region_by_name)

    return df


# =============================================================================
# Validation
# =============================================================================


def validate_countries(names: List[str]) -> dict:
    """
    Validate a list of country names.

    Returns:
        Dict with 'valid', 'invalid', 'aggregates' lists
    """
    valid = []
    invalid = []
    aggregates = []

    for name in names:
        if is_aggregate(name):
            aggregates.append(name)
        elif get_country_iso(name):
            valid.append(name)
        else:
            invalid.append(name)

    return {
        "valid": valid,
        "invalid": invalid,
        "aggregates": aggregates,
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "aggregate_count": len(aggregates),
    }
