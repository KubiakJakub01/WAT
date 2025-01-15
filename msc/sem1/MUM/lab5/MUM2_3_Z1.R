# Generowanie regul asocjacyjnych

# Zaimportowac zbi�r danych groceries,csv

# Zbi�r danych sklada sie z 9835 transakcji odnotowanych w ciagu miesiaca w malym sklepie 
# spozywczym.
# Ma podobna strukture co przedstawione wczesniej dane z belgijskiego supermarketu
# z dwoma podstawowymi r�znicami. Pierwsza jest to, ze w odr�znieniu od zbioru danych
# z supermarketu, w kt�rym elementy byly oddzielone bialymi znakami, elementy
# w tym zbiorze danych sa rozdzielone przecinkiem. Druga r�znica polega na tym,
# ze elementy w tym zbiorze danych nie zostaly zanonimizowane. Tym razem widac,
# jaki produkt reprezentuje kazdy z element�w. 
# 
# Zadamie polega na wygenerowaniu regul
# asocjacyjnych, kt�re opisuja interesujace wzorce zakupowe w danych.


#----------------------------------------------------------------------------
#          Tworzenie reguł asocjacyjnych dla zbioru "groceries"
#---------------------------------------------------------------------------

library(arules)
library(tidyverse)

# Wczytanie i inspekcja danych
groceries <- read.transactions("http://jolej.linuxpl.info/groceries.csv", sep = ",")
summary(groceries)
inspect(groceries[1:5])
itemFrequency(groceries[, "whole milk"])

# Sprawdzenie częstości występowania produktów
groceries_frequency <- tibble(
  Items     = names(itemFrequency(groceries)),
  Frequency = itemFrequency(groceries)
)
head(groceries_frequency)

# 10 najczęściej kupowanych produktów
groceries_frequency %>%
  arrange(desc(Frequency)) %>%
  slice(1:10)

#----------------------------------------------------------------------------
#          Ustalanie parametrów modelu
#---------------------------------------------------------------------------
min_support <- (30 * 3) / 9835
min_support
min_confidence <- 0.5
min_len <- 2

#----------------------------------------------------------------------------
#          Generowanie reguł przy pomocy algorytmu apriori
#---------------------------------------------------------------------------
groceries_rules <- apriori(
  groceries,
  parameter = list(
    support   = min_support,
    confidence = min_confidence,
    minlen    = min_len
  )
)
summary(groceries_rules)
inspect(groceries_rules[1:10])

groceries_rules %>%
  sort(by = "lift") %>%
  head(n = 10) %>%
  inspect()

groceries_rules %>%
  subset(items %in% "whole milk") %>%
  sort(by = "lift") %>%
  head(n = 10) %>%
  inspect()
