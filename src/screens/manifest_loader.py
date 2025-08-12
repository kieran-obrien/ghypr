import httpx
import json
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Button, Label, Header
from textual import work

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