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

# Standaryzacja danych
df_scaled <- scale(df)

# Tworzenie siatki SOM
set.seed(123)
som_grid <- somgrid(xdim = 5, ydim = 5, topo = "hexagonal")

# Przygotowanie zmiennej celu (klasteryzacja k-średnich do etykietowania)
set_clusters <- 6
kmeans_model <- kmeans(df_scaled, centers = set_clusters, nstart = 25)
df$cluster_label <- as.factor(kmeans_model$cluster)

# Model nadzorowany SOM
som_supervised <- xyf(df_scaled, df$cluster_label, grid = som_grid, rlen = 100, alpha = c(0.05, 0.01))
summary(som_supervised)

# Klasteryzacja hierarchiczna
som_clusters <- cutree(hclust(dist(som_supervised$codes[[1]])), set_clusters)
plot(som_supervised, type = "codes", bgcol = rainbow(set_clusters)[som_clusters])
add.cluster.boundaries(som_supervised, som_clusters)

# Predykcja na podstawie SOM
som_predictions <- predict(som_supervised)
table(df$cluster_label, factor(som_predictions$predictions[[2]]))

# Model nadzorowany supersom
som_supervised_2 <- supersom(list(df_scaled, df$cluster_label), grid = som_grid, rlen = 100, alpha = c(0.05, 0.01))
summary(som_supervised_2)

# Klasteryzacja hierarchiczna dla modelu supersom
som_clusters_2 <- cutree(hclust(dist(som_supervised_2$codes[[1]])), set_clusters)
plot(som_supervised_2, type = "codes", bgcol = rainbow(set_clusters)[som_clusters_2])

# Predykcja na podstawie supersom
som_predictions_2 <- predict(som_supervised_2)
table(df$cluster_label, factor(som_predictions_2$predictions[[2]]))
