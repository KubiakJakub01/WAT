library(kohonen)
library(tidyverse)
library(stringr)

# Wczytanie danych
df <- read_csv("http://jolej.linuxpl.info/mallcustomers.csv")

# Czyszczenie i przygotowanie danych
df <- df %>%
  mutate(
    Income_clean = str_replace_all(Income, "[^0-9.]", ""),
    Income_clean = as.numeric(Income_clean)
  ) %>%
  select(Income_clean, SpendingScore)

# Podział na zbiór treningowy i testowy
set.seed(1)
idx_n <- sample(nrow(df), round(0.8 * nrow(df)))
train <- df[idx_n,]
test <- df[-idx_n,]

# Standaryzacja danych
train_scaled <- scale(train)
test_scaled <- scale(test)

# Tworzenie siatki SOM
som_grid <- somgrid(xdim = 5, ydim = 5, topo = "hexagonal")

# Model nienadzorowany SOM
som_unsupervised <- som(train_scaled, grid = som_grid, rlen = 200, alpha = c(0.05, 0.01), keep.data = TRUE)

# Klasteryzacja hierarchiczna
set_clusters <- 6
som_clusters <- cutree(hclust(dist(som_unsupervised$codes[[1]])), set_clusters)
train_cluster <- as.factor(som_clusters[som_unsupervised$unit.classif])

# Tworzenie zbioru uczącego dla modelu nadzorowanego
train_supervised <- list(x = train_scaled, y = train_cluster)

# Model nadzorowany supersom
som_supervised <- supersom(train_supervised, grid = som_grid, maxNA.fraction = 0.5, rlen = 100, alpha = c(0.05, 0.01))
summary(som_supervised)

# Standaryzacja zbioru testowego
test_supervised <- list(x = as.matrix(test_scaled))

# Predykcja dla zbioru testowego
test_pred <- predict(som_supervised, newdata = test_supervised)

# Przypisanie klastrów do zbiorów
train_final <- cbind(train, cluster = train_cluster)
test_final <- cbind(test, cluster = test_pred$predictions$y)

# Analiza klastrów
by(train_final, train_final$cluster, summary)
by(test_final, test_final$cluster, summary)
