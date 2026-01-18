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

## Temat: **Wpływ rozwoju gospodarczego na emisję CO2 i transformację energetyczną**

**Kategorie:** Gospodarka + Ochrona środowiska

---

## 🎯 Pytania badawcze

### Główne pytanie
>
> **Jak poziom rozwoju gospodarczego kraju (PKB per capita) wpływa na emisję CO2 i udział energii odnawialnej w miksie energetycznym?**

### Pytania szczegółowe

| Nr | Pytanie | Typ analizy |
|----|---------|-------------|
| 1 | **Czy istnieje krzywa środowiskowa Kuznetsa (EKC)?** — Czy emisje CO2 per capita rosną wraz z PKB per capita do pewnego punktu, a następnie spadają? | Regresja nieliniowa (kwadratowa) |
| 2 | **Jakie czynniki strukturalne** (urbanizacja, dostęp do elektryczności, intensywność energetyczna) najsilniej różnicują kraje o podobnym PKB pod względem emisji CO2? | Regresja wieloraka, analiza skupień |
| 3 | **Czy tempo wzrostu PKB wpływa na tempo transformacji energetycznej** (wzrost udziału OZE)? | Analiza panelowa, korelacja zmian |
| 4 | **Jak region geograficzny moderuje związek między rozwojem a emisjami?** | Analiza interakcji, porównania grupowe |
| 5 | **Które źródła emisji CO2** (węgiel, ropa, gaz, cement) dominują na różnych poziomach rozwoju gospodarczego? | Analiza struktury, wizualizacja |

---

## 📁 Datasety

### Dataset 1 (główny): OWID CO2 Data

| Cecha | Wartość |
|-------|---------|
| Źródło | Our World in Data (GitHub) |
| Link | <https://github.com/owid/co2-data> |
| Plik | `owid-co2-data.csv` |
| Zakres czasowy | 1750–2023 |
| Liczba krajów | ~200 |
| Liczba zmiennych | ~79 |

**Kluczowe zmienne:**

- `country`, `year`, `iso_code` — identyfikatory
- `population`, `gdp` — dane demograficzne i ekonomiczne
- `co2`, `co2_per_capita`, `co2_per_gdp` — emisje CO2
- `coal_co2`, `oil_co2`, `gas_co2`, `cement_co2` — emisje według źródła
- `primary_energy_consumption`, `energy_per_capita` — zużycie energii
- `methane`, `nitrous_oxide` — inne gazy cieplarniane

---

### Dataset 2: Global Data on Sustainable Energy

| Cecha | Wartość |
|-------|---------|
| Źródło | Kaggle |
| Link | <https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy> |
| Plik | `global-data-on-sustainable-energy.csv` |
| Zakres czasowy | 2000–2020 |
| Liczba zmiennych | ~21 |

**Kluczowe zmienne:**

- `Entity`, `Year` — identyfikatory
- `Access to electricity (% of population)` — dostęp do elektryczności
- `Renewable energy share in total final energy consumption (%)` — udział OZE
- `Electricity from renewables (TWh)` — produkcja z OZE
- `gdp_per_capita`, `gdp_growth` — dane ekonomiczne
- `Density`, `Land Area` — dane geograficzne

---

### Dataset 3: Countries of the World 2023

| Cecha | Wartość |
|-------|---------|
| Źródło | Kaggle |
| Link | <https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023> |
| Plik | `world-data-2023.csv` |
| Typ | Dane przekrojowe (cross-sectional) |

**Kluczowe zmienne:**

- `Country` — identyfikator
- `Urban_population` — % populacji miejskiej
- `Agricultural Land (%)` — struktura gospodarcza
- `Unemployment Rate`, `Tax Revenue (%)` — wskaźniki ekonomiczne

---

## 🔗 Plan łączenia danych

```
OWID CO2 Data                    Sustainable Energy Data
     │                                    │
     │ (country, year)                    │ (Entity, Year)
     │                                    │
     └──────────────┬─────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  MERGED DATA  │
            │  (2000-2020)  │
            └───────┬───────┘
                    │
                    │ (country)
                    ▼
            ┌───────────────┐
            │ Country Info  │
            │ (urbanizacja) │
            └───────────────┘
```

**Klucz łączenia:** `country` + `year` (po standaryzacji nazw krajów)

---

## 🛠️ Plan przetwarzania danych

### 1. Pozyskanie danych

- [ ] Pobranie OWID CO2 Data z GitHub
- [ ] Pobranie Sustainable Energy z Kaggle
- [ ] Pobranie Country Info z Kaggle
- [ ] Dokumentacja źródeł i licencji

### 2. Ocena jakości danych

- [ ] Ocena wiarygodności źródeł (OWID = agregacja oficjalnych danych)
- [ ] Analiza kompletności czasowej i geograficznej
- [ ] Identyfikacja potencjalnych problemów (różne nazwy krajów)

### 3. Czyszczenie i łączenie

- [ ] Standaryzacja nazw krajów (np. "USA" vs "United States")
- [ ] Łączenie po kluczu `(country, year)`
- [ ] Obsługa duplikatów i niespójności
- [ ] Wybór wspólnego zakresu czasowego (2000–2020)

### 4. Eksploracyjna analiza danych (EDA)

- [ ] Statystyki opisowe wszystkich zmiennych
- [ ] Rozkłady zmiennych (histogramy, boxploty)
- [ ] Macierz korelacji
- [ ] Trendy czasowe (liniowe wykresy)
- [ ] Scatterploty kluczowych zależności

### 5. Przekształcanie zmiennych

Nowe zmienne do utworzenia:

| Zmienna | Formuła | Cel |
|---------|---------|-----|
| `co2_per_capita_log` | log(co2_per_capita) | Normalizacja rozkładu |
| `gdp_per_capita_log` | log(gdp_per_capita) | Normalizacja rozkładu |
| `gdp_per_capita_sq` | gdp_per_capita² | Test krzywej Kuznetsa |
| `renewable_share_change` | Δ renewable_share (rok do roku) | Tempo transformacji |
| `co2_change_rate` | Δ co2 / co2 (%) | Dynamika emisji |
| `development_level` | Kwartyle PKB per capita | Kategoryzacja krajów |
| `region` | Mapowanie ISO → kontynent | Analiza regionalna |
| `fossil_share` | (coal + oil + gas) / total CO2 | Struktura emisji |

### 6. Analiza danych nietypowych

- [ ] Identyfikacja outlierów (IQR, Z-score)
- [ ] Analiza przypadków ekstremalnych:
  - Katar, Kuwejt — bardzo wysokie emisje per capita
  - Norwegia, Islandia — wysokie PKB, niskie emisje
  - Chiny, Indie — duże całkowite emisje, niskie per capita
- [ ] Decyzja o obsłudze outlierów (usunięcie vs winsoryzacja)

### 7. Analiza braków danych

- [ ] Mapa braków danych (heatmapa)
- [ ] Analiza wzorców braków (MCAR, MAR, MNAR)
- [ ] Identyfikacja krajów/lat z największymi brakami
- [ ] Strategia imputacji:
  - Interpolacja czasowa dla szeregów czasowych
  - Mediana grupowa (według regionu) dla danych przekrojowych
  - Multiple imputation dla analizy wrażliwości

### 8. Wybór zmiennych i rekordów

**Kryteria wykluczenia:**

- Kraje z >30% brakujących danych
- Lata spoza zakresu 2000–2020
- Agregaty regionalne (np. "World", "Europe")

**Zmienne do finalnego zbioru:**

| Kategoria | Zmienne |
|-----------|---------|
| Identyfikatory | country, year, iso_code, region |
| Zmienna zależna | co2_per_capita, renewable_share |
| Zmienne niezależne | gdp_per_capita, gdp_growth, urbanization, energy_intensity, access_electricity |
| Kontrolne | population, land_area, latitude |

---

## 📈 Oczekiwane wyniki

### Zbiór danych końcowy

- **~150 krajów** × **21 lat** (2000–2020) = ~3000 obserwacji
- **~15-20 zmiennych** (po selekcji)
- Format: CSV + dokumentacja (codebook)

### Gotowość do modelowania

- [ ] Dane oczyszczone i połączone
- [ ] Braki danych obsłużone
- [ ] Outliers zidentyfikowane i opisane
- [ ] Zmienne przekształcone i gotowe do analizy
- [ ] Dokumentacja wszystkich kroków

---

## 📚 Struktura raportu

1. **Wstęp** — temat, pytania badawcze, uzasadnienie
2. **Źródła danych** — opis datasetów, ocena jakości
3. **Czyszczenie i łączenie** — procedury, problemy, rozwiązania
4. **EDA** — statystyki, rozkłady, korelacje, wizualizacje
5. **Przekształcenia** — nowe zmienne, uzasadnienie
6. **Analiza outlierów** — identyfikacja, interpretacja
7. **Analiza braków** — wzorce, imputacja
8. **Finalny zbiór danych** — opis, codebook
9. **Podsumowanie** — wnioski, ograniczenia
