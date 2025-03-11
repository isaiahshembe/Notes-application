class SettingsScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(name='settings', **kwargs)
        self.app = app
        self.layout = MDBoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Theme Settings
        theme_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        theme_label = MDLabel(text="Dark Mode:", halign="left")
        self.theme_switch = MDSwitch()
        self.theme_switch.active = self.app.theme_cls.theme_style == "Dark"
        self.theme_switch.bind(active=self.on_theme_change)
        theme_box.add_widget(theme_label)
        theme_box.add_widget(self.theme_switch)
        
        # Sort Order Settings
        sort_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        sort_label = MDLabel(text="Sort Notes By:")
        self.sort_button = MDRaisedButton(
            text=self.app.current_sort_order,
            on_release=self.open_sort_menu
        )
        sort_box.add_widget(sort_label)
        sort_box.add_widget(self.sort_button)

        # Add widgets to main layout
        self.layout.add_widget(MDLabel(text="Settings", font_style="H4"))
        self.layout.add_widget(theme_box)
        self.layout.add_widget(sort_box)
        
        self.add_widget(self.layout)

    def on_theme_change(self, instance, value):
        self.app.theme_cls.theme_style = "Dark" if value else "Light"

    def open_sort_menu(self, instance):
        menu_items = [
            {"text": "Date", "on_release": lambda: self.set_sort_order("Date")},
            {"text": "Title", "on_release": lambda: self.set_sort_order("Title")},
        ]
        self.sort_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.sort_menu.open()

    def set_sort_order(self, order):
        self.app.current_sort_order = order
        self.sort_button.text = order
        self.app.load_notes()
        if hasattr(self, 'sort_menu'):
            self.sort_menu.dismiss()