import pyttsx3
import speech_recognition as sr


speech_on = True
engine = pyttsx3.init(driverName="espeak")
voices = engine.getProperty("voices")
# Find and set Polish voice if available
for voice in voices:
    if "polish" in voice.name.lower() or "pl" in voice.id.lower():
        engine.setProperty("voice", voice.id)
        break
# Set speech rate slightly slower for better Polish pronunciation
engine.setProperty("rate", 150)
recognizer = sr.Recognizer()
microphone = sr.Microphone()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def recognize_speech():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Słucham...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="pl-PL")
        confidence = 0.9  # Dla uproszczenia - recognize_google nie zwraca confidence
        print(f"ROZPOZNANO (wiarygodność: {confidence:0.3f}): '{text}'")
        return text, confidence
    except sr.UnknownValueError:
        print("Nie rozpoznano mowy")
        return None, 0
    except sr.RequestError as e:
        print(f"Błąd serwisu rozpoznawania mowy; {e}")
        return None, 0


def handle_command(text, confidence):
    global speech_on

    if confidence > 0.60:
        text = text.lower()
        if "stop" in text:
            speech_on = False
            speak("Do widzenia")
        elif "pomoc" in text:
            speak(
                "Składnia polecenia: Oblicz liczba plus liczba. Na przykład: dwa plus trzy"
            )
        elif "oblicz" in text:
            words = text.split()
            try:
                if "+" in text:
                    num1 = word_to_number(words[1])
                    num2 = word_to_number(words[3])
                    result = num1 + num2
                    print(f"\tOBLICZONO: {num1} + {num2} = {result}")
                    speak(f"Wynik działania to: {result}")
                elif "-" in text:
                    num1 = word_to_number(words[1])
                    num2 = word_to_number(words[3])
                    result = num1 - num2
                    print(f"\tOBLICZONO: {num1} - {num2} = {result}")
                    speak(f"Wynik działania to: {result}")
                elif "x" in text:
                    num1 = word_to_number(words[1])
                    num2 = word_to_number(words[3])
                    result = num1 * num2
                    print(f"\tOBLICZONO: {num1} * {num2} = {result}")
                    speak(f"Wynik działania to: {result}")
                elif "/" in text or "podziel" in text:
                    num1 = word_to_number(words[1])
                    num2 = word_to_number(words[3])
                    if num2 != 0:
                        result = num1 / num2
                        print(f"\tOBLICZONO: {num1} / {num2} = {result}")
                        speak(f"Wynik działania to: {result}")
                    else:
                        speak("Nie można dzielić przez zero")
            except (IndexError, ValueError):
                speak("Nieprawidłowe polecenie. Proszę powtórzyć")
    else:
        print("\tNISKI WSPÓŁCZYNNIK WIARYGODNOŚCI - powtórz polecenie")
        speak("Proszę powtórzyć")


def word_to_number(word):
    # Prosta konwersja słów na liczby
    numbers = {
        "zero": 0,
        "jeden": 1,
        "dwa": 2,
        "trzy": 3,
        "cztery": 4,
        "pięć": 5,
        "sześć": 6,
        "siedem": 7,
        "osiem": 8,
        "dziewięć": 9,
    }
    return numbers.get(word.lower(), int(word))


def main():
    speak("Witam w kalkulatorze")
    print("\nAby zakończyć działanie programu powiedz 'STOP'\n")

    while speech_on:
        text, confidence = recognize_speech()
        if text:
            handle_command(text, confidence)

    print("\tWCIŚNIJ <ENTER> aby wyjść z programu\n")
    input()


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
        input()
