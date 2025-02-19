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


# Function to get a note by its ID
def get_note_by_id(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("SELECT title, body FROM notes WHERE id=?", (note_id,))
    note = c.fetchone()
    conn.close()
    return note


# Function to update a note in the database
def update_note_in_db(note_id, title, body):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, body=? WHERE id=?", (title, body, note_id))
    conn.commit()
    conn.close()


class EditNotePage(Screen):
    def __init__(self, note_id, **kwargs):
        super().__init__(**kwargs)
        self.note_id = note_id  # Store the note_id to identify the note being edited

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

        # Title label "Edit Note" in the app bar
        title_label = Label(text="Edit Note", bold=True, font_size=26, color=(0, 0, 0, 1), size_hint_x=0.8)
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

        # Load the note data to edit
        self.load_note_data()

        # Save button
        save_button = Button(text="Save Note", size_hint=(None, None), size=(200, 50), font_size=20, background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1))
        save_button.bind(on_press=self.save_edited_note)
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

    def load_note_data(self):
        # Retrieve the note data by its ID
        note = get_note_by_id(self.note_id)
        if note:
            title, body = note
            self.title_input.text = title
            self.body_input.text = body

    def save_edited_note(self, instance):
        # Get the edited title and body
        title = self.title_input.text
        body = self.body_input.text

        if title and body:
            # Update the note in the database
            update_note_in_db(self.note_id, title, body)
            print(f"Note Updated! Title: {title}, Body: {body}")

            # Clear the input fields after saving
            self.title_input.text = ""
            self.body_input.text = ""
            self.manager.current = 'main_page'  # Go back to the main page
        else:
            print("Both title and body are required to save a note.")


class MainPage(Screen):
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

        # Title label in the app bar
        title_label = Label(text="Notes App", bold=True, font_size=26, color=(0, 0, 0, 1), size_hint_x=0.8)
        app_bar.add_widget(title_label)

        # Add the app bar to the layout
        layout.add_widget(app_bar)

        # Display notes layout
        self.notes_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 10])

        # Simulated Notes List (You will replace this with actual data from the database)
        self.notes = [
            {'id': 1, 'title': "Sample Note 1", 'body': "This is the first note."},
            {'id': 2, 'title': "Sample Note 2", 'body': "This is the second note."}
        ]

        # Add note cards to the layout (for now we just display some mock data)
        for note in self.notes:
            note_card = Button(text=f"{note['title']}", size_hint_y=None, height=50)
            note_card.bind(on_press=self.go_to_edit_note_page(note['id']))  # Bind to edit note
            self.notes_layout.add_widget(note_card)

        layout.add_widget(self.notes_layout)

        # Add the layout to the screen
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_edit_note_page(self, note_id):
        def inner(instance):
            # Pass the note_id to the edit screen and navigate
            self.manager.current = 'edit_note_page'
            self.manager.get_screen('edit_note_page').note_id = note_id
        return inner
