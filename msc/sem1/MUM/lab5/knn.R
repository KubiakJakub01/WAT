# --------------------------------------------------------------------------
#               Metoda k-srednich
# --------------------------------------------------------------------------

library(tidyverse)

# Zaczytanie zbioru danych college dotyczace uczelni wyzszych w USA
# 
# - id to unikatowy liczbowy identyfikator instytucji,
# - name to nazwa instytucji,
# - city to nazwa miasta, w którym znajduje sie instytucja,
# - state to dwuznakowy skrót stanu, w którym znajduje sie instytucja,
# - region to jeden z czterech regionów USA, w którym znajduje sie instytucja: Northeast,
#   Midwest, West lub South,
# - highest_degree to najwyzszy stopien naukowy przyznawany przez instytucje: Associate,
#   Bachelor, Graduate lub Nondegree (bez stopnia naukowego),
# - control to rodzaj organizacji kontrolujacej instytucje: Public (publiczna) lub Private
#   (prywatna),
# - gender to podzial ze wzgledu na plec: CoEd (koedukacyjna), Male (meska) lub
#   Female (zenska),
# - dmission_rate to odsetek aplikantów, którzy zlozyli wniosek i dostali sie do szkoly,
# - sat_avg to sredni wynik egzaminu SAT aplikantów (punkty od 400 do 1600),
# - undergrads to liczba studentów studiów licencjackich,
# - uition to roczne czesne za studia w danej instytucji w dolarach,
# - faculty_salary_avg to srednia miesieczna pensja czlonka wydzialu w dolarach,
# - loan_default_rate to odsetek studentów, którzy pózniej zalegaja z oplacaniem rat
#   kredytu studenckiego,
# - median_debt to mediana wysokosci kredytu absolwentów w dolarach,
# - lon to dlugosc geograficzna glównego budynku uczelni,
# - lat to szerokosc geograficzna glównego budynku uczelni.


college <- read_csv("http://jolej.linuxpl.info/college.csv", col_types = "nccfffffnnnnnnnnn")

# Podglad zbioru danych
glimpse(college)


# Utworzenie nowego zbioru danych ograniczonego do stanu Maryland
# Nadanie etykiet wierszom odpowiadajacycm nazwie uczelni

maryland_college <- college %>%
  filter(state == "MD") %>%
  column_to_rownames(var = "name")


# Segmentacja bedzie prowadzona w oparciu o dwie zmienne :
# admission_rate (odsetek przyjmowanych kandydatów) oraz sat_avg
# (srednia wyników egzaminów SAT)

maryland_college %>%
  select(admission_rate, sat_avg) %>%
  summary()


# Cechy maja inne zakresy wartosci dlatego powinny zostac znormalizowane

maryland_college_scaled <- maryland_college %>%
  select(admission_rate, sat_avg) %>%
  scale()


maryland_college_scaled %>%
  summary()

# Klasteryzacja za pomoca funkcji kmeans()
# Funkcja kmeans() ma kilka argumentów, które kontroluja proces klasteryzacji.
# Pierwszym argumentem sa dane poddawane klasteryzacji. Drugim (centers) jest
# liczba klastrów. Reprezentuje ona wartosc k =3
# Ostatni argument (nstart) okresla liczbe iteracji.

library(stats)

set.seed(1234)
k_3 <- kmeans(maryland_college_scaled, centers=3, nstart = 25)

# Liczba obserwacji w kazdym z klastrów
k_3$size

# Srodki kazdego z klastrów
k_3$centers

# Wizualizacja klasteryzacji za pomoca funkcji fviz_cluster() z pakietu factoextra

library(factoextra)
fviz_cluster(k_3,
             data = maryland_college_scaled,
             repel = TRUE,
             ggtheme = theme_minimal()) + theme(text = element_text(size = 14))

# Uczelnie w klastrze 1 ( Johns Hopkins oraz University of Maryland–College Park)
# maja w porównaniu z innymi uczelniami w tym stanie wyzsze niz srednia (>0) wyniki
# SAT i nizszy niz srednia (<0) odsetek przyjmowanych kandydatów. Sa to prestizowe
# uczelnie, wiec przyjmuja najlepszych uczniów.

# Sredni wynik SAT dla uczelni w klastrze 2 jest nizszy niz srednia stanowa, 
# podobnie jak odsetek przyjmowanych kandydatów.
# 
# Uczelnie w klastrze 3 maja przewaznie równe lub wyzsze niz srednia stanowa wyniki
# SAT i odsetek przyjmowanych kandydatów.

# ocena róznic miedzy klastrami w zakresie takich atrybutów, jak czesne,
# splacalnosc kredytu studenckiego czy pensje pracowników wydzialu.

# Przypisanie etykiet klastrów do obserwacji w zbiorze danych maryland_
# college. 
# 
# Wybór atrybutów, do porównania poprzez pogrupowanie ich wedlug
# klastrów,  
# 
# Generowanie srednich wartosci dla kazdego z wybranych atrybutów

maryland_college %>%
  mutate(cluster = k_3$cluster) %>%
  select(cluster,
         undergrads,
         tuition,
         faculty_salary_avg,
         loan_default_rate,
         median_debt) %>%
  group_by(cluster) %>%
  summarise_all("mean")

# uczelnie w klastrze 1 (srednio) maja wiecej
# osób na studiach licencjackich (undergrads, 16286), wyzsze czesne (tuition, 28 244$)
# oraz lepiej wynagradzanych pracowników (faculty_salary_avg, 11 258$). Wynik wskazuje
# równiez, ze absolwenci tych uczelni rzadziej zalegaja ze splata kredytu studenckiego
# (loan_default_rate, 1,75 procent). Co koreluje z faktem, iz z reguly koncza oni studia
# z mniejszym kredytem do splacenia (median_debt, 17 875$).


# ------------------------------------------------------------------------------------------
#                     Wybieranie odpowiedniej liczby klastrów
# ------------------------------------------------------------------------------------------



# Metoda lokcia

# Funkcja fviz_nbclust() z pakietu factoextra ma trzy argumenty wejsciowe. 
# Pierwszym jest zbiór danych (maryland_college_scaled), 
# drugim metoda klasteryzacji (kmeans), 
# a ostatnim metoda oceniania (wss). W tej funkcji wartosc wss reprezentuje metode
# oceniania WCSS

fviz_nbclust(maryland_college_scaled, kmeans, method = "wss")

# Potencjalne wartosci k to 4 lub 7


# Metoda sredniego zarysu

# Róznica z poprzednim uzyciem funkcji fviz_nbclust() polega na zastosowaniu
# metody oceniania "silhouette" zamiast "wss"
fviz_nbclust(maryland_college_scaled, kmeans, method = "silhouette")

# Podobnie jak w przypadku metody „lokcia”, wyniki metody sredniego zarysu 
# sugeruja, ze k=4 i k=7 to optymalne liczby klastrów.


# Statystyka odstepu

# Róznica z poprzednim uzyciem funkcji fviz_nbclust() polega na zastosowaniu
# metody oceniania "gap_stat"

fviz_nbclust(maryland_college_scaled, kmeans, method = "gap_stat")

# Wynik sugeruje, ze optymalne liczby klastrów to 1 i 7


# Najwazniejszym czynnikiem decydujacym o wyborze
# wartosci k powinna byc przydatnosc koncowych klastrów z perspektywy uzytkownika.
# Biorac pod uwage, ze zbiór danych zawiera tylko 19 uczelni ze stanu Maryland,
# zastosowanie k = 7 oznaczaloby, ze kazdy z klastrów zawieralby srednio jedynie dwie
# lub trzy uczelnie. To nie zapewnia szerokich mozliwosci porównywania uczelni w klastrach,
# dlatego zostanie uzyta wartosc k = 4.

k_4 <- kmeans(maryland_college_scaled, centers = 4, nstart = 25)

fviz_cluster(
  k_4,
  data = maryland_college_scaled,
  main = "Maryland Colleges Segmented by SAT Scores and Admission Rates",
  repel = TRUE)

