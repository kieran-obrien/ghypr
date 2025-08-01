from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Button, Static, Label, ListItem, ListView, Header
import os, pathlib, re

class GhibliThemeSwitcher(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    
    def __init__(self, movies):
        super().__init__()
        self.movies = movies

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield ListView(*self.movies)
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
        self.styles.height = 3
    
    def on_mount(self):
        self.mount(Horizontal(Label(self.theme_name.capitalize()), create_color_preview_squares(self.theme_colours)))

def create_color_preview_squares(colors):
    squares = []
    for c in colors:
        square = Static("")          
        square.styles.background = c
        square.styles.width = 2        
        square.styles.height = 1  
        squares.append(square)
    return Horizontal(*squares)
    
def get_theme_colours_from_css(config_path, theme_name):
    css_path = config_path / theme_name / "styles.css"
    css_raw_text = css_path.read_text()
    color_pattern_regex = r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"
    theme_colors = re.findall(color_pattern_regex, css_raw_text)
    return theme_colors
        
def main():
    config_path = pathlib.Path.home() / ".config" / "ghypr"
    if not config_path.exists():
        raise FileNotFoundError(f"Config directory not found: {config_path}")

    theme_names = sorted([p.name for p in config_path.iterdir() if p.is_dir()])
    movies = [ThemeListItem(name.capitalize(), get_theme_colours_from_css(config_path, name)) for name in theme_names]
    
    app = GhibliThemeSwitcher(movies)
    app.run()
    
if __name__ == "__main__":
    main()
