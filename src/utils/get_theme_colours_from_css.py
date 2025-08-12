import re

def get_theme_colours_from_css(config_path, theme_name):
    css_path = config_path / theme_name / f"{theme_name}.css"
    css_raw_text = css_path.read_text()
    color_pattern_regex = r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"
    theme_colors = re.findall(color_pattern_regex, css_raw_text)
    return theme_colors