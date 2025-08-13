import subprocess
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Button, Label, ListView, Header
from pathlib import Path
from screens.manifest_loader import ManifestLoaderScreen
from screens.update_manifest import UpdateManifestProgressScreen
from screens.download_selection import ThemeDownloadSelectionScreen
from utils.get_theme_colours_from_css import get_theme_colours_from_css
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
                                           

            


 

    

        
