from textual.containers import Horizontal
from textual.widgets import Static

def create_color_preview_squares(colors):
    squares = []
    for c in colors:
        square = Static("")          
        square.styles.background = c
        square.styles.width = 2        
        square.styles.height = 1  
        squares.append(square)
    return Horizontal(*squares)