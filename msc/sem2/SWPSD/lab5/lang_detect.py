from langdetect import detect, DetectorFactory

# For consistent results (optional)
DetectorFactory.seed = 0


def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        return "Nie można określić języka"


# Example usage
text = input("Wprowadź tekst do analizy: ")
language = detect_language(text)
print(f"Wykryty język: {language}")
