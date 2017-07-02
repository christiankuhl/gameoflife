import random
import itertools
import time
import os
from repl import REPL
from screen import ScreenPainter
from game import Game
from parser import GameParser

class Main(object):
    """
    This class contains the main application logic. Entry point for the REPL
    is run_repl. The rest of the methods serve for dispatching the game's
    config/control language elements to the various application components.
    """
    def __init__(self):
        self.screen = ScreenPainter()
        self.game = Game(screen = self.screen, initial_state = [])
        self.repl = REPL(screen = self.screen)
        self.parser = GameParser(self)

    def run_repl(self):
        self.screen.clear()
        while True:
            try:
                text = self.repl.prompt()
                self.parser.parse(text)
            except GameOver:
                break
            except EOFError:
                break
        print("Goodbye!")

    def run(self, *args):
        if args:
            self.game = Game.from_file(args[0], screen=self.screen,
                                       topology = self.topology)
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

    def quit(self):
        print("Goodbye!")
        raise GameOver()

    exit = quit

    @property
    def topology(self):
        return self.game.topology
    @topology.setter
    def topology(self, value):
        self.game.topology = value.strip("'")

    @property
    def width(self):
        return self.screen.width
    @width.setter
    def width(self, value):
        self.screen.width = value
        self.game.width = value

    @property
    def height(self):
        return self.screen.height
    @height.setter
    def height(self, value):
        self.screen.height = value
        self.game.height = value

    @property
    def state(self):
        return self.game.living_cells
    @state.setter
    def state(self, state):
        self.game.living_cells = state

    def random_state(self):
        initial_state = set(random.sample(list(itertools.product(
                                        range(self.width),range(self.height))),
                                        int(self.height*self.width*proportion)))
        return initial_state

    def block(self, dim):
        initial_state = {(p,q) for p in range(dim) for q in range(dim)}
        return initial_state

class GameOver(KeyboardInterrupt, EOFError):
    pass

if __name__ == "__main__":
    app = Main()
    app.run_repl()
