# test_color_preview.py
from textual.widgets import Static
from textual.containers import Horizontal
from app import create_color_preview_squares

def test_create_color_preview_squares():
    colors = ["red", "green", "blue"]
    container = create_color_preview_squares(colors)
    
    # Check it's a Horizontal container
    assert isinstance(container, Horizontal)
