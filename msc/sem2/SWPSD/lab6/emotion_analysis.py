import librosa
import numpy as np
from datasets import load_dataset
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from tqdm import tqdm


def extract_features(y, sr):
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    return np.vstack([mfcc, chroma]).mean(axis=1)


def train_emotion_model(features, labels):
    model = SVC(random_state=42)
    model.fit(features, labels)
    return model


def predict_emotion(model, features):
    return model.predict(features)


def main():
    dataset = load_dataset("xbgoose/ravdess", split="train")

    features_list = []
    labels_list = []
    for item in tqdm(dataset):
        audio_data = item["audio"]
        y = audio_data["array"]
        sr = audio_data["sampling_rate"]
        features = extract_features(y, sr)
        features_list.append(features)
        labels_list.append(item["emotion"])

    X_train, X_test, y_train, y_test = train_test_split(
        features_list, labels_list, test_size=0.2, random_state=42
    )

    model = train_emotion_model(X_train, y_train)

    predictions = predict_emotion(model, X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Model Accuracy: {accuracy * 100:.2f}%")


if __name__ == "__main__":
    main()
