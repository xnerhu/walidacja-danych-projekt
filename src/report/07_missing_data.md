# Analiza brakow danych i imputacja

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport przedstawia analize brakow danych oraz zastosowane metody imputacji. Braki danych sa powszechne w danych miedzynarodowych i wymagaja starannej obslugi.

| Metric                 | Value            |
|:-----------------------|:-----------------|
| Lacznie komorek        | 701,778          |
| Braki przed imputacja  | 131,921 (18.80%) |
| Braki po imputacji     | 126,630 (18.04%) |
| Uzupelnionych wartosci | 5,291            |


---

## Braki wedlug zmiennych

| Metric                  |   Value |
|:------------------------|--------:|
| Zmienne z >30% brakow   |      27 |
| Zmienne z 10-30% brakow |      68 |
| Zmienne z <10% brakow   |      59 |

### Zmienne z wysokim odsetkiem brakow (>30%)

| column                                     |   missing_count |   missing_pct |
|:-------------------------------------------|----------------:|--------------:|
| other_co2_per_capita                       |            3591 |         78.8  |
| cumulative_other_co2                       |            3591 |         78.8  |
| share_global_cumulative_other_co2          |            3591 |         78.8  |
| other_industry_co2                         |            3591 |         78.8  |
| share_global_other_co2                     |            3591 |         78.8  |
| renewables_equivalent_primary_energy       |            3024 |         66.36 |
| financial_flows_to_developing_countries_us |            2997 |         65.77 |
| consumption_co2_per_gdp                    |            2064 |         45.29 |
| consumption_co2_per_capita                 |            2043 |         44.83 |
| consumption_co2                            |            2043 |         44.83 |
| trade_co2                                  |            2043 |         44.83 |
| trade_co2_share                            |            2043 |         44.83 |
| cumulative_gas_co2                         |            1941 |         42.59 |
| gas_share                                  |            1941 |         42.59 |
| share_global_cumulative_gas_co2            |            1941 |         42.59 |


---

## Braki wedlug krajow

**Kraje z najwieksza liczba brakow:**

| country                         |   total_missing |   n_years |   missing_pct |
|:--------------------------------|----------------:|----------:|--------------:|
| Holy See (Vatican City State)   |            2898 |        21 |         90.2  |
| Christmas Island                |            2773 |        21 |         86.31 |
| Monaco                          |            2709 |        21 |         84.31 |
| San Marino                      |            2541 |        21 |         79.08 |
| Faroe Islands                   |            2404 |        21 |         74.82 |
| Saint Pierre and Miquelon       |            2404 |        21 |         74.82 |
| Wallis and Futuna               |            2388 |        21 |         74.32 |
| Anguilla                        |            2299 |        21 |         71.55 |
| Greenland                       |            2299 |        21 |         71.55 |
| French Polynesia                |            2299 |        21 |         71.55 |
| Montserrat                      |            2299 |        21 |         71.55 |
| Sint Maarten (Dutch part)       |            2239 |        21 |         69.69 |
| Bonaire Sint Eustatius and Saba |            2239 |        21 |         69.69 |
| Virgin Islands, British         |            2089 |        21 |         65.02 |
| Turks and Caicos Islands        |            2089 |        21 |         65.02 |

**Uwaga:** 38 krajow ma >30% brakow i moze wymagac wykluczenia z analizy.


---

## Braki wedlug lat

|   year |   total_missing |   n_countries |   missing_pct |
|-------:|----------------:|--------------:|--------------:|
|   2000 |            8363 |           217 |         25.19 |
|   2001 |            6620 |           217 |         19.94 |
|   2002 |            6580 |           217 |         19.82 |
|   2003 |            6570 |           217 |         19.79 |
|   2004 |            6563 |           217 |         19.77 |
|   2005 |            6178 |           217 |         18.61 |
|   2006 |            6160 |           217 |         18.55 |
|   2007 |            6113 |           217 |         18.41 |
|   2008 |            6078 |           217 |         18.31 |
|   2009 |            6027 |           217 |         18.15 |
|   2010 |            5991 |           217 |         18.04 |
|   2011 |            5971 |           217 |         17.98 |
|   2012 |            6035 |           217 |         18.18 |
|   2013 |            6005 |           217 |         18.09 |
|   2014 |            5983 |           217 |         18.02 |
|   2015 |            5973 |           217 |         17.99 |
|   2016 |            5988 |           217 |         18.04 |
|   2017 |            5982 |           217 |         18.02 |
|   2018 |            5985 |           217 |         18.03 |
|   2019 |            5986 |           217 |         18.03 |
|   2020 |            6770 |           217 |         20.39 |


---

## Wizualizacje

![Figure 1](figures\missing\missing_bar.png)

![Figure 2](figures\missing\missing_heatmap.png)

![Figure 3](figures\missing\missing_by_year.png)


---

## Strategia imputacji

**Zastosowana strategia imputacji (w kolejnosci):**

1. **Interpolacja czasowa** - dla wartosci wewnatrz szeregu czasowego kraju

2. **Forward/backward fill** - dla wartosci na krawedziach szeregu

3. **Mediana regionalna** - dla pozostalych brakow w ramach regionu

4. **Mediana globalna** - jako ostatecznosc dla pojedynczych brakow


---

## Wyniki imputacji

| variable                   |   missing_before |   missing_after |   imputed |
|:---------------------------|-----------------:|----------------:|----------:|
| co2                        |               63 |               0 |        63 |
| co2_per_capita             |               84 |               0 |        84 |
| gdp                        |             1113 |               0 |      1113 |
| population                 |               21 |               0 |        21 |
| primary_energy_consumption |              300 |               0 |       300 |
| coal_co2                   |             1683 |               0 |      1683 |
| oil_co2                    |               86 |               0 |        86 |
| gas_co2                    |             1941 |               0 |      1941 |


---

## Podsumowanie

**Wnioski:**

- Wiekszosc brakow wystepuje w zmiennych pochodnych (cumulative, share)

- Kluczowe zmienne (co2, gdp, population) maja niski odsetek brakow

- Interpolacja czasowa jest najbardziej odpowiednia dla danych panelowych

**Zapisane pliki:**

- `out/imputed/panel_imputed.parquet` - dane po imputacji

- `out/missing/missing_stats.csv` - statystyki brakow
