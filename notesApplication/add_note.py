from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView


class AddNoteScreen(MDScreen):
    def __init__(self, callback, screen_manager, conn, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.screen_manager = screen_manager
        self.conn = conn
        self.dialog = None

        # Create a top app bar (Fixed at the top)
        top_app_bar = MDTopAppBar(
            title='Add Note',
            pos_hint={"top": 1},
            anchor_title='left',
            md_bg_color=(0, 0.5, 1, 1),  # Blue color
            size_hint_y=None,
            height=56,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],  # Back button
        )

        # Scrollable Content Layout
        scroll_view = ScrollView()

        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint_y=None,
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # Create fields for note title and body
        self.title_field = MDTextField(
            hint_text='Note Title',
            size_hint_x=1,
            font_size=18,
            mode="rectangle",
        )

        self.body_field = MDTextField(
            hint_text='Note Body',
            multiline=True,
            size_hint_x=1,
            height=200,
            mode='rectangle',
        )

        # Create a save button
        save_button = MDRaisedButton(
            text='Save Note',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},
            on_press=lambda x: self.save_note(),
        )

        # Add widgets to the layout
        content_layout.add_widget(self.title_field)
        content_layout.add_widget(self.body_field)
        content_layout.add_widget(save_button)
        content_layout.add_widget(Widget())  # Spacer

        scroll_view.add_widget(content_layout)

        # Create the final layout with top bar and content
        main_layout = MDBoxLayout(orientation='vertical')
        main_layout.add_widget(top_app_bar)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def save_note(self):
        title = self.title_field.text.strip()
        body = self.body_field.text.strip()

        if title and body:
            self.save_to_db(title, body)
            self.show_confirmation_dialog()
            self.title_field.text = ''
            self.body_field.text = ''

    def save_to_db(self, title, body):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO notes (title, body) VALUES (?, ?)', (title, body))
        self.conn.commit()
        self.callback(title, body)

    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Note saved successfully!",
                buttons=[MDFlatButton(text="OK", on_release=self.close_dialog)],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.go_back()

    def go_back(self):
        self.screen_manager.current = 'main'
