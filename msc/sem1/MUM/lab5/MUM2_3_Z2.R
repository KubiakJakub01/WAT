# Klasteryzacja metoda k-srednich

# Rekord kazdego klienta sklada sie z unikatowego identyfikatora
# (CustomerID), plci (Gender), wieku (Age), rocznej pensji (Income) oraz oceny
# wydatk�w, od 1 do 100, przypisanej w zaleznosci od nawyk�w zakupowych klienta
# i kilku innych czynnik�w (SpendingScore). 
# 
# 
# Zadamie polega na  segmentacji klient�w w oparciu o zmienne Income i SpendingScore.

# UWAGA
# cecha Income jest przechowywana w postaci ciagu znakowego.
# funkcji str_replace_all() z pakietu stringr do zastapienie podciag�w ciagiem pustym ("")


# -------------------------------------------------------------------------
#   Klasteryzacja klientów galerii handlowej metodą k-średnich
# -------------------------------------------------------------------------

library(tidyverse)
library(stringr)

mallcustomers <- read_csv("http://jolej.linuxpl.info/mallcustomers.csv")

glimpse(mallcustomers)

# Ponieważ cecha 'Income' może być zapisana jako tekst (np. "15,000 USD"),
# należy oczyścić i skonwertować ją do typu liczbowego.
mallcustomers <- mallcustomers %>%
  mutate(
    Income_clean = str_replace_all(Income, "[^0-9.]", ""),
    Income_clean = as.numeric(Income_clean)
  )

summary(mallcustomers$Income_clean)

# -------------------------------------------------------------------------
#   Wybór zmiennych i standaryzacja
# -------------------------------------------------------------------------

mallcustomers_subset <- mallcustomers %>%
  select(Income_clean, SpendingScore)
summary(mallcustomers_subset)
mallcustomers_scaled <- scale(mallcustomers_subset)
summary(mallcustomers_scaled)

# -------------------------------------------------------------------------
#   Klasteryzacja metodą k-średnich (k=3)
# -------------------------------------------------------------------------
library(stats)

set.seed(1234)
k3 <- kmeans(mallcustomers_scaled, centers = 3, nstart = 25)

# Podstawowe informacje:
k3$size     # liczba obserwacji w każdym klastrze
k3$centers  # środki klastrów w przestrzeni standaryzowanej
k3$withinss # sumy kwadratów odchyleń w obrębie klastrów

mallcustomers %>%
  mutate(cluster = k3$cluster) %>%
  group_by(cluster) %>%
  summarise(
    avg_income = mean(Income_clean, na.rm = TRUE),
    avg_spending = mean(SpendingScore, na.rm = TRUE),
    n = n()
  )

# -------------------------------------------------------------------------
#   Wizualizacja klasteryzacji
# -------------------------------------------------------------------------
library(factoextra)

fviz_cluster(
  k3,
  data = mallcustomers_scaled,
  geom = "point",
  ellipse.type = "norm",
  main = "K-means clustering of Mall Customers (Income vs SpendingScore)",
  ggtheme = theme_minimal()
) + theme(text = element_text(size = 14))

# -------------------------------------------------------------------------
#   Szukanie optymalnego k
# -------------------------------------------------------------------------

# Metoda łokcia
fviz_nbclust(mallcustomers_scaled, kmeans, method = "wss") +
  ggtitle("Elbow Method")

# Metoda sylwetki
fviz_nbclust(mallcustomers_scaled, kmeans, method = "silhouette") +
  ggtitle("Silhouette Method")

# Statystyka gap
fviz_nbclust(mallcustomers_scaled, kmeans, method = "gap_stat") +
  ggtitle("Gap Statistic")

# -------------------------------------------------------------------------
#   Klasteryzacja metodą k-średnich (k=6)
# -------------------------------------------------------------------------
library(stats)

set.seed(1234)
k6 <- kmeans(mallcustomers_scaled, centers = 6, nstart = 25)

# Podstawowe informacje:
k6$size     # liczba obserwacji w każdym klastrze
k6$centers  # środki klastrów w przestrzeni standaryzowanej
k6$withinss # sumy kwadratów odchyleń w obrębie klastrów

mallcustomers %>%
  mutate(cluster = k6$cluster) %>%
  group_by(cluster) %>%
  summarise(
    avg_income = mean(Income_clean, na.rm = TRUE),
    avg_spending = mean(SpendingScore, na.rm = TRUE),
    n = n()
  )

# -------------------------------------------------------------------------
#   Wizualizacja klasteryzacji
# -------------------------------------------------------------------------
library(factoextra)

fviz_cluster(
  k6,
  data = mallcustomers_scaled,
  geom = "point",
  ellipse.type = "norm",
  main = "K-means clustering of Mall Customers (Income vs SpendingScore)",
  ggtheme = theme_minimal()
) + theme(text = element_text(size = 14))
