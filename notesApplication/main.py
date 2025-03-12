from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from text_widget import NoteWidget
from menu import Menu
from add_note import AddNoteScreen
from edit_note import EditNoteScreen
from share_note import ShareNoteScreen
from kivy.uix.screenmanager import ScreenManager
import sqlite3
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.button import MDRaisedButton
from whatsapp_share import WhatsAppShare
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from view_note import ViewNoteScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.theming import ThemeManager  # Import ThemeManager

# Placeholder functions for social media sharing
def share_on_facebook(note_id):
    print(f"Sharing note {note_id} on Facebook (placeholder).")

def share_on_twitter(note_id):
    print(f"Sharing note {note_id} on Twitter (placeholder).")

def share_on_instagram(note_id):
    print(f"Sharing note {note_id} on Instagram (placeholder).")

class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.cursor = None
        self.init_db()
        self.notes = []  # Store notes for filtering
        self.whatsapp_share = WhatsAppShare()
        self.theme_cls = ThemeManager()  # Initialize ThemeManager
        self.dark_mode = False  # Track dark mode state

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

        # Main Screen
        self.main_screen = MDScreen(name='main')

        # Top App Bar (Header)
        top_app_bar = MDTopAppBar(
            title='Notes App',
            anchor_title='left',
            size_hint_y=None,
            height=dp(56),
            pos_hint={"top": 1},
            md_bg_color=get_color_from_hex("#2196F3")
        )
        top_app_bar.left_action_items = [['menu', lambda x: self.menu.open_menu(x)]]
        top_app_bar.right_action_items = [
            ["magnify", lambda x: self.open_search_screen()],
            ["weather-night", lambda x: self.toggle_dark_mode()]  # Dark mode button
        ]

        self.menu = Menu(self.open_customization_screen)

        # Content Layout
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={"top": 0.87},
            padding=dp(12),
            spacing=dp(12)
        )

        # Scrollable area for notes
        scroll_view = ScrollView(size_hint=(1, 1))
        self.notes_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))

        self.load_notes()
        scroll_view.add_widget(self.notes_layout)
        content_layout.add_widget(scroll_view)

        # Add the top app bar and content layout to the main screen
        self.main_screen.add_widget(top_app_bar)
        self.main_screen.add_widget(content_layout)

        # Floating add note button on the main screen
        add_note_button = MDRaisedButton(
            text="+",
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            pos_hint={"center_x": 0.5, "bottom": 0.1},  # Centered horizontally, near the bottom
            md_bg_color=get_color_from_hex("#6A1B9A"),  # Dark purple color
            theme_text_color="Custom",  # Ensure the text color is white
            text_color=(1, 1, 1, 1),  # White text color
            _radius=dp(28),  # Make the button circular
            on_release=self.open_add_note_screen
        )
        self.main_screen.add_widget(add_note_button)

        self.screen_manager.add_widget(self.main_screen)

        # -----------------------
        # Search Screen
        # -----------------------
        self.search_screen = MDScreen(name='search')
        search_layout = BoxLayout(orientation='vertical')

        # Top app bar for search screen with a back arrow
        search_top_app_bar = MDTopAppBar(
            title='Search',
            anchor_title='left',
            size_hint_y=None,
            height=56,
            pos_hint={"top": 1}
        )
        search_top_app_bar.left_action_items = [["arrow-left", lambda x: self.screen_manager.switch_to(self.main_screen)]]
        search_layout.add_widget(search_top_app_bar)

        # Full-width search bar
        self.search_bar = TextInput(
            hint_text='Search notes...',
            size_hint=(1, None),
            height=40,
            multiline=False,
        )
        # Bind changes to update search results dynamically
        self.search_bar.bind(text=self.filter_search_results)
        search_layout.add_widget(self.search_bar)

        # Scrollable area for search results
        scroll_view_search = ScrollView(size_hint=(1, 1))
        self.search_results_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        self.search_results_layout.bind(minimum_height=self.search_results_layout.setter('height'))
        scroll_view_search.add_widget(self.search_results_layout)
        search_layout.add_widget(scroll_view_search)

        self.search_screen.add_widget(search_layout)
        self.screen_manager.add_widget(self.search_screen)

        # -----------------------
        # Additional Screens
        # -----------------------
        self.add_note_screen = AddNoteScreen(self.add_note_callback, self.screen_manager, self.conn)
        self.add_note_screen.name = 'add_note'
        self.edit_note_screen = EditNoteScreen(None, None, None, self.update_note_callback, self.screen_manager, self.conn)
        self.edit_note_screen.name = 'edit_note'
        self.share_note_screen = ShareNoteScreen(None, None, None, self.update_share_callback, self.screen_manager)
        self.share_note_screen.name = 'share_note'

        # Add the ViewNoteScreen
        self.view_note_screen = ViewNoteScreen()
        self.view_note_screen.name = 'view_note'

        self.screen_manager.add_widget(self.add_note_screen)
        self.screen_manager.add_widget(self.edit_note_screen)
        self.screen_manager.add_widget(self.share_note_screen)
        self.screen_manager.add_widget(self.view_note_screen)

        return self.screen_manager

    def toggle_dark_mode(self):
        """
        Toggle between light and dark mode.
        """
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"  # Set dark mode
            self.theme_cls.primary_palette = "BlueGray"  # Dark mode primary color
        else:
            self.theme_cls.theme_style = "Light"  # Set light mode
            self.theme_cls.primary_palette = "Blue"  # Light mode primary color

    # Rest of your methods remain unchanged...
    def update_share_callback(self, *args):
        """
        Placeholder method for handling share callback logic.
        """
        print("Share callback triggered")

    def open_customization_screen(self, *args):
        self.screen_manager.current = 'customization'

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def open_search_screen(self, *args):
        self.load_notes()
        self.search_bar.text = ""
        self.search_results_layout.clear_widgets()
        self.screen_manager.current = 'search'

    def filter_search_results(self, instance, value):
        search_text = self.search_bar.text.lower()
        self.search_results_layout.clear_widgets()
        for note in self.notes:
            if search_text in note[1].lower() or search_text in note[2].lower():
                note_widget = NoteWidget(
                    note_id=note[0],
                    title=note[1],
                    body=note[2],
                    delete_callback=self.delete_note,
                    edit_callback=self.open_edit_note_screen,
                    share_callback=self.open_share_note_screen,
                    view_callback=self.open_view_note_screen
                )
                self.search_results_layout.add_widget(note_widget)

    def open_add_note_screen(self, *args):
        self.screen_manager.current = 'add_note'

    def add_note_callback(self, title, body):
        self.save_note(title, body)

    def load_notes(self):
        self.cursor.execute('SELECT id, title, body FROM notes')
        self.notes = self.cursor.fetchall()
        self.filter_notes()

    def filter_notes(self):
        self.notes_layout.clear_widgets()
        for note in self.notes:
            note_widget = NoteWidget(
                note_id=note[0],
                title=note[1],
                body=note[2],
                delete_callback=self.delete_note,
                edit_callback=self.open_edit_note_screen,
                share_callback=self.open_share_note_screen,
                view_callback=self.open_view_note_screen
            )
            self.notes_layout.add_widget(note_widget)

    def save_note(self, title, body):
        self.cursor.execute('INSERT INTO notes (title, body) VALUES (?, ?)', (title, body))
        self.conn.commit()
        self.load_notes()

    def delete_note(self, note_id, note_widget):
        self.cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()
        self.notes = [note for note in self.notes if note[0] != note_id]
        if note_widget.parent:
            note_widget.parent.remove_widget(note_widget)

    def open_edit_note_screen(self, note_id, title, body):
        self.edit_note_screen.note_id = note_id
        self.edit_note_screen.title_field.text = title
        self.edit_note_screen.body_field.text = body
        self.screen_manager.current = 'edit_note'

    def update_note_callback(self, title, body, note_id):
        self.cursor.execute('UPDATE notes SET title = ?, body = ? WHERE id = ?', (title, body, note_id))
        self.conn.commit()
        self.load_notes()
        self.screen_manager.current = 'main'

    def open_view_note_screen(self, note_id, title, body):
        self.view_note_screen.display_note(note_id, title, body, self.delete_note, self.open_edit_note_screen)
        self.screen_manager.current = 'view_note'

    def open_share_note_screen(self, note_id, title, body):
        # Instead of switching to a separate screen, open a dropdown menu
        self.current_share_note = {'id': note_id, 'title': title, 'body': body}

        menu_items = [
            {
                "text": "Share via Facebook",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("Facebook")
            },
            {
                "text": "Share via Twitter",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("Twitter")
            },
            {
                "text": "Share via Instagram",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("Instagram")
            },
            {
                "text": "Share via WhatsApp",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("WhatsApp")
            },
        ]

        self.share_menu = MDDropdownMenu(
            caller=self.screen_manager.get_screen('main'),
            items=menu_items,
            width_mult=4,
        )
        self.share_menu.open()

    def share_option_selected(self, platform):
        self.share_menu.dismiss()

        note_id = self.current_share_note['id']
        title = self.current_share_note['title']
        body = self.current_share_note['body']

        if platform == "Facebook":
            share_on_facebook(note_id)
        elif platform == "Twitter":
            share_on_twitter(note_id)
        elif platform == "Instagram":
            share_on_instagram(note_id)
        elif platform == "WhatsApp":
            try:
                self.whatsapp_share.share_on_whatsapp(
                    note_id, title, body, lambda: print("Shared on WhatsApp")
                )
            except Exception as e:
                print("Failed to share on WhatsApp:", e)


if __name__ == '__main__':
    NotesApp().run()