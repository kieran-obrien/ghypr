import pytest_asyncio
from textual.app import App
from textual.containers import Container

class MockApp(App):
    def __init__(self):
        super().__init__()
        self.test_container = None

    async def on_mount(self):
        self.test_container = Container()
        await self.mount(self.test_container)

@pytest_asyncio.fixture
async def mock_app():
    """A minimal Textual app for mounting widgets during tests."""
    app = MockApp()
    async with app.run_test():
        yield app