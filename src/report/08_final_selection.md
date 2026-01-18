# Wybor zmiennych i rekordow

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport dokumentuje proces selekcji zmiennych i rekordow do finalnego zbioru danych przeznaczonego do modelowania.

| Metric                 | Value   |
|:-----------------------|:--------|
| Wiersze przed selekcja | 4,557   |
| Wiersze po selekcji    | 4,557   |
| Kolumny przed selekcja | 154     |
| Kolumny po selekcji    | 50      |


---

## Selekcja krajow

**Kryterium:** Wykluczenie krajow z >30% brakujacych danych w kluczowych zmiennych (co2, gdp, population).

| Metric      |   Value |
|:------------|--------:|
| Kraje przed |     216 |
| Kraje po    |     216 |
| Wykluczone  |       0 |


---

## Selekcja lat

**Kryterium:** Zakres czasowy 2000-2020 (wspolny dla wszystkich zbiorow).

| Metric       | Value     |
|:-------------|:----------|
| Zakres przed | 2000-2020 |
| Zakres po    | 2000-2020 |
| Liczba lat   | 21        |


---

## Selekcja zmiennych

**Kryteria:** Wybrano zmienne istotne dla pytan badawczych oraz zmienne kontrolne niezbedne do modelowania.

| Metric        |   Value |
|:--------------|--------:|
| Zmienne przed |     154 |
| Zmienne po    |      50 |

### Zmienne wedlug kategorii

- identifiers: 4 zmiennych

- dependent: 3 zmiennych

- main_predictors: 6 zmiennych

- energy: 12 zmiennych

- renewable: 4 zmiennych

- dynamics: 6 zmiennych

- categorical: 1 zmiennych

- lagged: 4 zmiennych

- country_metadata: 4 zmiennych


---

## Walidacja finalnego zbioru

### Ogolne statystyki

| Metric                    | Value     |
|:--------------------------|:----------|
| Liczba obserwacji         | 4,557     |
| Liczba zmiennych          | 50        |
| Liczba krajow             | 216       |
| Zakres czasowy            | 2000-2020 |
| Duplikaty (country, year) | 21        |

### Pokrycie kluczowych zmiennych

| Metric                  | Value   |
|:------------------------|:--------|
| co2_coverage            | 100.0%  |
| co2_per_capita_coverage | 100.0%  |
| gdp_coverage            | 100.0%  |
| population_coverage     | 100.0%  |
| region_coverage         | 90.32%  |


---

## Lista zmiennych w finalnym zbiorze

```
country, year, iso_code, region, co2, co2_per_capita, co2_per_capita_log, gdp, gdp_per_capita, gdp_per_capita_sq, gdp_per_capita_cu, population, population_log, primary_energy_consumption, primary_energy_consumption_log, coal_co2, oil_co2, gas_co2, fossil_co2, fossil_share, coal_share, oil_share, gas_share, emission_intensity, energy_intensity, access_to_electricity_of_population, renewable_energy_share_in_the_total_final_energy_consumption, electricity_from_renewables_twh, renewable_share_change, co2_change, co2_pct_change, co2_per_capita_change, co2_per_capita_pct_change, gdp_change, gdp_pct_change, development_level, co2_per_capita_lag1, co2_per_capita_lag5, gdp_lag1, gdp_lag5, urban_population, agricultural_land, latitude, longitude, access_to_clean_fuels_for_cooking, renewable_electricity_generating_capacity_per_capita, electricity_from_fossil_fuels_twh, electricity_from_nuclear_twh, low_carbon_electricity_electricity, renewables_equivalent_primary_energy
```


---

## Podsumowanie

Finalny zbior danych zawiera **4,557 obserwacji** dla **216 krajow** w okresie **2000-2020**.

**Zapisany plik:**

- `out/final/final_panel.parquet`

**Zbiór jest gotowy do:**

- Modelowania regresyjnego (krzywa Kuznetsa)

- Analizy panelowej

- Analizy skupien (clustering)

- Wizualizacji i raportowania
