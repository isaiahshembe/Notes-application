from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFloatingActionButton


class AddNoteScreen(MDScreen):
    def __init__(self, add_note_callback, screen_manager, conn, **kwargs):
        super().__init__(**kwargs)
        self.add_note_callback = add_note_callback
        self.screen_manager = screen_manager
        self.conn = conn

        # Main layout (vertical)
        main_layout = BoxLayout(orientation='vertical')

        # --------------------------------------------------
        # Top App Bar
        # --------------------------------------------------
        self.top_app_bar = MDTopAppBar(
            title="Add Note",
            anchor_title='left',
            size_hint_y=None,
            height=56,
            pos_hint={"top": 1},
        )
        # Back arrow to return to main screen
        self.top_app_bar.left_action_items = [
            ["arrow-left", lambda x: setattr(self.screen_manager, 'current', 'main')]
        ]
        main_layout.add_widget(self.top_app_bar)

        # --------------------------------------------------
        # Scrollable area for note inputs
        # --------------------------------------------------
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_layout = BoxLayout(
            orientation='vertical',
            padding=12,
            spacing=12,
            size_hint_y=None
        )
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Title input
        self.title_input = TextInput(
            hint_text="Title",
            size_hint=(1, None),
            height=48,
            multiline=False,
            font_size=18,
        )
        scroll_layout.add_widget(self.title_input)

        # Body input
        self.body_input = TextInput(
            hint_text="Type something...",
            size_hint=(1, None),
            height=300,
            multiline=True,
            font_size=16
        )
        scroll_layout.add_widget(self.body_input)

        scroll_view.add_widget(scroll_layout)
        main_layout.add_widget(scroll_view)

        # --------------------------------------------------
        # Floating "Save" Button
        # --------------------------------------------------
        self.save_button = MDFloatingActionButton(
            icon="content-save",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.save_note
        )
        main_layout.add_widget(self.save_button)

        # Add the main layout to the screen
        self.add_widget(main_layout)

    def save_note(self, instance):
        """Save the note and return to main screen."""
        title = self.title_input.text.strip()
        body = self.body_input.text.strip()

        # Call the callback that actually inserts into DB
        self.add_note_callback(title, body)

        # Clear the inputs
        self.title_input.text = ""
        self.body_input.text = ""

        # Navigate back to main screen
        self.screen_manager.current = 'main'
