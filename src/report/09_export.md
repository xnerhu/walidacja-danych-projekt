# Eksport finalnego zbioru danych

*Generated: 2026-01-18 19:02*


---

## Podsumowanie finalnego zbioru danych

| Metric            | Value     |
|:------------------|:----------|
| Liczba obserwacji | 4,557     |
| Liczba zmiennych  | 50        |
| Rozmiar w pamieci | 2.56 MB   |
| Braki danych      | 15.98%    |
| Liczba krajow     | 216       |
| Zakres czasowy    | 2000-2020 |


---

## Struktura danych

**Typ zbioru:** Dane panelowe (panel data)

**Klucze:** `country`, `year`

**Format czasu:** Roczny (2000-2020)

### Typy zmiennych

| Metric   |   Value |
|:---------|--------:|
| float64  |      45 |
| object   |       4 |
| int64    |       1 |


---

## Pokrycie geograficzne

| Region        |   Liczba krajow |
|:--------------|----------------:|
| Africa        |              54 |
| Asia          |              49 |
| Europe        |              44 |
| North America |              23 |
| Oceania       |              14 |
| South America |              12 |


---

## Eksportowane pliki

**Pliki danych:**

- `final_dataset.csv` (2.13 MB)

- `final_dataset.parquet` (1.02 MB)

- `codebook.md` (0.01 MB)

- `codebook.csv` (0.00 MB)

- `summary_stats.csv` (0.01 MB)


---

## Instrukcja uzycia

### Python (pandas)

```python

import pandas as pd

# Wczytanie danych
df = pd.read_parquet("out/final/final_dataset.parquet")

# Lub z CSV
df = pd.read_csv("out/final/final_dataset.csv")

# Podstawowe operacje
print(df.shape)
print(df.columns.tolist())
print(df.describe())
    
```

### R

```r

library(arrow)
library(dplyr)

# Wczytanie danych
df <- read_parquet("out/final/final_dataset.parquet")

# Lub z CSV
df <- read.csv("out/final/final_dataset.csv")

# Podstawowe operacje
dim(df)
names(df)
summary(df)
    
```


---

## Przygotowane pytania badawcze

Zbior danych zostal przygotowany do odpowiedzi na nastepujace pytania:

1. Czy istnieje krzywa srodowiskowa Kuznetsa (EKC)?

  - Zmienne: `co2_per_capita`, `gdp_per_capita`, `gdp_per_capita_sq`

2. Jakie czynniki strukturalne roznicuja emisje?

  - Zmienne: `fossil_share`, `emission_intensity`, `energy_intensity`, `development_level`

3. Czy tempo wzrostu PKB wplywa na transformacje energetyczna?

  - Zmienne: `gdp_pct_change`, `renewable_share_change`

4. Jak region moderuje zwiazek rozwoj-emisje?

  - Zmienne: `region`, interakcje z `gdp_per_capita`


---

## Podsumowanie

Finalny zbior danych zawiera **4,557 obserwacji** dla **216 krajow** w okresie **2000-2020**.

**Pipeline przetwarzania obejmowal:**

1. Pobranie danych z 3 zrodel (OWID, Kaggle)

2. Ocene jakosci danych zrodlowych

3. Czyszczenie i standaryzacje nazw

4. Laczenie zbiorow po (country, year)

5. Eksploracyjna analize danych (EDA)

6. Tworzenie nowych zmiennych (feature engineering)

7. Analize outlierow

8. Analize i imputacje brakow danych

9. Selekcje zmiennych i rekordow

10. Eksport i dokumentacje

**Data eksportu:** 2026-01-18 19:02
