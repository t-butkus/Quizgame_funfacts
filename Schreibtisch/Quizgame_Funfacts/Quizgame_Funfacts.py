

import random
import requests
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

Window.clearcolor = (0.12, 0.12, 0.12, 1)

# Original Fragen
questions_data = {
    "Physik": [
        {"question": "Wie lange braucht Licht von der Sonne zur Erde?", "answers": ["8 Minuten", "1 Sekunde", "8 Stunden"], "correct": "8 Minuten"},
        {"question": "Was ist die Lichtgeschwindigkeit?", "answers": ["300.000 km/s", "30.000 km/s", "3.000 km/s"], "correct": "300.000 km/s"},
        {"question": "Was ist ein Proton?", "answers": ["Positiv geladen", "Negativ geladen", "Neutral"], "correct": "Positiv geladen"}
    ],
    "Karate": [
        {"question": "Was bedeutet Karate auf Japanisch?", "answers": ["Leere Hand", "Kampfsport", "Schwarzer Gürtel"], "correct": "Leere Hand"},
        {"question": "Welche Farbe hat der Anfänger-Gürtel?", "answers": ["Weiß", "Schwarz", "Grün"], "correct": "Weiß"},
        {"question": "Welche Körperhaltung ist typisch?", "answers": ["Zenkutsu-Dachi", "Lotussitz", "Sitzstellung"], "correct": "Zenkutsu-Dachi"}
    ],
    "Ski": [
        {"question": "Wie schnell ist der Rekord im Skifahren?", "answers": ["254 km/h", "180 km/h", "300 km/h"], "correct": "254 km/h"},
        {"question": "Welches Land gilt als Ursprungsland des Skifahrens?", "answers": ["Norwegen", "Schweiz", "Österreich"], "correct": "Norwegen"},
        {"question": "Wie nennt man das parallele Kurvenfahren?", "answers": ["Carving", "Sliding", "Powdern"], "correct": "Carving"}
    ]
}

# Version der App, die du anpassen musst, wenn du neue Version rausbringst
CURRENT_VERSION = "1.0.0"

# Link zur update.json auf GitHub (muss angepasst werden)
UPDATE_JSON_URL = "https://raw.githubusercontent.com/t-butkus/Quiz_funfacts/main/update.json"

class QuizApp(App):
    def build(self):
        self.score = 0
        self.selected_category = "Physik"
        self.question_pool = {cat: questions_data[cat][:] for cat in questions_data}

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Punkteanzeige
        self.score_label = Label(text=f"Punkte: {self.score}", font_size=18, color=(1, 1, 1, 1))
        self.layout.add_widget(self.score_label)

        # Kategorie-Auswahl
        self.category_spinner = Spinner(
            text=self.selected_category,
            values=list(questions_data.keys()),
            size_hint=(1, 0.2),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.category_spinner.bind(text=self.set_category)
        self.layout.add_widget(self.category_spinner)

        # Frage-Label
        self.question_label = Label(text="", font_size=20, color=(1, 1, 1, 1), halign='center', valign='middle')
        self.question_label.bind(size=self.question_label.setter('text_size'))
        self.layout.add_widget(self.question_label)

        # Antwort-Buttons
        self.answer_buttons = []
        for _ in range(3):
            btn = Button(size_hint=(1, 0.2), background_color=(0.1, 0.5, 0.8, 1), color=(1, 1, 1, 1))
            btn.bind(on_press=self.check_answer)
            self.answer_buttons.append(btn)
            self.layout.add_widget(btn)

        # Feedback Label
        self.feedback_label = Label(text="", font_size=18, color=(1, 1, 1, 1))
        self.layout.add_widget(self.feedback_label)

        # Nächste Frage Button
        self.next_button = Button(text="Nächste Frage", size_hint=(1, 0.2), background_color=(0.2, 0.7, 0.3, 1), color=(1, 1, 1, 1))
        self.next_button.bind(on_press=self.next_question)
        self.layout.add_widget(self.next_button)

        # Update-Button (unsichtbar, erscheint nur wenn Update da ist)
        self.update_button = Button(
            text="Neue Version verfügbar! Jetzt updaten",
            size_hint=(1, 0.2),
            background_color=(1, 0.5, 0.2, 1),
            color=(1, 1, 1, 1),
            opacity=0,
            disabled=True
        )
        self.update_button.bind(on_press=self.open_update_link)
        self.layout.add_widget(self.update_button)

        self.update_link = None

        self.next_question()
        self.check_for_update()

        return self.layout

    def set_category(self, spinner, text):
        self.selected_category = text
        self.next_question()

    def next_question(self, instance=None):
        # Pool zurücksetzen, wenn leer
        if not self.question_pool[self.selected_category]:
            self.question_pool[self.selected_category] = questions_data[self.selected_category][:]
        # Neue Frage holen und aus Pool entfernen
        self.current_question = random.choice(self.question_pool[self.selected_category])
        self.question_pool[self.selected_category].remove(self.current_question)

        self.question_label.text = self.current_question["question"]

        answers = self.current_question["answers"][:]
        random.shuffle(answers)
        for i, ans in enumerate(answers):
            self.answer_buttons[i].text = ans

        self.feedback_label.text = ""

    def check_answer(self, instance):
        if instance.text == self.current_question["correct"]:
            self.feedback_label.text = "✅ Richtig!"
            self.feedback_label.color = (0, 1, 0, 1)
            self.score += 1
        else:
            self.feedback_label.text = f"❌ Falsch! Richtige Antwort: {self.current_question['correct']}"
            self.feedback_label.color = (1, 0, 0, 1)
        self.score_label.text = f"Punkte: {self.score}"

    def check_for_update(self):
        try:
            r = requests.get(UPDATE_JSON_URL, timeout=5)
            data = r.json()
            if data["version"] != CURRENT_VERSION:
                self.update_link = data["apk_url"]
                self.update_button.opacity = 1
                self.update_button.disabled = False
        except Exception:
            pass  # Fehler ignorieren (kein Internet oder JSON-Problem)

    def open_update_link(self, instance):
        if self.update_link:
            webbrowser.open(self.update_link)

if __name__ == '__main__':
    QuizApp().run()
