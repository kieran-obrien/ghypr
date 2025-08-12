from textual.widgets import ListItem, Label
from textual.containers import Horizontal
from utils.create_colour_preview_squares import create_color_preview_squares

class ThemeListItem(ListItem):
    def __init__(self, theme_name, theme_colours):
        super().__init__()
        self.theme_name = theme_name
        self.theme_colours = theme_colours
        self.styles.height = 3

    def compose(self):
        yield Horizontal(
            Label(self.theme_name),
            create_color_preview_squares(self.theme_colours),
        )