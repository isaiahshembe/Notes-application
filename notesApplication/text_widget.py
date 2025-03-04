from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

class NoteWidget(MDCard):
    def __init__(self, note_id, title, body, delete_callback, edit_callback, share_callback, **kwargs):
        super().__init__(**kwargs)
        self.note_id = note_id  # Store the note ID
        self.delete_callback = delete_callback  # Store the delete callback
        self.edit_callback = edit_callback  # Store the edit callback
        self.share_callback = share_callback  # Store the share callback

        self.orientation = "vertical"
        self.padding = "12dp"
        self.size_hint = (1, None)
        self.height = 150
        self.elevation = 4
        self.margin = "12dp"

        # Title
        self.title_label = MDLabel(
            text=title,
            font_style="H6",
            size_hint_y=None,
            height=30,
            halign="left",
        )
        self.add_widget(self.title_label)

        # Body
        self.body_label = MDLabel(
            text=body,
            font_style="Body1",
            size_hint_y=None,
            height=60,
            halign="left",
        )
        self.add_widget(self.body_label)

        # Buttons (Edit, Share, Delete)
        button_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        
        edit_button = MDIconButton(icon="pencil", on_press=lambda x: self.edit_note())
        share_button = MDIconButton(icon="share-variant", on_press=lambda x: self.share_note())
        delete_button = MDIconButton(icon="delete", on_press=lambda x: self.delete_note())
        
        button_layout.add_widget(edit_button)
        button_layout.add_widget(share_button)
        button_layout.add_widget(delete_button)

        self.add_widget(button_layout)

    def update_note(self, title, body):
        self.title_label.text = title
        self.body_label.text = body

    def edit_note(self):
        # Call the edit callback
        self.edit_callback(self.note_id, self.title_label.text, self.body_label.text)

    def share_note(self):
        # Call the share callback
        self.share_callback(self.note_id, self.title_label.text, self.body_label.text)

    def delete_note(self):
        # Call the delete callback
        self.delete_callback(self.note_id, self)
