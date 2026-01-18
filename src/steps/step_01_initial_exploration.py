from typing import Dict, Any
import datasets as hf_datasets
import pandas as pd
import numpy as np
from datetime import datetime
import utils.markdown as md

NASA_POWER_VARIABLE_DESCRIPTIONS = {
    "YEAR": "Year of observation",
    "MO": "Month of observation (1-12)",
    "DY": "Day of month (1-31)",
    "LAT": "Latitude in degrees (-90 to 90)",
    "LON": "Longitude in degrees (-180 to 180)",
    "T2M": "Temperature at 2 meters (°C) - daily mean",
    "T2MDEW": "Dew/frost point temperature at 2 meters (°C)",
    "T2MWET": "Wet bulb temperature at 2 meters (°C)",
    "TS": "Earth skin temperature (°C)",
    "T2M_RANGE": "Temperature range at 2 meters (°C)",
    "T2M_MAX": "Maximum temperature at 2 meters (°C)",
    "T2M_MIN": "Minimum temperature at 2 meters (°C)",
    "RH2M": "Relative humidity at 2 meters (%)",
    "PRECTOTCORR": "Precipitation corrected (mm/day)",
    "WS2M": "Wind speed at 2 meters (m/s)",
    "WS2M_MAX": "Maximum wind speed at 2 meters (m/s)",
    "WS2M_MIN": "Minimum wind speed at 2 meters (m/s)",
    "WS2M_RANGE": "Wind speed range at 2 meters (m/s)",
    "WD2M": "Wind direction at 2 meters (degrees)",
    "GWETTOP": "Surface soil wetness (fraction)",
    "GWETROOT": "Root zone soil wetness (fraction)",
    "GWETPROF": "Profile soil wetness (fraction)",
    "CLOUD_AMT": "Cloud amount (%)",
    "ALLSKY_SFC_SW_DWN": "All-sky surface shortwave downward irradiance (MJ/m²/day)",
    "ALLSKY_SFC_PAR_TOT": "All-sky surface PAR total (MJ/m²/day)",
    "ALLSKY_SRF_ALB": "All-sky surface albedo (fraction)",
    "ALLSKY_SFC_LW_DWN": "All-sky surface longwave downward irradiance (MJ/m²/day)",
    "ALLSKY_SFC_SW_DNI": "All-sky surface shortwave direct normal irradiance (MJ/m²/day)",
    "ALLSKY_SFC_SW_DIFF": "All-sky surface shortwave diffuse irradiance (MJ/m²/day)",
    "CDD18_3": "Cooling degree days (base 18.3°C)",
    "HDD18_3": "Heating degree days (base 18.3°C)",
    "ET0": "Reference evapotranspiration (mm/day)",
    "EVPTRNS": "Evapotranspiration energy flux (MJ/m²/day)",
    "SNODP": "Snow depth (cm)",
    "FROST_DAYS": "Frost days (count)",
    "QV2M": "Specific humidity at 2 meters (g/kg)",
    "PS": "Surface pressure (kPa)",
    "VAD": "Vapor pressure deficit (kPa)",
}

WILDFIRES_VARIABLE_DESCRIPTIONS = {
    "FOD_ID": "Unique fire identifier",
    "FPA_ID": "Fire Program Analysis unique identifier",
    "SOURCE_SYSTEM_TYPE": "Type of source system (federal, state, local)",
    "SOURCE_SYSTEM": "Name of source system",
    "NWCG_REPORTING_AGENCY": "NWCG reporting agency code",
    "NWCG_REPORTING_UNIT_ID": "NWCG reporting unit ID",
    "NWCG_REPORTING_UNIT_NAME": "Name of reporting unit",
    "SOURCE_REPORTING_UNIT": "Source-specific reporting unit",
    "SOURCE_REPORTING_UNIT_NAME": "Name of source reporting unit",
    "LOCAL_FIRE_REPORT_ID": "Local fire report identifier",
    "LOCAL_INCIDENT_ID": "Local incident identifier",
    "FIRE_CODE": "Fire code",
    "FIRE_NAME": "Name given to the fire",
    "ICS_209_INCIDENT_NUMBER": "ICS-209 incident number",
    "ICS_209_NAME": "ICS-209 incident name",
    "MTBS_ID": "Monitoring Trends in Burn Severity ID",
    "MTBS_FIRE_NAME": "MTBS fire name",
    "COMPLEX_NAME": "Complex fire name",
    "FIRE_YEAR": "Year of fire discovery",
    "DISCOVERY_DATE": "Julian date of fire discovery",
    "DISCOVERY_DOY": "Day of year of fire discovery (1-366)",
    "DISCOVERY_TIME": "Time of fire discovery (HHMM)",
    "STAT_CAUSE_CODE": "Statistical cause code (1-13)",
    "STAT_CAUSE_DESCR": "Description of fire cause",
    "CONT_DATE": "Julian date of fire containment",
    "CONT_DOY": "Day of year of fire containment",
    "CONT_TIME": "Time of fire containment (HHMM)",
    "FIRE_SIZE": "Fire size in acres",
    "FIRE_SIZE_CLASS": "Fire size class (A-G)",
    "LATITUDE": "Latitude of fire origin (decimal degrees)",
    "LONGITUDE": "Longitude of fire origin (decimal degrees)",
    "OWNER_CODE": "Owner code",
    "OWNER_DESCR": "Owner description",
    "STATE": "US state abbreviation",
    "COUNTY": "County name",
    "FIPS_CODE": "FIPS code",
    "FIPS_NAME": "FIPS name",
}

FIRE_SIZE_CLASSES = {
    "A": "0 - 0.25 acres",
    "B": "0.26 - 9.9 acres",
    "C": "10 - 99.9 acres",
    "D": "100 - 299.9 acres",
    "E": "300 - 999.9 acres",
    "F": "1000 - 4999.9 acres",
    "G": "5000+ acres",
}

FIRE_CAUSE_CODES = {
    1: "Lightning",
    2: "Equipment Use",
    3: "Smoking",
    4: "Campfire",
    5: "Debris Burning",
    6: "Railroad",
    7: "Arson",
    8: "Children",
    9: "Miscellaneous",
    10: "Fireworks",
    11: "Powerline",
    12: "Structure",
    13: "Missing/Undefined",
}


def __nasa_power_get_initial_exporation_md(ds: hf_datasets.Dataset) -> str:
    pass


def __us_wildfires_get_initial_exporation_md(ds: hf_datasets.Dataset) -> str:
    pass


def get_initial_exporation_md(
    ds_nasa_power: hf_datasets.Dataset,
    ds_us_wildfires: hf_datasets.Dataset,
) -> str:
    return "xd"
