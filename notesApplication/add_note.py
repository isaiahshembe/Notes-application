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
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import datetime

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
        self.top_app_bar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
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

        # 1) Date field with a calendar icon
        today_str = datetime.datetime.now().strftime("%A, %d %B %Y")
        self.date_field = MDTextField(
            text=today_str,
            icon_left="calendar",
            mode="rectangle",
            line_color_focus=get_color_from_hex("#000000"),
            hint_text_color_normal=get_color_from_hex("#000000"),
            readonly=True,
        )
        # Set text color after creation
        try:
            self.date_field.text_color_normal = get_color_from_hex("#000000")
        except Exception as e:
            self.date_field.foreground_color = get_color_from_hex("#000000")
        scroll_layout.add_widget(self.date_field)

        # 2) Title input with placeholder "Add title"
        self.title_input = MDTextField(
            hint_text="Add title",
            mode="rectangle",
            line_color_focus=get_color_from_hex("#000000"),
            hint_text_color_normal=get_color_from_hex("#000000"),
        )
        try:
            self.title_input.text_color_normal = get_color_from_hex("#000000")
        except Exception as e:
            self.title_input.foreground_color = get_color_from_hex("#000000")
        scroll_layout.add_widget(self.title_input)

        # 3) Toolbar for icons (numbered circles, table, image, emoji, etc.)
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
            height=dp(48),
            spacing=dp(10)
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

        # Add image icon button with tooltip
        add_image_button = IconWithTooltip(
            icon="image-outline",  # You can choose a suitable image icon
            tooltip_text="Add Image",
            on_release=self.add_image
        )

        # Add emoji icon button with tooltip
        add_emoji_button = IconWithTooltip(
            icon="emoticon-happy-outline",  # Choose an emoji icon
            tooltip_text="Add Emoji",
            on_release=self.add_emoji
        )

        # Add all toolbar buttons
        icon_toolbar.add_widget(numbered_circle_button)
        icon_toolbar.add_widget(create_table_button)
        icon_toolbar.add_widget(add_image_button)
        icon_toolbar.add_widget(add_emoji_button)
        scroll_layout.add_widget(icon_toolbar)

        # 4) Body input with placeholder "Start typing here..."
        self.body_input = MDTextField(
            hint_text="Start typing here...",
            multiline=True,
            mode="rectangle",
            line_color_focus=get_color_from_hex("#000000"),
            hint_text_color_normal=get_color_from_hex("#000000"),
            font_size=16,
            size_hint_y=None,
            height=dp(200),
        )
        try:
            self.body_input.text_color_normal = get_color_from_hex("#000000")
        except Exception as e:
            self.body_input.foreground_color = get_color_from_hex("#000000")
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
                height=dp(100),
            ),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="CREATE", on_release=self.create_table),
            ],
        )
        from kivymd.uix.textfield import MDTextField
        self.rows_input = MDTextField(hint_text="Rows", mode="rectangle")
        self.columns_input = MDTextField(hint_text="Columns", mode="rectangle")
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
        """Add a numbered item at the end of the body text."""
        numbered_line = f"{self.circle_counter}. "
        self.body_input.text += ("\n" + numbered_line)
        self.circle_counter += 1

    def add_image(self, instance):
        """Stub for adding an image to the note.
           You can integrate a file chooser or pre-defined images here."""
        # For now, we'll simply append a placeholder text.
        image_placeholder = "\n[Image: your_image.png]"
        self.body_input.text += image_placeholder
        print("Add image tapped.")

    def add_emoji(self, instance):
        """Stub for adding an emoji to the note.
           You can integrate an emoji picker or a predefined list of emojis."""
        # For now, we'll simply append a sample emoji.
        emoji = " 😊"
        self.body_input.text += emoji
        print("Add emoji tapped.")

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
                    MDFlatButton(text="OK", on_release=self.close_dialog),
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
