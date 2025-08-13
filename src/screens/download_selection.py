from textual.screen import Screen
from textual.widgets import Footer, Button, Label, Header, SelectionList
from textual.widgets.selection_list import Selection
from textual.app import ComposeResult
from screens.download_progress import ThemeDownloadProgressScreen

class ThemeDownloadSelectionScreen(Screen):   
    def __init__(self):
        super().__init__()
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Select themes to download:")
        yield SelectionList(*[Selection(theme_name.capitalize(), theme_name) for theme_name in self.app.manifest["themes"]])
        yield Button("Start Download", id="start")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main screen
        elif event.button.id == "start":
            self.app.push_screen(ThemeDownloadProgressScreen(self.query_one(SelectionList).selected))