from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import datetime

# Import share functions (assumed implemented elsewhere)
from whatsapp_share import WhatsAppShare
from facebook_share import share_on_facebook
from twitter_share import share_on_twitter
from instagram_share import share_on_instagram


class ViewNoteScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Note data and callback placeholders
        self.note_id = None
        self.note_title = ""
        self.note_body = ""
        self.delete_callback = None  # Called when deletion is confirmed.
        self.edit_callback = None    # Called when editing is requested.

        # Create an instance for WhatsApp sharing.
        self.whatsapp_share = WhatsAppShare()

        # Main container layout
        self.main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12)
        )

        # Top row: Back button, Date, "Set Reminder", "Save", "Edit", and a three-dot menu icon.
        self.top_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )

        # Back button
        self.back_button = MDIconButton(
            icon="arrow-left",
            text_color=get_color_from_hex("#000000"),
            on_release=self.on_back
        )

        # Date label (e.g., "20 February 2025, Thursday")
        self.date_label = MDLabel(
            text="",
            font_style="H6",
            theme_text_color="Primary",
            halign="left"
        )

        # "Set Reminder" button
        self.reminder_button = MDFlatButton(
            text="Set Reminder",
            text_color=get_color_from_hex("#7B1FA2"),
            on_release=self.on_set_reminder
        )

        # "Save" button
        self.save_button = MDFlatButton(
            text="Save",
            text_color=get_color_from_hex("#7B1FA2"),
            on_release=self.on_save
        )

        # "Edit" button
        self.edit_button = MDFlatButton(
            text="Edit",
            text_color=get_color_from_hex("#7B1FA2"),
            on_release=self.on_edit
        )

        # Three-dot menu button for additional options (Share and Delete)
        self.menu_button = MDIconButton(
            icon="dots-vertical",
            text_color=get_color_from_hex("#000000"),
            on_release=self.open_menu
        )

        # Add the back button first, then the rest of the top row widgets.
        self.top_row.add_widget(self.back_button)
        self.top_row.add_widget(self.date_label)
        self.top_row.add_widget(self.reminder_button)
        self.top_row.add_widget(self.save_button)
        self.top_row.add_widget(self.edit_button)
        self.top_row.add_widget(self.menu_button)

        # Title label for the note
        self.title_label = MDLabel(
            text="",
            font_style="H5",
            theme_text_color="Primary",
            halign="left",
            size_hint_y=None,
            height=dp(40),
        )

        # Scrollable body area (in case of long notes)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.body_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None
        )
        self.body_label.bind(texture_size=self._adjust_body_height)
        self.scroll_view.add_widget(self.body_label)

        # Assemble the layout
        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.title_label)
        self.main_layout.add_widget(self.scroll_view)
        self.add_widget(self.main_layout)

    def display_note(self, note_id, title, body, delete_callback=None, edit_callback=None):
        """
        Populates the screen with the note's details.
        :param note_id: The note's database ID.
        :param title: The note's title.
        :param body: The note's content.
        :param delete_callback: Function to call when deletion is confirmed.
        :param edit_callback: Function to call when editing is requested.
        """
        self.note_id = note_id
        self.note_title = title
        self.note_body = body
        self.delete_callback = delete_callback
        self.edit_callback = edit_callback

        # Set the date (for example, using the current date)
        date_str = datetime.datetime.now().strftime("%d %B %Y, %A")
        self.date_label.text = date_str

        # Update title and body labels
        self.title_label.text = title
        self.body_label.text = body
        self.body_label.texture_update()
        self._adjust_body_height()

    def _adjust_body_height(self, *args):
        """Adjust the body_label's height to fit its text."""
        self.body_label.height = self.body_label.texture_size[1]

    def on_back(self, *args):
        """Called when the back button is tapped. Switches to the main screen if possible."""
        print("Back button tapped!")
        if self.manager:
            self.manager.current = 'main'

    def on_set_reminder(self, *args):
        """Callback for when 'Set Reminder' is tapped."""
        print("Set Reminder tapped!")
        # Add your reminder logic here (e.g., open a date/time picker)

    def on_save(self, *args):
        """Callback for when 'Save' is tapped."""
        print("Save button tapped!")
        # Insert your save logic here (e.g., update note in database)

    def on_edit(self, *args):
        """Callback for when 'Edit' is tapped."""
        print("Edit button tapped!")
        if self.edit_callback:
            self.edit_callback(self.note_id, self.note_title, self.note_body)
        else:
            print("No edit callback provided.")

    def open_menu(self, instance):
        """
        Opens the first dropdown menu with 'Share' and 'Delete' options.
        """
        menu_items = [
            {
                "text": "Share",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.open_share_menu()
            },
            {
                "text": "Delete",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.on_delete()
            },
        ]

        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()

    def open_share_menu(self):
        """
        Dismisses the first menu and opens a share menu with multiple platforms.
        """
        self.menu.dismiss()  # Close the previous menu

        share_menu_items = [
            {
                "text": "Share via Facebook",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("Facebook")
            },
            {
                "text": "Share via Twitter",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("Twitter")
            },
            {
                "text": "Share via Instagram",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("Instagram")
            },
            {
                "text": "Share via WhatsApp",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.share_option_selected("WhatsApp")
            },
        ]

        self.share_menu = MDDropdownMenu(
            caller=self.menu_button,
            items=share_menu_items,
            width_mult=3,
        )
        self.share_menu.open()

    def share_option_selected(self, platform):
        """
        Called when a specific share option is selected.
        Attempts to share the note using the appropriate method.
        """
        self.share_menu.dismiss()
        if platform == "Facebook":
            try:
                share_on_facebook(self.note_id)
                print("Shared on Facebook")
            except Exception as e:
                print("Failed to share on Facebook:", e)
        elif platform == "Twitter":
            try:
                share_on_twitter(self.note_id)
                print("Shared on Twitter")
            except Exception as e:
                print("Failed to share on Twitter:", e)
        elif platform == "Instagram":
            try:
                share_on_instagram(self.note_id)
                print("Shared on Instagram")
            except Exception as e:
                print("Failed to share on Instagram:", e)
        elif platform == "WhatsApp":
            try:
                self.whatsapp_share.share_on_whatsapp(
                    self.note_id, self.note_title, self.note_body, lambda: print("Shared on WhatsApp")
                )
            except Exception as e:
                print("Failed to share on WhatsApp:", e)

    def on_delete(self):
        """Called when 'Delete' is selected; executes the delete callback if provided."""
        self.menu.dismiss()
        print("Delete tapped!")
        if self.delete_callback:
            self.delete_callback(self.note_id)             
