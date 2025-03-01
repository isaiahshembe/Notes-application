import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout  # Add this import

# Constants
BACKGROUND_COLOR = (0.95, 0.95, 0.95, 1)  # Light gray background
BUTTON_COLOR = (0.2, 0.6, 1, 1)
DELETE_COLOR = (0.8, 0.2, 0.2, 1)
SHARE_COLOR = (0.3, 0.8, 0.3, 1)

# Database Functions
def create_db():
    """Create the database and notes table if it doesn't exist."""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY, title TEXT, body TEXT)''')
    conn.commit()
    conn.close()


def add_note_to_db(title, body):
    """Add a new note to the database."""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    conn.close()


def get_all_notes():
    """Retrieve all notes from the database."""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    notes = c.fetchall()
    conn.close()
    return notes


def delete_note_from_db(note_id):
    """Delete a note from the database by its ID."""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()


def update_note_in_db(note_id, title, body):
    """Update a note in the database by its ID."""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, body=? WHERE id=?", (title, body, note_id))
    conn.commit()
    conn.close()


# NoteCard Widget for displaying each note
class NoteCard(BoxLayout):
    def __init__(self, note_id, title, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = [10, 5]
        self.spacing = 10
        self.note_id = note_id

        # Title label
        self.title_label = Label(text=title, size_hint_x=0.6, font_size=18, color=(0, 0, 0, 1), halign='left', valign='middle')
        self.title_label.bind(size=self.title_label.setter('text_size'))  # Ensure text wraps
        self.add_widget(self.title_label)

        # Edit button
        edit_button = Button(text="Edit", size_hint_x=None, width=80, background_normal='', background_color=BUTTON_COLOR, color=(1, 1, 1, 1))
        edit_button.bind(on_press=self.edit_note)
        self.add_widget(edit_button)

        # Share button
        share_button = Button(text="Share", size_hint_x=None, width=80, background_normal='', background_color=SHARE_COLOR, color=(1, 1, 1, 1))
        share_button.bind(on_press=self.share_note)
        self.add_widget(share_button)

        # Delete button
        delete_button = Button(text="Delete", size_hint_x=None, width=80, background_normal='', background_color=DELETE_COLOR, color=(1, 1, 1, 1))
        delete_button.bind(on_press=self.delete_note)
        self.add_widget(delete_button)

    def edit_note(self, instance):
        """Switch to the edit screen and load the note for editing."""
        app = App.get_running_app()
        edit_screen = app.root.get_screen('second_page')
        edit_screen.load_note_for_editing(self.note_id, self.title_label.text)
        app.root.current = 'second_page'

    def share_note(self, instance):
        """Placeholder for sharing functionality."""
        print(f"Sharing note: {self.title_label.text}")

    def delete_note(self, instance):
        """Delete the note from the database and remove the card from the UI."""
        delete_note_from_db(self.note_id)
        self.parent.remove_widget(self)


# Main Page Screen: Displays notes
class MainPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        layout = BoxLayout(orientation='vertical')

        # App bar layout
        app_bar = BoxLayout(size_hint_y=None, height=50, orientation='horizontal', padding=[10, 5], spacing=10)

        # App bar label
        app_bar_label = Label(text="Notes App", bold=True, font_size=24, color=(0, 0, 0, 1))
        app_bar.add_widget(app_bar_label)

        # Refresh button
        refresh_button = Button(text="Refresh", size_hint=(None, None), size=(80, 40), background_normal='', background_color=BUTTON_COLOR, font_size=18, color=(1, 1, 1, 1))
        refresh_button.bind(on_press=self.refresh_notes)
        app_bar.add_widget(refresh_button)

        layout.add_widget(app_bar)

        # ScrollView for notes
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.notes_layout = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=[10, 10])
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))  # Allow scrolling

        # Display notes from DB
        self.display_notes()

        scroll_view.add_widget(self.notes_layout)
        layout.add_widget(scroll_view)

        # Add note button
        button_layout = AnchorLayout(anchor_x='right', anchor_y='bottom')
        button = Button(text="+", size_hint=(None, None), size=(80, 80), background_normal='', background_color=BUTTON_COLOR, font_size=40, color=(1, 1, 1, 1))
        button.bind(on_press=self.go_to_second_page)
        button_layout.add_widget(button)

        layout.add_widget(button_layout)

        # Add to the screen
        self.add_widget(layout)

    def go_to_second_page(self, instance):
        """Switch to the second page to add a new note."""
        self.manager.current = 'second_page'

    def refresh_notes(self, instance):
        """Refresh the list of notes."""
        self.notes_layout.clear_widgets()
        self.display_notes()

    def display_notes(self):
        """Display all notes from the database."""
        notes = get_all_notes()
        for note in notes:
            note_card = NoteCard(note_id=note[0], title=note[1])
            self.notes_layout.add_widget(note_card)


# Second Page Screen: For adding/editing a note
class SecondPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=20)

        # App bar with back button
        app_bar = BoxLayout(size_hint_y=None, height=60, orientation='horizontal', padding=[10, 5], spacing=10)
        back_button = Button(text="←", size_hint=(None, None), size=(50, 50), background_normal='', background_color=BUTTON_COLOR, font_size=24, color=(1, 1, 1, 1))
        back_button.bind(on_press=self.go_to_main_page)
        app_bar.add_widget(back_button)

        self.title_label = Label(text="Add Note", bold=True, font_size=26, color=(0, 0, 0, 1), size_hint_x=0.8)
        app_bar.add_widget(self.title_label)
        layout.add_widget(app_bar)

        # Form layout for note
        form_layout = BoxLayout(orientation='vertical', spacing=15, padding=[20, 10])
        self.title_input = TextInput(hint_text="Enter Note Title", size_hint_y=None, height=50, multiline=False, font_size=18)
        form_layout.add_widget(self.title_input)

        self.body_input = TextInput(hint_text="Enter Note Body", size_hint_y=None, height=200, multiline=True, font_size=18)
        form_layout.add_widget(self.body_input)

        save_button = Button(text="Save Note", size_hint=(None, None), size=(200, 50), font_size=20, background_normal='', background_color=BUTTON_COLOR, color=(1, 1, 1, 1))
        save_button.bind(on_press=self.save_note)
        form_layout.add_widget(save_button)

        layout.add_widget(form_layout)

        self.add_widget(layout)

    def go_to_main_page(self, instance):
        """Switch back to the main page."""
        self.manager.current = 'main_page'

    def save_note(self, instance):
        """Save the note to the database."""
        title = self.title_input.text
        body = self.body_input.text

        if title and body:
            add_note_to_db(title, body)
            print(f"Note Saved! Title: {title}, Body: {body}")

            # Clear the input fields
            self.title_input.text = ""
            self.body_input.text = ""

            # Refresh the MainPage
            self.manager.get_screen('main_page').refresh_notes()

            self.manager.current = 'main_page'  # Go back to main page
        else:
            print("Both title and body are required to save a note.")

    def load_note_for_editing(self, note_id, title):
        """Load a note for editing."""
        self.title_label.text = "Edit Note"
        self.title_input.text = title
        # You can load the body from the database here if needed.


# Main App
class MyApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # White background

        # Create the screen manager for navigation
        screen_manager = ScreenManager()

        # Create screens
        main_page = MainPage(name='main_page')
        second_page = SecondPage(name='second_page')

        # Add screens to the manager
        screen_manager.add_widget(main_page)
        screen_manager.add_widget(second_page)

        return screen_manager


if __name__ == '__main__':
    create_db()  # Ensure the database is created
    MyApp().run()