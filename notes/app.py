import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput

# Constants
BACKGROUND_COLOR = (0.95, 0.95, 0.95, 1)  # Light gray background
BUTTON_COLOR = (0.2, 0.6, 1, 1)
DELETE_COLOR = (0.8, 0.2, 0.2, 1)
SHARE_COLOR = (0.3, 0.8, 0.3, 1)

# Database Functions
def create_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY, title TEXT, body TEXT)''')
    conn.commit()
    conn.close()


def add_note_to_db(title, body):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    conn.close()


def get_all_notes():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    notes = c.fetchall()
    conn.close()
    return notes


def delete_note_from_db(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

def update_note_in_db(note_id, title, body):
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

        # Edit button (circular)
        edit_button = Button(text="Edit", size_hint_x=None, width=50, height=50, background_normal='', 
                             background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1), 
                             border=[25, 25, 25, 25])  # Circular button
        edit_button.bind(on_press=self.edit_note)
        self.add_widget(edit_button)

        # Share button (circular)
        share_button = Button(text="Share", size_hint_x=None, width=50, height=50, background_normal='', 
                              background_color=(0.3, 0.8, 0.3, 1), color=(1, 1, 1, 1), 
                              border=[25, 25, 25, 25])  # Circular button
        share_button.bind(on_press=self.share_note)
        self.add_widget(share_button)

        # Delete button (circular)
        delete_button = Button(text="Delete", size_hint_x=None, width=50, height=50, background_normal='', 
                               background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), 
                               border=[25, 25, 25, 25])  # Circular button
        delete_button.bind(on_press=self.delete_note)
        self.add_widget(delete_button)

    def edit_note(self, instance):
        print(f"Editing note: {self.title_label.text}")
        # You can implement functionality to edit the note here

    def share_note(self, instance):
        print(f"Sharing note: {self.title_label.text}")
        # You can implement functionality to share the note here

    def delete_note(self, instance):
        print(f"Deleting note: {self.title_label.text}")
        delete_note_from_db(self.note_id)  # Delete from database
        self.parent.remove_widget(self)  # Remove the card from the list

# Main Page Screen: Displays notes
class MainPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        layout = BoxLayout(orientation='vertical')

        # App bar layout
        app_bar = BoxLayout(size_hint_y=None, height=50, orientation='horizontal')
        app_bar.bg_color = (1, 1, 1, 1)  # White background for the app bar

        # App bar label
        app_bar_label = Label(text="Notes App", bold=True, font_size=24, size_hint=(None, None), color=(0, 0, 0, 1))
        app_bar_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        app_bar_layout.add_widget(app_bar_label)
        app_bar.add_widget(app_bar_layout)

        # Refresh button
        refresh_button = Button(text="Refresh", size_hint=(None, None), size=(80, 40), background_normal='', background_color=(0.2, 0.6, 1, 1), font_size=18, color=(1, 1, 1, 1))
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
        button = Button(text="+", size_hint=(None, None), size=(80, 80), background_normal='', background_color=(0.2, 0.6, 1, 1), font_size=40, color=(1, 1, 1, 1))
        button.bind(on_press=self.go_to_second_page)
        button_layout.add_widget(button)

        layout.add_widget(button_layout)

        # Add to the screen
        self.add_widget(layout)

    def go_to_second_page(self, instance):
        self.manager.current = 'second_page'  # Go to second page to add note

    def refresh_notes(self, instance):
        # Clear the current notes
        self.notes_layout.clear_widgets()

        # Reload notes from the database
        self.display_notes()

    def display_notes(self):
        notes = get_all_notes()
        for note in notes:
            note_card = NoteCard(note_id=note[0], title=note[1])
            self.notes_layout.add_widget(note_card)


# Second Page Screen: For adding a new note
class SecondPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=20)

        # App bar with back button
        app_bar = BoxLayout(size_hint_y=None, height=60, orientation='horizontal', padding=[10, 5], spacing=10)
        back_button = Button(text="←", size_hint=(None, None), size=(50, 50), background_normal='', background_color=(0.1, 0.5, 0.9, 1), font_size=24, color=(1, 1, 1, 1))
        back_button.bind(on_press=self.go_to_main_page)
        app_bar.add_widget(back_button)

        title_label = Label(text="Add Note", bold=True, font_size=26, color=(0, 0, 0, 1), size_hint_x=0.8)
        app_bar.add_widget(title_label)
        layout.add_widget(app_bar)

        # Form layout for note
        form_layout = BoxLayout(orientation='vertical', spacing=15, padding=[20, 10])
        self.title_input = TextInput(hint_text="Enter Note Title", size_hint_y=None, height=50, multiline=False, font_size=18)
        form_layout.add_widget(self.title_input)

        self.body_input = TextInput(hint_text="Enter Note Body", size_hint_y=None, height=200, multiline=True, font_size=18)
        form_layout.add_widget(self.body_input)

        save_button = Button(text="Save Note", size_hint=(None, None), size=(200, 50), font_size=20, background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1))
        save_button.bind(on_press=self.save_note)
        form_layout.add_widget(save_button)

        layout.add_widget(form_layout)

        self.add_widget(layout)

    def go_to_main_page(self, instance):
        self.manager.current = 'main_page'  # Switch back to main page

    def save_note(self, instance):
        title = self.title_input.text
        body = self.body_input.text

        if title and body:
            add_note_to_db(title, body)
            print(f"Note Saved! Title: {title}, Body: {body}")

            # Clear the input fields
            self.title_input.text = ""
            self.body_input.text = ""
            self.manager.get_screen('main_page').refresh_notes()  # Refresh the main page

            self.manager.current = 'main_page'  # Go back to main page
        else:
            print("Both title and body are required to save a note.")


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
