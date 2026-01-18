# Przeksztalcanie zmiennych (Feature Engineering)

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport dokumentuje proces tworzenia nowych zmiennych (feature engineering) na potrzeby dalszej analizy. Nowe zmienne maja na celu uchycenie nieliniowych zaleznosci, dynamiki zmian i kategoryzacji krajow.

| Metric        |   Value |
|:--------------|--------:|
| Kolumny przed |     128 |
| Kolumny po    |     154 |
| Nowe kolumny  |      26 |


---

## Transformacje logarytmiczne

Transformacje logarytmiczne zastosowano dla zmiennych o silnie prawoskosnych rozkladach. Uzyto transformacji log1p(x) = log(1+x) dla obslugi wartosci zerowych.

**Dodane zmienne:**

- `co2_per_capita_log`

- `gdp_log`

- `population_log`

- `co2_log`

- `primary_energy_consumption_log`

**Uzasadnienie:** Transformacja logarytmiczna normalizuje rozklady i stabilizuje wariancje, co jest istotne dla modelowania regresyjnego.


---

## Cechy wielomianowe (dla krzywej Kuznetsa)

Dodano cechy wielomianowe PKB per capita do testowania hipotezy krzywej srodowiskowej Kuznetsa (EKC), ktora zaklada odwrocona zaleznosc U miedzy rozwojem a emisjami.

**Dodane zmienne:**

- `gdp_per_capita_sq`

- `gdp_per_capita_cu`

**Model EKC:** CO2_per_capita = b0 + b1*GDP_pc + b2*GDP_pc^2 + e

Jesli b1 > 0 i b2 < 0, to istnieje punkt zwrotny (peak) emisji.


---

## Cechy zmiany (dynamika rok-do-roku)

Dodano cechy uchycujace dynamike zmian w czasie, co pozwala analizowac tempo transformacji energetycznej.

**Dodane zmienne:**

- `co2_change`

- `co2_pct_change`

- `co2_per_capita_change`

- `co2_per_capita_pct_change`

- `gdp_change`

- `gdp_pct_change`

- `renewable_share_change`


---

## Cechy kategoryczne

Dodano zmienne kategoryczne do analizy grupowej i porownawczej.

**Dodane zmienne:**

- `development_level`

### Rozklad poziomu rozwoju

| Metric    |   Value |
|:----------|--------:|
| High      |      40 |
| Low       |      41 |
| Medium    |      40 |
| Very High |      41 |


---

## Cechy stosunkowe (ratios)

Dodano cechy wyrazajace udzialy i intensywnosci, co normalizuje porownania miedzy krajami o roznych wielkosciach.

**Dodane zmienne:**

- `fossil_co2`

- `fossil_share`

- `coal_share`

- `oil_share`

- `gas_share`

- `emission_intensity`

- `energy_intensity`


---

## Cechy opoznione (lagged)

Dodano zmienne opoznione o 1 i 5 lat, co pozwala modelowac efekty opoznione i przyczynowe.

**Dodane zmienne:**

- `co2_per_capita_lag1`

- `co2_per_capita_lag5`

- `gdp_lag1`

- `gdp_lag5`


---

## Podsumowanie

| Metric             |   Value |
|:-------------------|--------:|
| Transformacje log  |       5 |
| Cechy wielomianowe |       2 |
| Cechy zmiany       |       7 |
| Cechy kategoryczne |       1 |
| Cechy stosunkowe   |       7 |
| Cechy opoznione    |       4 |
| LACZNIE            |      26 |

**Zapisany plik:**

- `out/features/panel_with_features.parquet`

**Kluczowe zmienne dla modelowania:**

- `co2_per_capita_log` - zmienna zalezna (log)

- `gdp_per_capita_log` - glowny predyktor (log)

- `gdp_per_capita_sq` - test krzywej Kuznetsa

- `development_level` - kategoryzacja krajow

- `region` - analiza regionalna

- `renewable_share_change` - tempo transformacji
