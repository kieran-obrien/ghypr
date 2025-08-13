import httpx
from pathlib import Path
from textual.widgets import Button, Label, ProgressBar
from textual.app import ComposeResult
from textual.screen import Screen
from textual import work
from utils.download_file import download_file

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