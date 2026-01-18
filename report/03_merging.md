# Laczenie zbiorow danych

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport dokumentuje proces laczenia trzech zbiorow danych w jeden spojny zbior panelowy. Laczenie odbywa sie po kluczach `country` i `year` dla danych czasowych oraz `country` dla danych przekrojowych.

**Schemat laczenia:**

```

OWID CO2 Data                    Sustainable Energy Data
     |                                    |
     | (country, year)                    | (country, year)
     |                                    |
     +----------------+-------------------+
                      |
                      v
              +---------------+
              |  MERGED DATA  |
              |  (2000-2020)  |
              +-------+-------+
                      |
                      | (country)
                      v
              +---------------+
              | Country Info  |
              | (urbanizacja) |
              +---------------+
    
```


---

## Laczenie OWID CO2 z Sustainable Energy

### Statystyki przed laczeniem

| Metric                       | Value   |
|:-----------------------------|:--------|
| OWID CO2 - wiersze           | 4,557   |
| OWID CO2 - kraje             | 216     |
| Sustainable Energy - wiersze | 3,649   |
| Sustainable Energy - kraje   | 176     |

### Wynik laczenia

| Metric                    | Value   |
|:--------------------------|:--------|
| Polaczony zbior - wiersze | 4,557   |
| Polaczony zbior - kraje   | 216     |
| Nowe kolumny z Energy     | 19      |

**Usuniete duplikaty kolumn z Energy:**

- `iso_code`

**Nowe kolumny dodane z Sustainable Energy:**

- `access_to_electricity_of_population`

- `access_to_clean_fuels_for_cooking`

- `renewable_electricity_generating_capacity_per_capita`

- `financial_flows_to_developing_countries_us`

- `renewable_energy_share_in_the_total_final_energy_consumption`

- `electricity_from_fossil_fuels_twh`

- `electricity_from_nuclear_twh`

- `electricity_from_renewables_twh`

- `low_carbon_electricity_electricity`

- `primary_energy_consumption_per_capita_kwhperson`

- `energy_intensity_level_of_primary_energy_mj2017_ppp_gdp`

- `value_co2_emissions_kt_by_country`

- `renewables_equivalent_primary_energy`

- `gdp_growth`

- `gdp_per_capita`


---

## Dodanie metadanych krajow (Countries 2023)

| Metric        | Value   |
|:--------------|:--------|
| Wiersze przed | 4,557   |
| Wiersze po    | 4,557   |
| Kolumny przed | 4557    |
| Kolumny po    | 127     |
| Nowe kolumny  | 29      |

**Dodane kolumny z Countries 2023:**

- `density_pkm2`

- `abbreviation`

- `agricultural_land`

- `armed_forces_size`

- `birth_rate`

- `calling_code`

- `capitalmajor_city`

- `co2_emissions`

- `cpi`

- `cpi_change`

- `currency_code`

- `fertility_rate`

- `forested_area`

- `gasoline_price`

- `gross_primary_education_enrollment`


---

## Walidacja polaczonego zbioru

### Ogolne statystyki

| Metric         | Value       |
|:---------------|:------------|
| Liczba wierszy | 4,557       |
| Liczba kolumn  | 127         |
| Unikalne kraje | 216         |
| Zakres lat     | 2000 - 2020 |
| Unikalne lata  | 21          |

### Pokrycie kluczowych zmiennych

| Metric         | Value   |
|:---------------|:--------|
| co2            | 98.62%  |
| co2_per_capita | 98.16%  |
| gdp            | 75.58%  |
| population     | 99.54%  |

> ⚠️ **Warning:** Znaleziono 42 zduplikowanych kluczy (country, year)!


---

## Analiza pokrycia krajow

| Metric               |   Value |
|:---------------------|--------:|
| Kraje w obu zbiorach |     173 |
| Kraje tylko w OWID   |      43 |
| Kraje tylko w Energy |       0 |

**Przykladowe kraje tylko w OWID:**

- Andorra

- Anguilla

- Bolivia, Plurinational State of

- Bonaire Sint Eustatius and Saba

- Brunei Darussalam

- Cabo Verde

- Christmas Island

- Congo, The Democratic Republic of the

- Cook Islands

- Côte d'Ivoire


---

## Struktura finalnego zbioru

### Kolumny identyfikujace

`country`, `year`, `iso_code`

### Kolumny emisji (wybrane)

`cement_co2`, `cement_co2_per_capita`, `co2`, `co2_growth_abs`, `co2_growth_prct`, `co2_including_luc`, `co2_including_luc_growth_abs`, `co2_including_luc_growth_prct`, `co2_including_luc_per_capita`, `co2_including_luc_per_gdp`

### Kolumny energetyczne (wybrane)

`co2_including_luc_per_unit_energy`, `co2_per_unit_energy`, `energy_per_capita`, `energy_per_gdp`, `primary_energy_consumption`, `access_to_electricity_of_population`, `renewable_electricity_generating_capacity_per_capita`, `renewable_energy_share_in_the_total_final_energy_consumption`, `electricity_from_fossil_fuels_twh`, `electricity_from_nuclear_twh`

### Kolumny ekonomiczne

`population`, `gdp`, `co2_including_luc_per_gdp`, `co2_per_gdp`, `consumption_co2_per_gdp`, `energy_per_gdp`, `access_to_electricity_of_population`, `energy_intensity_level_of_primary_energy_mj2017_ppp_gdp`, `gdp_growth`, `gdp_per_capita`


---

## Podsumowanie

**Wynik laczenia:**

1. Polaczony zbior panelowy: 4,557 obserwacji

2. Liczba krajow: 216

3. Zakres czasowy: 2000-2020

4. Liczba zmiennych: 127

**Zapisany plik:**

- `out/merged/merged_panel.parquet`

**Nastepne kroki:**

- Eksploracyjna analiza danych (EDA)

- Tworzenie nowych zmiennych

- Analiza outlierow i brakow danych
