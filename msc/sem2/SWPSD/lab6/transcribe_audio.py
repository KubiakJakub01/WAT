from datasets import load_dataset
from transformers import pipeline


def transcribe_audio(audio_path):
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
    text = transcriber(audio_path)["text"]
    return text


def main():
    dataset = load_dataset("xbgoose/ravdess", split="train")
    item = dataset[0]
    text = transcribe_audio(item["audio"])
    print(text)


if __name__ == "__main__":
    main()
