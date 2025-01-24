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

# Trening SOM (nienadzorowany)
som_model <- som(df_scaled, grid = som_grid, rlen = 200, alpha = c(0.05, 0.01), keep.data = TRUE)

# Wizualizacje wyników
plot(som_model, type = "changes")
plot(som_model, type = "count")
plot(som_model, type = "mapping")
plot(som_model, type = "dist.neighbours")
plot(som_model, type = "codes")

# Klasteryzacja hierarchiczna
set_clusters <- 6
som_clusters <- cutree(hclust(dist(som_model$codes[[1]])), set_clusters)
plot(som_model, type = "codes", bgcol = rainbow(set_clusters)[som_clusters])
add.cluster.boundaries(som_model, som_clusters)

# Przypisanie klastrów do danych
df$cluster <- som_clusters[som_model$unit.classif]

# Podsumowanie klastrów
summary(df %>% group_by(cluster))

# Klasteryzacja k-średnich dla porównania
set.seed(1234)
kmeans_model <- kmeans(df_scaled, centers = set_clusters, nstart = 25)
df$kmeans_cluster <- kmeans_model$cluster

# Porównanie klasteryzacji
comparison <- table(df$cluster, df$kmeans_cluster)
print(comparison)
