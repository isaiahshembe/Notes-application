import sqlite3
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window


# Function to add a note to the database
def add_note_to_db(title, body):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    conn.close()


class SecondPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the background color of the screen
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=20)

        # App bar at the top
        app_bar = BoxLayout(size_hint_y=None, height=60, orientation='horizontal', padding=[10, 5], spacing=10)
        app_bar.bg_color = (0.2, 0.6, 1, 1)  # Blue background for the app bar

        # Back button (arrow) in the app bar
        back_button = Button(text="←", size_hint=(None, None), size=(50, 50), background_normal='', background_color=(0.1, 0.5, 0.9, 1), font_size=24, color=(1, 1, 1, 1))
        back_button.bind(on_press=self.go_to_main_page)
        app_bar.add_widget(back_button)

        # Title label "Add Note" in the app bar
        title_label = Label(text="Add Note", bold=True, font_size=26, color=(0, 0, 0, 1), size_hint_x=0.8)
        app_bar.add_widget(title_label)

        # Add the app bar to the layout
        layout.add_widget(app_bar)

        # Form layout
        form_layout = BoxLayout(orientation='vertical', spacing=15, padding=[20, 10])

        # Note title input field
        self.title_input = TextInput(hint_text="Enter Note Title", size_hint_y=None, height=50, multiline=False, font_size=18, background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.title_input)

        # Note body input field
        self.body_input = TextInput(hint_text="Enter Note Body", size_hint_y=None, height=200, multiline=True, font_size=18, background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.body_input)

        # Save button
        save_button = Button(text="Save Note", size_hint=(None, None), size=(200, 50), font_size=20, background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1))
        save_button.bind(on_press=self.save_note)
        form_layout.add_widget(save_button)

        # Add the form layout to the main layout
        layout.add_widget(form_layout)

        # Add the layout to the screen
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_main_page(self, instance):
        self.manager.current = 'main_page'  # Switch to main page

    def save_note(self, instance):
        # Get the title and body of the note
        title = self.title_input.text
        body = self.body_input.text

        # Perform the note saving logic
        if title and body:
            # Save the note to the database
            add_note_to_db(title, body)
            print(f"Note Saved! Title: {title}, Body: {body}")

            # Clear the input fields after saving
            self.title_input.text = ""  # Clear the title input
            self.body_input.text = ""  # Clear the body input
        else:
            print("Both title and body are required to save a note.")
