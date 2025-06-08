import matplotlib.pyplot as plt
import streamlit as st
from transformers import pipeline


def predict_emotion(text):
    # Initialize emotion classifier pipeline
    classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=True,
    )

    # Get emotion predictions
    emotion_scores = classifier(text)[0]

    # Convert to dictionary of emotion:score pairs
    emotions = {item["label"]: item["score"] for item in emotion_scores}

    return emotions


def transcribe_audio(audio_file):
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
    text = transcriber(audio_file)["text"]
    return text


def main():
    st.title("Analizator Mowy")
    audio_file = st.file_uploader("Wgraj nagranie", type=["wav", "mp3"])

    if audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes)
        text = transcribe_audio(audio_bytes)

        st.subheader("Transkrypcja")
        st.write(text)

        st.subheader("Analiza emocji")
        emotions = predict_emotion(text)
        fig, ax = plt.subplots()
        ax.bar(emotions.keys(), emotions.values())
        st.pyplot(fig)


if __name__ == "__main__":
    main()
