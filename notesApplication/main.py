from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.button import MDRaisedButton
import sqlite3

class NoteWidget(BoxLayout):
    def __init__(self, note_id, title, body, delete_callback, edit_callback, share_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.note_id = note_id
        self.add_widget(Label(text=title))
        self.add_widget(Label(text=body))
        delete_button = Button(text='Delete', on_release=lambda x: delete_callback(note_id, self))
        edit_button = Button(text='Edit', on_release=lambda x: edit_callback(note_id, title, body))
        share_button = Button(text='Share', on_release=lambda x: share_callback(note_id, title, body))
        self.add_widget(delete_button)
        self.add_widget(edit_button)
        self.add_widget(share_button)

class Menu(BoxLayout):
    def __init__(self, open_customization_screen, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (0.2, 1)
        self.pos_hint = {'top': 1}
        self.add_widget(Button(text='Customization', on_release=open_customization_screen))

class CustomizationScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.color_picker = ColorPicker()
        layout.add_widget(self.color_picker)
        self.apply_button = Button(text='Apply', size_hint_y=None, height=50)
        self.apply_button.bind(on_release=self.apply_colors)
        layout.add_widget(self.apply_button)
        self.add_widget(layout)

    def apply_colors(self, instance):
        color = self.color_picker.color
        MDApp.get_running_app().theme_cls.primary_palette = "Custom"
        MDApp.get_running_app().theme_cls.primary_color = color

class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.cursor = None
        self.init_db()
        self.notes = []  # Store notes for filtering

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
        top_app_bar = MDTopAppBar(
            title='Notes App',
            anchor_title='left',
            size_hint_y=None,
            height=56,
            pos_hint={"top": 1}
        )
        top_app_bar.left_action_items = [['menu', lambda x: self.menu.open_menu(x)]]
        top_app_bar.right_action_items = [["magnify", lambda x: self.open_search_screen()]]

        self.menu = Menu(self.open_customization_screen)

        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={"top": 0.87},
            padding=(12, 0, 12, 12)
        )
        with content_layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.rect = RoundedRectangle(size=content_layout.size, pos=content_layout.pos, radius=[10, 10, 10, 10])
        content_layout.bind(size=self.update_rect, pos=self.update_rect)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.notes_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))

        self.load_notes()

        scroll_view.add_widget(self.notes_layout)
        content_layout.add_widget(scroll_view)

        self.main_screen.add_widget(content_layout)
        self.main_screen.add_widget(top_app_bar)

        add_note_button = MDRaisedButton(
            text="+",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"right": 0.98, "bottom": 0.1},
            on_release=self.open_add_note_screen
        )
        self.main_screen.add_widget(add_note_button)

        self.screen_manager.add_widget(self.main_screen)

        # Customization Screen
        self.customization_screen = CustomizationScreen(name='customization')
        self.screen_manager.add_widget(self.customization_screen)

        return self.screen_manager

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

    def open_share_note_screen(self, note_id, title, body):
        self.share_note_screen.note_id = note_id
        self.share_note_screen.title = title
        self.share_note_screen.body = body
        self.screen_manager.current = 'share_note'

    def update_share_callback(self, *args):
        pass

if __name__ == '__main__':
    NotesApp().run()