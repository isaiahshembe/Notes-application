from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.dialog import MDDialog
from whatsapp_share import WhatsAppShare
from facebook_share import share_on_facebook
from twitter_share import share_on_twitter
from instagram_share import share_on_instagram

class ShareNoteScreen(MDScreen):
    def __init__(self, note_id, title, body, callback, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.note_id = note_id
        self.title = title
        self.body = body
        self.callback = callback
        self.screen_manager = screen_manager
        self.dialog = None
        self.whatsapp_share = WhatsAppShare()

        # Create a top app bar (Fixed at the top)
        top_app_bar = MDTopAppBar(
            title='Share Note',
            pos_hint={"top": 1},  # Keeps it fixed at the top
            anchor_title='left',
            md_bg_color=(0, 0.5, 1, 1),  # Blue color
            size_hint_y=None,
            height=56,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],  # Back button
        )

        # Create a vertical layout for the content
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=20,  # Add padding for better spacing
            spacing=20,  # Add space between elements
            size_hint_y=None,  # Disable automatic sizing
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))  # Adjust height dynamically

        # Create buttons for sharing on different platforms
        facebook_button = MDRaisedButton(
            text='Facebook',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},  # Center the button
            on_press=lambda x: self.share_on_facebook(),
        )

        twitter_button = MDRaisedButton(
            text='Twitter',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},  # Center the button
            on_press=lambda x: self.share_on_twitter(),
        )

        instagram_button = MDRaisedButton(
            text='Instagram',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},  # Center the button
            on_press=lambda x: self.share_on_instagram(),
        )

        whatsapp_button = MDRaisedButton(
            text='WhatsApp',
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},  # Center the button
            on_press=lambda x: self.share_on_whatsapp(),
        )

        # Add widgets to the layout
        content_layout.add_widget(facebook_button)
        content_layout.add_widget(twitter_button)
        content_layout.add_widget(instagram_button)
        content_layout.add_widget(whatsapp_button)
        content_layout.add_widget(Widget())  # Spacer for better alignment

        # Add the widgets to the screen
        self.add_widget(content_layout)  # Content
        self.add_widget(top_app_bar)  # Fixed App Bar

    def share_on_facebook(self):
        share_on_facebook(self.note_id)
        self.show_confirmation_dialog("Facebook")

    def share_on_twitter(self):
        share_on_twitter(self.note_id)
        self.show_confirmation_dialog("Twitter")

    def share_on_instagram(self):
        share_on_instagram(self.note_id)
        self.show_confirmation_dialog("Instagram")

    def share_on_whatsapp(self):
        self.whatsapp_share.share_on_whatsapp(self.note_id, self.title, self.body, lambda: self.show_confirmation_dialog("WhatsApp"))

    def show_confirmation_dialog(self, platform):
        if not self.dialog:
            self.dialog = MDDialog(
                text=f"Note shared on {platform}!",
                buttons=[
                    MDFlatButton(
                        text="OK", on_release=self.close_dialog
                    ),
                ],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def go_back(self):
        self.screen_manager.current = 'main'
