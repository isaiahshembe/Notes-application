from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import ScreenManager
import sqlite3


class EditNoteScreen(MDScreen):
    def __init__(self, note_id, title, body, callback, screen_manager, conn, **kwargs):
        super().__init__(**kwargs)
        self.note_id = note_id
        self.callback = callback
        self.screen_manager = screen_manager
        self.conn = conn
        self.dialog = None

        # Main layout holds the top app bar and content
        main_layout = MDBoxLayout(orientation='vertical')

        # Top App Bar with explicitly set orange color (#FFA500)
        top_app_bar = MDTopAppBar(
            title='Edit Note',
            anchor_title='left',
            md_bg_color=(1, 0.647, 0, 1),  # RGBA for "#FFA500"
            size_hint_y=None,
            height=56,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],
        )
        main_layout.add_widget(top_app_bar)

        # Content Layout
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
        )

        # Title Field with fixed height for visibility
        self.title_field = MDTextField(
            hint_text='Note Title',
            size_hint_x=1,
            size_hint_y=None,
            height=50,
            font_size=18,
        )

        # Body Field
        self.body_field = MDTextField(
            hint_text='Note Body',
            multiline=True,
            size_hint_x=1,
            height=200,
            mode='rectangle',
        )

        # Save Button
        save_button = MDRaisedButton(
            text='Save Changes',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},
            on_press=lambda x: self.save_changes(),
        )

        # Add widgets to the content layout
        content_layout.add_widget(self.title_field)
        content_layout.add_widget(self.body_field)
        content_layout.add_widget(save_button)
        content_layout.add_widget(Widget())

        # Add content layout to the main layout
        main_layout.add_widget(content_layout)

        # Add main layout to the screen
        self.add_widget(main_layout)

        # Load existing title and body if provided
        if title is not None and body is not None:
            self.title_field.text = title
            self.body_field.text = body

    def save_changes(self):
        title = self.title_field.text
        body = self.body_field.text
        

        if title.strip() and body.strip():  # Check if fields are filled
            self.update_note_in_db(title, body)
            self.callback(title, body,  self.note_id)
            self.show_confirmation_dialog()
            self.go_back()
        else:
            self.show_error_dialog("Both Title and Body are required!")

    def update_note_in_db(self, title, body):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE notes SET title = ?, body = ? WHERE id = ?', (title, body, self.note_id))
        self.conn.commit()

    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Note edited successfully!",
                buttons=[
                    MDFlatButton(text="OK", on_release=self.close_dialog),
                ],
            )
        self.dialog.open()

    def show_error_dialog(self, message):
        error_dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss()),
            ],
        )
        error_dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def go_back(self):
        self.screen_manager.current = 'main'


class NotesApp(MDApp):
    def build(self):
        self.conn = sqlite3.connect('notes.db')
        self.screen_manager = ScreenManager()

        def dummy_callback(title, body, note_id):
            print(f"Updated Note {note_id}: {title} - {body}")

        edit_note_screen = EditNoteScreen(
            note_id=1,
            title="Sample Note Title",
            body="Sample Note Body",
            callback=dummy_callback,
            screen_manager=self.screen_manager,
            conn=self.conn,
            name='edit_note'
        )

        self.screen_manager.add_widget(edit_note_screen)
        self.screen_manager.add_widget(MDScreen(name='main'))

        return self.screen_manager

    def on_stop(self):
        self.conn.close()


if __name__ == '__main__':
    NotesApp().run()
