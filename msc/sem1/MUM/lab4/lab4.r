# Prosze zaimportowac ,  zbi�r Wesbrook znajdujacy sie pod adresem # http://jolej.linuxpl.info/Wesbrook.csv
# Nast�pnie prosz� zbudowa� i sparametryzowa�  modele klasyfikacyjne z wykorzystaniem # nast�puj�cych metod 

# 1. K-najbli�szych s�siad�w
# 2. Naiwnego klasyfikatora Bayesa
# 3. Drzew klasyfikacyjnych
# 4. Las�w Losowych (Random Forest)
# 5. Algorytmu XGBoost
# 6. Metody SVM

# Dla ka�dego ze zbudowanych modeli prosz� wykona� ewaluacj� z wykorzystaniem :
# - macierzy pomy�ek
# - krzywej ROC
# - wsp�czynnika AUC

# Dla ka�dego z modeli prosz� wykona� k-krotn� walidacj� krzy�ow� oraz
# losow� walidacj� krzy�ow�

# Prosz� sformu�owa� wnioski

library(tidyverse)

#--------------------------------------------------------
#               Import danych
#--------------------------------------------------------

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

# Wybrane zmienne istotne (na podstawie analizy przeprowadzonej w pierwszych laboratoriach)
wesbrook2 <- wesbrook_data %>%
  select(
    WESBROOK, TOTLGIVE, AVE_INC, DWEL_VAL, SD_INC,
    PARENT, CHILD, SPOUSE, SEX, FACSTAFF, ATHLTCS, OTHERACT
  )
head(wesbrook2)

# Usunięcie rekordów z pustymi wartościami

wesbrook2 <- wesbrook2 %>%
  filter_at(
    c("TOTLGIVE", "AVE_INC", "DWEL_VAL", "SD_INC"),
    ~ !is.na(.)
  )

# Sprawdzenie czy usunięto rekordy z pustymi wartościami

sum(is.na(wesbrook2))

#--------------------------------------------------------
#               Normalizacja danych
#--------------------------------------------------------

normalize <- function(x) {
  return((x - min(x)) / (max(x) - min(x)))
}

wesbrook2 <- wesbrook2 %>%
  mutate(TOTLGIVE = normalize(TOTLGIVE)) %>%
  mutate(AVE_INC = normalize(AVE_INC)) %>%
  mutate(DWEL_VAL = normalize(DWEL_VAL)) %>%
  mutate(SD_INC = normalize(SD_INC))

#-------------------------------------------------------
# Kodowanie zero jedynkowe zmiennych typu factor
#-------------------------------------------------------

library(dummies)

wesbrook2 <- data.frame(wesbrook2)

# Podgląd statystyk opisowych
glimpse(wesbrook2)

wesbrook2 <- dummy.data.frame(
    data=wesbrook2, c("PARENT", "CHILD", "SPOUSE", "SEX", "FACSTAFF", "ATHLTCS", "OTHERACT"),
    sep = "_"
)


#-----------------------------------------------------------------------
#           Budowa modelu KNN
#-----------------------------------------------------------------------
library(class)

# Wydzielenie ze zbioru wesbrook2 zmiennej objaśnianej WESBROOK

wesbrook_labels <- wesbrook2 %>% select(WESBROOK)
knn_wesbrook2 <- wesbrook2 %>% select(-WESBROOK)

# Podział danych na zbiór treningowy i testowy

set.seed(123)
sample_index <-
  sample(nrow(knn_wesbrook2), round(nrow(knn_wesbrook2) * .75), replace = FALSE)
knn_wesbrook_train <- na.omit(knn_wesbrook2[sample_index, ])
knn_wesbrook_test <- na.omit(knn_wesbrook2[-sample_index, ])

wesbrook_labels_train <- as.factor(wesbrook_labels[sample_index, ])
wesbrook_labels_test <- as.factor(wesbrook_labels[-sample_index, ])

# Budowa modelu

wesbrook_pred_knn <- knn(
  train = knn_wesbrook_train,
  test = knn_wesbrook_test,
  cl = wesbrook_labels_train,
  k = 20
)


#-----------------------------------------------------------------------
#           Budowa modelu BayesNK
#-----------------------------------------------------------------------
library(e1071)

# Podział danych na zbiór treningowy i test
sample_index <-
  sample(nrow(wesbrook2), round(nrow(wesbrook2) * .75), replace = FALSE)
wesbrook_train <- wesbrook2[sample_index,]
wesbrook_test <- wesbrook2[-sample_index,]

# Budowa modelu

wesbrook_bayes <- naiveBayes(WESBROOK ~ ., data = wesbrook_train, laplace = 1)
wesbrook_pred_bayes <- predict(wesbrook_bayes, wesbrook_test, type = "class")

#------------------------------------------------------------------------
#                   Drzewa klasyfikacyjne
#------------------------------------------------------------------------
library(rpart)

wesbrook_dt <-
  rpart(
    WESBROOK ~ .,
    method = "class",
    data = wesbrook_train,
    cp = 0.0000001
  )
wesbrook_pred_dt <- predict(wesbrook_dt, wesbrook_test, type = "class")

#------------------------------------------------------------------------
#                   Lasy losowe
#------------------------------------------------------------------------
library(randomForest)

# Podział danych na zbiór treningowy i test
sample_index <-
  sample(nrow(wesbrook2), round(nrow(wesbrook2) * .75), replace = FALSE)
wesbrook_train <- wesbrook2[sample_index,]
wesbrook_test <- wesbrook2[-sample_index,]

# Budowa modelu

wesbrook_rf <- randomForest(WESBROOK ~ ., data = wesbrook_train, ntrees = 150)
wesbrook_pred_rf <- predict(wesbrook_rf, wesbrook_test, type = "class")

#------------------------------------------------------------------------
#                XGBoost
#------------------------------------------------------------------------
library(xgboost)

# Podział danych na zbiór treningowy i test
sample_index <-
  sample(nrow(wesbrook2), round(nrow(wesbrook2) * .75), replace = FALSE)
wesbrook_train <- wesbrook2[sample_index,]
wesbrook_test <- wesbrook2[-sample_index,]

# Budowa modelu

wesbrook_xgb <- train(
  WESBROOK ~ .,
  data = wesbrook_train,
  metric = "Accuracy",
  method = "xgbTree",
  trControl = trainControl(method = "none"),
  tuneGrid = expand.grid(
    nrounds = 100,
    max_depth = 6,
    eta = 0.3,
    gamma = 0.01,
    colsample_bytree = 1,
    min_child_weight = 1,
    subsample = 1
  )
)
wesbrook_pred_xgb <- predict(wesbrook_xgb, wesbrook_test, type = "raw")

#------------------------------------------------------------------------
#                SVM
#------------------------------------------------------------------------
library(e1071)

# Podział danych na zbiór treningowy i test
sample_index <-
  sample(nrow(wesbrook2), round(nrow(wesbrook2) * .75), replace = FALSE)
wesbrook_train <- wesbrook2[sample_index,]
wesbrook_test <- wesbrook2[-sample_index,]

# Budowa modelu

wesbrook_svm <- svm(WESBROOK ~ ., data = wesbrook_train, probability = TRUE)
wesbrook_pred_svm <- predict(wesbrook_svm, wesbrook_test, type = "class")

#--------------------------------------------------------------------------
#              Macierz pomyłek
#--------------------------------------------------------------------------

library(caret)
library(ROCR)

# KNN
confusionMatrix(wesbrook_pred_knn, wesbrook_labels_test)

# BayesNK
confusionMatrix(wesbrook_pred_bayes, wesbrook_test$WESBROOK)

# Drzewa klasyfikacyjne
confusionMatrix(wesbrook_pred_dt, wesbrook_test$WESBROOK)

# Lasy losowe
confusionMatrix(wesbrook_pred_rf, wesbrook_test$WESBROOK)

# XGBoost
confusionMatrix(wesbrook_pred_xgb, wesbrook_test$WESBROOK)

# SVM
confusionMatrix(wesbrook_pred_svm, wesbrook_test$WESBROOK)

#--------------------------------------------------------------------------
#              ROC Curve
#--------------------------------------------------------------------------

# KNN
wesbrook_pred_p <- as.numeric(wesbrook_pred_knn) - 1
roc_pred <- prediction(predictions = wesbrook_pred_p, labels = as.numeric(wesbrook_labels_test) - 1)
roc_perf <- performance(roc_pred, measure = "tpr", x.measure = "fpr")
plot(roc_perf, main = "ROC Curve KNN", col = "red", lwd = 3)
abline(a = 0, b = 1, lwd = 3, lty = 2, col = 1)
auc_perf <- performance(roc_pred, measure = "auc")
wesbrook_auc <- unlist(slot(auc_perf, "y.values"))
wesbrook_auc

# BayesNK
wesbrook_pred_p <- predict(wesbrook_bayes, wesbrook_test, type = "raw")
roc_pred <-
  prediction(
    predictions = wesbrook_pred_p[, "Y"],
    labels = wesbrook_test$WESBROOK
  )
roc_perf <- performance(roc_pred, measure = "tpr", x.measure = "fpr")
plot(roc_perf, main = "ROC Curve BayesNK", col = "red", lwd = 3)
abline(a = 0, b = 1, lwd = 3, lty = 2, col = 1)
auc_perf <- performance(roc_pred, measure = "auc")
wesbrook_auc <- unlist(slot(auc_perf, "y.values"))
wesbrook_auc

# Drzewa klasyfikacyjne
wesbrook_pred_p <- predict(wesbrook_dt, wesbrook_test, type = "prob")
roc_pred <-
  prediction(
    predictions = wesbrook_pred_p[, "Y"],
    labels = wesbrook_test$WESBROOK
  )
roc_perf <- performance(roc_pred, measure = "tpr", x.measure = "fpr")
plot(roc_perf, main = "ROC Curve Drzewa klasyfikacyjne", col = "red", lwd = 3)
abline(a = 0, b = 1, lwd = 3, lty = 2, col = 1)
auc_perf <- performance(roc_pred, measure = "auc")
wesbrook_auc <- unlist(slot(auc_perf, "y.values"))
wesbrook_auc

# Lasy losowe
wesbrook_pred_p <- predict(wesbrook_rf, wesbrook_test, type = "prob")
roc_pred <-
  prediction(
    predictions = wesbrook_pred_p[, "Y"],
    labels = wesbrook_test$WESBROOK
  )
roc_perf <- performance(roc_pred, measure = "tpr", x.measure = "fpr")
plot(roc_perf, main = "ROC Curve Lasy losowe", col = "red", lwd = 3)
abline(a = 0, b = 1, lwd = 3, lty = 2, col = 1)
auc_perf <- performance(roc_pred, measure = "auc")
wesbrook_auc <- unlist(slot(auc_perf, "y.values"))
wesbrook_auc

# XGBoost
wesbrook_pred_p <- predict(wesbrook_xgb, wesbrook_test, type = "prob")
roc_pred <-
  prediction(
    predictions = wesbrook_pred_p[, "Y"],
    labels = wesbrook_test$WESBROOK
  )
roc_perf <- performance(roc_pred, measure = "tpr", x.measure = "fpr")
plot(roc_perf, main = "ROC Curve XGBoost", col = "red", lwd = 3)
abline(a = 0, b = 1, lwd = 3, lty = 2, col = 1)
auc_perf <- performance(roc_pred, measure = "auc")
wesbrook_auc <- unlist(slot(auc_perf, "y.values"))
wesbrook_auc

# SVM
wesbrook_pred_p <- predict(wesbrook_svm, wesbrook_test, probability = TRUE)
wesbrook_pred_p <- attr(wesbrook_pred_p, "probabilities")
roc_pred <-
  prediction(
    predictions = wesbrook_pred_p[, "Y"],
    labels = wesbrook_test$WESBROOK
  )
roc_perf <- performance(roc_pred, measure = "tpr", x.measure = "fpr")
plot(roc_perf, main = "ROC Curve SVM", col = "red", lwd = 3)
abline(a = 0, b = 1, lwd = 3, lty = 2, col = 1)
auc_perf <- performance(roc_pred, measure = "auc")
wesbrook_auc <- unlist(slot(auc_perf, "y.values"))
wesbrook_auc

#------------------------------------------------------------------------------
#                   k-krotnej walidacji krzyzowej
#------------------------------------------------------------------------------
library(caret)

# Definicja kontroli treningu
train_control <- trainControl(method = "cv", number = 10)

# KNN
knn_cv <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "knn",
  trControl = train_control,
  tuneGrid = expand.grid(k = 20)
)
print(knn_cv)

# Naive Bayes
bayes_cv <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "nb",
  trControl = train_control
)
print(bayes_cv)

# Drzewa klasyfikacyjne
dt_cv <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "rpart",
  trControl = train_control,
  tuneLength = 10
)
print(dt_cv)

# Lasy losowe
rf_cv <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "rf",
  trControl = train_control,
  tuneLength = 10
)
print(rf_cv)

# XGBoost
xgb_cv <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "xgbTree",
  trControl = train_control,
  tuneLength = 10
)
print(xgb_cv)

# SVM
svm_cv <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "svmRadial",
  trControl = train_control,
  tuneLength = 10
)
print(svm_cv)

#----------------------------------------------------------------
#               Walidacji krzyżowa metoda losowa
#---------------------------------------------------------------
library(caret)

# Definicja kontroli treningu dla walidacji krzyżowej metodą losową
train_control_mc <- trainControl(method = "LGOCV", p = .1, number = 10)

# KNN
knn_mc <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "knn",
  trControl = train_control_mc,
  tuneGrid = expand.grid(k = 20)
)
print(knn_mc)

# Naive Bayes
bayes_mc <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "nb",
  trControl = train_control_mc
)
print(bayes_mc)

# Drzewa klasyfikacyjne
dt_mc <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "rpart",
  trControl = train_control_mc,
  tuneLength = 10
)
print(dt_mc)

# Drzewa losowe
rf_mc <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "rf",
  trControl = train_control_mc,
  tuneLength = 10
)
print(rf_mc)

# XGBoost
xgb_mc <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "xgbTree",
  trControl = train_control_mc,
  tuneLength = 10
)
print(xgb_mc)

# SVM
svm_mc <- train(
  WESBROOK ~ .,
  data = wesbrook2,
  method = "svmRadial",
  trControl = train_control_mc,
  tuneLength = 10
)
print(svm_mc)
