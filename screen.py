import sys
import os

class ScreenPainter(object):
    """
    This class contains methods to write the game's state on stdout.
    """
    def __init__(self, cell_char="\u2593"):
        self.height, self.width = map(int,os.popen('stty size', 'r').read().split())
        self.cell_char = cell_char
    def print_there(self, row, col, text):
        if 2 <= row + 2 <= self.height and 1 <= col + 1 <= self.width:
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (row + 2, col + 1, text))
    def clear(self):
        os.system("clear")
    def draw_state(self, game):
        # print(game.living_cells)
        for p in game.interesting_cells:
            if p in game.living_cells:
                char = self.cell_char
            else:
                char = " "
            self.print_there(p[1], p[0], char)
        sys.stdout.flush()
