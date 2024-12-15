library(car)
library(RcmdrMisc)
library(corrplot)
library(ggplot2)
library(dplyr)


# Załadowanie danych
day_data <- read.csv("bike-sharing-dataset/day.csv")
hour_data <- read.csv("bike-sharing-dataset/hour.csv")

# Sprawdzenie wszystkich zmiennych
head(day_data)
head(hour_data)

# Wykres macierzowy
scatterplotMatrix(~ temp + atemp + hum + windspeed + casual + registered + cnt, 
                  reg.line = lm, smooth = TRUE, spread = FALSE, span = 0.5, id.n = 0, 
                  diagonal = 'boxplot', data = day_data)

# Wykres punktowy
scatterplot(
    cnt ~ temp,
    reg.line = lm,
    smooth = TRUE,
    spread = FALSE,
    id.method = 'mahal',
    id.n = 2,
    boxplots = 'xy',
    span = 0.5,
    data = day_data
)

# Policzenie korelacji
corr_data <- day_data %>% 
  select(temp, atemp, hum, windspeed, casual, registered, cnt) %>% 
  cor()

# Wykres korelacji
corrplot(corr_data, method = "color", title = "Correlation Matrix", mar = c(0, 0, 1, 0))

# Analiza szeregów czasowych

# Dzienny wykres liczby wypożyczeń
ggplot(day_data, aes(x = as.Date(dteday), y = cnt)) +
  geom_line(color = "blue") +
  labs(title = "Daily Bike Rental Counts Over Time", x = "Date", y = "Count") +
  theme_minimal()

# Sezonowy wykres liczby wypożyczeń
ggplot(day_data, aes(x = season, y = cnt, fill = as.factor(season))) +
  geom_boxplot() +
  labs(title = "Bike Rentals by Season", x = "Season", y = "Count") +
  scale_fill_brewer(palette = "Set3") +
  theme_minimal()

# Liniowy model regresji
linear_model <- lm(cnt ~ temp + atemp + hum + windspeed + season + yr + holiday + weekday + workingday + weathersit, data = day_data)
summary(linear_model)
Anova(linear_model)

# Logarytmowanie zmiennych ciągłych
day_data <- day_data %>%
  mutate(log_cnt = log(cnt),
         log_temp = log(temp + 1),
         log_hum = log(hum + 1))

# Model nielinowy
nonlinear_model <- lm(log_cnt ~ log_temp + log_hum + windspeed + season + yr + holiday + weekday + workingday + weathersit, data = day_data)
summary(nonlinear_model)
Anova(nonlinear_model)

# Wykres reszt dla modelu linowego
scatterplot(linear_model$residuals ~ linear_model$fitted.values, 
            reg.line = lm, smooth = TRUE, spread = FALSE, id.n = 0, 
            main = "Residuals vs Fitted Values", xlab = "Fitted Values", ylab = "Residuals")

# Wykres reszt dla modelu nieliniowego
scatterplot(nonlinear_model$residuals ~ nonlinear_model$fitted.values, 
            reg.line = lm, smooth = TRUE, spread = FALSE, id.n = 0, 
            main = "Residuals vs Fitted Values", xlab = "Fitted Values", ylab = "Residuals")

# Porównanie modeli
summary(linear_model)$r.squared
summary(nonlinear_model)$r.squared

summary(linear_model)$sigma
summary(nonlinear_model)$sigma

# Predykcja liczby wypożyczeń rowerów na podstawie modelu liniowego
day_data$predicted_cnt <- predict(linear_model, newdata = day_data)

# Błąd średniokwadratowy
sqrt(mean((day_data$cnt - day_data$predicted_cnt)^2))

# Wykres predykcji modelu liniowego
ggplot(day_data, aes(x = predicted_cnt, y = cnt)) +
  geom_point(alpha = 0.5) +
  geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
  labs(title = "Actual vs Predicted Bike Rentals", x = "Predicted Count", y = "Actual Count") +
  theme_minimal()

# Predykcja liczby wypożyczeń rowerów na podstawie modelu nieliniowego
day_data$predicted_cnt_nonlinear <- exp(predict(nonlinear_model, newdata = day_data))

# Błąd średniokwadratowy
sqrt(mean((day_data$cnt - day_data$predicted_cnt_nonlinear)^2))

# Wykres predykcji modelu nieliniowego
ggplot(day_data, aes(x = predicted_cnt_nonlinear, y = cnt)) +
  geom_point(alpha = 0.5) +
  geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
  labs(title = "Actual vs Predicted Bike Rentals", x = "Predicted Count", y = "Actual Count") +
  theme_minimal()
