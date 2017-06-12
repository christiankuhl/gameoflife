import random
import itertools
import time
import os
from repl import REPL
from screen import ScreenPainter
from game import Game

class Main(object):
    def __init__(self):
        self.screen = ScreenPainter()
        self.state = []
        self.game = Game(screen = self.screen, initial_state = [])
        self.repl = REPL(screen = self.screen)

    def run_repl(self):
        self.screen.clear()
        while True:
            try:
                text = self.repl.prompt()
            except EOFError:
                break  # Control-D pressed.
            self.evaluate_input(text)
        print('Goodbye!')

    def run_game(self):
        self.screen.clear()
        os.system("setterm -cursor off")
        try:
            while True:
                self.screen.draw_state(self.game)
                time.sleep(.1)
                self.game.next()
        except KeyboardInterrupt:
            self.screen.clear()
            os.system("setterm -cursor on")

    def evaluate_input(self, text):
        print(text)
        if text == "run":
            initial_state = set(random.sample(
                list(itertools.product(range(self.screen.WIDTH),range(self.screen.HEIGHT))),
                                                int(self.screen.HEIGHT*self.screen.WIDTH*.25)))
            self.game = Game(self.screen, initial_state)
            self.run_game()

class ArgParser(object):
    def __init__(self, screen):
        self.WIDTH, self.HEIGHT = screen.WIDTH, screen.HEIGHT
    def get_state(self, args):
        proportion = None
        initial_state = None
        try:
            if args[1].lower() == 'repl':
                return 'repl'
            dim = float(args[1])
            if dim == int(dim):
                dim = int(dim)
                initial_state = {(p,q) for p in range(dim) for q in range(dim)}
            else:
                proportion = max(min(1., float(args[1])),0.)
        except ValueError:
            try:
                with open(args[1], "r") as file:
                    initial_state = set()
                    for (row, line) in enumerate(file):
                        for (col, char) in enumerate(line):
                            if char == "*":
                                initial_state.add((col, row))
            except:
                pass
        except IndexError:
            initial_state = None
        if not initial_state:
            if not proportion:
                proportion = .25
            initial_state = set(random.sample(
                list(itertools.product(range(self.WIDTH),range(self.HEIGHT))),
                                                int(self.HEIGHT*self.WIDTH*proportion)))
        return initial_state

if __name__ == "__main__":
    app = Main()
    app.run_repl()
