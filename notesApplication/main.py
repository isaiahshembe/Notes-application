from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
import os
import platform
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import sqlite3
from kivy.uix.image import Image
import webbrowser
from datetime import datetime
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

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

# Custom modules
from add_note import AddNoteScreen
from edit_note import EditNoteScreen
from share_note import ShareNoteScreen
from view_note import ViewNoteScreen
from whatsapp_share import WhatsAppShare

# Try to import plyer.share with fallback
try:
    from plyer import share
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Plyer share not available")

def share_note_text(note_id, title, body):
    """Share a note's title and body as plain text using platform-specific methods"""
    try:
        text_to_share = f"{title}\n\n{body}"
        
        if platform == 'android':
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                String = autoclass('java.lang.String')
                intent = Intent()
                intent.setAction(Intent.ACTION_SEND)
                intent.setType("text/plain")
                intent.putExtra(Intent.EXTRA_TEXT, String(text_to_share))
                current_activity = autoclass('org.kivy.android.PythonActivity').mActivity
                current_activity.startActivity(Intent.createChooser(intent, String("Share via")))
            except Exception as e:
                print(f"Android sharing failed: {e}")
                # Fallback to email
                webbrowser.open(f"mailto:?subject={title}&body={body}")
        elif PLYER_AVAILABLE:
            share.share(text=text_to_share)
        else:
            # Fallback for other platforms
            webbrowser.open(f"mailto:?subject={title}&body={body}")
            
        print(f"Note {note_id} shared successfully!")
    except Exception as e:
        print(f"Failed to share note: {e}")

def share_on_facebook(note_id, title, body):
    """Share note on Facebook"""
    try:
        text_to_share = f"{title}\n\n{body}"
        url = f"https://www.facebook.com/sharer/sharer.php?u=&quote={text_to_share}"
        webbrowser.open(url)
        print(f"Note {note_id} shared on Facebook")
    except Exception as e:
        print(f"Failed to share on Facebook: {e}")

def share_on_twitter(note_id, title, body):
    """Share note on Twitter"""
    try:
        text_to_share = f"{title}\n\n{body}"
        url = f"https://twitter.com/intent/tweet?text={text_to_share}"
        webbrowser.open(url)
        print(f"Note {note_id} shared on Twitter")
    except Exception as e:
        print(f"Failed to share on Twitter: {e}")

def share_on_instagram(note_id, title, body):
    """Share note text (Instagram doesn't support direct text sharing)"""
    try:
        share_note_text(note_id, title, body)
        print(f"Note {note_id} shared via system sharing (Instagram)")
    except Exception as e:
        print(f"Failed to share on Instagram: {e}")

class MyNavigationDrawer(MDNavigationDrawer):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
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
            source='assets/notepad.png',
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
        
        # Favorite
        item_favorite = OneLineIconListItem(text="Favorite")
        item_favorite.add_widget(IconLeftWidget(icon="star"))
        item_favorite.bind(on_release=lambda x: self.on_item_press("favorite"))
        drawer_list.add_widget(item_favorite)

        # Rate Us
        item_rate = OneLineIconListItem(text="Rate Us")
        item_rate.add_widget(IconLeftWidget(icon="heart-circle"))
        item_rate.bind(on_release=lambda x: self.on_item_press("rate_us"))
        drawer_list.add_widget(item_rate)

        # Share App
        item_recommend = OneLineIconListItem(text="Share App")
        item_recommend.add_widget(IconLeftWidget(icon="share"))
        item_recommend.bind(on_release=lambda x: self.on_item_press("share_app"))
        drawer_list.add_widget(item_recommend)

        # Get Premium
        item_premium = OneLineIconListItem(text="Get Premium")
        item_premium.add_widget(IconLeftWidget(icon="crown"))
        item_premium.bind(on_release=lambda x: self.on_item_press("premium"))
        drawer_list.add_widget(item_premium)

        # Feedback
        item_feedback = OneLineIconListItem(text="Feedback")
        item_feedback.add_widget(IconLeftWidget(icon="message-processing"))
        item_feedback.bind(on_release=lambda x: self.on_item_press("feedback"))
        drawer_list.add_widget(item_feedback)

        # Recycle Bin
        item_bin = OneLineIconListItem(text="Recycle Bin")
        item_bin.add_widget(IconLeftWidget(icon="trash-can"))
        item_bin.bind(on_release=lambda x: self.on_item_press("recycle_bin"))
        drawer_list.add_widget(item_bin)

        # About
        item_about = OneLineIconListItem(text="About")
        item_about.add_widget(IconLeftWidget(icon="information"))
        item_about.bind(on_release=lambda x: self.on_item_press("about"))
        drawer_list.add_widget(item_about)

        # Privacy Policy
        item_privacy = OneLineIconListItem(text="Privacy Policy")
        item_privacy.add_widget(IconLeftWidget(icon="shield-account-outline"))
        item_privacy.bind(on_release=lambda x: self.on_item_press("privacy"))
        drawer_list.add_widget(item_privacy)

        main_layout.add_widget(drawer_list)
        self.add_widget(main_layout)

    def on_item_press(self, item_name):
        self.set_state("close")
        app = self.app
        
        if item_name == "favorite":
            app.show_favorite_notes()
        elif item_name == "rate_us":
            app.rate_app()
        elif item_name == "share_app":
            app.share_app()
        elif item_name == "premium":
            app.show_premium_dialog()
        elif item_name == "feedback":
            app.send_feedback()
        elif item_name == "recycle_bin":
            app.show_recycle_bin()
        elif item_name == "about":
            app.show_about()
        elif item_name == "privacy":
            app.show_privacy_policy()

class NoteWidget(ButtonBehavior, MDBoxLayout):
    def __init__(self, note_id, title, date, body, delete_callback, edit_callback, share_callback, view_callback, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(140), padding=dp(10), spacing=dp(10), **kwargs)
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

        # Create inner container for title, date and body
        text_container = MDBoxLayout(orientation='vertical', spacing=dp(4))
        self.title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30),
            halign="left",
        )
        
        self.date_label = MDLabel(
            text=date,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            halign="left",
        )
        
        self.body_label = MDLabel(
            text=body,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(70),
            halign="left",
        )
        
        text_container.add_widget(self.title_label)
        text_container.add_widget(self.date_label)
        text_container.add_widget(self.body_label)
        self.add_widget(text_container)

        # Menu button on the right
        self.menu_button = MDIconButton(
            icon="dots-vertical",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=get_color_from_hex("#000000"))
        self.menu_button.bind(on_release=self.open_menu)
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
        self.view_callback(self.note_id, self.title_label.text, self.date_label.text, self.body_label.text)

class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.cursor = None
        self.init_db()
        self.notes = []
        self.theme_cls = ThemeManager()
        self.dark_mode = False
        self.whatsapp_share = WhatsAppShare()
        self.current_share_note = None
        self.dialog = None
        self.showing_favorites = False
        self.showing_deleted = False

    def init_db(self):
        """Initialize or upgrade the database schema"""
        self.conn = sqlite3.connect('notes.db')
        self.cursor = self.conn.cursor()
        
        # Check if table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        table_exists = self.cursor.fetchone()
        
        if not table_exists:
            # Create new table with all columns
            self.cursor.execute('''
                CREATE TABLE notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    body TEXT,
                    date TEXT,
                    favorite INTEGER DEFAULT 0,
                    deleted INTEGER DEFAULT 0
                )
            ''')
        else:
            # Check for missing columns
            self.cursor.execute("PRAGMA table_info(notes)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'date' not in columns:
                self.cursor.execute("ALTER TABLE notes ADD COLUMN date TEXT")
                # Set default date for existing records
                default_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("UPDATE notes SET date=?", (default_date,))
            
            if 'favorite' not in columns:
                self.cursor.execute("ALTER TABLE notes ADD COLUMN favorite INTEGER DEFAULT 0")
            
            if 'deleted' not in columns:
                self.cursor.execute("ALTER TABLE notes ADD COLUMN deleted INTEGER DEFAULT 0")
        
        self.conn.commit()

    def build(self):
        self.nav_layout = MDNavigationLayout()
        self.screen_manager = ScreenManager()

        # Welcome Screen
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

        # Main Screen
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

        # Search Screen
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

        # Additional Screens
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
        Clock.schedule_once(self.switch_to_main_screen, 3)
        self.nav_layout.add_widget(self.screen_manager)

        self.drawer = MyNavigationDrawer(callback=self.open_add_note_screen)
        self.nav_layout.add_widget(self.drawer)

        return self.nav_layout

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
            self.theme_cls.primary_palette = "Orange"
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
        
        if self.showing_favorites:
            notes = [note for note in self.notes if note[4] == 1]  # favorite=1
        elif self.showing_deleted:
            notes = [note for note in self.notes if note[5] == 1]  # deleted=1
        else:
            notes = [note for note in self.notes if note[5] == 0]  # deleted=0

        for note in notes:
            if search_text in note[1].lower() or search_text in note[2].lower():
                note_widget = NoteWidget(
                    note_id=note[0],
                    title=note[1],
                    date=note[3],
                    body=note[2],
                    delete_callback=self.delete_note,
                    edit_callback=self.open_edit_note_screen,
                    share_callback=self.open_share_note_screen,
                    view_callback=self.open_view_note_screen
                )
                self.search_results_layout.add_widget(note_widget)

    def open_add_note_screen(self, *args):
        self.screen_manager.current = 'add_note'

    def add_note_callback(self, title, body, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_note(title, body, date)

    def save_note(self, title, body, date):
        self.cursor.execute('INSERT INTO notes (title, body, date) VALUES (?, ?, ?)', (title, body, date))
        self.conn.commit()
        self.load_notes()

    def load_notes(self):
        self.cursor.execute('SELECT id, title, body, date, favorite, deleted FROM notes')
        self.notes = self.cursor.fetchall()
        self.filter_notes()

    def filter_notes(self):
        self.notes_layout.clear_widgets()
        
        if self.showing_favorites:
            notes = [note for note in self.notes if note[4] == 1]  # favorite=1
            self.show_snackbar("Showing favorite notes")
        elif self.showing_deleted:
            notes = [note for note in self.notes if note[5] == 1]  # deleted=1
            self.show_snackbar("Showing deleted notes")
        else:
            notes = [note for note in self.notes if note[5] == 0]  # deleted=0

        # Sort by date (newest first)
        notes.sort(key=lambda x: x[3], reverse=True)
        
        for note in notes:
            note_widget = NoteWidget(
                note_id=note[0],
                title=note[1],
                date=note[3],
                body=note[2],
                delete_callback=self.delete_note,
                edit_callback=self.open_edit_note_screen,
                share_callback=self.open_share_note_screen,
                view_callback=self.open_view_note_screen
            )
            self.notes_layout.add_widget(note_widget)

    def delete_note(self, note_id, note_widget):
        # Soft delete (mark as deleted instead of actually deleting)
        self.cursor.execute('UPDATE notes SET deleted=1 WHERE id=?', (note_id,))
        self.conn.commit()
        self.notes = [note for note in self.notes if note[0] != note_id]
        if note_widget.parent:
            note_widget.parent.remove_widget(note_widget)
        self.show_snackbar("Note moved to recycle bin")

    def open_edit_note_screen(self, note_id, title, body):
        self.edit_note_screen.note_id = note_id
        self.edit_note_screen.title_field.text = title
        self.edit_note_screen.body_field.text = body
        self.screen_manager.current = 'edit_note'

    def update_note_callback(self, title, date, body, note_id):
        self.cursor.execute('UPDATE notes SET title=?, date=?, body=? WHERE id=?', 
                          (title, date, body, note_id))
        self.conn.commit()
        self.load_notes()
        self.screen_manager.current = 'main'

    def open_view_note_screen(self, note_id, title, date, body):
        self.view_note_screen.display_note(note_id, title, date, body, 
                                         self.delete_note, self.open_edit_note_screen)
        self.screen_manager.current = 'view_note'

    def open_share_note_screen(self, note_id, title, body):
        self.current_share_note = {'id': note_id, 'title': title, 'body': body}
        menu_items = [
            {"text": "Share via Facebook", "viewclass": "OneLineListItem", 
             "on_release": lambda: self.share_option_selected("Facebook")},
            {"text": "Share via Twitter", "viewclass": "OneLineListItem",
             "on_release": lambda: self.share_option_selected("Twitter")},
            {"text": "Share via Instagram", "viewclass": "OneLineListItem",
             "on_release": lambda: self.share_option_selected("Instagram")},
            {"text": "Share via WhatsApp", "viewclass": "OneLineListItem",
             "on_release": lambda: self.share_option_selected("WhatsApp")},
            {"text": "Share via Email", "viewclass": "OneLineListItem",
             "on_release": lambda: self.share_option_selected("Email")},
        ]
        self.share_menu = MDDropdownMenu(
            caller=self.screen_manager.get_screen('main'), 
            items=menu_items, 
            width_mult=4
        )
        self.share_menu.open()

    def share_option_selected(self, platform):
        self.share_menu.dismiss()
        note_id = self.current_share_note['id']
        title = self.current_share_note['title']
        body = self.current_share_note['body']

        if platform == "Facebook":
            share_on_facebook(note_id, title, body)
        elif platform == "Twitter":
            share_on_twitter(note_id, title, body)
        elif platform == "Instagram":
            share_on_instagram(note_id, title, body)
        elif platform == "WhatsApp":
            try:
                self.whatsapp_share.share_on_whatsapp(note_id, title, body, 
                                                     lambda: print("Shared on WhatsApp"))
            except Exception as e:
                print("Failed to share on WhatsApp:", e)
        elif platform == "Email":
            share_note_text(note_id, title, body)

    # Navigation Drawer Functions
    def show_favorite_notes(self):
        """Show only favorite notes"""
        self.showing_favorites = True
        self.showing_deleted = False
        self.load_notes()

    def rate_app(self):
        """Open app store for rating"""
        try:
            webbrowser.open("https://play.google.com/store/apps/details?id=com.your.app")
        except Exception as e:
            self.show_snackbar(f"Couldn't open store: {str(e)}")

    def share_app(self):
        """Share app download link"""
        try:
            share_text = "Check out this awesome notes app: https://play.google.com/store/apps/details?id=com.your.app"
            if PLYER_AVAILABLE:
                share.share(text=share_text)
            else:
                webbrowser.open(f"mailto:?subject=Check%20this%20app&body={share_text}")
        except Exception as e:
            self.show_snackbar(f"Couldn't share app: {str(e)}")

    def show_premium_dialog(self):
        """Show premium features dialog"""
        self.dialog = MDDialog(
            title="Premium Features",
            text="Unlock these premium features:\n\n- Unlimited notes\n- Cloud sync\n- Advanced formatting\n- Dark mode themes",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="UPGRADE",
                    on_release=self.purchase_premium
                ),
            ],
        )
        self.dialog.open()

    def purchase_premium(self, *args):
        """Handle premium purchase"""
        self.dialog.dismiss()
        self.show_snackbar("Premium features unlocked!")

    def send_feedback(self):
        """Open email for feedback"""
        try:
            webbrowser.open("mailto:support@yourapp.com?subject=Notes%20App%20Feedback")
        except Exception as e:
            self.show_snackbar(f"Couldn't open email: {str(e)}")

    def show_recycle_bin(self):
        """Show deleted notes"""
        self.showing_deleted = True
        self.showing_favorites = False
        self.load_notes()

    def show_about(self):
        """Show about dialog"""
        self.dialog = MDDialog(
            title="About Notes App",
            text="Version 1.0\n\nA simple notes app to keep your thoughts organized.\n\n© 2023 Your Company",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        self.dialog.open()

    def show_privacy_policy(self):
        """Show privacy policy dialog"""
        self.dialog = MDDialog(
            title="Privacy Policy",
            text="We respect your privacy:\n\n- We don't collect personal data\n- Your notes stay on your device\n- No tracking or analytics",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        self.dialog.open()

    def show_snackbar(self, message):
        """Helper to show snackbar messages"""
        snackbar = Snackbar(
            text=message,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(
                (Window.width - (dp(10) * 2)) / Window.width
            )
        )
        snackbar.open()

if __name__ == '__main__':
    NotesApp().run()