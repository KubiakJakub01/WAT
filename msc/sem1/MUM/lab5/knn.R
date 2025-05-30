# --------------------------------------------------------------------------
#               Metoda k-srednich
# --------------------------------------------------------------------------

library(tidyverse)

# Zaczytanie zbioru danych college dotyczace uczelni wyzszych w USA
# 
# - id to unikatowy liczbowy identyfikator instytucji,
# - name to nazwa instytucji,
# - city to nazwa miasta, w kt�rym znajduje sie instytucja,
# - state to dwuznakowy skr�t stanu, w kt�rym znajduje sie instytucja,
# - region to jeden z czterech region�w USA, w kt�rym znajduje sie instytucja: Northeast,
#   Midwest, West lub South,
# - highest_degree to najwyzszy stopien naukowy przyznawany przez instytucje: Associate,
#   Bachelor, Graduate lub Nondegree (bez stopnia naukowego),
# - control to rodzaj organizacji kontrolujacej instytucje: Public (publiczna) lub Private
#   (prywatna),
# - gender to podzial ze wzgledu na plec: CoEd (koedukacyjna), Male (meska) lub
#   Female (zenska),
# - dmission_rate to odsetek aplikant�w, kt�rzy zlozyli wniosek i dostali sie do szkoly,
# - sat_avg to sredni wynik egzaminu SAT aplikant�w (punkty od 400 do 1600),
# - undergrads to liczba student�w studi�w licencjackich,
# - uition to roczne czesne za studia w danej instytucji w dolarach,
# - faculty_salary_avg to srednia miesieczna pensja czlonka wydzialu w dolarach,
# - loan_default_rate to odsetek student�w, kt�rzy p�zniej zalegaja z oplacaniem rat
#   kredytu studenckiego,
# - median_debt to mediana wysokosci kredytu absolwent�w w dolarach,
# - lon to dlugosc geograficzna gl�wnego budynku uczelni,
# - lat to szerokosc geograficzna gl�wnego budynku uczelni.


college <- read_csv("http://jolej.linuxpl.info/college.csv", col_types = "nccfffffnnnnnnnnn")

# Podglad zbioru danych
glimpse(college)


# Utworzenie nowego zbioru danych ograniczonego do stanu Maryland
# Nadanie etykiet wierszom odpowiadajacycm nazwie uczelni

maryland_college <- college %>%
  filter(state == "MD") %>%
  column_to_rownames(var = "name")


# Segmentacja bedzie prowadzona w oparciu o dwie zmienne :
# admission_rate (odsetek przyjmowanych kandydat�w) oraz sat_avg
# (srednia wynik�w egzamin�w SAT)

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
# Funkcja kmeans() ma kilka argument�w, kt�re kontroluja proces klasteryzacji.
# Pierwszym argumentem sa dane poddawane klasteryzacji. Drugim (centers) jest
# liczba klastr�w. Reprezentuje ona wartosc k =3
# Ostatni argument (nstart) okresla liczbe iteracji.

library(stats)

set.seed(1234)
k_3 <- kmeans(maryland_college_scaled, centers=3, nstart = 25)

# Liczba obserwacji w kazdym z klastr�w
k_3$size

# Srodki kazdego z klastr�w
k_3$centers

# Wizualizacja klasteryzacji za pomoca funkcji fviz_cluster() z pakietu factoextra

library(factoextra)
fviz_cluster(k_3,
             data = maryland_college_scaled,
             repel = TRUE,
             ggtheme = theme_minimal()) + theme(text = element_text(size = 14))

# Uczelnie w klastrze 1 ( Johns Hopkins oraz University of Maryland�College Park)
# maja w por�wnaniu z innymi uczelniami w tym stanie wyzsze niz srednia (>0) wyniki
# SAT i nizszy niz srednia (<0) odsetek przyjmowanych kandydat�w. Sa to prestizowe
# uczelnie, wiec przyjmuja najlepszych uczni�w.

# Sredni wynik SAT dla uczelni w klastrze 2 jest nizszy niz srednia stanowa, 
# podobnie jak odsetek przyjmowanych kandydat�w.
# 
# Uczelnie w klastrze 3 maja przewaznie r�wne lub wyzsze niz srednia stanowa wyniki
# SAT i odsetek przyjmowanych kandydat�w.

# ocena r�znic miedzy klastrami w zakresie takich atrybut�w, jak czesne,
# splacalnosc kredytu studenckiego czy pensje pracownik�w wydzialu.

# Przypisanie etykiet klastr�w do obserwacji w zbiorze danych maryland_
# college. 
# 
# Wyb�r atrybut�w, do por�wnania poprzez pogrupowanie ich wedlug
# klastr�w,  
# 
# Generowanie srednich wartosci dla kazdego z wybranych atrybut�w

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
# os�b na studiach licencjackich (undergrads, 16286), wyzsze czesne (tuition, 28 244$)
# oraz lepiej wynagradzanych pracownik�w (faculty_salary_avg, 11 258$). Wynik wskazuje
# r�wniez, ze absolwenci tych uczelni rzadziej zalegaja ze splata kredytu studenckiego
# (loan_default_rate, 1,75 procent). Co koreluje z faktem, iz z reguly koncza oni studia
# z mniejszym kredytem do splacenia (median_debt, 17 875$).


# ------------------------------------------------------------------------------------------
#                     Wybieranie odpowiedniej liczby klastr�w
# ------------------------------------------------------------------------------------------



# Metoda lokcia

# Funkcja fviz_nbclust() z pakietu factoextra ma trzy argumenty wejsciowe. 
# Pierwszym jest zbi�r danych (maryland_college_scaled), 
# drugim metoda klasteryzacji (kmeans), 
# a ostatnim metoda oceniania (wss). W tej funkcji wartosc wss reprezentuje metode
# oceniania WCSS

fviz_nbclust(maryland_college_scaled, kmeans, method = "wss")

# Potencjalne wartosci k to 4 lub 7


# Metoda sredniego zarysu

# R�znica z poprzednim uzyciem funkcji fviz_nbclust() polega na zastosowaniu
# metody oceniania "silhouette" zamiast "wss"
fviz_nbclust(maryland_college_scaled, kmeans, method = "silhouette")

# Podobnie jak w przypadku metody �lokcia�, wyniki metody sredniego zarysu 
# sugeruja, ze k=4 i k=7 to optymalne liczby klastr�w.


# Statystyka odstepu

# R�znica z poprzednim uzyciem funkcji fviz_nbclust() polega na zastosowaniu
# metody oceniania "gap_stat"

fviz_nbclust(maryland_college_scaled, kmeans, method = "gap_stat")

# Wynik sugeruje, ze optymalne liczby klastr�w to 1 i 7


# Najwazniejszym czynnikiem decydujacym o wyborze
# wartosci k powinna byc przydatnosc koncowych klastr�w z perspektywy uzytkownika.
# Biorac pod uwage, ze zbi�r danych zawiera tylko 19 uczelni ze stanu Maryland,
# zastosowanie k = 7 oznaczaloby, ze kazdy z klastr�w zawieralby srednio jedynie dwie
# lub trzy uczelnie. To nie zapewnia szerokich mozliwosci por�wnywania uczelni w klastrach,
# dlatego zostanie uzyta wartosc k = 4.

k_4 <- kmeans(maryland_college_scaled, centers = 4, nstart = 25)

fviz_cluster(
  k_4,
  data = maryland_college_scaled,
  main = "Maryland Colleges Segmented by SAT Scores and Admission Rates",
  repel = TRUE)

