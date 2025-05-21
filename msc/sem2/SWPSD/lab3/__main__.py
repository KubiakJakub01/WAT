import queue
import re
import tkinter as tk
from threading import Thread
from tkinter import messagebox, ttk

import pyttsx3
import speech_recognition as sr


class VoiceFormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Formularz głosowy")
        self.root.geometry("600x500")

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "pl" in voice.languages or "Polish" in voice.name:
                self.engine.setProperty("voice", voice.id)
                break
        else:
            print("Nie znaleziono polskiego głosu, używam domyślnego.")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.command_queue = queue.Queue()
        self.speech_active = False
        self.current_field = None

        self.form_data = {
            "name": "",
            "email": "",
            "phone": "",
            "birth_date": "",
            "city": "",
        }

        self.load_srgs_grammar()
        self.create_ui()

        self.process_thread = Thread(target=self.process_commands, daemon=True)
        self.process_thread.start()

    def load_srgs_grammar(self):
        self.grammar = {
            "root": {
                "name": r"(imię|nazwisko|imię i nazwisko) (.*)",
                "email": r"(e-mail|email|mail) (.*)",
                "phone": r"(telefon|numer telefonu|numer) (.*)",
                "birth_date": r"(data urodzenia|urodziny|data) (.*)",
                "city": r"(miasto|miejscowość) (.*)",
                "submit": r"(wyślij|wyślij formularz|zapisz)",
            },
            "validation": {
                "email": r"[^@]+@[^@]+\.[^@]+",
                "phone": r"\+?[\d\s-]+",
                "birth_date": r"\d{2}-\d{2}-\d{4}",
            },
        }

    def create_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Formularz głosowy", font=("Arial", 16)).grid(
            row=0, column=0, columnspan=2, pady=10
        )

        fields = [
            ("Imię i nazwisko", "name"),
            ("Adres e-mail", "email"),
            ("Numer telefonu", "phone"),
            ("Data urodzenia (dd-mm-rrrr)", "birth_date"),
            ("Miasto zamieszkania", "city"),
        ]

        self.entries = {}

        for i, (label, field_name) in enumerate(fields, start=1):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)
            entry.bind("<FocusIn>", lambda e, fn=field_name: self.set_current_field(fn))
            self.entries[field_name] = entry

        voice_frame = ttk.Frame(main_frame)
        voice_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(
            voice_frame, text="Start nasłuchiwania", command=self.start_listening
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            voice_frame,
            text="Stop nasłuchiwania",
            command=self.stop_listening,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Wyślij formularz", command=self.submit_form).grid(
            row=7, column=0, columnspan=2, pady=20
        )

        self.status_label = ttk.Label(
            main_frame, text="Gotowy do wprowadzania danych", wraplength=400
        )
        self.status_label.grid(row=8, column=0, columnspan=2)

        main_frame.columnconfigure(1, weight=1)

    def set_current_field(self, field_name):
        self.current_field = field_name

    def start_listening(self):
        if not self.speech_active:
            self.speech_active = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_status("Nasłuchiwanie... Mów wyraźnie")
            self.speak("Nasłuchuję, możesz wprowadzać dane")
            listen_thread = Thread(target=self.listen_loop, daemon=True)
            listen_thread.start()

    def stop_listening(self):
        if self.speech_active:
            self.speech_active = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.update_status("Nasłuchiwanie zatrzymane")

    def listen_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.speech_active:
                try:
                    audio = self.recognizer.listen(
                        source, timeout=1, phrase_time_limit=5
                    )
                    command = self.recognizer.recognize_google(
                        audio, language="pl-PL"
                    ).lower()
                    self.command_queue.put(command)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.command_queue.put("nie rozumiem")
                except Exception as e:
                    self.command_queue.put(f"błąd: {str(e)}")

    def process_commands(self):
        while True:
            try:
                command = self.command_queue.get(timeout=0.1)
                self.root.after(0, self.process_command, command)
            except queue.Empty:
                continue

    def process_command(self, command):
        self.update_status(f"Rozpoznano: {command}")

        if "nie rozumiem" in command or "błąd" in command:
            self.speak("Nie zrozumiałem, powtórz proszę")
            return

        if any(word in command for word in ["wyślij", "wyślij formularz", "zapisz"]):
            self.submit_form()
            return

        processed = False

        for field, pattern in self.grammar["root"].items():
            if field == "submit":
                continue
            match = re.match(pattern, command)
            if match:
                value = match.group(2).strip()
                self.update_field(field, value)
                processed = True
                break

        if not processed and self.current_field:
            self.update_field(self.current_field, command)

    def update_field(self, field_name, value):
        self.form_data[field_name] = value
        self.entries[field_name].delete(0, tk.END)
        self.entries[field_name].insert(0, value)

        field_labels = {
            "name": "Imię i nazwisko",
            "email": "Adres e-mail",
            "phone": "Numer telefonu",
            "birth_date": "Data urodzenia",
            "city": "Miasto zamieszkania",
        }
        self.speak(f"Wprowadzono {field_labels[field_name]}: {value}")

    def validate_field(self, field_name, value):
        if field_name in self.grammar["validation"]:
            pattern = self.grammar["validation"][field_name]
            if not re.fullmatch(pattern, value):
                return False
        return bool(value.strip())

    def submit_form(self):
        for field_name, entry in self.entries.items():
            self.form_data[field_name] = entry.get()

        missing_fields = []
        field_labels = {
            "name": "Imię i nazwisko",
            "email": "Adres e-mail",
            "phone": "Numer telefonu",
            "birth_date": "Data urodzenia",
            "city": "Miasto zamieszkania",
        }

        for field_name, value in self.form_data.items():
            if not self.validate_field(field_name, value):
                missing_fields.append(field_labels[field_name])

        if missing_fields:
            message = "Proszę uzupełnić następujące pola: " + ", ".join(missing_fields)
            self.speak(message)
            self.update_status(message)
            messagebox.showwarning("Niekompletne dane", message)
        else:
            summary = (
                "Podsumowanie formularza:\n\n"
                f"Imię i nazwisko: {self.form_data['name']}\n"
                f"Adres e-mail: {self.form_data['email']}\n"
                f"Numer telefonu: {self.form_data['phone']}\n"
                f"Data urodzenia: {self.form_data['birth_date']}\n"
                f"Miasto zamieszkania: {self.form_data['city']}"
            )
            self.speak("Formularz został wypełniony. Dziękujemy!")
            self.update_status("Formularz wysłany pomyślnie")
            messagebox.showinfo("Podsumowanie", summary)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def update_status(self, text):
        self.status_label.config(text=text)

    def on_closing(self):
        self.speech_active = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceFormApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
