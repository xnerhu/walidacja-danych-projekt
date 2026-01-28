# Podsumowanie wykonanych prac i zastosowanych technik statystycznych

## Temat projektu

**Wpływ rozwoju gospodarczego na emisję CO2 i transformację energetyczną**

Kategorie: Gospodarka + Ochrona środowiska

---

## Pytania badawcze

1. Czy istnieje krzywa środowiskowa Kuznetsa (EKC)? — Czy emisje CO2 per capita rosną wraz z PKB per capita do pewnego punktu, a następnie spadają?
2. Jakie czynniki strukturalne (urbanizacja, dostęp do elektryczności, intensywność energetyczna) najsilniej różnicują kraje o podobnym PKB pod względem emisji CO2?
3. Czy tempo wzrostu PKB wpływa na tempo transformacji energetycznej (wzrost udziału OZE)?
4. Jak region geograficzny moderuje związek między rozwojem a emisjami?
5. Które źródła emisji CO2 (węgiel, ropa, gaz, cement) dominują na różnych poziomach rozwoju gospodarczego?

---

## 1. Pozyskanie danych

**Plik:** `src/steps/step_00_download.py`

### Źródła danych

| Dataset | Źródło | Typ danych | Wiarygodność |
|---------|--------|------------|--------------|
| OWID CO2 Data | Our World in Data (GitHub) | Dane wtórne (agregacja oficjalnych źródeł) | 5/5 |
| Global Data on Sustainable Energy | Kaggle | Dane wtórne (kompilacja) | 3/5 |
| Countries of the World 2023 | Kaggle | Dane przekrojowe | 3/5 |

### Funkcje

| Funkcja | Opis |
|---------|------|
| `get_owid_co2_dataset()` | Pobiera dane OWID CO2 z GitHub |
| `get_sustainable_energy_dataset()` | Pobiera dane o energii z Kaggle |
| `get_countries_of_world_dataset()` | Pobiera dane przekrojowe o krajach z Kaggle |

### Charakterystyka zbiorów

- **OWID CO2 Data**: 50,411 wierszy, 79 zmiennych, zakres 1750-2024
- **Sustainable Energy**: 3,649 wierszy, 21 zmiennych, zakres 2000-2020
- **Countries 2023**: 195 wierszy, 35 zmiennych (dane przekrojowe)

---

## 2. Ocena jakości danych

**Plik:** `src/steps/step_01_quality_assessment.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `assess_source_credibility()` | Ocena wiarygodności źródeł danych |
| `assess_completeness()` | Ocena kompletności czasowej i geograficznej |
| `assess_variable_coverage()` | Obliczenie pokrycia zmiennych (% non-null) |
| `generate_quality_report()` | Generowanie raportu jakości w Markdown |
| `run_step_01()` | Uruchomienie całego kroku |

### Zastosowane techniki

- **Analiza kompletności** — obliczenie procentu braków danych dla każdej zmiennej
- **Analiza pokrycia czasowego i geograficznego** — identyfikacja zakresów lat i liczby krajów
- **Identyfikacja agregatów** — rozróżnienie krajów od agregatów regionalnych (World, Europe, itp.)
- **Ocena wiarygodności źródeł** — analiza pochodzenia danych (instytucje, metodologia)

### Wyniki

| Zbiór | Procent braków | Zakres czasowy | Liczba krajów |
|-------|----------------|----------------|---------------|
| OWID CO2 | 52.87% | 1750-2024 | 215 |
| Sustainable Energy | 9.11% | 2000-2020 | 176 |
| Countries 2023 | 5.00% | 2023 | 190 |

---

## 3. Czyszczenie i porządkowanie danych

**Plik:** `src/steps/step_02_cleaning.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `standardize_column_names()` | Standaryzacja nazw kolumn do snake_case |
| `filter_aggregates()` | Usunięcie agregatów regionalnych |
| `filter_year_range()` | Filtrowanie do zakresu lat 2000-2020 |
| `standardize_country_names_in_df()` | Standaryzacja nazw krajów |
| `add_iso_codes()` | Dodanie kodów ISO |
| `validate_percentage_columns()` | Walidacja kolumn procentowych |
| `clean_owid_dataset()` | Czyszczenie OWID CO2 |
| `clean_sustainable_energy_dataset()` | Czyszczenie Sustainable Energy |
| `clean_countries_dataset()` | Czyszczenie Countries 2023 |
| `run_step_02()` | Uruchomienie całego kroku |

### Zastosowane techniki

- **Standaryzacja nazw kolumn** — konwersja do formatu snake_case
- **Standaryzacja nazw krajów** — mapowanie aliasów (np. "USA" → "United States")
- **Usuwanie agregatów regionalnych** — filtrowanie 33 agregatów (World, Europe, Africa, itp.)
- **Filtrowanie zakresu czasowego** — ograniczenie do lat 2000-2020
- **Walidacja zakresów wartości** — sprawdzenie wartości nieujemnych
- **Konwersja typów danych** — zapewnienie poprawnych typów (numeric, string)

### Wyniki czyszczenia

| Operacja | Przed | Po |
|----------|-------|-----|
| OWID CO2 - wiersze | 50,411 | 4,557 |
| Usunięte agregaty | 33 | 0 |
| Standaryzowane nazwy krajów | ~50 aliasów | ujednolicone |

---

## 4. Łączenie danych z różnych źródeł

**Plik:** `src/steps/step_03_merging.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `merge_owid_sustainable()` | Łączenie OWID CO2 z Sustainable Energy po (country, year) |
| `add_country_metadata()` | Dodanie danych przekrojowych (Countries 2023) |
| `validate_merge()` | Walidacja jakości łączenia |
| `analyze_merge_coverage()` | Analiza pokrycia krajów i lat |
| `run_step_03()` | Uruchomienie całego kroku |

### Zastosowane techniki

- **Left join** — łączenie po kluczu (country, year) dla danych panelowych
- **Left join** — łączenie po kluczu (country) dla danych przekrojowych
- **Usuwanie duplikatów kolumn** — eliminacja powtórzonych zmiennych
- **Walidacja łączenia** — sprawdzenie pokrycia i duplikatów

### Schemat łączenia

```
OWID CO2 Data ──┬── (country, year) ──┬── Sustainable Energy
                │                      │
                └──────────────────────┘
                           │
                   MERGED DATA (2000-2020)
                           │
                     (country)
                           │
                   Countries 2023
```

### Wyniki łączenia

- **Finalny zbiór**: 4,557 obserwacji, 127 zmiennych
- **Wspólne kraje** (wszystkie 3 zbiory): 168
- **Zakres czasowy**: 2000-2020 (21 lat)

---

## 5. Eksploracyjna analiza danych (EDA)

**Plik:** `src/steps/step_04_eda.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `compute_descriptive_stats()` | Obliczenie statystyk opisowych (średnia, mediana, std, skośność, kurtoza) |
| `analyze_key_variables()` | Szczegółowa analiza kluczowych zmiennych |
| `compute_correlation_analysis()` | Analiza korelacji (macierz + top korelacje) |
| `analyze_temporal_trends()` | Analiza trendów czasowych |
| `analyze_by_region()` | Analiza statystyk według regionów |
| `create_distribution_plots()` | Histogramy i boxploty |
| `create_correlation_plot()` | Heatmapa korelacji |
| `create_scatter_plots()` | Wykresy rozrzutu z regresją |
| `create_trend_plots()` | Wykresy trendów czasowych |
| `run_step_04()` | Uruchomienie całego kroku |

### Zastosowane techniki statystyczne

#### 5.1 Statystyki opisowe
- **Miary położenia**: średnia, mediana, kwartyle (Q1, Q3), minimum, maksimum
- **Miary rozproszenia**: odchylenie standardowe, rozstęp międzykwartylowy (IQR)
- **Miary kształtu rozkładu**: skośność (skewness), kurtoza (kurtosis)

#### 5.2 Analiza rozkładów
- **Histogramy** — wizualizacja rozkładów zmiennych ciągłych
- **Wykresy pudełkowe (boxploty)** — identyfikacja mediany, kwartyli i outlierów
- **Identyfikacja asymetrii** — stwierdzono silną prawoskośność dla CO2 i PKB

#### 5.3 Analiza korelacji
- **Współczynnik korelacji Pearsona** — badanie liniowych zależności między zmiennymi
- **Macierz korelacji** — wizualizacja powiązań między wszystkimi zmiennymi
- **Heatmapa korelacji** — graficzna prezentacja macierzy korelacji

**Najsilniejsze korelacje:**
| Zmienna 1 | Zmienna 2 | Korelacja |
|-----------|-----------|-----------|
| co2 | primary_energy_consumption | 0.99 |
| gdp | primary_energy_consumption | 0.97 |
| co2 | gdp | 0.95 |

#### 5.4 Analiza trendów czasowych
- **Agregacja roczna** — obliczenie sum i średnich globalnych emisji
- **Analiza zmian procentowych** — wzrost emisji o 38.8% w latach 2000-2020
- **Wykresy liniowe** — wizualizacja trendów czasowych

#### 5.5 Analiza regionalna
- **Grupowanie po regionach** — porównanie emisji między kontynentami
- **Porównania grupowe** — analiza średnich emisji per capita według regionów

---

## 6. Przekształcanie zmiennych (Feature Engineering)

**Plik:** `src/steps/step_05_feature_engineering.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `add_log_transforms()` | Transformacje logarytmiczne (log1p) |
| `add_polynomial_features()` | Cechy wielomianowe (kwadrat, sześcian) |
| `add_change_features()` | Cechy zmiany rok-do-roku (diff, pct_change) |
| `add_categorical_features()` | Cechy kategoryczne (development_level) |
| `add_ratio_features()` | Cechy stosunkowe (fossil_share, intensity) |
| `add_lag_features()` | Cechy opóźnione (lag1, lag5) |
| `run_step_05()` | Uruchomienie całego kroku |

### Zastosowane techniki

#### 6.1 Transformacje logarytmiczne
- **Transformacja log1p(x)** = log(1+x) dla obsługi wartości zerowych
- **Cel**: normalizacja rozkładów prawoskośnych, stabilizacja wariancji

**Utworzone zmienne:**
- `co2_per_capita_log`
- `gdp_log`
- `population_log`
- `co2_log`
- `primary_energy_consumption_log`

#### 6.2 Cechy wielomianowe (test krzywej Kuznetsa)
- **Zmienne kwadratowe i sześcienne** — do testowania nieliniowych zależności
- **Model EKC**: CO2_per_capita = β₀ + β₁·GDP_pc + β₂·GDP_pc² + ε

**Utworzone zmienne:**
- `gdp_per_capita_sq` (kwadrat)
- `gdp_per_capita_cu` (sześcian)

#### 6.3 Cechy dynamiczne (rok-do-roku)
- **Różnice pierwszego rzędu** — Δx = x(t) - x(t-1)
- **Zmiany procentowe** — (x(t) - x(t-1)) / x(t-1) × 100%

**Utworzone zmienne:**
- `co2_change`, `co2_pct_change`
- `co2_per_capita_change`, `co2_per_capita_pct_change`
- `gdp_change`, `gdp_pct_change`
- `renewable_share_change`

#### 6.4 Cechy kategoryczne
- **Kategoryzacja według kwartyli PKB** — podział na 4 grupy rozwoju
- **Etykiety**: Low, Medium, High, Very High

**Utworzona zmienna:**
- `development_level`

#### 6.5 Cechy stosunkowe (ratios)
- **Udziały procentowe** — normalizacja przez sumę składowych
- **Intensywności** — normalizacja przez PKB lub zużycie energii

**Utworzone zmienne:**
- `fossil_share`, `coal_share`, `oil_share`, `gas_share`
- `emission_intensity`, `energy_intensity`

#### 6.6 Cechy opóźnione (lagged)
- **Opóźnienia czasowe** — lag1 (1 rok) i lag5 (5 lat)
- **Cel**: modelowanie efektów przyczynowych

**Utworzone zmienne:**
- `co2_per_capita_lag1`, `co2_per_capita_lag5`
- `gdp_lag1`, `gdp_lag5`

---

## 7. Analiza danych nietypowych (Outliers)

**Plik:** `src/steps/step_06_outliers.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `detect_outliers_multiple_methods()` | Wykrywanie outlierów metodami IQR i Z-score |
| `identify_extreme_cases()` | Identyfikacja ekstremalnych przypadków (top N) |
| `analyze_known_outliers()` | Analiza znanych kategorii (kraje naftowe, nordyckie) |
| `create_outlier_plots()` | Boxploty z zaznaczonymi outlierami |
| `run_step_06()` | Uruchomienie całego kroku |

**Plik pomocniczy:** `src/utils/df.py`

| Funkcja | Opis |
|---------|------|
| `detect_outliers_iqr()` | Wykrywanie outlierów metodą IQR |
| `detect_outliers_zscore()` | Wykrywanie outlierów metodą Z-score |
| `get_outlier_bounds_iqr()` | Obliczenie granic IQR (Q1-1.5×IQR, Q3+1.5×IQR) |

### Zastosowane techniki

#### 7.1 Metoda IQR (Interquartile Range)
- **Definicja outlitera**: x < Q1 - 1.5×IQR lub x > Q3 + 1.5×IQR
- **IQR** = Q3 - Q1

#### 7.2 Metoda Z-score
- **Definicja outlitera**: |z| > 3, gdzie z = (x - μ) / σ
- **Standaryzacja**: przeskalowanie do średniej 0 i odchylenia 1

### Wyniki analizy outlierów

| Zmienna | Liczba outlierów (IQR) | % outlierów | Liczba outlierów (Z-score) |
|---------|------------------------|-------------|----------------------------|
| co2 | 674 | 14.79% | 47 |
| co2_per_capita | 278 | 6.10% | 102 |
| gdp | 455 | 9.98% | 50 |
| population | 502 | 11.02% | 42 |

### Zidentyfikowane kategorie outlierów

1. **Kraje naftowe** (wysokie emisje per capita): Katar (67.73 t CO2/os), Kuwejt, ZEA
2. **Duże gospodarki** (wysokie emisje całkowite): Chiny (10,896 Mt CO2), USA, Indie
3. **Kraje nordyckie** (niskie emisje przy wysokim PKB): Norwegia, Szwecja, Islandia

### Decyzja o obsłudze
- **Zachowano** wszystkie outliery jako prawdziwe wartości ekstremalne
- **Rekomendacja**: analiza wrażliwości z i bez outlierów, dodanie zmiennych kontrolnych

---

## 8. Analiza braków danych

**Plik:** `src/steps/step_07_missing_data.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `compute_missing_stats()` | Statystyki braków dla każdej zmiennej |
| `analyze_missing_by_country()` | Analiza braków według krajów |
| `analyze_missing_by_year()` | Analiza braków według lat |
| `analyze_missing_patterns()` | Analiza wzorców braków (które zmienne brakują razem) |
| `impute_data()` | Imputacja wieloetapowa (interpolacja → fill → mediana) |
| `create_missing_plots()` | Heatmapa i wykresy braków |
| `run_step_07()` | Uruchomienie całego kroku |

**Plik pomocniczy:** `src/utils/df.py`

| Funkcja | Opis |
|---------|------|
| `df_missing_summary()` | Podsumowanie braków danych |
| `impute_interpolate()` | Interpolacja czasowa w ramach grupy |
| `impute_forward_backward()` | Forward/backward fill |
| `impute_by_group()` | Imputacja medianą grupową |

### Zastosowane techniki

#### 8.1 Analiza wzorców braków
- **Mapa braków (heatmapa)** — wizualizacja wzorców brakujących wartości
- **Analiza według zmiennych** — procent braków dla każdej zmiennej
- **Analiza według krajów** — identyfikacja krajów z największą liczbą braków
- **Analiza według lat** — identyfikacja lat z największą liczbą braków

#### 8.2 Klasyfikacja mechanizmów braków
- **MCAR** (Missing Completely At Random) — braki losowe
- **MAR** (Missing At Random) — braki zależne od obserwowanych zmiennych
- **MNAR** (Missing Not At Random) — braki zależne od wartości brakującej

### Wyniki analizy braków

| Kategoria | Liczba zmiennych |
|-----------|------------------|
| >30% braków | 27 |
| 10-30% braków | 68 |
| <10% braków | 59 |

**Kraje z największą liczbą braków:**
- Watykan (90.2%)
- Wyspa Bożego Narodzenia (86.3%)
- Monako (84.3%)

### Strategia imputacji

#### Zastosowane metody (w kolejności):

1. **Interpolacja czasowa** — dla wartości wewnątrz szeregu czasowego kraju
   - Metoda liniowa między znanymi punktami

2. **Forward/backward fill** — dla wartości na krawędziach szeregu
   - Propagacja ostatniej znanej wartości

3. **Mediana regionalna** — dla pozostałych braków
   - Mediana obliczona w ramach regionu geograficznego

4. **Mediana globalna** — jako ostateczność
   - Mediana ze wszystkich obserwacji

### Wyniki imputacji

| Zmienna | Braki przed | Braki po | Uzupełniono |
|---------|-------------|----------|-------------|
| co2 | 63 | 0 | 63 |
| co2_per_capita | 84 | 0 | 84 |
| gdp | 1,113 | 0 | 1,113 |
| population | 21 | 0 | 21 |
| primary_energy_consumption | 300 | 0 | 300 |
| coal_co2 | 1,683 | 0 | 1,683 |
| oil_co2 | 86 | 0 | 86 |
| gas_co2 | 1,941 | 0 | 1,941 |

---

## 9. Wybór zmiennych i rekordów

**Plik:** `src/steps/step_08_final_selection.py`

### Funkcje

| Funkcja | Opis |
|---------|------|
| `select_countries()` | Selekcja krajów (wykluczenie z >30% braków) |
| `select_years()` | Selekcja lat (2000-2020) |
| `select_variables()` | Selekcja zmiennych (istotność, braki <30%) |
| `validate_final_dataset()` | Walidacja finalnego zbioru |
| `run_step_08()` | Uruchomienie całego kroku |

**Plik:** `src/steps/step_09_export.py`

| Funkcja | Opis |
|---------|------|
| `export_to_csv()` | Eksport do CSV |
| `export_to_parquet()` | Eksport do Parquet |
| `generate_codebook()` | Generowanie codebooka |
| `run_step_09()` | Uruchomienie całego kroku |

### Kryteria selekcji

#### Kryteria wykluczenia krajów:
- Kraje z >30% brakujących danych w kluczowych zmiennych
- Agregaty regionalne (World, Europe, Africa, itp.)

#### Kryteria wyboru lat:
- Zakres czasowy 2000-2020 (wspólny dla wszystkich źródeł)

#### Kryteria wyboru zmiennych:
- Istotność dla pytań badawczych
- Akceptowalny poziom braków (<30%)
- Unikanie redundancji (wysoka korelacja)

### Finalny zbiór danych

| Charakterystyka | Wartość |
|-----------------|---------|
| Liczba obserwacji | 4,557 |
| Liczba krajów | 216 |
| Zakres czasowy | 2000-2020 |
| Liczba zmiennych | 50 |

### Kategorie zmiennych w finalnym zbiorze

| Kategoria | Liczba zmiennych | Przykłady |
|-----------|------------------|-----------|
| Identyfikatory | 4 | country, year, iso_code, region |
| Zmienne zależne | 3 | co2, co2_per_capita, co2_per_capita_log |
| Główne predyktory | 6 | gdp, gdp_per_capita, gdp_per_capita_sq |
| Energia | 12 | primary_energy_consumption, coal_co2, oil_co2 |
| OZE | 4 | renewable_energy_share, electricity_from_renewables |
| Dynamika | 6 | co2_change, gdp_pct_change, renewable_share_change |
| Kategoryczne | 1 | development_level |
| Opóźnione | 4 | co2_per_capita_lag1, gdp_lag5 |
| Metadane krajów | 4 | urban_population, agricultural_land |

---

## Podsumowanie zastosowanych technik statystycznych

### Statystyki opisowe

| Technika | Opis | Zastosowanie w projekcie |
|----------|------|--------------------------|
| Średnia arytmetyczna | Suma wartości / liczba obserwacji | Średnie emisje CO2 per capita według regionów |
| Mediana | Wartość środkowa po uporządkowaniu | Odporna na outliery miara tendencji centralnej |
| Odchylenie standardowe | Miara rozproszenia wokół średniej | Ocena zmienności emisji między krajami |
| Wariancja | Kwadrat odchylenia standardowego | Analiza zmienności w czasie |
| Kwartyle (Q1, Q2, Q3) | Podział rozkładu na 4 części | Kategoryzacja krajów (development_level) |
| Rozstęp międzykwartylowy (IQR) | Q3 - Q1 | Wykrywanie outlierów |
| Skośność (skewness) | Asymetria rozkładu | Identyfikacja potrzeby transformacji log |
| Kurtoza | Spłaszczenie/wypiętrzenie rozkładu | Ocena "ciężkości ogonów" rozkładu |
| Minimum, maksimum | Wartości ekstremalne | Identyfikacja zakresu zmiennych |

### Analiza korelacji

| Technika | Wzór | Zastosowanie w projekcie |
|----------|------|--------------------------|
| Współczynnik korelacji Pearsona | r = Σ(x-x̄)(y-ȳ) / √[Σ(x-x̄)²Σ(y-ȳ)²] | Badanie zależności liniowej CO2-PKB |
| Macierz korelacji | Korelacje parami dla wszystkich zmiennych | Identyfikacja współliniowości |
| Korelacja rang Spearmana | ρ = 1 - 6Σd²/n(n²-1) | Alternatywa dla danych nieparametrycznych |

### Wykrywanie wartości odstających (outlierów)

| Technika | Kryterium | Zastosowanie w projekcie |
|----------|-----------|--------------------------|
| Metoda IQR | x < Q1 - 1.5×IQR lub x > Q3 + 1.5×IQR | Identyfikacja krajów o ekstremalnych emisjach |
| Metoda Z-score | \|z\| > 3, gdzie z = (x - μ) / σ | Standaryzowana identyfikacja outlierów |
| Wizualna inspekcja (boxploty) | Punkty poza wąsami | Weryfikacja outlierów |

### Transformacje zmiennych

| Technika | Wzór | Cel |
|----------|------|-----|
| Transformacja logarytmiczna | y = log(x) | Normalizacja rozkładów prawoskośnych |
| Transformacja log1p | y = log(1 + x) | Obsługa wartości zerowych |
| Cechy wielomianowe | x², x³ | Test nieliniowych zależności (krzywa Kuznetsa) |
| Standaryzacja (Z-score) | z = (x - μ) / σ | Porównywalność zmiennych o różnych skalach |
| Różnicowanie | Δx = x(t) - x(t-1) | Usuwanie trendu, analiza dynamiki |
| Zmiany procentowe | (x(t) - x(t-1)) / x(t-1) × 100% | Porównywalna miara tempa zmian |
| Opóźnienia czasowe (lag) | x(t-k) | Modelowanie efektów przyczynowych |

### Imputacja braków danych

| Technika | Opis | Zastosowanie w projekcie |
|----------|------|--------------------------|
| Interpolacja liniowa | Estymacja między znanymi punktami | Uzupełnianie luk w szeregach czasowych |
| Forward fill | Propagacja ostatniej wartości w przód | Wypełnianie końcówek szeregów |
| Backward fill | Propagacja pierwszej wartości wstecz | Wypełnianie początków szeregów |
| Mediana grupowa | Mediana w ramach grupy (regionu) | Uzupełnianie braków z uwzględnieniem podobieństwa |
| Mediana globalna | Mediana ze wszystkich obserwacji | Ostateczna metoda dla pojedynczych braków |

### Wizualizacja danych

| Typ wykresu | Zastosowanie |
|-------------|--------------|
| Histogram | Rozkład zmiennych ciągłych (CO2, PKB) |
| Wykres pudełkowy (boxplot) | Porównanie rozkładów, identyfikacja outlierów |
| Wykres rozrzutu (scatter plot) | Zależności między zmiennymi (PKB vs CO2) |
| Heatmapa | Macierz korelacji, wzorce braków danych |
| Wykres liniowy | Trendy czasowe emisji |
| Wykres słupkowy | Porównania między kategoriami (regionami) |

---

## Techniki przygotowane do modelowania (gotowość danych)

Dane zostały przygotowane do zastosowania następujących technik statystycznych i ekonometrycznych:

### Regresja liniowa

| Model | Wzór | Zastosowanie |
|-------|------|--------------|
| Regresja liniowa prosta | Y = β₀ + β₁X + ε | Podstawowa zależność CO2 od PKB |
| Regresja liniowa wieloraka | Y = β₀ + β₁X₁ + β₂X₂ + ... + βₖXₖ + ε | Wieloczynnikowy model emisji |
| Metoda najmniejszych kwadratów (OLS) | min Σ(yᵢ - ŷᵢ)² | Estymacja parametrów regresji |

### Regresja nieliniowa (krzywa Kuznetsa)

| Model | Wzór | Interpretacja |
|-------|------|---------------|
| Model kwadratowy | CO2 = β₀ + β₁·GDP + β₂·GDP² + ε | Test hipotezy odwróconego U |
| Model sześcienny | CO2 = β₀ + β₁·GDP + β₂·GDP² + β₃·GDP³ + ε | Test kształtu N (wielokrotne punkty zwrotne) |
| Punkt zwrotny EKC | GDP* = -β₁ / (2β₂) | PKB przy maksymalnych emisjach |

### Analiza panelowa (dane przekrojowo-czasowe)

| Model | Opis | Zastosowanie |
|-------|------|--------------|
| Pooled OLS | Ignoruje strukturę panelową | Punkt odniesienia |
| Model efektów stałych (FE) | Kontrola nieobserwowanej heterogeniczności krajów | Eliminacja stałych cech krajów |
| Model efektów losowych (RE) | Heterogeniczność jako składnik losowy | Gdy FE nieefektywny |
| Test Hausmana | H₀: RE jest spójny | Wybór między FE a RE |

### Analiza skupień (clustering)

| Technika | Opis | Zastosowanie |
|----------|------|--------------|
| K-means | Podział na k grup minimalizujący wariancję wewnątrzgrupową | Grupowanie krajów według profili emisji |
| Hierarchiczne grupowanie | Dendrogramy, łączenie aglomeracyjne | Identyfikacja struktury podobieństwa |
| Metoda łokcia | Wybór optymalnej liczby klastrów | Określenie k dla K-means |

### Analiza interakcji i moderacji

| Technika | Wzór | Zastosowanie |
|----------|------|--------------|
| Efekt interakcji | Y = β₀ + β₁X + β₂Z + β₃(X×Z) + ε | Wpływ regionu na zależność PKB-CO2 |
| Analiza podgrup | Oddzielne modele dla kategorii | Porównanie współczynników między regionami |

### Testy statystyczne

| Test | Hipoteza | Zastosowanie |
|------|----------|--------------|
| Test t-Studenta | H₀: μ₁ = μ₂ | Porównanie średnich między grupami |
| Test F | H₀: β₁ = β₂ = ... = 0 | Istotność łączna modelu regresji |
| Test Shapiro-Wilka | H₀: rozkład normalny | Sprawdzenie założeń regresji |
| Test Breusch-Pagana | H₀: homoskedastyczność | Diagnostyka reszt regresji |
| Test Durbin-Watsona | H₀: brak autokorelacji | Diagnostyka dla danych czasowych |

---

## Struktura kodu - pliki i funkcje

### Główne kroki (steps/)

| Plik | Krok | Główne funkcje |
|------|------|----------------|
| `step_00_download.py` | Pozyskanie danych | `get_owid_co2_dataset()`, `get_sustainable_energy_dataset()`, `get_countries_of_world_dataset()` |
| `step_01_quality_assessment.py` | Ocena jakości | `assess_completeness()`, `assess_variable_coverage()`, `generate_quality_report()` |
| `step_02_cleaning.py` | Czyszczenie | `standardize_column_names()`, `filter_aggregates()`, `clean_owid_dataset()` |
| `step_03_merging.py` | Łączenie | `merge_owid_sustainable()`, `add_country_metadata()`, `validate_merge()` |
| `step_04_eda.py` | EDA | `compute_descriptive_stats()`, `compute_correlation_analysis()`, `analyze_temporal_trends()` |
| `step_05_feature_engineering.py` | Feature Engineering | `add_log_transforms()`, `add_polynomial_features()`, `add_change_features()` |
| `step_06_outliers.py` | Analiza outlierów | `detect_outliers_multiple_methods()`, `identify_extreme_cases()` |
| `step_07_missing_data.py` | Analiza braków | `compute_missing_stats()`, `impute_data()`, `analyze_missing_patterns()` |
| `step_08_final_selection.py` | Selekcja | `select_countries()`, `select_variables()`, `validate_final_dataset()` |
| `step_09_export.py` | Eksport | `export_to_csv()`, `generate_codebook()` |

### Narzędzia pomocnicze (utils/)

| Plik | Funkcje |
|------|---------|
| `df.py` | `df_info()`, `df_describe_all()`, `correlation_matrix()`, `detect_outliers_iqr()`, `detect_outliers_zscore()`, `impute_interpolate()`, `impute_by_group()` |
| `plotting.py` | `plot_histogram()`, `plot_boxplot()`, `plot_correlation_heatmap()`, `plot_scatter()`, `plot_time_series()`, `plot_missing_heatmap()` |
| `country.py` | `standardize_country_name()`, `is_aggregate()`, `get_region()`, `add_region_column()` |
| `report.py` | `ReportBuilder` - klasa do generowania raportów Markdown |

### Punkt wejściowy

| Plik | Opis |
|------|------|
| `main.py` | Uruchomienie całego pipeline'u (wszystkie kroki sekwencyjnie) |

---

## Podsumowanie

Projekt obejmował pełny proces przygotowania danych zgodny z metodyką Data Science:

1. **Pozyskanie danych** — 3 źródła, łącznie ~54,000 rekordów
2. **Ocena jakości** — analiza kompletności, wiarygodności źródeł
3. **Czyszczenie** — standaryzacja, filtrowanie, walidacja
4. **Łączenie** — integracja zbiorów po kluczach
5. **EDA** — statystyki opisowe, korelacje, rozkłady, trendy
6. **Feature engineering** — 26 nowych zmiennych
7. **Analiza outlierów** — metody IQR i Z-score
8. **Analiza braków** — wzorce, imputacja wieloetapowa
9. **Selekcja** — finalny zbiór 4,557 obs. × 50 zmiennych

**Dane są gotowe do modelowania statystycznego i ekonometrycznego.**

---

*Raport wygenerowany na podstawie przeprowadzonej analizy danych w ramach projektu "Walidacja i przygotowanie danych"*
