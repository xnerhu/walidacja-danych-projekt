# Czyszczenie i standaryzacja danych

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport dokumentuje proces czyszczenia i standaryzacji trzech zbiorów danych. Celem było przygotowanie danych do łączenia i analizy.

**Wykonane operacje:**

- Standaryzacja nazw kolumn (snake_case)

- Usunięcie agregatów regionalnych (World, Europe, itp.)

- Filtrowanie do zakresu lat 2000-2020

- Standaryzacja nazw krajów

- Dodanie/weryfikacja kodów ISO

- Walidacja zakresów wartości


---

## OWID CO2 Data

### Podsumowanie zmian

| Metric           | Value     |
|:-----------------|:----------|
| Wiersze (przed)  | 50,411    |
| Wiersze (po)     | 4,557     |
| Usunięte wiersze | 45,854    |
| Kolumny          | 79        |
| Unikalne kraje   | 216       |
| Unikalne lata    | 21        |
| Zakres lat       | 2000-2020 |

### Usunięte agregaty

Usunięto 33 agregatów regionalnych:

- Africa

- Africa (GCP)

- Antarctica

- Asia

- Asia (GCP)

- Asia (excl. China and India)

- Central America (GCP)

- Europe

- Europe (GCP)

- Europe (excl. EU-27)

*... i 10 więcej*

### Przykłady standaryzacji nazw krajów

- Bolivia → Bolivia, Plurinational State of

- British Virgin Islands → Virgin Islands, British

- Brunei → Brunei Darussalam

- Cape Verde → Cabo Verde

- Cote d'Ivoire → Côte d'Ivoire

### Walidacja danych

Brak problemów z walidacją wartości nieujemnych.


---

## Sustainable Energy

### Podsumowanie zmian

| Metric          | Value   |
|:----------------|:--------|
| Wiersze (przed) | 3,649   |
| Wiersze (po)    | 3,649   |
| Kolumny (przed) | 21      |
| Kolumny (po)    | 22      |
| Unikalne kraje  | 176     |

### Przykłady zmian nazw kolumn

- `Entity` → `entity`

- `Year` → `year`

- `Access to electricity (% of population)` → `access_to_electricity_of_population`

- `Access to clean fuels for cooking` → `access_to_clean_fuels_for_cooking`

- `Renewable-electricity-generating-capacity-per-capita` → `renewable_electricity_generating_capacity_per_capita`

- `Financial flows to developing countries (US $)` → `financial_flows_to_developing_countries_us`

- `Renewable energy share in the total final energy consumption (%)` → `renewable_energy_share_in_the_total_final_energy_consumption`

- `Electricity from fossil fuels (TWh)` → `electricity_from_fossil_fuels_twh`

- `Electricity from nuclear (TWh)` → `electricity_from_nuclear_twh`

- `Electricity from renewables (TWh)` → `electricity_from_renewables_twh`


---

## Countries 2023

### Podsumowanie zmian

| Metric          |   Value |
|:----------------|--------:|
| Wiersze (przed) |     195 |
| Wiersze (po)    |     195 |
| Kolumny (przed) |      35 |
| Kolumny (po)    |      36 |
| Unikalne kraje  |     195 |


---

## Porównanie krajów między zbiorami

| Metric                     |   Value |
|:---------------------------|--------:|
| Kraje w OWID CO2           |     216 |
| Kraje w Sustainable Energy |     176 |
| Kraje w Countries 2023     |     195 |
| Wspólne (wszystkie 3)      |     168 |
| Wspólne (OWID + Energy)    |     173 |

**Kraje tylko w OWID (21):** Anguilla, Bonaire Sint Eustatius and Saba, Christmas Island, Congo, The Democratic Republic of the, Cook Islands, Faroe Islands, French Polynesia, Greenland, Hong Kong, Macao...

**Kraje tylko w Sustainable Energy (3):** Cayman Islands, French Guiana, Puerto Rico...


---

## Struktura oczyszczonych zbiorów

### OWID CO2 - kolumny

Liczba kolumn: 79

Kluczowe zmienne:

- `country` - object

- `year` - int64

- `iso_code` - object

- `population` - float64

- `gdp` - float64

- `co2` - float64

- `co2_per_capita` - float64

- `co2_per_gdp` - float64

### Sustainable Energy - kolumny

```
country, year, access_to_electricity_of_population, access_to_clean_fuels_for_cooking, renewable_electricity_generating_capacity_per_capita, financial_flows_to_developing_countries_us, renewable_energy_share_in_the_total_final_energy_consumption, electricity_from_fossil_fuels_twh, electricity_from_nuclear_twh, electricity_from_renewables_twh, low_carbon_electricity_electricity, primary_energy_consumption_per_capita_kwhperson, energy_intensity_level_of_primary_energy_mj2017_ppp_gdp, value_co2_emissions_kt_by_country, renewables_equivalent_primary_energy, gdp_growth, gdp_per_capita, densityn_pkm2, land_area_km2, latitude, longitude, iso_code
```

### Countries 2023 - kolumny

```
country, density_pkm2, abbreviation, agricultural_land, land_area_km2, armed_forces_size, birth_rate, calling_code, capitalmajor_city, co2_emissions, cpi, cpi_change, currency_code, fertility_rate, forested_area, gasoline_price, gdp, gross_primary_education_enrollment, gross_tertiary_education_enrollment, infant_mortality, largest_city, life_expectancy, maternal_mortality_ratio, minimum_wage, official_language, out_of_pocket_health_expenditure, physicians_per_thousand, population, population_labor_force_participation, tax_revenue, total_tax_rate, unemployment_rate, urban_population, latitude, longitude, iso_code
```


---

## Podsumowanie

**Wykonane operacje:**

1. Standaryzacja nazw kolumn we wszystkich zbiorach

2. Usunięcie agregatów regionalnych

3. Filtrowanie OWID do lat 2000-2020

4. Standaryzacja nazw krajów (mapowanie aliasów)

5. Dodanie kodów ISO do zbiorów, które ich nie miały

**Zapisane pliki:**

- `out/cleaned/owid_co2_cleaned.parquet` (4,557 wierszy)

- `out/cleaned/sustainable_energy_cleaned.parquet` (3,649 wierszy)

- `out/cleaned/countries_cleaned.parquet` (195 wierszy)

**Gotowość do łączenia:**

Po standaryzacji 173 krajów można połączyć między OWID a Sustainable Energy. Łączenie będzie wykonane po kluczach `(country, year)` dla danych panelowych.
