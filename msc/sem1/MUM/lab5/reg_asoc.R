#----------------------------------------------------------------------------
#          Tworzenie regul asocjacyjnych
#---------------------------------------------------------------------------
library(arules)

# Funkcja read.transactions() z pakietu arules
# wczytuje zbiór danych do macierzy rzadkiej. Macierz rzadka
# to macierz jedynek i zer, w której zdecydowana wiekszosc wartosci to zera. W tym
# przypadku kazdy wiersz w macierzy reprezentuje pojedyncza transakcje, natomiast kazda
# kolumna reprezentuje unikatowy produkt sprzedawany przez supermarket. Wartosc
# danej komórki wynosi 1, gdy produkt reprezentowany przez kolumne zostal zakupiony
# w ramach transakcji reprezentowanej przez ten wiersz.

supermart <- read.transactions("http://jolej.linuxpl.info/retail.txt", sep = "")
  

summary(supermart)

# Wynik dostarcza pewne ogólne spostrzezenia dotyczace
# danych. Z trzech pierwszych wierszy dowiadujemy sie, ze zbiór danych zawiera
# 88162 transakcje (wiersze) i 16470 unikatowych elementów (kolumn). 
# Gestosc zbioru danych wynosi 0,0006257289. Gestosc jest odwrotnoscia rzadkosci, 
# czyli reprezentuje odsetek elementów,
# które sa brakujacymi wartosciami. Zbiór danych supermarketu jest bardzo rzadki,

# Kolejne trzy wiersze danych wyjsciowych to najczesciej kupowane produkty w sklepie
# wraz z liczba transakcji, w jakich wystepuja. Na ich podstawie widac, ze element
# 39 to najczesciej kupowany produkt i ze zostal kupiony w 50675 z 88162 transakcji
# w zbiorze danych.

# Kolejne 14 wierszy danych wyjsciowych to podsumowanie dlugosci transakcji
# w zbiorze danych wraz z liczba transakcji o danej dlugosci.

# Pozostale wiersze wyniku
# pokazuja po prostu zakres wartosci dla dlugosci transakcji i próbke 
# trzech elementów ze zbioru danych.

#Przy pomocy funkcji inspect() mozna wyswietlic liste wskazanych transakcji w zbiorze
#danych.

inspect(supermart[1:5], linebreak = FALSE)

# funkcja itemFrequency() zwraca czestotliwosc (wsparcie) elementu
itemFrequency(supermart[ ,"39"])

# element {39} pojawia sie w okolo 60% transakcji


# Tworzymy obiekt tibble zawierajacy czestotliwosc wszystkich elementów w zbiorze
library(tidyverse)
supermart_frequency <-
  tibble(
    Items = names(itemFrequency(supermart)),
    Frequency = itemFrequency(supermart)
  )


head(supermart_frequency)


# Jaka jest czestotliwosc 10 najczesciej kupowanych artykulów ?
supermart_frequency %>%
  arrange(desc(Frequency)) %>%
  slice(1:10)

# Po uwzgledniu zasady antymonotonicznosci wsparcia, widac, ze próg
# wsparcia dla regul asocjacyjnych bedzie musial byc nie wiekszy niz 0,0344, aby uchwycic
# reguly zawierajace te 10 elementów.


# Ustalenie paramtrów modelu

# Minimalny próg wsparcia
# Jak czesto wzorzec musi sie pojawiac, aby byl uzyteczny. Przy zalozeniu ze 
# interesujace sa wzorce pojawiajace sie przynajmniej piec razy dziennie. Wiadomo, ze dane byly
# zbierane przez piec miesiecy i mozna w uproszczeniu zalozyc, ze kazdy z nich mial 30
# dni, w zwiazku z tym wzorzec pojawiajacy sie przynajmniej piec razy dziennie powinien
# wystepowac w przynajmniej 5×150 transakcjach w zbiorze danych. Wiadomo, ze zbiór
# danych zawiera 88162 transakcje, dlatego minimalnym wsparciem dla wzorca bedzie
# 5×150/88162=0,0085.

# Wyznaczanie progu ufnosci. Przy zalozeniu , ze aby regula
# zostala dolaczona, poprzednik i nastepnik musza pojawiac sie razem w przynajmniej
# polowie przypadków. W zwiazku z tym  próg ufnosci zostal ustawiony na 0,5.

# Aby wylaczyc reguly, które maja mniej niz dwa elementy, 
# minimalna dlugosc reguly zostala ustawiona na 2.

supermartrules <-
  apriori(supermart,
          parameter = list(
            support = 0.0085,
            confidence = 0.5,
            minlen = 2
          ))

supermart,rules

summary(supermartrules)

# Dwie pierwsze sekcje
# danych wyjsciowych infor muja, ze zgodnie z ustawionymi progami wygenerowanych
# zostalo 145 regul. Z wygenerowanych regul 76 ma dlugosc 2, 54 maja dlugosc 3, a 15
# ma dlugosc 4. Kolejna sekcja danych wyjsciowych zawiera podsumowanie statystyczne
# wsparcia, ufnosci, przyrostu i liczby (count) wygenerowanych regul. W ostatniej sekcji
# znajduje sie lista parametrów, które zostaly wykorzystane do generowania regul.


# Wyswietlenie 10-ciu pierwszych wygenerowanych regul
inspect(supermartrules[1:10])

# Pierwsza regula mówi, ze w 98 procent (ufnosc) transakcji klienci, którzy kupili
# element 371, kupili równiez element 38. Ten wzorzec mozna znalezc w 0.86 procent
# czy 767 transakcjach (wsparcie i licznik) w zbiorze danych. Regula mówi równiez,
# ze jesli klient kupil element 371, istnieje 5,54 razy (przyrost) wieksze prawdopodobienstwo,
# ze kupi równiez element 38. To bardzo silna regula.

# Posortowane  dziesiec pierwszych regul w oparciu o przyrost, w tym celu zostala uzyta 
# funkcja sort() dostepna w pakiecie arules.
supermartrules %>%
  sort(by = "lift") %>%
  head(n = 10) %>%
  inspect() 


# Wyswietlenie tylko tych regul, które zawieraja element {41}
supermartrules %>%
  subset(items %in% "41") %>%
  inspect()

# Wyswietlenie dziesieciu regul zawierajacych artykul {41} o najwiekszym przyroscie
supermartrules %>%
  subset(items %in% "41") %>%
  sort(by = "lift") %>%
  head(n = 10) %>%
  inspect()


