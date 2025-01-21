# Przeanalizować zbiór Wesbrook.csv
# Zbudować model sieci neuronowej
# Skorzystać z wszystkich dostępnych pakietów
# Szuakc najlepszych parametrów
# Porównać wyniki z lab 4
# Sprawozdanie

# Załadowanie bibliotek
library(tidyverse)
library(caret)
library(ROCR)

# Załadowanie zbioru danych
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

# Wybór istotnych zmiennych
wesbrook2 <- wesbrook_data %>%
  select(
    WESBROOK, TOTLGIVE, AVE_INC, DWEL_VAL, SD_INC,
    PARENT, CHILD, SPOUSE, SEX, FACSTAFF, ATHLTCS, OTHERACT
  )
head(wesbrook2)

# Usunięcie brakujących wartości
wesbrook2 <- wesbrook2 %>%
  filter_at(
    c("TOTLGIVE", "AVE_INC", "DWEL_VAL", "SD_INC"),
    ~ !is.na(.)
  )
sum(is.na(wesbrook2))

# Normalizacja zmiennych numerycznych
normalize <- function(x) {
  return((x - min(x)) / (max(x) - min(x)))
}

wesbrook2 <- wesbrook2 %>%
  mutate(TOTLGIVE = normalize(TOTLGIVE)) %>%
  mutate(AVE_INC = normalize(AVE_INC)) %>%
  mutate(DWEL_VAL = normalize(DWEL_VAL)) %>%
  mutate(SD_INC = normalize(SD_INC))

# Kodowanie zmiennych kategorycznych na 0/1
library(dummies)
wesbrook2 <- data.frame(wesbrook2)
wesbrook2 <- dummy.data.frame(
    data=wesbrook2, c("PARENT", "CHILD", "SPOUSE", "SEX", "FACSTAFF", "ATHLTCS", "OTHERACT"),
    sep = "_"
)

# Podział na zbiór treningowy i testowy
set.seed(123)
train_index <- createDataPartition(wesbrook2$WESBROOK, p = 0.75, list = FALSE)
wesbrook_train <- wesbrook2[train_index, ]
wesbrook_test <- wesbrook2[-train_index, ]

#-----------------------------------------------------------------------
#           Budowa modelu neuralnet
#-----------------------------------------------------------------------
library(neuralnet)

set.seed(123)
wesbrook_nn <- neuralnet(WESBROOK ~ ., data = wesbrook_train, hidden = c(20, 10), linear.output = FALSE)

plot(wesbrook_nn)

predicted_nn <- predict(wesbrook_nn, wesbrook_test)
predicted_nn <- encodeClassLabels(predicted_nn)
predicted_nn <- factor(predicted_nn, levels = c(1, 2), labels = c("N", "Y"))

confusionMatrix(wesbrook_test$WESBROOK, predicted_nn)

#-----------------------------------------------------------------------
#           Budowa modelu nnet
#-----------------------------------------------------------------------
library(nnet)

set.seed(123)
wesbrook_nnet <- nnet(
    WESBROOK ~ .,
    data = wesbrook_train,
    size = 25,
    decay = 5e-4,
    maxit = 2000
)

predicted_nnet <- predict(wesbrook_nnet, wesbrook_test, type = "class")
predicted_nnet <- factor(predicted_nnet, levels = c("Y", "N"))

confusionMatrix(predicted_nnet, wesbrook_test$WESBROOK)

#-----------------------------------------------------------------------
#           Budowa modelu RSNNS
#-----------------------------------------------------------------------
library(RSNNS)

# Przygotowanie danych do RSNNS
WE <- wesbrook_train[, -1]
WY <- decodeClassLabels(wesbrook_train$WESBROOK)

# Podział zbioru na uczący i testowy
wesbrook_split <- splitForTrainingAndTest(WE, WY, ratio = 0.3)

# Budowa modelu
set.seed(123)
wesbrook_mlp <- mlp(wesbrook_split$inputsTrain, wesbrook_split$targetsTrain, size = 15, learnFuncParams = 0.1, maxit = 50)

# Predykcja
predicted_mlp <- predict(wesbrook_mlp, wesbrook_split$inputsTest)
predicted_mlp <- round(predicted_mlp, 0)
predicted_mlp <- factor(encodeClassLabels(predicted_mlp))

length(predicted_mlp)
length(factor(encodeClassLabels(wesbrook_split$targetsTest)))
predicted_mlp
factor(encodeClassLabels(wesbrook_split$targetsTest))

# Ewaluacja
confusionMatrix(predicted_mlp, factor(encodeClassLabels(wesbrook_split$targetsTest)))
