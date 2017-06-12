import sys
import os

class ScreenPainter(object):
    def print_there(self, row, col, text):
        if 2 <= row + 2 <= self.HEIGHT and 1 <= col + 1 <= self.WIDTH:
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (row + 2, col + 1, text))
    def __init__(self, cell_char="\u2593"):
        self.HEIGHT, self.WIDTH = map(int,os.popen('stty size', 'r').read().split())
        self.cell_char = cell_char
    def clear(self):
        os.system("clear")
    def draw_state(self, game):
        for p in game.interesting_cells:
            if p in game.living_cells:
                char = self.cell_char
            else:
                char = " "
            self.print_there(p[1], p[0], char)
        sys.stdout.flush()
