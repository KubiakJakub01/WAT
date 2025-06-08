import random
import tempfile

import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torchaudio
from datasets import load_dataset
from sklearn.metrics import confusion_matrix
from speechbrain.inference.interfaces import foreign_class
from tqdm import tqdm


def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True)
    plt.savefig("img/confusion_matrix.png")


def classify_emotion(item, classifier):
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        torchaudio.save(
            temp_file.name,
            torch.tensor(item["audio"]["array"]).unsqueeze(0),
            item["audio"]["sampling_rate"],
        )
        _, _, _, text_lab = classifier.classify_file(temp_file.name)
    return text_lab[0]


def main():
    dataset = load_dataset("xbgoose/ravdess", split="train")
    classifier = foreign_class(
        source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        pymodule_file="custom_interface.py",
        classname="CustomEncoderWav2vec2Classifier",
    )
    y_true = []
    y_pred = []
    dataset = dataset.select(random.sample(range(len(dataset)), 100))
    for item in tqdm(dataset, desc="Evaluating emotion recognition"):
        emotion_reference = item["emotion"]
        emotion_predicted = classify_emotion(item, classifier)
        y_true.append(emotion_reference)
        y_pred.append(emotion_predicted)
    plot_confusion_matrix(y_true, y_pred)


if __name__ == "__main__":
    main()
