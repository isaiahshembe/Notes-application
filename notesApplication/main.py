from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from text_widget import NoteWidget
from menu import Menu
from add_note import AddNoteScreen
from edit_note import EditNoteScreen
from share_note import ShareNoteScreen
from kivy.uix.screenmanager import ScreenManager
import sqlite3
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.button import MDRaisedButton

class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.cursor = None
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('notes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                body TEXT
            )
        ''')
        self.conn.commit()

    def build(self):
        self.screen_manager = ScreenManager()
        
        # Create the main screen
        self.main_screen = MDScreen(name='main')
        
        # Create the top app bar (Fixed at the top)
        top_app_bar = MDTopAppBar(
            title='Notes App',
            anchor_title='left',
            size_hint_y=None,
            height=56,
            pos_hint={"top": 1}  # Fix it at the top
        )
        
        # Create a menu instance
        self.menu = Menu(self.open_add_note_screen)
        
        # Set up the menu button
        top_app_bar.left_action_items = [['menu', lambda x: self.menu.open_menu(x)]]

        # Main layout (content should start below the app bar)
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={"top": 0.87},  # Start right below the app bar
            padding=(12, 0, 12, 12)  # Add padding around the content
        )

        # Add a background with rounded corners and color
        with content_layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Set background color (light gray)
            self.rect = RoundedRectangle(size=(content_layout.width, content_layout.height), 
                                         pos=content_layout.pos, radius=[10, 10, 10, 10])

        content_layout.bind(size=self.update_rect, pos=self.update_rect)  # Update the background size and position
        
        # ScrollView for notes
        scroll_view = ScrollView(size_hint=(1, 1))
        self.notes_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)  # Add spacing between notes
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))  # Dynamically adjust height

        # Load notes from database
        self.load_notes()

        scroll_view.add_widget(self.notes_layout)
        content_layout.add_widget(scroll_view)

        # Add widgets to the main screen
        self.main_screen.add_widget(content_layout)  # Scrollable content
        self.main_screen.add_widget(top_app_bar)  # Fixed App Bar

        # Create the add note screen
        self.add_note_screen = AddNoteScreen(self.add_note_callback, self.screen_manager, self.conn)
        self.add_note_screen.name = 'add_note'  # Set the screen name
        
        # Create the edit note screen
        self.edit_note_screen = EditNoteScreen(None, None, None, self.update_note_callback, self.screen_manager, self.conn)
        self.edit_note_screen.name = 'edit_note'  # Set the screen name
        
        # Create the share note screen
        self.share_note_screen = ShareNoteScreen(None, None, None, self.update_share_callback, self.screen_manager)
        self.share_note_screen.name = 'share_note'  # Set the screen name
        
        # Add screens to the screen manager
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.add_note_screen)
        self.screen_manager.add_widget(self.edit_note_screen)
        self.screen_manager.add_widget(self.share_note_screen)

        # Add a button at the bottom-right corner to open the add note screen
        add_note_button = MDRaisedButton(
            text="+",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"right": 1, "bottom": 0.1},
            on_release=self.open_add_note_screen
        )
        self.main_screen.add_widget(add_note_button)

        return self.screen_manager

    def update_rect(self, instance, value):
        """Update the rectangle background size and position dynamically."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def open_add_note_screen(self, *args):
        self.screen_manager.current = 'add_note'

    def add_note_callback(self, title, body):
        self.save_note(title, body)

    def load_notes(self):
        self.cursor.execute('SELECT id, title, body FROM notes')
        notes = self.cursor.fetchall()
        for note in notes:
            note_widget = NoteWidget(
                note_id=note[0],  # Pass the note ID
                title=note[1],
                body=note[2],
                delete_callback=self.delete_note,
                edit_callback=self.open_edit_note_screen,
                share_callback=self.open_share_note_screen,
            )
            self.notes_layout.add_widget(note_widget)

    def save_note(self, title, body):
        self.cursor.execute('INSERT INTO notes (title, body) VALUES (?, ?)', (title, body))
        self.conn.commit()
        note_id = self.cursor.lastrowid  # Get the ID of the newly inserted note
        note_widget = NoteWidget(
            note_id=note_id,
            title=title,
            body=body,
            delete_callback=self.delete_note,
            edit_callback=self.open_edit_note_screen,
            share_callback=self.open_share_note_screen,
        )
        self.notes_layout.add_widget(note_widget)

    def delete_note(self, note_id, note_widget):
        self.cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()
        self.notes_layout.remove_widget(note_widget)
        self.notes_layout.height -= note_widget.height

    def open_edit_note_screen(self, note_id, title, body):
        self.edit_note_screen.note_id = note_id
        self.edit_note_screen.title_field.text = title
        self.edit_note_screen.body_field.text = body
        self.screen_manager.current = 'edit_note'

    def update_note_callback(self, title, body, note_id):
        self.cursor.execute('UPDATE notes SET title = ?, body = ? WHERE id = ?', (title, body, note_id))
        self.conn.commit()
        for widget in self.notes_layout.children:
            if hasattr(widget, 'note_id') and widget.note_id == note_id:
                widget.update_note(title, body)
        self.screen_manager.current = 'main'

    def open_share_note_screen(self, note_id, title, body):
        self.share_note_screen.note_id = note_id
        self.share_note_screen.title = title
        self.share_note_screen.body = body
        self.screen_manager.current = 'share_note'

    def update_share_callback(self, *args):
        pass

if __name__ == '__main__':
    NotesApp().run()
