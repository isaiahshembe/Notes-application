import webbrowser
import platform
import pywhatkit
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton


class WhatsAppShare:
    def __init__(self):
        self.dialog = None
        self.phone_number_field = None

    def share_on_whatsapp(self, note_id, title, body, callback):
        # Format the note's content
        message = f"Title: {title}\n\n{body}"

        if platform.system() in ["Android", "iOS"]:
            # For mobile devices, use WhatsApp URL intent
            self.share_on_mobile(note_id, message)
        else:
            # For desktop, use pywhatkit
            self.show_phone_number_dialog(note_id, message, callback)

    def share_on_mobile(self, note_id, message):
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/?text={encoded_message}"
        webbrowser.open(whatsapp_url)
        print(f"Sharing note {note_id} on WhatsApp (mobile)...")

    def show_phone_number_dialog(self, note_id, message, callback):
        if not self.dialog:
            # Create a text field for phone number input
            self.phone_number_field = MDTextField(
                hint_text="Phone Number (with country code)",
                multiline=False,
                size_hint_x=1,
                helper_text="Example: +1234567890",
                helper_text_mode="on_focus",
            )

            # Create a layout to hold the text field
            content_layout = MDBoxLayout(
                orientation="vertical",
                spacing=10,
                padding=10,
                size_hint=(1, None),
                height=50,
            )
            content_layout.add_widget(self.phone_number_field)

            # Create the dialog with the text field as content_cls
            self.dialog = MDDialog(
                title="Enter Recipient's Phone Number",
                type="custom",
                content_cls=content_layout,
                buttons=[
                    MDFlatButton(
                        text="Cancel", on_release=self.close_dialog
                    ),
                    MDFlatButton(
                        text="Share", on_release=lambda x: self.share_on_desktop(note_id, message, callback)
                    ),
                ],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        if self.dialog:
            self.dialog.dismiss()

    def share_on_desktop(self, note_id, message, callback):
        phone_number = self.phone_number_field.text.strip()
        if not phone_number:
            print("Phone number is required!")
            return

        try:
            pywhatkit.sendwhatmsg_instantly(phone_number, message)
            print(f"Sharing note {note_id} on WhatsApp (desktop)...")
            callback()
        except Exception as e:
            print(f"An error occurred while sharing on WhatsApp: {e}")
        finally:
            self.close_dialog(None)
