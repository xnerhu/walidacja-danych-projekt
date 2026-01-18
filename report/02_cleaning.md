# Czyszczenie i standaryzacja danych

*Generated: 2026-01-18 18:36*


---

Niniejszy raport dokumentuje proces czyszczenia i standaryzacji trzech zbiorów danych wykorzystywanych w projekcie. Proces obejmuje: standaryzację nazw krajów, ujednolicenie nazw kolumn, usunięcie agregatów regionalnych, konwersję typów danych oraz walidację zakresów wartości.

## Podsumowanie czyszczenia

| Dataset            | Wiersze (przed)   | Wiersze (po)   | Usunięte wiersze   |   Kolumny (przed) |   Kolumny (po) |
|:-------------------|:------------------|:---------------|:-------------------|------------------:|---------------:|
| OWID CO2           | 50,411            | 7,514          | 42,897             |                79 |             79 |
| Sustainable Energy | 3,649             | 3,649          | 0                  |                21 |             21 |
| Countries 2023     | 195               | 195            | 0                  |                35 |             35 |


---

## Dataset: OWID CO2

### Filtrowanie agregatów

Usunięto **33** encji agregujących (7,508 wierszy).

**Usunięte encje:**

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

- Europe (excl. EU-28)

- European Union (27)

- European Union (28)

- High-income countries

- International aviation

- International shipping

- Kuwaiti Oil Fires

- Kuwaiti Oil Fires (GCP)

- Low-income countries

- Lower-middle-income countries

*... oraz 13 innych*

### Standaryzacja nazw krajów

Znormalizowano nazwy **4** krajów do standardowego formatu.

| Nazwa oryginalna             | Nazwa znormalizowana   |
|:-----------------------------|:-----------------------|
| Cape Verde                   | Cabo Verde             |
| Democratic Republic of Congo | DR Congo               |
| East Timor                   | Timor-Leste            |
| Vatican                      | Vatican City           |

### Filtrowanie zakresu czasowego

Ograniczono dane do zakresu lat **1990-2023** (z 275 do 34 unikalnych lat).


---

## Dataset: Sustainable Energy

### Standaryzacja nazw kolumn

Zmieniono nazwy 17 kolumn na format snake_case.

| Oryginalna nazwa                                                 | Nowa nazwa                                                   |
|:-----------------------------------------------------------------|:-------------------------------------------------------------|
| Access to electricity (% of population)                          | access_to_electricity_of_population                          |
| Access to clean fuels for cooking                                | access_to_clean_fuels_for_cooking                            |
| Renewable-electricity-generating-capacity-per-capita             | renewable_electricity_generating_capacity_per_capita         |
| Financial flows to developing countries (US $)                   | financial_flows_to_developing_countries_us                   |
| Renewable energy share in the total final energy consumption (%) | renewable_energy_share_in_the_total_final_energy_consumption |
| Electricity from fossil fuels (TWh)                              | electricity_from_fossil_fuels_twh                            |
| Electricity from nuclear (TWh)                                   | electricity_from_nuclear_twh                                 |
| Electricity from renewables (TWh)                                | electricity_from_renewables_twh                              |
| Low-carbon electricity (% electricity)                           | low_carbon_electricity_electricity                           |
| Primary energy consumption per capita (kWh/person)               | primary_energy_consumption_per_capita_kwhperson              |

*... oraz 7 innych zmian*

### Filtrowanie agregatów

Nie znaleziono agregatów do usunięcia.

### Standaryzacja nazw krajów

Wszystkie nazwy krajów były już w standardowym formacie.

### Konwersja typów danych

| Kolumna       | Typ (przed)   | Typ (po)   |   Utracone wartości |
|:--------------|:--------------|:-----------|--------------------:|
| densityn_pkm2 | object        | float64    |                   0 |


---

## Dataset: Countries 2023

### Standaryzacja nazw kolumn

Zmieniono nazwy 35 kolumn na format snake_case.

| Oryginalna nazwa      | Nowa nazwa        |
|:----------------------|:------------------|
| Country               | country           |
| Density               | density_pkm2      |
| (P/Km2)               |                   |
| Abbreviation          | abbreviation      |
| Agricultural Land( %) | agricultural_land |
| Land Area(Km2)        | land_area_km2     |
| Armed Forces size     | armed_forces_size |
| Birth Rate            | birth_rate        |
| Calling Code          | calling_code      |
| Capital/Major City    | capitalmajor_city |
| Co2-Emissions         | co2_emissions     |

*... oraz 25 innych zmian*

### Filtrowanie agregatów

Nie znaleziono agregatów do usunięcia.

### Standaryzacja nazw krajów

Znormalizowano nazwy **9** krajów do standardowego formatu.

| Nazwa oryginalna                 | Nazwa znormalizowana   |
|:---------------------------------|:-----------------------|
| The Bahamas                      | Bahamas                |
| Ivory Coast                      | Cote d'Ivoire          |
| Cape Verde                       | Cabo Verde             |
| Republic of the Congo            | Congo                  |
| Czech Republic                   | Czechia                |
| Democratic Republic of the Congo | DR Congo               |
| The Gambia                       | Gambia                 |
| Federated States of Micronesia   | Micronesia             |
| East Timor                       | Timor-Leste            |

### Konwersja typów danych

| Kolumna           | Typ (przed)   | Typ (po)   |   Utracone wartości |
|:------------------|:--------------|:-----------|--------------------:|
| density_pkm2      | object        | float64    |                   0 |
| agricultural_land | object        | float64    |                   0 |
| land_area_km2     | object        | float64    |                   0 |
| armed_forces_size | object        | float64    |                   0 |
| co2_emissions     | object        | float64    |                   0 |
| cpi               | object        | float64    |                   0 |
| cpi_change        | object        | float64    |                   0 |
| forested_area     | object        | float64    |                   0 |
| gasoline_price    | object        | float64    |                   0 |
| gdp               | object        | float64    |                   0 |

*... oraz 10 innych konwersji*


---

## Wnioski i następne kroki

Wszystkie trzy datasety zostały wyczyszczone i przygotowane do etapu łączenia (merging). Kluczowe zmiany:

- Nazwy krajów zostały znormalizowane, co umożliwi łączenie po kluczu `country`

- Usunięto agregaty regionalne (World, Europe, etc.), pozostawiając tylko kraje

- Nazwy kolumn zostały ujednolicone do formatu snake_case

- Kolumny numeryczne zapisane jako tekst zostały skonwertowane



**Następny krok:** Łączenie datasetów po kluczu `(country, year)` w celu utworzenia zintegrowanego zbioru danych panelowych.


---

## Pliki wyjściowe

- OWID CO2: `../out/cleaned/owid_co2_cleaned.parquet`

- Sustainable Energy: `../out/cleaned/sustainable_energy_cleaned.parquet`

- Countries 2023: `../out/cleaned/countries_cleaned.parquet`
