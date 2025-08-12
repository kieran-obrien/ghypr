import pytest
from app import create_color_preview_squares
from textual.widgets import Static

@pytest.mark.asyncio
async def test_create_color_preview_squares(mock_app):
    colors = ["#ff0000", "#00ff00", "#0000ff"]
    container = create_color_preview_squares(colors)
    
    # Mount widget inside the mock app’s container
    await mock_app.test_container.mount(container)

    assert len(container.children) == len(colors)
    print(container.children)
    
     # Check each child widget's background color
    for widget, color in zip(container.children, colors):
        assert isinstance(widget, Static)
        assert widget.styles.background.hex.lower() == color

    # Check child sizing
    for widget in container.children:
        assert widget.styles.width.value == 2
        assert widget.styles.height.value == 1