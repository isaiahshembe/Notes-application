from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
import os

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import sqlite3
from kivy.uix.image import Image

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.theming import ThemeManager

# Custom modules (ensure these paths are correct or adjust as needed)
from text_widget import NoteWidget  # We'll override this with our new NoteWidget below
from add_note import AddNoteScreen
from edit_note import EditNoteScreen
from share_note import ShareNoteScreen
from view_note import ViewNoteScreen
from whatsapp_share import WhatsAppShare

# Placeholder social sharing functions
def share_on_facebook(note_id):
    print(f"Sharing note {note_id} on Facebook (placeholder).")

def share_on_twitter(note_id):
    print(f"Sharing note {note_id} on Twitter (placeholder).")

def share_on_instagram(note_id):
    print(f"Sharing note {note_id} on Instagram (placeholder).")


# ----------------------------------------------------------------
# Custom Navigation Drawer Class with Pink Header
# ----------------------------------------------------------------
class MyNavigationDrawer(MDNavigationDrawer):
    def __init__(self, callback, **kwargs):
        """
        :param callback: a function to be called when certain items are pressed.
        """
        super().__init__(**kwargs)
        self.callback = callback

        # Main layout of the navigation drawer
        main_layout = MDBoxLayout(orientation="vertical")

        # Header area (pink background)
        header_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=dp(10),
            spacing=dp(10),
        )
        header_layout.md_bg_color = get_color_from_hex("#FFA500")
        
        # Layout for icon and text
        icon_text_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(100),
            pos_hint={"center_x": 0.5},
            
        )

        # App icon
        
        app_icon = Image(
            source='assets/notepad.png',  # Replace with your icon name (or use an image)
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            allow_stretch=True
        )

        icon_text_layout.add_widget(app_icon)

        account_label = MDLabel(
            text="NOTEPAD",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        header_layout.add_widget(icon_text_layout)
        header_layout.add_widget(account_label)
        main_layout.add_widget(header_layout)

        # MDList for menu items
        drawer_list = MDList()
        item_calender = OneLineIconListItem(text="Calender")
        item_calender.add_widget(IconLeftWidget(icon="calender-month",))
        item_calender.bind(on_release=lambda x: self.on_item_press("rate_us"))
        drawer_list.add_widget(item_calender)

        
        item_rate = OneLineIconListItem(text="Rate Us")
        item_rate.add_widget(IconLeftWidget(icon="heart-circle"))
        item_rate.bind(on_release=lambda x: self.on_item_press("rate_us"))
        drawer_list.add_widget(item_rate)

        item_recommend = OneLineIconListItem(text="Share App")
        item_recommend.add_widget(IconLeftWidget(icon="share"))
        item_recommend.bind(on_release=lambda x: self.on_item_press("recommend"))
        drawer_list.add_widget(item_recommend)

        item_premium = OneLineIconListItem(text="Get Premium")
        item_premium.add_widget(IconLeftWidget(icon="crown"))
        item_premium.bind(on_release=lambda x: self.on_item_press("premium"))
        drawer_list.add_widget(item_premium)

        item_facebook = OneLineIconListItem(text="Feedback")
        item_facebook.add_widget(IconLeftWidget(icon="message-processing"))
        item_facebook.bind(on_release=lambda x: self.on_item_press("feedback"))
        drawer_list.add_widget(item_facebook)

        item_feedback = OneLineIconListItem(text="Recycle Bin")
        item_feedback.add_widget(IconLeftWidget(icon="trash-can"))
        item_feedback.bind(on_release=lambda x: self.on_item_press("feedback"))
        drawer_list.add_widget(item_feedback)

        item_about = OneLineIconListItem(text="About")
        item_about.add_widget(IconLeftWidget(icon="information"))
        item_about.bind(on_release=lambda x: self.on_item_press("about"))
        drawer_list.add_widget(item_about)

        item_privacy = OneLineIconListItem(text="Privacy Policy")
        item_privacy.add_widget(IconLeftWidget(icon="shield-account-outline"))
        item_privacy.bind(on_release=lambda x: self.on_item_press("privacy"))
        drawer_list.add_widget(item_privacy)

        main_layout.add_widget(drawer_list)
        self.add_widget(main_layout)

    def on_item_press(self, item_name):
        print(f"You pressed: {item_name}")
        self.set_state("close")
        if item_name == "recommend":
            self.callback()


# ----------------------------------------------------------------
# Updated NoteWidget Class
# ----------------------------------------------------------------
class NoteWidget(ButtonBehavior, MDBoxLayout):
    def __init__(self, note_id, title, body, delete_callback, edit_callback, share_callback, view_callback, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=dp(120), padding=dp(10), spacing=dp(10), **kwargs)
        self.note_id = note_id
        self.delete_callback = delete_callback
        self.edit_callback = edit_callback
        self.share_callback = share_callback
        self.view_callback = view_callback

        # Background with rounded corners
        with self.canvas.before:
            self.bg_color = Color(rgba=get_color_from_hex("#FFFFFF"))
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(15),])
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Create inner container for title and body
        text_container = MDBoxLayout(orientation='vertical', spacing=dp(4))
        self.title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30),
            halign="left",
            text_size=(Window.width - dp(100), None),
            shorten=True,
        )
        self.date_label = MDLabel(
            text=date,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )
        self.body_label = MDLabel(
            text=body,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(70),
            halign="left",
            text_size=(Window.width - dp(100), None),
            shorten=True,
        )
        text_container.add_widget(self.title_label)
        text_container.add_widget(self.body_label)
        self.add_widget(text_container)

        # Menu button on the right
        self.menu_button = MDIconButton(
            icon="dots-vertical",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=get_color_from_hex("#000000")
        )
        self.menu_button.bind(on_release=self.open_menu)

        self.add_widget(self.title_label)
        self.add_widget(self.body_label)
        self.add_widget(self.menu_button)

        # Bind tap to open view screen
        self.bind(on_release=self.open_view_screen)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def open_menu(self, instance):
        menu_items = [
            {
                "text": "Edit",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.edit_callback(self.note_id, self.title_label.text, self.body_label.text),
            },
            {
                "text": "Share",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_callback(self.note_id, self.title_label.text, self.body_label.text),
            },
            {
                "text": "Delete",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.delete_callback(self.note_id, self),
            },
        ]
        self.menu = MDDropdownMenu(caller=instance, items=menu_items, width_mult=4)
        self.menu.open()

    def open_view_screen(self, *args):
        self.view_callback(self.note_id, self.title_label.text, self.body_label.text)


# ----------------------------------------------------------------
# Main App
# ----------------------------------------------------------------
class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.cursor = None
        self.init_db()
        self.notes = []  # Store notes for filtering
        self.theme_cls = ThemeManager()  # Initialize ThemeManager
        self.dark_mode = False  # Track dark mode state
        self.whatsapp_share = WhatsAppShare()

    def init_db(self):
        self.conn = sqlite3.connect('notes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                body TEXT,
                date TEXT
            )
        ''')
        self.cursor.execute("PRAGMA table_info(notes)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        if 'date' not in column_names:
         self.cursor.execute("ALTER TABLE notes ADD COLUMN date TEXT")
       

        self.conn.commit()

    def build(self):
        # Wrap everything in an MDNavigationLayout
        self.nav_layout = MDNavigationLayout()
        self.screen_manager = ScreenManager()

        # ----------------------------------------------------------------
        # 1) Welcome Screen
        # ----------------------------------------------------------------
        self.welcome_screen = MDScreen(name='welcome')
        welcome_layout = BoxLayout(orientation='vertical')
        with self.welcome_screen.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=Window.size, pos=self.welcome_screen.pos)
        self.welcome_screen.bind(size=self.update_rect, pos=self.update_rect)
        welcome_image = Image(source='assets/notepad.png')
        welcome_label = Label(text='Welcome to Notes App', font_size='24sp', color=(0, 0, 1, 1))
        welcome_layout.add_widget(welcome_image)
        welcome_layout.add_widget(welcome_label)
        self.welcome_screen.add_widget(welcome_layout)
        self.screen_manager.add_widget(self.welcome_screen)

        # ----------------------------------------------------------------
        # 2) Main Screen
        # ----------------------------------------------------------------
        self.main_screen = MDScreen(name='main')
        top_app_bar = MDTopAppBar(
            title='Notes App',
            anchor_title='left',
            size_hint_y=None,
            height=dp(56),
            pos_hint={"top": 1},
            md_bg_color=get_color_from_hex("#FFA500"),
        )
        top_app_bar.left_action_items = [['cog', lambda x: self.drawer.set_state("open")]]
        top_app_bar.right_action_items = [
            ["magnify", lambda x: self.open_search_screen()],
            ["weather-night", lambda x: self.toggle_dark_mode()],
        ]

        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={"top": 0.87},
            padding=dp(12),
            spacing=dp(12),
        )
        scroll_view = ScrollView(size_hint=(1, 1))
        self.notes_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))
        self.load_notes()
        scroll_view.add_widget(self.notes_layout)
        content_layout.add_widget(scroll_view)
        self.main_screen.add_widget(top_app_bar)
        self.main_screen.add_widget(content_layout)

        add_note_button = MDIconButton(
            icon="pencil",
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            pos_hint={"center_x": 0.5, "bottom": 0.1},
            md_bg_color=get_color_from_hex("#6A1B9A"),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.open_add_note_screen,
        )
        self.main_screen.add_widget(add_note_button)
        self.screen_manager.add_widget(self.main_screen)

        # ----------------------------------------------------------------
        # 3) Search Screen
        # ----------------------------------------------------------------
        self.search_screen = MDScreen(name='search')
        search_layout = BoxLayout(orientation='vertical')
        search_top_app_bar = MDTopAppBar(
            title='Search',
            anchor_title='left',
            size_hint_y=None,
            height=56,
            pos_hint={"top": 1},
            md_bg_color=get_color_from_hex("#FFA500"),
        )
        search_top_app_bar.left_action_items = [["arrow-left", lambda x: self.screen_manager.switch_to(self.main_screen)]]
        search_layout.add_widget(search_top_app_bar)
        self.search_bar = TextInput(hint_text='Search notes...', size_hint=(1, None), height=40, multiline=False)
        self.search_bar.bind(text=self.filter_search_results)
        search_layout.add_widget(self.search_bar)
        scroll_view_search = ScrollView(size_hint=(1, 1))
        self.search_results_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        self.search_results_layout.bind(minimum_height=self.search_results_layout.setter('height'))
        scroll_view_search.add_widget(self.search_results_layout)
        search_layout.add_widget(scroll_view_search)
        self.search_screen.add_widget(search_layout)
        self.screen_manager.add_widget(self.search_screen)

        # ----------------------------------------------------------------
        # 4) Additional Screens (Add, Edit, Share, View)
        # ----------------------------------------------------------------
        self.add_note_screen = AddNoteScreen(self.add_note_callback, self.screen_manager, self.conn)
        self.add_note_screen.name = 'add_note'
        self.edit_note_screen = EditNoteScreen(None, None, None, self.update_note_callback, self.screen_manager, self.conn)
        self.edit_note_screen.name = 'edit_note'
        self.share_note_screen = ShareNoteScreen(None, None, None, self.update_share_callback, self.screen_manager)
        self.share_note_screen.name = 'share_note'
        self.view_note_screen = ViewNoteScreen()
        self.view_note_screen.name = 'view_note'
        self.screen_manager.add_widget(self.add_note_screen)
        self.screen_manager.add_widget(self.edit_note_screen)
        self.screen_manager.add_widget(self.share_note_screen)
        self.screen_manager.add_widget(self.view_note_screen)

        self.screen_manager.current = 'welcome'
        Clock.schedule_once(self.switch_to_main_screen, 5)
        self.nav_layout.add_widget(self.screen_manager)

        self.drawer = MyNavigationDrawer(callback=self.open_add_note_screen)
        self.nav_layout.add_widget(self.drawer)

        return self.nav_layout

    # ----------------------------------------------------------------
    # Utility Methods
    # ----------------------------------------------------------------
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def switch_to_main_screen(self, dt):
        self.screen_manager.current = 'main'

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "BlueGray"
            text_color = (0.4, 0.5, 0.6, 1)
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Blue"
            text_color = (0, 0, 0, 1)
        for note_widget in self.notes_layout.children:
            if isinstance(note_widget, NoteWidget):
                note_widget.title_label.theme_text_color = "Custom"
                note_widget.title_label.text_color = text_color
                note_widget.body_label.theme_text_color = "Custom"
                note_widget.body_label.text_color = text_color

    def update_share_callback(self, *args):
        print("Share callback triggered")

    def open_search_screen(self, *args):
        self.load_notes()
        self.search_bar.text = ""
        self.search_results_layout.clear_widgets()
        self.screen_manager.current = 'search'

    def filter_search_results(self, instance, value):
        search_text = self.search_bar.text.lower()
        self.search_results_layout.clear_widgets()
        sorted_notes = sorted(self.notes, key=lambda x: x[0], reverse=True)
        for note in sorted_notes:
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

    def add_note_callback(self, title, body, date):
        self.save_note(title, body, date)

    def load_notes(self):
        self.cursor.execute('SELECT id, title, body, date FROM notes ')
        self.notes = self.cursor.fetchall()
        self.filter_notes()

    def filter_notes(self):
        self.notes_layout.clear_widgets()
        sorted_notes = sorted(self.notes, key=lambda x: x[0], reverse=True)
        for note in sorted_notes:
            note_widget = NoteWidget(
                note_id=note[0],
                title=note[1],
                body=note[2],
                date=note[3],
                delete_callback=self.delete_note,
                edit_callback=self.open_edit_note_screen,
                share_callback=self.open_share_note_screen,
                view_callback=self.open_view_note_screen
            )
            self.notes_layout.add_widget(note_widget)

    def save_note(self, title, body, date):
        self.cursor.execute('INSERT INTO notes (title, body, date) VALUES (?, ?, ?)', (title, body, date))
        self.conn.commit()
        self.cursor.execute('SELECT id, title, body FROM notes')
        print("DEBUG: All notes in DB:", self.cursor.fetchall())
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
        self.current_share_note = {'id': note_id, 'title': title, 'body': body}
        menu_items = [
            {"text": "Share via Facebook", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("Facebook")},
            {"text": "Share via Twitter", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("Twitter")},
            {"text": "Share via Instagram", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("Instagram")},
            {"text": "Share via WhatsApp", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("WhatsApp")},
        ]
        self.share_menu = MDDropdownMenu(caller=self.screen_manager.get_screen('main'), items=menu_items, width_mult=4)
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
                self.whatsapp_share.share_on_whatsapp(note_id, title, body, lambda: print("Shared on WhatsApp"))
            except Exception as e:
                print("Failed to share on WhatsApp:", e)


if __name__ == '__main__':
    NotesApp().run()
