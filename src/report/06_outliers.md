# Analiza danych nietypowych (outliers)

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport przedstawia analize wartosci odstajacych (outlierow) w zbiorze danych. Outliery moga byc bledy pomiaru lub prawdziwe, ale ekstremalne wartosci wymagajace interpretacji.

**Metody wykrywania outlierow:**

- IQR (Interquartile Range): wartosci < Q1-1.5*IQR lub > Q3+1.5*IQR

- Z-score: wartosci z |z| > 3


---

## Podsumowanie outlierow wedlug zmiennych

| variable                   |   n_total |   n_outliers_iqr |   pct_outliers_iqr |   n_outliers_zscore |
|:---------------------------|----------:|-----------------:|-------------------:|--------------------:|
| co2                        |      4494 |              674 |              14.79 |                  47 |
| co2_per_capita             |      4473 |              278 |               6.1  |                 102 |
| gdp                        |      3444 |              455 |               9.98 |                  50 |
| population                 |      4536 |              502 |              11.02 |                  42 |
| primary_energy_consumption |      4257 |              622 |              13.65 |                  42 |
| coal_co2                   |      2874 |              433 |               9.5  |                  33 |
| oil_co2                    |      4471 |              582 |              12.77 |                  51 |


---

## Ekstremalne przypadki

### Ekstrema dla: co2_per_capita

**Najwyzsze wartosci:**

| country   |   year |   co2_per_capita | type   |
|:----------|-------:|-----------------:|:-------|
| Qatar     |   2001 |            67.73 | high   |
| Qatar     |   2002 |            63.52 | high   |
| Qatar     |   2000 |            62.65 | high   |
| Qatar     |   2003 |            62.62 | high   |
| Qatar     |   2006 |            61.42 | high   |

**Najnizsze wartosci:**

| country                  |   year |   co2_per_capita | type   |
|:-------------------------|-------:|-----------------:|:-------|
| Burundi                  |   2005 |             0.02 | low    |
| Central African Republic |   2013 |             0.02 | low    |
| Burundi                  |   2007 |             0.02 | low    |
| Burundi                  |   2003 |             0.02 | low    |
| Burundi                  |   2006 |             0.02 | low    |

### Ekstrema dla: co2

**Najwyzsze wartosci:**

| country   |   year |      co2 | type   |
|:----------|-------:|---------:|:-------|
| China     |   2020 | 10896.5  | high   |
| China     |   2019 | 10713.5  | high   |
| China     |   2018 | 10346.8  | high   |
| China     |   2017 | 10000    | high   |
| China     |   2014 |  9976.03 | high   |

**Najnizsze wartosci:**

| country          |   year |   co2 | type   |
|:-----------------|-------:|------:|:-------|
| Christmas Island |   2000 |     0 | low    |
| Christmas Island |   2001 |     0 | low    |
| Christmas Island |   2002 |     0 | low    |
| Christmas Island |   2003 |     0 | low    |
| Christmas Island |   2004 |     0 | low    |

### Ekstrema dla: gdp

**Najwyzsze wartosci:**

| country   |   year |         gdp | type   |
|:----------|-------:|------------:|:-------|
| China     |   2020 | 2.41518e+13 | high   |
| China     |   2019 | 2.36319e+13 | high   |
| China     |   2018 | 2.22943e+13 | high   |
| China     |   2017 | 2.08944e+13 | high   |
| China     |   2016 | 1.95457e+13 | high   |

**Najnizsze wartosci:**

| country               |   year |         gdp | type   |
|:----------------------|-------:|------------:|:-------|
| Sao Tome and Principe |   2000 | 3.12854e+08 | low    |
| Sao Tome and Principe |   2001 | 3.23367e+08 | low    |
| Sao Tome and Principe |   2002 | 3.30763e+08 | low    |
| Sao Tome and Principe |   2003 | 3.56841e+08 | low    |
| Sao Tome and Principe |   2004 | 3.70949e+08 | low    |


---

## Analiza znanych kategorii outlierow

### Kraje naftowe (wysokie emisje per capita)

Kraje takie jak Katar, Kuwejt czy ZEA maja bardzo wysokie emisje CO2 per capita ze wzgledu na przemysl naftowy i niewielka populacje.

| country              |   co2_per_capita |         gdp |
|:---------------------|-----------------:|------------:|
| Bahrain              |            24.68 | 3.69771e+10 |
| Kuwait               |            27.71 | 1.72469e+11 |
| Qatar                |            48.42 | 2.18653e+11 |
| Saudi Arabia         |            20.58 | 1.14705e+12 |
| United Arab Emirates |            25.2  | 4.76884e+11 |

### Kraje nordyckie (niskie emisje przy wysokim PKB)

Norwegia, Szwecja i inne kraje nordyckie maja relatywnie niskie emisje pomimo wysokiego PKB - dzieki energii odnawialnej (hydro, wiatr).

| country   |   co2_per_capita |         gdp |
|:----------|-----------------:|------------:|
| Denmark   |             8.28 | 2.42858e+11 |
| Finland   |            10.4  | 1.99905e+11 |
| Iceland   |            10.6  | 1.22289e+10 |
| Norway    |             8.99 | 3.7024e+11  |
| Sweden    |             5.2  | 3.8931e+11  |


---

## Wizualizacje

![Figure 1](figures\outliers\outliers_box_co2_per_capita.png)

![Figure 2](figures\outliers\outliers_box_co2.png)

![Figure 3](figures\outliers\outliers_box_gdp.png)

![Figure 4](figures\outliers\outliers_scatter_gdp_co2.png)


---

## Rekomendacje dotyczace obslugi outlierow

**Strategia:**

1. **Zachowaj** outliery bedace prawdziwymi ekstremalnym wartosciami (kraje naftowe, duze gospodarki)

2. **Rozważ winsoryzacje** dla skrajnych wartosci w analizie regresyjnej

3. **Dodaj zmienne kontrolne** (region, poziom rozwoju) aby wyjasnic zroznicowanie

4. **Przeprowadź analize wrazliwosci** - modele z i bez outlierow

**Wniosek:** Wiekszosc outlierow to prawdziwe wartosci odzwierciedlajace specyfike krajow (kraje naftowe, duze gospodarki). Nie nalezy ich usuwac, ale uwzglednic w interpretacji wynikow.
