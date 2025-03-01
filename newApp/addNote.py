import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout  # Add this import


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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_id = None  # Initialize note_id as None

        # Set the background color of the screen
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=20)

        # App bar at the top
        app_bar = BoxLayout(size_hint_y=None, height=60, orientation='horizontal', padding=[10, 5], spacing=10)

        # Back button (arrow) in the app bar
        back_button = Button(text="←", size_hint=(None, None), size=(50, 50), background_normal='', background_color=(0.1, 0.5, 0.9, 1), font_size=24, color=(1, 1, 1, 1))
        with back_button.canvas.before:
            Color(0.1, 0.5, 0.9, 1)  # Button background color
            RoundedRectangle(size=back_button.size, pos=back_button.pos, radius=[10,])  # Rounded corners
        back_button.bind(on_press=self.go_to_main_page)
        app_bar.add_widget(back_button)

        # Title label "Edit Note" in the app bar
        title_label = Label(text="Edit Note", bold=True, font_size=26, color=(1, 1, 1, 1), size_hint_x=0.8)
        app_bar.add_widget(title_label)

        # Add the app bar to the layout
        layout.add_widget(app_bar)

        # Form layout with ScrollView to allow scrolling for larger content
        scroll_layout = BoxLayout(orientation='vertical', spacing=15, padding=[20, 10])
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 120))
        
        # Note title input field
        self.title_input = TextInput(hint_text="Enter Note Title", size_hint_y=None, height=50, multiline=False, font_size=18, background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), hint_text_color=(0.5, 0.5, 0.5, 1), padding=(10, 10))
        scroll_layout.add_widget(self.title_input)

        # Note body input field
        self.body_input = TextInput(hint_text="Enter Note Body", size_hint_y=None, height=200, multiline=True, font_size=18, background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), hint_text_color=(0.5, 0.5, 0.5, 1), padding=(10, 10))
        scroll_layout.add_widget(self.body_input)

        # Save button
        save_button = Button(text="Save Note", size_hint=(None, None), size=(200, 50), font_size=20, background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1))
        with save_button.canvas.before:
            Color(0.2, 0.6, 1, 1)  # Button background color
            RoundedRectangle(size=save_button.size, pos=save_button.pos, radius=[10,])  # Rounded corners
        save_button.bind(on_press=self.save_edited_note)
        scroll_layout.add_widget(save_button)

        # Add the scroll view and form layout to the main layout
        scroll_view.add_widget(scroll_layout)
        layout.add_widget(scroll_view)

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

        # Title label in the app bar
        title_label = Label(text="Notes App", bold=True, font_size=26, color=(1, 1, 1, 1), size_hint_x=0.8)
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
            note_card = Button(text=f"{note['title']}", size_hint_y=None, height=50, background_color=(0.1, 0.5, 0.9, 1), color=(1, 1, 1, 1))
            with note_card.canvas.before:
                Color(0.1, 0.5, 0.9, 1)  # Button background color
                RoundedRectangle(size=note_card.size, pos=note_card.pos, radius=[10,])  # Rounded corners
            note_card.bind(on_press=self.go_to_edit_note_page(note['id']))  # Bind to edit note
            self.notes_layout.add_widget(note_card)

        layout.add_widget(self.notes_layout)

        # Add a floating circular "Add Note" button
        float_layout = FloatLayout()
        add_button = Button(size_hint=(None, None), size=(60, 60), background_normal='', background_color=(0.2, 0.6, 1, 1), pos_hint={'right': 0.95, 'bottom': 0.95})
        with add_button.canvas.before:
            Color(0.2, 0.6, 1, 1)  # Button background color
            RoundedRectangle(size=add_button.size, pos=add_button.pos, radius=[30,])  # Circular shape
        add_button.bind(on_press=self.go_to_second_page)

        # Add a plus sign inside the button
        plus_label = Label(text="+", font_size=30, color=(1, 1, 1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        add_button.add_widget(plus_label)

        float_layout.add_widget(add_button)
        layout.add_widget(float_layout)

        # Add the layout to the screen
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_edit_note_page(self, note_id):
        def inner(instance):
            # Pass the note_id to the edit screen and navigate
            edit_screen = self.manager.get_screen('edit_note_page')
            edit_screen.note_id = note_id
            edit_screen.load_note_data()  # Load the note data
            self.manager.current = 'edit_note_page'
        return inner

    def go_to_second_page(self, instance):
        self.manager.current = 'second_page'  # Switch to the second page to add a new note


class NotesApp(App):
    def build(self):
        # Create the ScreenManager
        screen_manager = ScreenManager()

        # Add screens to the ScreenManager
        screen_manager.add_widget(MainPage(name='main_page'))
        screen_manager.add_widget(EditNotePage(name='edit_note_page'))

        return screen_manager


if __name__ == '__main__':
    # Create the database if it doesn't exist
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY, title TEXT, body TEXT)''')
    conn.commit()
    conn.close()

    # Run the app
    NotesApp().run()