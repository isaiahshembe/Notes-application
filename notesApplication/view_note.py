from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import ScrollView

class ViewNoteScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout for the view note screen
        self.layout = MDBoxLayout(orientation='vertical', padding="12dp", spacing="12dp")
        
        # Top app bar with a back button
        self.top_bar = MDTopAppBar(
            title="View Note",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=10,
            pos_hint={"top": 1}
        )
        self.layout.add_widget(self.top_bar)
        
        # Title label (read-only)
        self.title_label = MDLabel(
            text="",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height="50dp"
        )
        self.layout.add_widget(self.title_label)
        
        # Body label (read-only) wrapped in ScrollView for long text
        self.body_label = MDLabel(
            text="",
            font_style="Body1",
            halign="left",
            size_hint_y=None,  # Allow dynamic resizing
        )
        
        # Wrap body label in ScrollView to make it scrollable if content is large
        scroll_view = ScrollView()
        scroll_view.add_widget(self.body_label)
        
        self.layout.add_widget(scroll_view)
        
        self.add_widget(self.layout)

    def display_note(self, note_id, title, body):
        # Display note content on the view note screen
        self.note_id = note_id
        self.title_label.text = title
        self.body_label.text = body

    def go_back(self):
        # Switch back to the main screen using the screen manager
        self.manager.current = 'main'
