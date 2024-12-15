# Prosze zaimportowac , dokonac wstepnej analizy i przygotowac do obr�bki zni�r
# Wesbrook znajdujacy sie pod adresem http://jolej.linuxpl.info/Wesbrook.csv
# W tym celu nalezy:

# 1. Zaimportowac zbi�r danych z odpowiednimi typami zmiennych z uzyciem funkcji read_csv()
# 2. Dokonac wstepnej analizy zbioru z wykorzystaniem statystyk opisowych
# 3. Dokonac analizy istotnosci zmiennych , utworzyc nowy zbi�r Wesbrook2 zawierajacy tylko 
# istotne zmienne.
# 4. Wykonac wizualna analize danych, w ramach analizy wizualnej rozklad zmiennych numerycznych 
# przedstawic na jednym wykresie macierzowym uzywajac histogram�w
# 5. Przygotowac dane do analizy w tym celu:
#  - dokonac imputacji brakujacych wartosci
#  - normalizacji zmiennych numerycznych metoda z-score i min-max
#  - wykonac kodowanie zero jedynkowe (wprowadzic zmienne sztuczne) dla zmiennej MARTIAL
#  - wykoac pr�bkowanie warstwowe dzielac zbi�r na treningowy i walidacyjny w proporcji 
#  80 % do 20% wedlug zmiennej WESBROOK

# Kod + raport co się zrobiło, analiza, wnioski i obrazki

library(tidyverse)
library(ggplot2)

# 1. Zaimportowac zbi�r danych z odpowiednimi typami zmiennych z uzyciem funkcji read_csv()
wesbrook_data <- read_csv("http://jolej.linuxpl.info/Wesbrook.csv", col_types = cols(
  ID = col_integer(),
  WESBROOK = col_factor(levels = c("Y", "N")),
  TOTLGIVE = col_double(),
  INDUPDT = col_date(format = "%m/%d/%Y"),
  GRADYR1 = col_integer(),
  FACULTY1 = col_character(),
  DEPT1 = col_character(),
  MAJOR1 = col_character(),
  PARENT = col_factor(levels = c("Y", "N")),
  CHILD = col_factor(levels = c("Y", "N")),
  SPOUSE = col_factor(levels = c("Y", "N")),
  SEX = col_factor(levels = c("M", "F")),
  MARITAL = col_character(),
  EA = col_integer(),
  FACSTAFF = col_factor(levels = c("Y", "N")),
  ATHLTCS = col_factor(levels = c("Y", "N")),
  BIGBLOCK = col_factor(levels = c("Y", "N")),
  OTHERACT = col_factor(levels = c("Y", "N")),
  FRSTYEAR = col_integer(),
  MOV_DWEL = col_double(),
  HH_1PER = col_double(),
  HH_2PER = col_double(),
  HH_3PER = col_double(),
  HH_45PER = col_double(),
  AVE_INC = col_double(),
  DWEL_VAL = col_double(),
  PROV = col_character(),
  CNDN_PCT = col_double(),
  ENG_PCT = col_double(),
  OWN_PCT = col_double(),
  SD_INC = col_double()
))
head(wesbrook_data)

# 2. Dokonac wstepnej analizy zbioru z wykorzystaniem statystyk opisowych
glimpse(wesbrook_data)

# Statystyki opisowe dla zmiennych numerycznych
summary(wesbrook_data %>% select(where(is.numeric)))

# Proporcje zmiennych kategorii
wesbrook_data %>%
  select(where(is.factor)) %>%
  map(table)


# 3. Dokonac analizy istotnosci zmiennych , utworzyc nowy zbi�r Wesbrook2 zawierajacy tylko
# istotne zmienne.

# Testy t-test i Wilcoxon dla zmiennych numerycznych
numeric_vars <- wesbrook_data %>%
  select(where(is.numeric))
numeric_tests <- numeric_vars %>%
  map(~ t.test(.x ~ wesbrook_data$WESBROOK, na.action = na.omit))
print(numeric_tests)

# Analiza istotności przy zmiennych kategorycznych
anova_results <- wesbrook_data %>%
  select(WESBROOK, where(is.factor)) %>%
  map(~ chisq.test(table(.x, wesbrook_data$WESBROOK)))
print(anova_results)

# Wybrane zmienne istotne
wesbrook2 <- wesbrook_data %>%
  select(
    WESBROOK, TOTLGIVE, GRADYR1, FRSTYEAR, AVE_INC, DWEL_VAL, SD_INC,
    PARENT, CHILD, SPOUSE, SEX, FACSTAFF, ATHLTCS, OTHERACT
  )
head(wesbrook2)

# 4. Wykonac wizualna analize danych, w ramach analizy wizualnej rozklad zmiennych numerycznych
# przedstawic na jednym wykresie macierzowym uzywajac histogram�w
# Wyodrębnienie zmiennych numerycznych
numeric_data <- wesbrook2 %>%
  select(where(is.numeric))

# Przygotowanie danych w formacie długim
long_data <- numeric_data %>%
  pivot_longer(everything(), names_to = "Variable", values_to = "Value")

# Histogramy
ggplot(long_data, aes(x = Value)) +
  geom_histogram(bins = 30, fill = "blue", alpha = 0.7, color = "black") +
  facet_wrap(~ Variable, scales = "free", ncol = 3) +
  theme_minimal() +
  labs(title = "Rozkład zmiennych numerycznych", x = "Wartość", y = "Częstotliwość")

# 5. Przygotowac dane do analizy w tym celu:

# Imputacja brakujących wartości
print(colSums(is.na(wesbrook2)))
wesbrook2 <- wesbrook2 %>%
  mutate(across(where(is.numeric), ~ if_else(is.na(.), mean(., na.rm = TRUE), .)))
print(colSums(is.na(wesbrook2)))

# Normalizacja zmiennych numerycznych metoda z-score i min-max
z_score <- wesbrook2 %>%
  select(where(is.numeric)) %>%
  scale()
head(z_score)

min_max <- wesbrook2 %>%
    select(where(is.numeric)) %>%
    map_dfc(~ (.-min(.))/(max(.)-min(.)))
head(min_max)

# Kodowanie zero jedynkowe (wprowadzic zmienne sztuczne) dla zmiennych katagorycznych
library(dummies)
categorical_columns <- c("PARENT", "CHILD", "SPOUSE", "SEX", "FACSTAFF", "ATHLTCS", "OTHERACT")
wesbrook2 <- dummy.data.frame(
  wesbrook2,
  names = categorical_columns,
  sep = "_"
)
head(wesbrook2)

# Pr�bkowanie warstwowe dzielac zbi�r na treningowy i walidacyjny w proporcji 80 % do 20% wedlug zmiennej WESBROOK
set.seed(1234)
sample_set <-
  sample(nrow(wesbrook2), nrow(wesbrook2) * 0.80, replace = FALSE)

nrow(wesbrook2)
train_set <- wesbrook2[sample_set, ]
nrow(train_set)
test_set <- wesbrook2[-sample_set, ]
nrow(test_set)
