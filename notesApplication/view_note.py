from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
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
    def __init__(self, note_title="", note_body="", **kwargs):
        super().__init__(**kwargs)

        # Note data and callback placeholders
        self.note_id = None
        self.note_title = note_title
        self.note_body = note_body
        self.delete_callback = None  
        self.edit_callback = None    

        # Create an instance for WhatsApp sharing.
        self.whatsapp_share = WhatsAppShare()

        # Main container layout
        self.main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12)
        )

        # ------------------------------
        # Top Row: Back button, Date, Menu
        # ------------------------------
        self.top_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[dp(10), dp(5), dp(10), dp(5)],
            md_bg_color=get_color_from_hex("#FFA500")  # Orange background
        )

        self.back_button = MDIconButton(
            icon="arrow-left",
            text_color=get_color_from_hex("#FFFFFF"),
            on_release=self.on_back
        )

        # Date label (Centered)
        self.date_label = MDLabel(
            text="",
            font_style="H6",
            theme_text_color="Secondary",
            halign="center",
            size_hint_x=1
        )

        self.menu_button = MDIconButton(
            icon="dots-vertical",
            text_color=get_color_from_hex("#FFFFFF"),
            on_release=self.open_menu
        )

        self.top_row.add_widget(self.back_button)
        self.top_row.add_widget(self.date_label)
        self.top_row.add_widget(self.menu_button)

        # ------------------------------
        # Buttons Row: Alarm Icon (Reminder), Save, Edit
        # ------------------------------
        self.button_row = MDGridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        # Change reminder button to an alarm icon
        self.reminder_button = MDIconButton(
            icon="alarm",
            text_color=get_color_from_hex("#7B1FA2"),
            on_release=self.on_set_reminder
        )

        self.save_button = MDFlatButton(
            text="Save",
            text_color=get_color_from_hex("#7B1FA2"),
            on_release=self.on_save
        )

        self.edit_button = MDFlatButton(
            text="Edit",
            text_color=get_color_from_hex("#7B1FA2"),
            on_release=self.on_edit
        )

        self.button_row.add_widget(self.reminder_button)
        self.button_row.add_widget(self.save_button)
        self.button_row.add_widget(self.edit_button)

        # Title Label
        self.title_label = MDLabel(
            text=self.note_title,
            font_style="H5",
            theme_text_color="Primary",
            halign="left",
            size_hint_y=None,
            height=dp(50),
            padding=[dp(10), dp(5)]
        )

        # ------------------------------
        # Scrollable Body
        # ------------------------------
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.body_label = MDLabel(
            text=self.note_body,
            font_style="Body1",
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
            padding=[dp(10), dp(10)]
        )
        self.body_label.bind(texture_size=self._adjust_body_height)
        self.scroll_view.add_widget(self.body_label)

        # Set the date (formatted)
        date_str = datetime.datetime.now().strftime("%d %B %Y, %A")
        self.date_label.text = date_str

        # Adjust body height based on content
        self.body_label.texture_update()
        self._adjust_body_height()

        # Assemble the layout
        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.button_row)
        self.main_layout.add_widget(self.title_label)
        self.main_layout.add_widget(self.scroll_view)

        self.add_widget(self.main_layout)

    def _adjust_body_height(self, *args):
        """Adjust the body_label's height to fit its text."""
        self.body_label.height = self.body_label.texture_size[1]

    def on_back(self, *args):
        """Handle Back Button Press."""
        if self.manager:
            self.manager.current = 'main'

    def on_set_reminder(self, *args):
        """Open a calendar (MDDatePicker) to set a reminder."""
        date_dialog = MDDatePicker(callback=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, date_obj):
        """Callback for the selected date from MDDatePicker."""
        print("Reminder set for:", date_obj)

    def on_save(self, *args):
        """Handle Save Button Press."""
        print("Save button tapped!")

    def on_edit(self, *args):
        """Handle Edit Button Press."""
        if self.edit_callback:
            self.edit_callback(self.note_id, self.note_title, self.note_body)

    def open_menu(self, instance):
        """Opens the menu with Share and Delete options."""
        menu_items = [
            {"text": "Share", "viewclass": "OneLineListItem", "on_release": lambda: self.open_share_menu()},
            {"text": "Delete", "viewclass": "OneLineListItem", "on_release": lambda: self.on_delete()},
        ]
        self.menu = MDDropdownMenu(caller=instance, items=menu_items, width_mult=3)
        self.menu.open()

    def open_share_menu(self):
        """Opens the share menu."""
        self.menu.dismiss()
        share_menu_items = [
            {"text": "Facebook", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("Facebook")},
            {"text": "Twitter", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("Twitter")},
            {"text": "Instagram", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("Instagram")},
            {"text": "WhatsApp", "viewclass": "OneLineListItem", "on_release": lambda: self.share_option_selected("WhatsApp")},
        ]
        self.share_menu = MDDropdownMenu(caller=self.menu_button, items=share_menu_items, width_mult=3)
        self.share_menu.open()

    def share_option_selected(self, platform):
        """Handles sharing options."""
        self.share_menu.dismiss()
        try:
            if platform == "Facebook":
                share_on_facebook(self.note_id)
            elif platform == "Twitter":
                share_on_twitter(self.note_id)
            elif platform == "Instagram":
                share_on_instagram(self.note_id)
            elif platform == "WhatsApp":
                self.whatsapp_share.share_on_whatsapp(
                    self.note_id,
                    self.note_title,
                    self.note_body,
                    lambda: print("Shared on WhatsApp")
                )
        except Exception as e:
            print(f"Failed to share on {platform}: {e}")

    def on_delete(self):
        """Handles Delete action."""
        if self.delete_callback:
            self.delete_callback(self.note_id)

    def display_note(self, note_id, title, body, delete_callback, edit_callback):
        """
        Updates the screen with the given note data and callbacks.
        """
        self.note_id = note_id
        self.note_title = title
        self.note_body = body
        self.delete_callback = delete_callback
        self.edit_callback = edit_callback

        # Update UI elements
        self.title_label.text = title
        self.body_label.text = body
        self.body_label.texture_update()
        self._adjust_body_height()
