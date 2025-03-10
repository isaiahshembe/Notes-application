from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton

class Menu:
    def __init__(self, callback):
        self.callback = callback
        self.menu_items = [
            {
                "text": "Add New Note",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Add New Note": self.menu_callback(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=None,
            items=self.menu_items,
            width_mult=4,
        )

    def open_menu(self, instance_menu):
        self.menu.caller = instance_menu
        self.menu.open()

    def menu_callback(self, instance_menu):
        if instance_menu == "Add New Note":
            self.callback()
        self.menu.dismiss()
