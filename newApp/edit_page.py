from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from database import update_note_in_db, get_all_notes


class EditPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_id = None  # To store the current note's ID

        # Layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title Input
        self.title_input = TextInput(hint_text="Edit Title", multiline=False)
        layout.add_widget(self.title_input)

        # Body Input
        self.body_input = TextInput(hint_text="Edit Note", multiline=True)
        layout.add_widget(self.body_input)

        # Save Button
        save_button = Button(text="Save Changes", size_hint=(1, 0.2))
        save_button.bind(on_press=self.save_note_changes)
        layout.add_widget(save_button)

        # Cancel Button
        cancel_button = Button(text="Cancel", size_hint=(1, 0.2))
        cancel_button.bind(on_press=self.go_to_main_page)
        layout.add_widget(cancel_button)

        self.add_widget(layout)

    def load_note_for_edit(self, note_id):
        """Load the selected note's details into the text fields for editing."""
        self.note_id = note_id
        notes = get_all_notes()

        for note in notes:
            if note[0] == note_id:
                self.title_input.text = note[1]
                self.body_input.text = note[2]
                break

    def save_note_changes(self, instance):
        """Save the updated note information to the database."""
        updated_title = self.title_input.text.strip()
        updated_body = self.body_input.text.strip()

        if updated_title and updated_body:
            update_note_in_db(self.note_id, updated_title, updated_body)
            print(f"Updated Note {self.note_id}: {updated_title}")

            # Return to main page
            self.manager.current = 'main_page'
            main_page = self.manager.get_screen('main_page')
            main_page.refresh_notes()  # Refresh the displayed notes

    def go_to_main_page(self, instance):
        """Return to the main page without saving changes."""
        self.manager.current = 'main_page'
