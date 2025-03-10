from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

class NoteWidget(MDCard):
    def __init__(self, note_id, title, body, delete_callback, edit_callback, share_callback, view_callback, **kwargs):
        # Save the view_callback before calling super().__init__
        self.view_callback = view_callback
        super().__init__(**kwargs)

        self.note_id = note_id  # Store the note ID
        self.delete_callback = delete_callback  # Store the delete callback
        self.edit_callback = edit_callback  # Store the edit callback
        self.share_callback = share_callback  # Store the share callback

        # Configure the card appearance
        self.orientation = "vertical"
        self.padding = "12dp"
        self.size_hint = (1, None)
        self.height = 150  # You can make this dynamic based on content
        self.elevation = 4
        self.margin = "12dp"

        # Title label
        self.title_label = MDLabel(
            text=title,
            font_style="H6",
            size_hint_y=None,
            height=30,
            halign="left",
        )
        self.add_widget(self.title_label)

        # Body label
        self.body_label = MDLabel(
            text=self.trim_body_text(body),
            font_style="Body1",
            size_hint_y=None,
            height=60,  # You can adjust this or make it dynamic if needed
            halign="left",
        )
        self.add_widget(self.body_label)

        # Button layout for Edit, Share, and Delete
        button_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=40)

        edit_button = MDIconButton(icon="pencil", on_press=lambda x: self.edit_note())
        share_button = MDIconButton(icon="share-variant", on_press=lambda x: self.share_note())
        delete_button = MDIconButton(icon="delete", on_press=lambda x: self.delete_note())

        button_layout.add_widget(edit_button)
        button_layout.add_widget(share_button)
        button_layout.add_widget(delete_button)

        self.add_widget(button_layout)

    def update_note(self, title, body):
        """Update the title and body of the note widget"""
        self.title_label.text = title
        self.body_label.text = self.trim_body_text(body)

    def trim_body_text(self, body):
        """Trim body text if it's too long, or add '...' for a preview"""
        max_length = 100  # Set a character limit for the preview
        return body if len(body) <= max_length else body[:max_length] + '...'

    def edit_note(self):
        """Trigger the edit callback"""
        self.edit_callback(self.note_id, self.title_label.text, self.body_label.text)

    def share_note(self):
        """Trigger the share callback"""
        self.share_callback(self.note_id, self.title_label.text, self.body_label.text)

    def delete_note(self):
        """Trigger the delete callback"""
        self.delete_callback(self.note_id, self)

    def on_touch_up(self, touch):
        """Handle touch event, checking if the user clicked outside the widget"""
        if not self.collide_point(*touch.pos):
            return super().on_touch_up(touch)

        # Check if the touch is inside the widget, but outside any icon button
        for child in self.walk():
            if isinstance(child, MDIconButton) and child.collide_point(*touch.pos):
                # Do nothing if the touch is on any icon button
                return super().on_touch_up(touch)

        # Check if the touch is on the title or body labels
        if self.title_label.collide_point(*touch.pos) or self.body_label.collide_point(*touch.pos):
            # Trigger the view callback only if the title or body is clicked
            self.view_callback(self.note_id, self.title_label.text, self.body_label.text)
            return True

        return super().on_touch_up(touch)