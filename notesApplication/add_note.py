from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton

from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.dialog import MDDialog

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
            pos_hint={"top": 1},  # Keeps it fixed at the top
            anchor_title='left',
            md_bg_color=(0, 0.5, 1, 1),  # Blue color
            size_hint_y=None,
            height=56,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],  # Back button
        )

        # Create a vertical layout for the content
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=20,  # Add padding for better spacing
            spacing=20,  # Add space between elements
            size_hint_y=None,  # Disable automatic sizing
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))  # Adjust height dynamically

        # Create fields for note title and body
        self.title_field = MDTextField(
            hint_text='Note Title',
            size_hint_x=1,
            font_size=18,
        )

        self.body_field = MDTextField(
            hint_text='Note Body',
            multiline=True,
            size_hint_x=1,
            height=200,
            mode='rectangle',  # Makes it more prominent
        )

        # Create a save button (Centered)
        save_button = MDRaisedButton(
            text='Save Note',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},  # Center the button
            on_press=lambda x: self.save_note(),
        )

        # Add widgets to the layout
        content_layout.add_widget(self.title_field)
        content_layout.add_widget(self.body_field)
        content_layout.add_widget(save_button)
        content_layout.add_widget(Widget())  # Spacer for better alignment

        # Add the widgets to the screen
        self.add_widget(content_layout)  # Content
        self.add_widget(top_app_bar)  # Fixed App Bar

    def save_note(self):
        title = self.title_field.text
        body = self.body_field.text

        if title.strip() and body.strip():  # Ensure fields are not empty
            self.save_to_db(title, body)
            self.show_confirmation_dialog()

        # Clear the fields
        self.title_field.text = ''
        self.body_field.text = ''

        # Go back to the main screen
        self.go_back()

    def save_to_db(self, title, body):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO notes (title, body) VALUES (?, ?)', (title, body))
        self.conn.commit()
        self.callback(title, body)

    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Note saved successfully!",
                buttons=[
                    MDFlatButton(
                        text="OK", on_release=self.close_dialog
                    ),
                ],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def go_back(self):
        self.screen_manager.current = 'main'
