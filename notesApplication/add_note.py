from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFloatingActionButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.pickers import MDDatePicker  # Correct import

class IconWithTooltip(MDIconButton, MDTooltip):
    pass

class AddNoteScreen(MDScreen):
    def __init__(self, add_note_callback, screen_manager, conn, **kwargs):
        super().__init__(**kwargs)
        self.add_note_callback = add_note_callback
        self.screen_manager = screen_manager
        self.conn = conn
        self.dialog = None
        self.circle_counter = 1  # Counter for numbered circles

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

        # Calendar button
        self.calendar_button = Button(
            text="Select Date",
            size_hint=(1, None),
            height=48,
            on_release=self.show_date_picker
        )
        scroll_layout.add_widget(self.calendar_button)

        # Toolbar for icons (like in your image)
        icon_toolbar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=48,
            spacing=10
        )

        # Numbered circle icon button with tooltip
        numbered_circle_button = IconWithTooltip(
            icon="format-list-numbered",
            tooltip_text="Add Numbered Item",
            on_release=self.add_numbered_circle
        )

        # Create table icon button with tooltip
        create_table_button = IconWithTooltip(
            icon="table",
            tooltip_text="Insert Table",
            on_release=self.show_table_dialog
        )

        # Add icons to toolbar
        icon_toolbar.add_widget(numbered_circle_button)
        icon_toolbar.add_widget(create_table_button)

        # Add toolbar to layout
        scroll_layout.add_widget(icon_toolbar)

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

    # --------------------- Existing Functions --------------------- #

    def show_table_dialog(self, instance):
        """Show a dialog to input rows and columns for table creation."""
        self.dialog = MDDialog(
            title="Create Table",
            type="custom",
            content_cls=BoxLayout(
                orientation='vertical',
                spacing=12,
                size_hint_y=None,
                height=100,
            ),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="CREATE", on_release=self.create_table),
            ],
        )
        self.rows_input = TextInput(hint_text="Rows", multiline=False)
        self.columns_input = TextInput(hint_text="Columns", multiline=False)
        self.dialog.content_cls.add_widget(self.rows_input)
        self.dialog.content_cls.add_widget(self.columns_input)

        self.dialog.open()

    def create_table(self, instance):
        """Create a table based on the rows and columns input."""
        try:
            rows = int(self.rows_input.text)
            columns = int(self.columns_input.text)
        except ValueError:
            print("Please enter valid numbers for rows and columns.")
            return

        if rows <= 0 or columns <= 0:
            print("Rows and columns must be greater than 0.")
            return

        table = ""
        horizontal_border = "+" + ("-" * 10 + "+") * columns + "\n"
        row_template = "|" + (" " * 10 + "|") * columns + "\n"

        table += horizontal_border
        for _ in range(rows):
            table += row_template
            table += horizontal_border

        existing_text = self.body_input.text
        self.body_input.text = existing_text + "\n" + table
        self.dialog.dismiss()

    def add_numbered_circle(self, instance):
        """Add a numbered circle to the body_input at the current cursor position."""
        cursor_pos = self.body_input.cursor_index()
        numbered_circle = f"{self.circle_counter}. "  # Simple number instead of circle for compatibility
        self.body_input.text = (
            self.body_input.text[:cursor_pos] + numbered_circle + self.body_input.text[cursor_pos:]
        )
        self.body_input.cursor = (cursor_pos + len(numbered_circle), cursor_pos + len(numbered_circle))
        self.circle_counter += 1

    def save_note(self, instance):
        """Save the note and return to main screen."""
        title = self.title_input.text.strip()
        body = self.body_input.text.strip()
        date = self.calendar_button.text  # Get the selected date

        if title and body:
            self.add_note_callback(title, body, date)  # Pass the date to the callback
            self.title_input.text = ""
            self.body_input.text = ""
            self.show_confirmation_dialog()
        else:
            print("Title, body and date cannot be empty.")

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
        self.screen_manager.current = 'main'

    def show_date_picker(self, instance):
        """Show a date picker dialog."""
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.on_date_selected)  # Bind to the on_save event
        date_picker.open()

    def on_date_selected(self, instance, date, *args):
        """Handle the selected date."""
        self.calendar_button.text = date.strftime("%Y-%m-%d")

    def go_back(self, obj=None):
        self.screen_manager.current = 'main'