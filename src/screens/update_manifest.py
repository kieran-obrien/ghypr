import httpx
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, ProgressBar, Header
from textual import work

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