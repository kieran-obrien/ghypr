from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Button, Static, Label, ListItem, ListView, Header
import os, pathlib

class GhibliThemeSwitcher(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    
    def __init__(self, movies):
        super().__init__()
        self.movies = movies

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield ListView(*self.movies)
        yield ListView(ThemeListItem("test_name", ["#ff6b6b", "#4ecdc4", "#ffe66d"]))
        yield Footer()
        
    def on_mount(self) -> None:
        self.title = "ghypr"
        self.sub_title = "Choose a theme:"

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

class ThemeListItem(ListItem):
    def __init__(self, theme_name, theme_colours):
        super().__init__()
        self.theme_name = theme_name
        self.theme_colours = theme_colours
    
    def _on_mount(self):
        self.mount(Horizontal(Label(self.theme_name.capitalize()), create_color_preview(self.theme_colours)))

def create_color_preview(colors):
    print(colors)
    squares = []
    for c in colors:
        square = Static("")             # create the widget
        square.styles.background = c    # set background color
        square.styles.width = 2         # set width
        square.styles.height = 1        # set height
        squares.append(square)
    return Horizontal(*squares)
  
def main():
    config_path = pathlib.Path.home() / ".config" / "ghypr"
    if not config_path.exists():
        raise FileNotFoundError(f"Config directory not found: {config_path}")

    themes = sorted([p.name for p in config_path.iterdir() if p.is_dir()])
    movies = [ListItem(Label(name.capitalize())) for name in themes]
    
    app = GhibliThemeSwitcher(movies)
    app.run()
    
if __name__ == "__main__":
    main()
