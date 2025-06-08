from datasets import load_dataset
from jiwer import wer
from transformers import pipeline


def transcribe_audio(audio_path):
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
    text = transcriber(audio_path)["text"]
    return text


def main():
    dataset = load_dataset("xbgoose/ravdess", split="train")
    item = dataset[0]
    reference = item["statement"]
    text = transcribe_audio(item["audio"])
    error = wer(reference, text)
    print(f"Współczynnik błędów: {error:.2%}")
    print(f"Referencja: {reference}")
    print(f"Transkrypcja: {text}")


if __name__ == "__main__":
    main()
