from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class AddNoteScreen(MDScreen):
    def __init__(self, add_note_callback, screen_manager, conn, **kwargs):
        super().__init__(**kwargs)
        self.add_note_callback = add_note_callback
        self.screen_manager = screen_manager
        self.conn = conn
        self.dialog = None

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
            ["arrow-left", lambda x: self.go_back()]
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

        # Table creation inputs
        table_creation_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=48)
        self.rows_input = TextInput(hint_text="Rows", size_hint=(0.4, 1), multiline=False)
        self.columns_input = TextInput(hint_text="Columns", size_hint=(0.4, 1), multiline=False)
        create_table_button = Button(text="Create Table", size_hint=(0.2, 1), on_press=self.create_table)
        table_creation_layout.add_widget(self.rows_input)
        table_creation_layout.add_widget(self.columns_input)
        table_creation_layout.add_widget(create_table_button)
        scroll_layout.add_widget(table_creation_layout)

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

    def create_table(self, instance):
        """Create a fully enclosed table in the body_input based on the specified rows and columns."""
        try:
            rows = int(self.rows_input.text)
            columns = int(self.columns_input.text)
        except ValueError:
            print("Please enter valid numbers for rows and columns.")
            return

        if rows <= 0 or columns <= 0:
            print("Rows and columns must be greater than 0.")
            return

        # Generate the table structure
        table = ""
        # Create the horizontal border
        horizontal_border = "+" + ("-" * 10 + "+") * columns + "\n"
        # Create the row template
        row_template = "|" + (" " * 10 + "|") * columns + "\n"

        # Build the table
        table += horizontal_border
        for _ in range(rows):
            table += row_template
            table += horizontal_border

        # Insert the table into the body_input
        self.body_input.text = table

    def save_note(self, instance):
        """Save the note and return to main screen."""
        title = self.title_input.text.strip()
        body = self.body_input.text.strip()

        # Ensure fields are not empty
        if title and body:
            # Call the callback that actually inserts into DB
            self.add_note_callback(title, body)

            # Clear the inputs
            self.title_input.text = ""
            self.body_input.text = ""

            # Navigate back to main screen
            self.show_confirmation_dialog()
        else:
            print("Title and body cannot be empty.")

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
        self.go_back()

    def go_back(self, obj=None):
        # Navigate back to main screen
        self.screen_manager.current = 'main'