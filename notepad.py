from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox

import sqlite3

# Database setup
def create_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (title TEXT, body TEXT)''')
    conn.commit()
    conn.close()

def add_note_to_db(title, body):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    conn.close()

def get_notes_from_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("SELECT title, body FROM notes")
    notes = c.fetchall()
    conn.close()
    return notes


# Main Page
class MainPage(Screen):
    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)

        # Create a BoxLayout to hold everything
        layout = BoxLayout(orientation='vertical')

        # Create a canvas to set background color
        with layout.canvas.before:
            Color(1, 1, 1, 1)  # White background color
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)

        # Set up widgets
        self.note_list = GridLayout(cols=1, spacing=10, padding=10)
        self.update_notes()

        self.add_note_button = Button(text="Add Note", size_hint=(None, None), size=(200, 50))
        self.add_note_button.bind(on_release=self.go_to_second_page)

        # Adding widgets to the layout
        layout.add_widget(self.add_note_button)
        layout.add_widget(self.note_list)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_notes(self):
        self.note_list.clear_widgets()  # Clear previous notes

        notes = get_notes_from_db()
        for title, body in notes:
            note = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            note.add_widget(Label(text=title, size_hint_x=0.8))
            note.add_widget(Button(text="View", size_hint_x=0.2, on_release=lambda btn, t=title, b=body: self.view_note(t, b)))
            self.note_list.add_widget(note)

    def view_note(self, title, body):
        self.manager.current = 'second_page'
        self.manager.get_screen('second_page').set_note_details(title, body)

    def go_to_second_page(self, instance):
        self.manager.current = 'second_page'


# Second Page (Add/Update Note)
class SecondPage(Screen):
    def __init__(self, **kwargs):
        super(SecondPage, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20)

        self.title_input = TextInput(hint_text="Note Title", multiline=False)
        self.body_input = TextInput(hint_text="Note Body", multiline=True)

        save_button = Button(text="Save", size_hint=(None, None), size=(200, 50))
        save_button.bind(on_release=self.save_note)

        layout.add_widget(self.title_input)
        layout.add_widget(self.body_input)
        layout.add_widget(save_button)

        self.add_widget(layout)

    def set_note_details(self, title, body):
        self.title_input.text = title
        self.body_input.text = body

    def save_note(self, instance):
        title = self.title_input.text
        body = self.body_input.text

        if title and body:
            add_note_to_db(title, body)
            self.manager.current = 'main_page'  # Go back to main page to see the new note


# Main App
class NotesApp(App):
    def build(self):
        create_db()

        sm = ScreenManager()
        sm.add_widget(MainPage(name='main_page'))
        sm.add_widget(SecondPage(name='second_page'))

        return sm


# Run the app
if __name__ == '__main__':
    NotesApp().run()
