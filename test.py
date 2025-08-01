import httpx
import asyncio
from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Button, Static, Label, ListItem, ListView, Header, SelectionList, ProgressBar
from textual.widgets.selection_list import Selection
import re
from pathlib import Path

class GhibliThemeSwitcher(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    
    def __init__(self, movies):
        super().__init__()
        self.movies = movies

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Button("Download Themes", id="download")
        yield ListView(*self.movies)
        yield Footer()
        
    def on_mount(self) -> None:
        self.title = "ghypr"
        self.sub_title = "Ghibli inspired theme switcher!"
        self.push_screen(ManifestLoaderScreen())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download":
            self.push_screen(DownloadScreen())  
            
class ManifestLoaderScreen(Screen):
    def __init__(self):
        super().__init__()
        self.ok_button = Button("OK", id="ok")
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Loading theme manifest from .config/ghypr")
        yield self.ok_button
        yield Footer()
        
    def on_mount(self):
        self.call_later(self.check_manifest)  # schedule async task right after mount
        
    @work(exclusive=True)       
    async def check_manifest(self):
        # In future will load manifest from assets repo       
        #async with httpx.AsyncClient(timeout=None) as client:
         #   for url in test_urls:
           #     save_path = Path.home() / f"{url.split('/')[-3]}.jpg"
            #    await download_file(client, url, save_path)
             #   self.progress.advance(1)  # update progress bar
        
        manifest_path = Path.home() / ".config" / "ghypr" / "manifest.json"
        if not manifest_path.exists():
            self.query_one(Label).update(f"Manifest not present. Downloading from ghypr assets...")
        
        await asyncio.sleep(3)
        self.ok_button.disabled = False
        self.query_one(Label).update("Manifest check complete! Click OK to continue.")
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.app.pop_screen()
    
        
class DownloadScreen(Screen):   
    def __init__(self):
        super().__init__()
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Select themes to download:")
        yield SelectionList[str](  
            Selection("Howl's Moving Castle", "howls"),
            Selection("Spirited Away", "spirited"),
            Selection("Laputa: Castle in the Sky", "laputa"),
        )
        yield Button("Start Download", id="start")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main screen
        elif event.button.id == "start":
            self.app.push_screen(DownloadProgressScreen([1, 2, 3, 4, 5]))
            
class DownloadProgressScreen(Screen):
    def __init__(self, themes_selection):
        super().__init__()
        self.themes = themes_selection
        
    def compose(self) -> ComposeResult:
        self.progress = ProgressBar(total=len(self.themes))
        self.ok_button = Button("OK", id="ok", disabled=True)
        yield Label("Downloading...")
        yield self.progress
        yield self.ok_button
        
    def on_mount(self):
        self.call_later(self.start_downloads)  # schedule async task right after mount

    @work(exclusive=True)       
    async def start_downloads(self):
        
        test_urls = [
            "https://picsum.photos/seed/ghibli1/800/600",
            "https://picsum.photos/seed/ghibli2/800/600",
            "https://picsum.photos/seed/ghibli3/800/600",
            "https://picsum.photos/seed/ghibli4/800/600",
            "https://picsum.photos/seed/ghibli5/800/600"
        ]
               
        async with httpx.AsyncClient(timeout=None) as client:
            for url in test_urls:
                save_path = Path.home() / f"{url.split('/')[-3]}.jpg"
                await download_file(client, url, save_path)
                self.progress.advance(1)  # update progress bar
        
        self.ok_button.disabled = False
        self.query_one(Label).update("Downloads complete! Click OK to continue.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen() # go back to download screen
        self.app.pop_screen() # go back to main screen
    
async def download_file(client, url, save_path: Path):
    """Download a file asynchronously using httpx."""
    async with client.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with open(save_path, "wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)   
    
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
    config_path = Path.home() / ".config" / "ghypr"
    if not config_path.exists():
        raise FileNotFoundError(f"Config directory not found: {config_path}. Ensure .config/ghypr exists.")

    theme_names = sorted([p.name for p in config_path.iterdir() if p.is_dir()])
    movies = [ThemeListItem(name.capitalize(), get_theme_colours_from_css(config_path, name)) for name in theme_names]
    
    app = GhibliThemeSwitcher(movies)
    app.run()
    
if __name__ == "__main__":
    main()
