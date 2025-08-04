import httpx
import asyncio
import json
import subprocess
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
            self.push_screen(ThemeDownloadScreen())
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
        manifest_path = Path.home() / ".config" / "ghypr" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_url = "https://raw.githubusercontent.com/kieran-obrien/ghypr-assets/main/manifest.json"

        try:
            if not manifest_path.exists():
                self.query_one(Label).update("Manifest not found. Downloading...")
                async with httpx.AsyncClient(timeout=None) as client:
                    res = await client.get(manifest_url)
                    res.raise_for_status()

                    tmp_path = manifest_path.with_suffix(".tmp")
                    tmp_path.write_bytes(res.content)
                    tmp_path.replace(manifest_path)
                    self.app.manifest = res.json()
                    
            else:
                self.app.manifest = json.loads(manifest_path.read_text())

            self.query_one(Label).update("Manifest check complete! Click OK to continue.")
        except Exception as e:
            self.query_one(Label).update(f"[red]Failed to load manifest: {e}[/red]")

        self.ok_button.disabled = False
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.app.pop_screen()
            
class ThemeDownloadScreen(Screen):   
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

class UpdateManifestProgressScreen(Screen):
    def __init__(self):
        super().__init__()
        
    def compose(self) -> ComposeResult:
        self.progress = ProgressBar(total=100)
        self.ok_button = Button("OK", id="ok", disabled=True)
        yield Label("Updating theme manifest...")
        yield self.progress
        yield self.ok_button
        
    def on_mount(self):
        self.call_later(self.update_manifest)  # schedule async task right after mount

    @work(exclusive=True)       
    async def update_manifest(self):                              
        manifest_path = Path.home() / ".config" / "ghypr" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_url = "https://raw.githubusercontent.com/kieran-obrien/ghypr-assets/main/manifest.json"

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                res = await client.get(manifest_url)
                res.raise_for_status()

                tmp_path = manifest_path.with_suffix(".tmp")
                tmp_path.write_bytes(res.content)
                tmp_path.replace(manifest_path)
                self.app.manifest = res.json()
                self.progress.advance(100)
                self.query_one(Label).update("Manifest update complete! Click OK to continue.")
        except Exception as e:
            self.query_one(Label).update(f"[red]Failed to update manifest: {e}[/red]")
        self.ok_button.disabled = False
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen() # go back to main screen
           
class ThemeListItem(ListItem):
    def __init__(self, theme_name, theme_colours):
        super().__init__()
        self.theme_name = theme_name
        self.theme_colours = theme_colours
        self.styles.height = 3\
    
    def on_mount(self):
        self.mount(Horizontal(Label(self.theme_name.capitalize()), create_color_preview_squares(self.theme_colours)))

async def download_file(client, url, save_path: Path):
    """Download a file asynchronously using httpx."""
    async with client.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with open(save_path, "wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)   
 
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
    css_path = config_path / theme_name / f"{theme_name}.css"
    css_raw_text = css_path.read_text()
    color_pattern_regex = r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"
    theme_colors = re.findall(color_pattern_regex, css_raw_text)
    return theme_colors
        
def main():
    app = GhibliThemeSwitcher()
    app.run()
    
if __name__ == "__main__":
    main()
