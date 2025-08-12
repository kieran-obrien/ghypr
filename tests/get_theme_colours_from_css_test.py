import pytest
from pathlib import Path
from utils.get_theme_colours_from_css import get_theme_colours_from_css

@pytest.fixture
def sample_css_file(tmp_path):
    css_content = """
    :root {
      --base0: #1e1c2c;      
      --base1: #2f2b4a;      
      --muted: #a6a3ba;      
      --accent1: #ffb347;    
      --accent2: #f28482;    
      --accent3: #9ae1e2;    
      --text: #f7f6f2;      
      --highlight: #4c437b;  
    }
    """
    theme_name = "testtheme"
    theme_dir = tmp_path / theme_name
    theme_dir.mkdir()
    (theme_dir / f"{theme_name}.css").write_text(css_content)
    return tmp_path  # returns the config_path parent

def test_get_theme_colours_from_css(sample_css_file):
    colors = get_theme_colours_from_css(sample_css_file, "testtheme")
    expected_colors = [
        "#1e1c2c",
        "#2f2b4a",
        "#a6a3ba",
        "#ffb347",
        "#f28482",
        "#9ae1e2",
        "#f7f6f2",
        "#4c437b"
    ]
    for color in expected_colors:
        assert color in colors
    assert len(colors) == len(expected_colors)