import librosa
import numpy as np
import matplotlib.pyplot as plt


def plot_voice_features(audio_path):
    y, sr = librosa.load(audio_path)

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    librosa.display.waveshow(y, sr=sr)
    plt.title("Waveform")

    plt.subplot(1, 3, 2)
    stft = np.abs(librosa.stft(y))
    librosa.display.specshow(
        librosa.amplitude_to_db(stft), sr=sr, x_axis="time", y_axis="log"
    )
    plt.title("Spektrogram")

    plt.subplot(1, 3, 3)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma")
    plt.title("Chromagram")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_voice_features("data/sample.wav")
