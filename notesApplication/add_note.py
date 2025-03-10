from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel

class AddNoteScreen(MDScreen):
    def __init__(self, add_note_callback, screen_manager, conn, **kwargs):
        super().__init__(**kwargs)
        self.add_note_callback = add_note_callback
        self.screen_manager = screen_manager
        self.conn = conn

        # Main layout
        main_layout = BoxLayout(orientation='vertical')

        # Top App Bar
        self.top_app_bar = MDTopAppBar(
            title="Add Note",
            anchor_title='left',
            size_hint_y=None,
            height=56,
            pos_hint={"top": 1},
        )
        self.top_app_bar.left_action_items = [
            ["arrow-left", lambda x: setattr(self.screen_manager, 'current', 'main')]
        ]
        main_layout.add_widget(self.top_app_bar)

        # Toolbar for editing options
        edit_toolbar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            padding=5,
            spacing=10
        )

        # Editing buttons
        self.bold_btn = MDIconButton(icon="format-bold", on_release=lambda x: self.apply_format("**"))
        self.italic_btn = MDIconButton(icon="format-italic", on_release=lambda x: self.apply_format("*"))
        self.underline_btn = MDIconButton(icon="format-underline", on_release=lambda x: self.apply_format("__"))
        self.strikethrough_btn = MDIconButton(icon="format-strikethrough", on_release=lambda x: self.apply_format("~~"))
        self.undo_btn = MDIconButton(icon="undo", on_release=lambda x: self.undo_action())
        self.redo_btn = MDIconButton(icon="redo", on_release=lambda x: self.redo_action())

        for btn in [self.bold_btn, self.italic_btn, self.underline_btn, self.strikethrough_btn, self.undo_btn, self.redo_btn]:
            edit_toolbar.add_widget(btn)

        main_layout.add_widget(edit_toolbar)

        # Font selection
        self.font_label = MDLabel(text="Font: ", size_hint_x=None, width=50, theme_text_color="Secondary")
        self.font_button = MDIconButton(icon="format-font", on_release=self.open_font_menu)
        self.selected_font = "Roboto"

        # Font dropdown menu
        self.font_options = ["Roboto", "Arial", "Courier", "Georgia", "Times New Roman", "Comic Sans MS"]
        self.font_menu_items = [
            {"viewclass": "OneLineListItem", "text": font, "on_release": lambda x=font: self.set_font(x)}
            for font in self.font_options
        ]
        self.font_menu = MDDropdownMenu(
            caller=self.font_button,
            items=self.font_menu_items,
            width_mult=4
        )

        font_toolbar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=50, padding=5, spacing=10)
        font_toolbar.add_widget(self.font_label)
        font_toolbar.add_widget(self.font_button)
        main_layout.add_widget(font_toolbar)

        # Scrollable area for note input
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_layout = BoxLayout(orientation='vertical', padding=12, spacing=12, size_hint_y=None)
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
            font_size=16,
            font_name=self.selected_font
        )
        scroll_layout.add_widget(self.body_input)

        scroll_view.add_widget(scroll_layout)
        main_layout.add_widget(scroll_view)

        # Save button
        self.save_button = MDFloatingActionButton(
            icon="content-save",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.save_note
        )
        main_layout.add_widget(self.save_button)

        # Scrollable layout for displaying saved notes
        self.notes_layout = BoxLayout(orientation='vertical', padding=12, spacing=12, size_hint_y=None)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))

        scroll_view_notes = ScrollView(size_hint=(1, 1))
        scroll_view_notes.add_widget(self.notes_layout)
        main_layout.add_widget(scroll_view_notes)

        self.add_widget(main_layout)

        # Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        self.store_undo_state()
        self.body_input.bind(text=self.track_changes)

    def open_font_menu(self, instance):
        """Opens the font selection menu."""
        self.font_menu.open()

    def set_font(self, font):
        """Sets the selected font."""
        self.selected_font = font
        self.body_input.font_name = font
        self.font_menu.dismiss()

    def apply_format(self, symbol):
        """Applies formatting to selected text or inserts format markers."""
        start, end = self.body_input.selection_text_start, self.body_input.selection_text_end
        if start != end:
            # Wrap selected text
            selected_text = self.body_input.text[start:end]
            new_text = f"{symbol}{selected_text}{symbol}"
            self.body_input.text = self.body_input.text[:start] + new_text + self.body_input.text[end:]
            self.body_input.cursor = (end + len(symbol) * 2, 0)
        else:
            # Insert format markers at cursor position
            cursor_pos = self.body_input.cursor_index()
            self.body_input.text = self.body_input.text[:cursor_pos] + f"{symbol}{symbol}" + self.body_input.text[cursor_pos:]
            self.body_input.cursor = (cursor_pos + len(symbol), 0)

        self.store_undo_state()

    def track_changes(self, instance, value):
        """Tracks text changes for undo/redo."""
        if not self.undo_stack or self.undo_stack[-1] != value:
            self.store_undo_state()

    def store_undo_state(self):
        """Stores the current text for undo."""
        self.undo_stack.append(self.body_input.text)

    def undo_action(self):
        """Undo the last text change."""
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.body_input.text = self.undo_stack[-1]

    def redo_action(self):
        """Redo the last undone change."""
        if self.redo_stack:
            new_text = self.redo_stack.pop()
            self.undo_stack.append(new_text)
            self.body_input.text = new_text

    def save_note(self, instance):
        """Save the note and return to main screen."""
        title = self.title_input.text.strip()
        body = self.body_input.text.strip()
        
        # Create a new note label and menu
        note_label = MDLabel(
            text=title if title else "Untitled", 
            size_hint_y=None, 
            height=40,
            font_style="H6"
        )
        
        # Create a three-dot icon button for each note
        more_options_button = MDIconButton(
            icon="dots-vertical", 
            on_release=lambda x: self.show_note_menu(x, title, body)
        )
        
        note_layout = MDBoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=40,
            padding=5,
            spacing=10
        )
        note_layout.add_widget(note_label)
        note_layout.add_widget(more_options_button)

        # Add this note to the layout
        self.notes_layout.add_widget(note_layout)

        # Callback to add the note (optional if needed)
        self.add_note_callback(title, body)
        
        # Clear the inputs
        self.title_input.text = ""
        self.body_input.text = ""
        self.screen_manager.current = 'main'

    def show_note_menu(self, instance, title, body):
        """Display the dropdown menu with options for the note."""
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Edit", "on_release": lambda x: self.edit_note(title, body)},
            {"viewclass": "OneLineListItem", "text": "Share", "on_release": lambda x: self.share_note(title, body)},
            {"viewclass": "OneLineListItem", "text": "Delete", "on_release": lambda x: self.delete_note(title)}
        ]
        
        menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4
        )
        
        menu.open()

    def edit_note(self, title, body):
        """Edit the selected note."""
        # Logic to edit the note (can be used to navigate back to the AddNoteScreen with existing title and body)
        self.title_input.text = title
        self.body_input.text = body
        self.screen_manager.current = 'add_note'

    def share_note(self, title, body):
        """Share the selected note."""
        # Logic for sharing the note (for now, we just print the note)
        print(f"Sharing note: {title}\n{body}")

    def delete_note(self, title):
        """Delete the selected note."""
        # Logic to delete the note (remove from UI, database, etc.)
        for note in self.notes_layout.children:
            if note.children[0].text == title:
                self.notes_layout.remove_widget(note)
                break
