from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.dialog import MDDialog
from whatsapp_share import WhatsAppShare
from facebook_share import share_on_facebook
from instagram_share import share_on_instagram
from twitter_share import TwitterShare

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

        # Initialize TwitterShare with your API credentials
        self.twitter_share = TwitterShare(
            api_key='your_api_key',
            api_secret_key='your_api_secret_key',
            access_token='your_access_token',
            access_token_secret='your_access_token_secret'
        )

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

    def share_on_twitter(self):
        try:
            # Share the note on Twitter using the initialized self.twitter_share instance
            self.twitter_share.share_note_on_twitter(self.note_id, self.title, self.body)
            self.show_confirmation_dialog("Twitter", success=True)
        except Exception as e:
            self.show_confirmation_dialog("Twitter", success=False)

    def show_confirmation_dialog(self, platform, success):
        if not self.dialog:
            dialog_text = f"Note shared on {platform}!"
            if not success:
                dialog_text = f"Failed to share on {platform}. Please try again."
            
            self.dialog = MDDialog(
                text=dialog_text,
                buttons=[MDFlatButton(
                    text="OK", on_release=self.close_dialog
                )],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def go_back(self):
        self.screen_manager.current = 'main'
