## Zadanie

Proszę przeprowadzić i udokumentować proces przygotowania danych. Proces ten powinien obejmować zagadnienia przedstawiane na wykładzie i ćwiczeniach. W szczególności powinien on obejmować następujące elementy:

Samodzielne pozyskanie danych (ze źródła pierwotnego lub wtórnego);
Ocenę jakości danych (w tym ocenę źródła danych, przydatności danych, możliwości uogólnienia wniosków z przyszłej analizy danych);
Czyszczenie i porządkowanie danych (w tym łączenie danych z różnych źródeł)
Eksploracyjną analizę danych (w tym badanie rozkładów zmiennych, badanie współzależności między zmiennymi; w sposób tabelaryczny, parametryczny i graficzny)
Przekształcanie zmiennych (w tym dodawanie nowych, użytecznych zmiennych)
Analizę danych nietypowych
Analizę braków danych (w tym analizę wzorców braków danych, imputację brakujących wartości)
Wybór zmiennych i rekordów do przykładowej analizy
Szczegółowy temat projektu powinien być ustalany samodzielnie przez grupę i powinien się mieścić w jednej z niżej podanych kategorii:

Sport
Poruszanie się po mieście
Ochrona środowiska
Rozrywka
Gospodarka
(Przykładowo, jeżeli grupa zdecyduje się na kategorię „Poruszanie się po mieście”, to może zająć się tematem związanym z rowerem miejskim i poszukać danych dotyczących wypożyczeń rowerów (czasów, odległości, dostępności). Następnie grupa może postawić pytanie badawcze o zależność liczby wypożyczeń z warunkami pogodowymi, a więc poszukać danych pogodowych i połączyć je z danymi dotyczącymi wypożyczeń.)

W ramach projektu proszę sformułować pytania badawcze, ale nie należy na nie odpowiadać, a jedynie przygotować dane, które będą mogły być w przyszłości wykorzystane do budowania modeli statystycznych, które na te pytania by odpowiadały.  

W ramach jednego projektu można przygotować jeden lub kilka zbiorów danych (na ten sam temat).  

Źródło surowych danych może być dowolne. W przypadku danych wtórnych można korzystać z repozytoriów danych nieoficjalnych, takich jak <www.kaggle.com>, archive.ics.uci.edu, a także repozytoriów danych z badań naukowych (np. data.mendeley.com). Bazy danych oficjalnych instytucji (krajowych urzędów statystycznych, międzynarodowych organizacji itp.) mogą być tu mniej przydatne, gdyż zwykle zawierają dane oczyszczone i uporządkowane (niemniej mogą się przydać jako dane pomocnicze oraz do analizy braków i obserwacji nietypowych).

Produkty końcowe projektu:

Raport z przeprowadzonych działań – dokument zawierający opisy i uzasadnienia wszystkich działań, wyniki obliczeń (w tym prezentację graficzną), interpretacje wyników
Skrypt z kodem
R i/lub Python
skrypt powinien być czytelny i dobrze opisany
skrypt może być elementem raportu
Prezentacja projektu
Prezentacja wykonywana jest w wyznaczonym dla każdej grupy terminie.
Prezentacja odbywa się przed inną grupą, która zadaje pytania i/lub krytycznie ocenia projekt.
Prezentacja powinna trwać maksymalnie 10 min., a dyskusja 5 min. (przekroczenie czasu prezentacji wpływa negatywnie na jej ocenę)

---

## Szczegółowy plan analizy

### 1. POZYSKANIE DANYCH (Data Acquisition)

#### 1.1 NASA POWER (dane pogodowe)

| Element | Opis |
|---------|------|
| Źródło | HuggingFace: `notadib/NASA-Power-Daily-Weather` |
| Okres | 1984-2022 (ograniczymy do **1992-2020** dla spójności z pożarami) |
| Region | USA (filtrujemy tylko punkty z USA) |
| Liczba zmiennych | 31 |
| Format wejściowy | CSV/Parquet via HuggingFace datasets |

#### 1.2 US Wildfires FPA-FOD (dane o pożarach)

| Element | Opis |
|---------|------|
| Źródło | Kaggle: `behroozsohrabi/us-wildfire-records-6th-edition` |
| Okres | 1992-2020 |
| Region | USA |
| Liczba rekordów | ~2.3 miliona |
| Format wejściowy | SQLite |

---

### 2. OCENA JAKOŚCI DANYCH (Data Quality Assessment)

#### 2.1 Ocena źródeł

| Kryterium | NASA POWER | US Wildfires |
|-----------|-----------|--------------|
| **Wiarygodność** | NASA - agencja rządowa, dane satelitarne | USDA Forest Service - oficjalne raporty |
| **Metodologia** | Modele asymilacyjne + satelity | Raporty federalne, stanowe, lokalne |
| **Dokumentacja** | Pełna dokumentacja API | Publikacja naukowa (Short, 2014) |
| **Aktualizacje** | Regularne | 6 edycji (ostatnia 2022) |
| **Ograniczenia** | Rozdzielczość gridowa (nie punktowa) | Brak małych pożarów z prywatnych terenów |

#### 2.2 Kompletność danych

- Zliczenie rekordów per rok/miesiąc
- Identyfikacja luk czasowych
- Sprawdzenie pokrycia geograficznego

#### 2.3 Spójność danych

- Walidacja zakresów wartości (np. temperatura -50°C do +50°C)
- Sprawdzenie jednostek
- Wykrycie niespójności logicznych (np. CONT_DATE < DISCOVERY_DATE)

---

### 3. ANALIZA BRAKÓW DANYCH (Missing Data Analysis)

#### 3.1 NASA POWER

| Analiza | Opis |
|---------|------|
| Zliczenie braków | Per zmienna i per rok |
| Wzorce braków | MCAR vs MAR vs MNAR |
| Wizualizacja | Macierz braków (missingno), heatmapa |
| Korelacja z czasem | Czy braki częstsze w określonych okresach? |
| Korelacja z lokalizacją | Czy braki częstsze w określonych regionach? |

#### 3.2 US Wildfires

| Zmienna | Oczekiwane braki | Analiza |
|---------|------------------|---------|
| `DISCOVERY_TIME` | ~50% | Czy brak wpływa na analizę? |
| `CONT_DATE` | ~40% | Pożary nadal aktywne vs brak danych |
| `COUNTY` | ~30% | Możliwość uzupełnienia z lat/lon |
| `FIRE_NAME` | ~50% | Małe pożary bez nazwy |

#### 3.3 Strategie imputacji

- **Usunięcie** - dla zmiennych z >50% braków (opcjonalnie)
- **Interpolacja czasowa** - dla danych pogodowych (średnia z sąsiednich dni)
- **Interpolacja przestrzenna** - dla danych pogodowych (średnia z sąsiednich punktów)
- **Mediana/średnia** - dla zmiennych numerycznych
- **Moda** - dla zmiennych kategorycznych
- **KNN Imputer** - dla złożonych wzorców

---

### 4. CZYSZCZENIE I ŁĄCZENIE DANYCH (Data Cleaning & Merging)

#### 4.1 Czyszczenie NASA POWER

| Operacja | Szczegóły |
|----------|-----------|
| Filtrowanie regionu | Tylko punkty z USA (lat: 24-50, lon: -125 do -66) |
| Filtrowanie czasu | 1992-01-01 do 2020-12-31 |
| Korekta typów | Daty, numeryczne, kategoryczne |
| Usunięcie duplikatów | Po (lat, lon, date) |
| Standaryzacja nazw | Ujednolicenie nazw kolumn |

#### 4.2 Czyszczenie US Wildfires

| Operacja | Szczegóły |
|----------|-----------|
| Ekstrakcja z SQLite | Wybór potrzebnych kolumn |
| Konwersja dat | Julian date → datetime |
| Walidacja współrzędnych | Usunięcie rekordów poza USA |
| Kategoryzacja | STAT_CAUSE_CODE → kategorie tekstowe |
| Usunięcie duplikatów | Po FOD_ID |

#### 4.3 Łączenie datasetów ⭐

| Metoda | Opis |
|--------|------|
| **Spatial join** | Przypisanie pożaru do najbliższego punktu gridowego NASA POWER |
| **Temporal join** | Dopasowanie danych pogodowych z dnia wykrycia pożaru (i N dni przed) |
| **Agregacja** | Dla każdego pożaru: warunki pogodowe z dnia D, D-1, D-7, D-30 |

**Klucze łączenia:**

- `latitude`, `longitude` → najbliższy punkt NASA POWER (Haversine distance)
- `discovery_date` → data w NASA POWER

---

### 5. EKSPLORACYJNA ANALIZA DANYCH (EDA)

#### 5.1 Statystyki opisowe

**NASA POWER - wszystkie 31 zmiennych:**

| Statystyka | Zmienne |
|------------|---------|
| Min, Max, Mean, Median, Std | Wszystkie numeryczne |
| Kwartyle (Q1, Q3) | Wszystkie numeryczne |
| Skośność, Kurtoza | Wszystkie numeryczne |
| Liczba unikalnych | Zmienne kategoryczne |

**US Wildfires:**

| Statystyka | Zmienne |
|------------|---------|
| Rozkład przyczyn | `STAT_CAUSE_DESCR` |
| Rozkład rozmiarów | `FIRE_SIZE`, `FIRE_SIZE_CLASS` |
| Rozkład czasowy | `FIRE_YEAR`, `DISCOVERY_DOY` |
| Rozkład przestrzenny | `STATE`, `LATITUDE`, `LONGITUDE` |

#### 5.2 Rozkłady zmiennych (wizualizacje)

| Typ wykresu | Zastosowanie |
|-------------|--------------|
| **Histogramy** | Rozkład każdej zmiennej pogodowej |
| **Box plots** | Porównanie rozkładów między sezonami/regionami |
| **Violin plots** | Rozkład FIRE_SIZE per przyczyna |
| **KDE plots** | Gęstość rozkładu temperatury, opadów |
| **Bar plots** | Liczba pożarów per przyczyna, stan, rok |

#### 5.3 Analiza czasowa (trendy i sezonowość)

| Analiza | Opis |
|---------|------|
| **Trend roczny** | Średnia temperatura, opady, liczba pożarów per rok (1992-2020) |
| **Sezonowość** | Rozkład zmiennych per miesiąc |
| **Dekompozycja** | Trend + sezonowość + reszta (dla wybranych zmiennych) |
| **Sezon pożarowy** | Kiedy występuje najwięcej pożarów? (per region) |

**Pytania:**

- Czy temperatura rośnie w czasie? (zmiana klimatu)
- Czy liczba pożarów rośnie w czasie?
- Czy sezon pożarowy się wydłuża?

#### 5.4 Analiza przestrzenna

| Analiza | Opis |
|---------|------|
| **Mapy cieplne** | Średnia temperatura, opady, liczba pożarów per region |
| **Clustering przestrzenny** | Hotspoty pożarów |
| **Porównanie regionów** | Zachód vs Wschód USA |

#### 5.5 Analiza korelacji

| Macierz korelacji | Zmienne |
|-------------------|---------|
| **Wewnątrz NASA POWER** | Wszystkie 31 zmiennych (Pearson, Spearman) |
| **Między datasetami** | Zmienne pogodowe vs FIRE_SIZE |

**Kluczowe korelacje do zbadania:**

| Zmienna 1 | Zmienna 2 | Hipoteza |
|-----------|-----------|----------|
| `T2M` | `FIRE_SIZE` | Wyższa temperatura → większe pożary? |
| `PRECTOTCORR` | `FIRE_SIZE` | Mniej opadów → większe pożary? |
| `RH2M` | `FIRE_SIZE` | Niższa wilgotność → większe pożary? |
| `WS2M` | `FIRE_SIZE` | Silniejszy wiatr → większe pożary? |
| `GWETPROF` | pożary | Sucha gleba → więcej pożarów? |
| `T2M` | `ET0` | Temperatura vs ewapotranspiracja |
| `ALLSKY_SFC_SW_DWN` | `CLOUD_AMT` | Promieniowanie vs zachmurzenie |

#### 5.6 Związki między zmiennymi (szczegółowe)

| Typ analizy | Opis |
|-------------|------|
| **Scatter plots** | T2M vs FIRE_SIZE, PRECTOTCORR vs FIRE_SIZE |
| **Pair plots** | Wybrane grupy zmiennych |
| **Regresja liniowa** | Preliminary relationships |
| **Chi-square test** | STAT_CAUSE vs FIRE_SIZE_CLASS |
| **ANOVA** | Różnice w warunkach pogodowych per przyczyna pożaru |

---

### 6. PRZEKSZTAŁCANIE ZMIENNYCH (Feature Engineering)

#### 6.1 Nowe zmienne z NASA POWER

| Nowa zmienna | Formuła/Opis | Uzasadnienie |
|--------------|--------------|--------------|
| `drought_index` | f(PRECTOTCORR, ET0, GWETPROF, VAD) | Złożony wskaźnik suszy |
| `solar_potential` | f(ALLSKY_SFC_SW_DWN, CLOUD_AMT, ALLSKY_SRF_ALB) | Potencjał energii słonecznej |
| `fire_weather_index` | f(T2M, RH2M, WS2M, PRECTOTCORR) | Wskaźnik warunków pożarowych |
| `heat_stress` | f(T2M, RH2M, T2MWET) | Stres cieplny |
| `temp_range` | T2M_MAX - T2M_MIN | Amplituda dobowa |
| `precip_deficit` | ET0 - PRECTOTCORR | Deficyt wodny |

#### 6.2 Zmienne czasowe

| Zmienna | Opis |
|---------|------|
| `year` | Rok |
| `month` | Miesiąc (1-12) |
| `day_of_year` | Dzień roku (1-366) |
| `season` | Zima/Wiosna/Lato/Jesień |
| `is_summer` | Czerwiec-Sierpień (0/1) |
| `is_fire_season` | Maj-Październik (0/1) |

#### 6.3 Zmienne opóźnione (lagged features)

| Zmienna | Opis |
|---------|------|
| `T2M_lag7` | Średnia temperatura z ostatnich 7 dni |
| `PRECTOTCORR_lag30` | Suma opadów z ostatnich 30 dni |
| `drought_days` | Liczba dni bez opadów |
| `heatwave_days` | Liczba dni z T2M > 35°C w ostatnich 14 dniach |

#### 6.4 Zmienne z US Wildfires

| Nowa zmienna | Formuła/Opis |
|--------------|--------------|
| `fire_duration` | CONT_DATE - DISCOVERY_DATE |
| `is_large_fire` | FIRE_SIZE > 100 acres (0/1) |
| `is_human_caused` | STAT_CAUSE_CODE != 1 (Lightning) |
| `fire_month` | Miesiąc wykrycia |
| `region` | Zachód/Środkowy Zachód/Południe/Północny Wschód |

#### 6.5 Zmienne agregowane (per lokalizacja/czas)

| Zmienna | Opis |
|---------|------|
| `fires_per_month` | Liczba pożarów w danym miesiącu/regionie |
| `total_burned_area` | Suma spalonej powierzchni |
| `avg_fire_size` | Średni rozmiar pożaru |

---

### 7. ANALIZA DANYCH NIETYPOWYCH (Outlier Analysis)

#### 7.1 Metody detekcji

| Metoda | Zastosowanie |
|--------|--------------|
| **IQR (Interquartile Range)** | Wszystkie zmienne numeryczne |
| **Z-score** | Zmienne o rozkładzie zbliżonym do normalnego |
| **Modified Z-score (MAD)** | Zmienne z outlierami |
| **Isolation Forest** | Multivariate outlier detection |
| **DBSCAN** | Przestrzenne anomalie |
| **LOF (Local Outlier Factor)** | Lokalne anomalie |

#### 7.2 Zmienne do szczegółowej analizy outlierów

| Zmienna | Oczekiwane outliers | Interpretacja |
|---------|---------------------|---------------|
| `FIRE_SIZE` | Mega-pożary | Prawdziwe ekstremalne zdarzenia |
| `T2M` | Ekstremalne temperatury | Fale upałów/mrozów |
| `PRECTOTCORR` | Intensywne opady | Burze, huragany |
| `WS2M` | Silne wiatry | Tornada, huragany |
| `SNODP` | Ekstremalne opady śniegu | Burze śnieżne |

#### 7.3 Analiza outlierów

| Krok | Opis |
|------|------|
| 1. Identyfikacja | Lista outlierów per zmienna |
| 2. Wizualizacja | Box plots, scatter plots |
| 3. Weryfikacja | Czy to błąd czy prawdziwe ekstremum? |
| 4. Kontekst | Sprawdzenie dat (np. huragan, fala upałów) |
| 5. Decyzja | Zachować / usunąć / winsoryzować |

#### 7.4 Strategie obsługi

| Strategia | Kiedy stosować |
|-----------|----------------|
| **Zachowanie** | Prawdziwe ekstremalne zdarzenia (mega-pożary) |
| **Usunięcie** | Błędy pomiarowe (np. temperatura 999°C) |
| **Winsoryzacja** | Ograniczenie do percentyla 1-99 |
| **Transformacja** | Log-transformacja dla skośnych rozkładów |
| **Osobna analiza** | Ekstrema jako osobna kategoria |

---

### 8. WYBÓR ZMIENNYCH I REKORDÓW (Variable & Record Selection)

#### 8.1 Filtrowanie rekordów

| Filtr | Uzasadnienie |
|-------|--------------|
| Okres: 1992-2020 | Nakładający się okres obu datasetów |
| Region: Kontynentalne USA | Wykluczenie Alaski, Hawajów (inne klimaty) |
| Kompletność | Rekordy z <20% braków |
| Jakość | Wykluczenie błędnych rekordów |

#### 8.2 Selekcja zmiennych dla pytań badawczych

**Pytanie 1: Ryzyko suszy**

| Zmienna | Typ | Rola |
|---------|-----|------|
| `PRECTOTCORR` | NASA POWER | Predictor |
| `ET0` | NASA POWER | Predictor |
| `GWETPROF` | NASA POWER | Predictor |
| `VAD` | NASA POWER | Predictor |
| `T2M` | NASA POWER | Predictor |
| `drought_index` | Engineered | Target/Predictor |

**Pytanie 2: Potencjał solarny**

| Zmienna | Typ | Rola |
|---------|-----|------|
| `ALLSKY_SFC_SW_DWN` | NASA POWER | Predictor/Target |
| `ALLSKY_SFC_PAR_TOT` | NASA POWER | Predictor |
| `CLOUD_AMT` | NASA POWER | Predictor |
| `ALLSKY_SRF_ALB` | NASA POWER | Predictor |
| `solar_potential` | Engineered | Target |

**Pytanie 3: Zapotrzebowanie energetyczne**

| Zmienna | Typ | Rola |
|---------|-----|------|
| `CDD18_3` | NASA POWER | Target |
| `HDD18_3` | NASA POWER | Target |
| `T2M`, `T2M_MAX`, `T2M_MIN` | NASA POWER | Predictors |

**Pytanie 4: Przewidywanie pożarów** ⭐

| Zmienna | Źródło | Rola |
|---------|--------|------|
| `FIRE_SIZE` | Wildfires | Target |
| `is_large_fire` | Engineered | Target (klasyfikacja) |
| `T2M`, `T2M_MAX` | NASA POWER | Predictor |
| `PRECTOTCORR` | NASA POWER | Predictor |
| `RH2M` | NASA POWER | Predictor |
| `WS2M` | NASA POWER | Predictor |
| `GWETPROF` | NASA POWER | Predictor |
| `drought_index` | Engineered | Predictor |
| `fire_weather_index` | Engineered | Predictor |
| `STAT_CAUSE_CODE` | Wildfires | Predictor |
| `season`, `month` | Engineered | Predictor |

#### 8.3 Analiza współliniowości

| Analiza | Próg |
|---------|------|
| Macierz korelacji | r > 0.8 → potencjalny problem |
| VIF (Variance Inflation Factor) | VIF > 5 → usunięcie zmiennej |
| PCA | Redukcja wymiarowości (opcjonalnie) |

#### 8.4 Ranking ważności zmiennych

| Metoda | Opis |
|--------|------|
| Korelacja z targetem | Prosty ranking |
| Mutual Information | Nieliniowe zależności |
| Random Forest Feature Importance | Wstępny model |
| Permutation Importance | Bardziej wiarygodne |

---

### 9. FINALNE ZBIORY DANYCH (Final Datasets)

#### 9.1 Dataset: `drought_analysis.csv`

- Dane dzienne NASA POWER dla USA
- Zmienne związane z suszą
- ~X milionów rekordów

#### 9.2 Dataset: `solar_potential.csv`

- Dane NASA POWER agregowane per region/miesiąc
- Zmienne związane z energią słoneczną
- ~X tysięcy rekordów

#### 9.3 Dataset: `fire_prediction.csv` ⭐

- Połączone dane pożarów + warunki pogodowe
- Każdy rekord = 1 pożar + warunki z dnia wykrycia
- ~2 miliony rekordów

#### 9.4 Dataset: `full_merged.csv`

- Pełny dataset do dalszych analiz
- Wszystkie zmienne

#### 9.5 Podział train/test

| Zbiór | Opis |
|-------|------|
| Train | 1992-2016 (80%) |
| Test | 2017-2020 (20%) |

*Podział czasowy, nie losowy - symulacja real-world scenario*

---

### 10. PODSUMOWANIE ANALIZ W RAPORCIE

| Sekcja raportu | Zawartość |
|----------------|-----------|
| 1. Wprowadzenie | Cel, pytania badawcze, źródła danych |
| 2. Pozyskanie danych | Opis procesu pobierania |
| 3. Ocena jakości | Tabele z oceną źródeł |
| 4. Braki danych | Wizualizacje, wzorce, imputacja |
| 5. Czyszczenie | Operacje, liczba usuniętych rekordów |
| 6. Łączenie | Metodologia, statystyki dopasowania |
| 7. EDA | Kluczowe wykresy i wnioski |
| 8. Feature engineering | Nowe zmienne, uzasadnienie |
| 9. Outliers | Wykryte anomalie, decyzje |
| 10. Selekcja | Finalne zmienne per pytanie |
| 11. Podsumowanie | Gotowość danych do modelowania |
