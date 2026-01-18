# Ocena jakości danych źródłowych

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport przedstawia ocenę jakości trzech zbiorów danych wykorzystywanych w projekcie dotyczącym wpływu rozwoju gospodarczego na emisję CO2 i transformację energetyczną.

**Analizowane zbiory danych:**

- OWID CO2 Data - dane o emisjach CO2 i gazach cieplarnianych

- Global Data on Sustainable Energy - dane o zrównoważonej energii

- Countries of the World 2023 - dane przekrojowe o krajach


---

## Ocena wiarygodności źródeł

### OWID CO2 Data

| Metric              | Value                                      |
|:--------------------|:-------------------------------------------|
| Źródło              | Our World in Data (University of Oxford)   |
| URL                 | https://github.com/owid/co2-data           |
| Licencja            | CC BY 4.0                                  |
| Typ danych          | Dane wtórne (agregacja oficjalnych źródeł) |
| Ocena wiarygodności | 5/5                                        |

**Źródła pierwotne:** Global Carbon Project, Climate Watch, BP Statistical Review, IEA, World Bank

**Uwagi:** Bardzo wysoka wiarygodność - dane agregowane z oficjalnych źródeł, metodologia transparentna



### Sustainable Energy

| Metric              | Value                                                                        |
|:--------------------|:-----------------------------------------------------------------------------|
| Źródło              | Kaggle (dane zebrane przez społeczność)                                      |
| URL                 | https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy |
| Licencja            | CC0 Public Domain                                                            |
| Typ danych          | Dane wtórne (kompilacja)                                                     |
| Ocena wiarygodności | 3/5                                                                          |

**Źródła pierwotne:** World Bank, IEA, UN Statistics Division

**Uwagi:** Średnia wiarygodność - dane zebrane przez społeczność, wymaga weryfikacji



### Countries 2023

| Metric              | Value                                                                        |
|:--------------------|:-----------------------------------------------------------------------------|
| Źródło              | Kaggle (dane zebrane przez społeczność)                                      |
| URL                 | https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023 |
| Licencja            | CC0 Public Domain                                                            |
| Typ danych          | Dane przekrojowe (cross-sectional)                                           |
| Ocena wiarygodności | 3/5                                                                          |

**Źródła pierwotne:** CIA World Factbook, World Bank, UN Statistics

**Uwagi:** Średnia wiarygodność - dane z wielu źródeł, brak pełnej dokumentacji metodologii




---

## Podstawowe charakterystyki zbiorów danych

### OWID CO2 Data

| Metric               | Value     |
|:---------------------|:----------|
| Liczba wierszy       | 50,411    |
| Liczba kolumn        | 79        |
| Rozmiar w pamięci    | 34.75 MB  |
| Łączna liczba braków | 2,105,679 |
| Procent braków       | 52.87%    |



### Sustainable Energy

| Metric               | Value   |
|:---------------------|:--------|
| Liczba wierszy       | 3,649   |
| Liczba kolumn        | 21      |
| Rozmiar w pamięci    | 0.91 MB |
| Łączna liczba braków | 6,978   |
| Procent braków       | 9.11%   |



### Countries 2023

| Metric               | Value   |
|:---------------------|:--------|
| Liczba wierszy       | 195     |
| Liczba kolumn        | 35      |
| Rozmiar w pamięci    | 0.27 MB |
| Łączna liczba braków | 341     |
| Procent braków       | 5.00%   |




---

## Kompletność czasowa i geograficzna

### OWID CO2 Data

**Zakres czasowy:**

| Metric        | Value       |
|:--------------|:------------|
| Lata          | 1750 - 2024 |
| Zakres        | 275 lat     |
| Unikalne lata | 275         |

**Pokrycie geograficzne:**

| Metric                    |   Value |
|:--------------------------|--------:|
| Łączna liczba encji       |     254 |
| Kraje                     |     215 |
| Agregaty (regiony, grupy) |      33 |
| Nierozpoznane             |       6 |

Przykładowe agregaty: Africa, Africa (GCP), Antarctica, Asia, Asia (GCP)

### Sustainable Energy

**Zakres czasowy:**

| Metric        | Value       |
|:--------------|:------------|
| Lata          | 2000 - 2020 |
| Zakres        | 21 lat      |
| Unikalne lata | 21          |

**Pokrycie geograficzne:**

| Metric              |   Value |
|:--------------------|--------:|
| Łączna liczba encji |     176 |
| Kraje               |     175 |
| Agregaty            |       0 |

### Countries 2023

**Uwaga:** To są dane przekrojowe (cross-sectional) - pojedynczy rok.

| Metric        |   Value |
|:--------------|--------:|
| Liczba krajów |     190 |
| Agregaty      |       0 |
| Nierozpoznane |       5 |


---

## Analiza braków danych

### OWID CO2 Data

| Metric                  |   Value |
|:------------------------|--------:|
| Zmienne z >50% braków   |      45 |
| Zmienne z 10-50% braków |      32 |
| Zmienne z <10% braków   |       2 |

**Zmienne z największą liczbą braków (>50%):**

| variable                          |   missing_pct |   coverage_pct |
|:----------------------------------|--------------:|---------------:|
| share_global_other_co2            |         95.7  |           4.3  |
| share_global_cumulative_other_co2 |         95.7  |           4.3  |
| other_co2_per_capita              |         94.73 |           5.27 |
| cumulative_other_co2              |         93.55 |           6.45 |
| other_industry_co2                |         93.55 |           6.45 |
| consumption_co2_per_gdp           |         91.18 |           8.82 |
| consumption_co2_per_capita        |         90.79 |           9.21 |
| trade_co2                         |         90.65 |           9.35 |
| trade_co2_share                   |         90.65 |           9.35 |
| consumption_co2                   |         89.98 |          10.02 |
| energy_per_gdp                    |         84.55 |          15.45 |
| co2_including_luc_per_unit_energy |         80.12 |          19.88 |
| energy_per_capita                 |         79.25 |          20.75 |
| primary_energy_consumption        |         79.17 |          20.83 |
| co2_per_unit_energy               |         78.78 |          21.22 |

![Procent braków danych według zmiennych - OWID CO2 Data](figures\quality\missing_bar_OWID_CO2.png)

*Figure 1: Procent braków danych według zmiennych - OWID CO2 Data*



### Sustainable Energy

| Metric                  |   Value |
|:------------------------|--------:|
| Zmienne z >50% braków   |       2 |
| Zmienne z 10-50% braków |       2 |
| Zmienne z <10% braków   |      17 |

**Zmienne z największą liczbą braków (>50%):**

| variable                                       |   missing_pct |   coverage_pct |
|:-----------------------------------------------|--------------:|---------------:|
| Renewables (% equivalent primary energy)       |         58.56 |          41.44 |
| Financial flows to developing countries (US $) |         57.25 |          42.75 |

![Procent braków danych według zmiennych - Sustainable Energy](figures\quality\missing_bar_Sustainable_Energy.png)

*Figure 2: Procent braków danych według zmiennych - Sustainable Energy*



### Countries 2023

| Metric                  |   Value |
|:------------------------|--------:|
| Zmienne z >50% braków   |       0 |
| Zmienne z 10-50% braków |       4 |
| Zmienne z <10% braków   |      31 |

![Procent braków danych według zmiennych - Countries 2023](figures\quality\missing_bar_Countries_2023.png)

*Figure 3: Procent braków danych według zmiennych - Countries 2023*




---

## Ocena przydatności do analizy

### OWID CO2 Data

**Ocena:** Bardzo dobra przydatność. Zbiór zawiera kompleksowe dane o emisjach CO2 dla większości krajów świata od 1750 roku. Kluczowe zmienne (co2, co2_per_capita, gdp, population) mają wysokie pokrycie dla lat 2000-2023.

- Zalety: Długi zakres czasowy, duża liczba zmiennych, wiarygodne źródła

- Wady: Duża liczba braków dla starszych lat i mniejszych krajów

### Sustainable Energy

**Ocena:** Dobra przydatność jako uzupełnienie. Zawiera dane o odnawialnych źródłach energii i dostępie do elektryczności, które uzupełniają dane OWID.

- Zalety: Dane o OZE, dostępie do elektryczności

- Wady: Krótszy zakres czasowy (2000-2020), wymaga standaryzacji nazw krajów

### Countries 2023

**Ocena:** Dobra jako dane uzupełniające (przekrojowe). Zawiera informacje o urbanizacji, strukturze gospodarczej, które nie są dostępne w pozostałych zbiorach.

- Zalety: Dane o urbanizacji, strukturze gospodarczej

- Wady: Dane przekrojowe (tylko jeden rok), wymaga standaryzacji nazw


---

## Podsumowanie i rekomendacje

**Kluczowe wnioski:**

1. OWID CO2 Data będzie głównym źródłem danych dla analizy

2. Zakres czasowy analizy: 2000-2020 (wspólny dla wszystkich zbiorów)

3. Konieczna standaryzacja nazw krajów przed łączeniem zbiorów

4. Należy usunąć agregaty regionalne (World, Europe, itp.)

5. Wymagana analiza i obsługa braków danych

**Rekomendacje dla kolejnych kroków:**

- Standaryzacja nazw krajów we wszystkich zbiorach

- Usunięcie agregatów i encji niebędących krajami

- Filtrowanie do lat 2000-2020

- Selekcja zmiennych z akceptowalnym poziomem braków (<30%)
