

import random
import requests
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0.4, 0.4, 0.4, 1)

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
        {"question": "Wie schnell ist der Rekord im Skifahren?", "answers": ["254 km/h", "182 km/h", "301 km/h"], "correct": "254 km/h"},
        {"question": "Welches Land gilt als Ursprungsland des Skifahrens?", "answers": ["Norwegen", "Frankreich", "Österreich"], "correct": "Norwegen"},
        {"question": "Was ist der längste Skisprung der Welt?", "answers": ["91m", "191m", "291m"], "correct": "291m"},
        {"question": "Was ist die höchste erreichte Geschwindigkeit auf Skiern?", "answers": ["107 km/h", "198 km/h", "255 km/h"], "correct": "255 km/h"},
        {"question": "Welcher ist der größte Skiort der Welt? (Nach Pistenkilometern)", "answers": ["Les 3 Vallées", "Zermatt", "Les portes du Soleil"], "correct": "Les 3 Vallées"}
    ]
}

# Version der App, die du anpassen musst, wenn du neue Version rausbringst
CURRENT_VERSION = "1.0.1"

# Link zur update.json auf GitHub (muss angepasst werden)
UPDATE_JSON_URL = "https://raw.githubusercontent.com/t-butkus/Quizgame_funfacts/main/update.json"

class QuizApp(App):
    def build(self):
        self.score = 0
        self.selected_category = "Physik"
        self.question_pool = {cat: questions_data[cat][:] for cat in questions_data}

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Punkteanzeige
        self.score_label = Label(text=f"Punkte: {self.score}", font_size=30, color=(1, 1, 1, 1))
        self.layout.add_widget(self.score_label)

        # Kategorie-Auswahl in stylischer dunkler Box
        category_box = BoxLayout(orientation='vertical', size_hint=(None, None), size=(320, 110), padding=10, spacing=8)
        with category_box.canvas.before:
            Color(0.5, 0.7, 0.8, 1)  # Box Farbe (helles Blau)
            self.rect = RoundedRectangle(size=category_box.size, pos=category_box.pos, radius=[18])
        category_box.bind(size=lambda instance, value: setattr(self.rect, 'size', value))
        category_box.bind(pos=lambda instance, value: setattr(self.rect, 'pos', value))

        self.category_label = Label(
            text="Kategorie:",
            font_size=28,
            color=(1, 1, 1, 1),  # Helles Blau
            size_hint=(1, 0.4),
            bold=True
        )
        category_box.add_widget(self.category_label)

        self.category_spinner = Spinner(
            text=self.selected_category,
            values=list(questions_data.keys()),
            size_hint=(1, 0.5),
            font_size=22,
            background_color=(0.12, 0.12, 0.18, 0.2),  # gleiche Farbe wie Box
            color=(1, 1, 1, 1),  # Weißer Text
            border=(22, 22, 22, 22)
        )
        self.category_spinner.bind(text=self.set_category)
        category_box.add_widget(self.category_spinner)

        category_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        category_anchor.add_widget(category_box)
        self.layout.add_widget(category_anchor)

        # Frage-Label
        self.question_label = Label(text="", font_size=40, color=(1, 1, 1, 1), halign='center', valign='middle')
        self.question_label.bind(size=self.question_label.setter('text_size'))
        self.layout.add_widget(self.question_label)

        # Antwort-Buttons
        self.answer_buttons = []
        for _ in range(3):
            btn = Button(size_hint=(1, 0.2), background_color=(0.3, 0.7, 1, 1), color=(1, 1, 1, 1))
            btn.bind(on_press=self.check_answer)
            self.answer_buttons.append(btn)
            self.layout.add_widget(btn)

        # Feedback Label
        self.feedback_label = Label(text="", font_size=30, color=(1, 1, 1, 1))
        self.layout.add_widget(self.feedback_label)

        # Nächste Frage Button
        self.next_button = Button(text="Nächste Frage", size_hint=(1, 0.2), background_color=(0.2, 0.7, 0.3, 1), color=(1, 1, 1, 1))
        self.next_button.bind(on_press=self.next_question)
        self.layout.add_widget(self.next_button)

        # Update-Button (unsichtbar, erscheint nur wenn Update da ist)
        self.update_button = Button(
            text="Neue Version verfügbar! Jetzt updaten",
            size_hint=(1, 0.5),
            background_color=(1, 0.5, 0.2, 1),
            color=(1, 1, 1, 1),
            opacity=0,
            disabled=False
        )
        self.update_button.bind(on_press=self.open_update_link)
        self.layout.add_widget(self.update_button)

        
        #self.update_button.opacity = 1  # Button immer sichtbar machen
        #self.update_button.disabled = False

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
            self.answer_buttons[i].disabled = False  # Buttons aktivieren

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

        # Alle Antwort-Buttons deaktivieren
        for btn in self.answer_buttons:
            btn.disabled = True

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
