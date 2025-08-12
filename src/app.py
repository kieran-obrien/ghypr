import httpx
import subprocess
from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal
from textual.widgets import Footer, Button, Static, Label, ListItem, ListView, Header, SelectionList, ProgressBar
from textual.widgets.selection_list import Selection
from pathlib import Path
from screens.manifest_loader import ManifestLoaderScreen
from screens.update_manifest import UpdateManifestProgressScreen
from utils.get_theme_colours_from_css import get_theme_colours_from_css
from utils.create_colour_preview_squares import create_color_preview_squares
from utils.download_file import download_file
from widgets.theme_list_item import ThemeListItem

class GhibliThemeSwitcher(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
       
    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".config" / "ghypr"
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)
        self.manifest = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(Button("Download Themes", id="download"), Button("Update Manifest", id="manifest"))
        yield ListView()
        yield Label()
        yield Footer()
        
    def on_mount(self) -> None:
        self.title = "ghypr"
        self.sub_title = "Ghibli inspired theme switcher!"
        self.push_screen(ManifestLoaderScreen())
        self.refresh_theme_list()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download":
            self.push_screen(ThemeDownloadSelectionScreen())
        elif event.button.id == "manifest":
            self.push_screen(UpdateManifestProgressScreen())
            
    def on_list_view_selected(self, event: ListView.Selected):
        list_item = event.item  
        self.apply_theme(list_item.theme_name.lower())
        
    def apply_theme(self, theme_name):
        wallpaper_path = Path.home() / ".config" / "ghypr" / theme_name / f"{theme_name}-wallpaper.jpg"
        
        subprocess.run(["hyprctl", "hyprpaper", "unload", "all"], check=True)
        subprocess.run(["hyprctl", "hyprpaper", "preload", str(wallpaper_path)], check=True)
        subprocess.run(["hyprctl", "hyprpaper", "wallpaper", f",{wallpaper_path}"], check=True)

            
    def refresh_theme_list(self):
        theme_names = sorted([p.name for p in self.config_path.iterdir() if p.is_dir()])
        list_view = self.query_one(ListView)
        list_view.clear()
        for name in theme_names:
            colors = get_theme_colours_from_css(self.config_path, name)
            list_view.append(ThemeListItem(name.capitalize(), colors))
        self.query_one(Label).update("")
        if not theme_names:
            self.query_one(Label).update("No themes installed!")
                                           
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
            
class ThemeDownloadProgressScreen(Screen):
    def __init__(self, themes_selection):
        super().__init__()
        self.themes = themes_selection
        
    def compose(self) -> ComposeResult:
        self.progress = ProgressBar(total=len(self.themes) * 2)
        self.ok_button = Button("OK", id="ok", disabled=True)
        yield Label("Downloading...")
        yield Label(str(self.themes))
        yield self.progress
        yield self.ok_button
        
    def on_mount(self):
        self.call_later(self.download_themes)  # schedule async task right after mount

    @work(exclusive=True)       
    async def download_themes(self):        
        color_urls = [url for movie_name in self.themes for url in (self.app.manifest["themes"][movie_name]["colors_conf"], self.app.manifest["themes"][movie_name]["colors_css"])]
                       
        async with httpx.AsyncClient(timeout=None) as client:
            for url in color_urls:
                save_path = Path.home() / ".config" / "ghypr" / url.split("/")[-1].split(".")[0] / url.split("/")[-1]
                save_path.parent.mkdir(parents=True, exist_ok=True)
                await download_file(client, url, save_path)
                self.progress.advance(1)
            for movie_name in self.themes:
                save_path = Path.home() / ".config" / "ghypr" / movie_name / f"{movie_name}-wallpaper.jpg"
                save_path.parent.mkdir(parents=True, exist_ok=True)
                wallpaper_url = self.app.manifest["themes"][movie_name]["wallpaper"]
                await download_file(client, wallpaper_url, save_path)
                self.progress.advance(1)
        
        self.app.refresh_theme_list()
        self.ok_button.disabled = False
        self.query_one(Label).update("Downloads complete! Click OK to continue.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen() # go back to download screen
        self.app.pop_screen() # go back to main screen

 

    

        
