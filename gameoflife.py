import random
import itertools
import sys
import time
import os


def run_game(screen, game):
    screen.clear()
    os.system("setterm -cursor off")
    try:
        while True:
            screen.draw_state(game)
            time.sleep(.1)
            game.next()
    except KeyboardInterrupt:
        screen.clear()
        os.system("setterm -cursor on")

def run_repl(screen):
    pass

class Game(object):
    def __init__(self, screen, initial_state, mode="Klein"):
        self.MODE = mode
        self.BUFFER = 20
        self.HEIGHT, self.WIDTH = screen.HEIGHT, screen.WIDTH
        self.living_cells = initial_state
        self.interesting_cells = set().union(*[self.neighbors(p) for p in self.living_cells])
        self.interesting_cells = self.interesting_cells.union(self.living_cells)
    def neighbors(self, p):
        if self.MODE == "Torus":
            l = [((u+p[0]) % self.WIDTH, (v+p[1]) % self.HEIGHT) for u in
                                            range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q != p)
        elif self.MODE == "Cylinder":
            l = [((u+p[0]) % self.WIDTH, v+p[1]) for u in range(-1, 2) for v in
                                                                    range(-1, 2)]
            return set(q for q in l if q[1] in range(self.HEIGHT + self.BUFFER)
                                                                    and q != p)
        elif self.MODE == "Moebius":
            l = [((u+p[0]) % self.WIDTH, self.mirror("y",p[0]+u, v+p[1])) for
                                        u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q[1] in range(self.HEIGHT + self.BUFFER)
                                                                    and q != p)
        elif self.MODE == "Klein":
            l = [(self.mirror("x",p[1]+v, u+p[0]) % self.WIDTH, self.mirror("y",
                                            p[0]+u, v+p[1]) % self.HEIGHT) for
                                    u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q != p)
        else:
            l = [(u+p[0], v+p[1]) for u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q[0] in range(-self.BUFFER, self.WIDTH
                                                     + self.BUFFER+1) and q[1]
                                                     in range(self.HEIGHT +
                                                     self.BUFFER+1) and q != p)
    def mirror(self, axis, x, y):
        if axis == "y":
            h, w = self.HEIGHT, self.WIDTH
        else:
            h, w = self.WIDTH, self.HEIGHT
        if x == -1 or x == w:
            return  h - y
        else:
            return y
    def next(self):
        new_cells = set()
        self.interesting_cells = set().union(*[self.neighbors(p) for p in self.living_cells])
        self.interesting_cells = self.interesting_cells.union(self.living_cells)
        if self.MODE == None:
            self.interesting_cells = [c for c in self.interesting_cells if
                                  -self.BUFFER/2 < c[0] < self.WIDTH + self.BUFFER/2
                                  and -self.BUFFER/2 < c[1] < self.HEIGHT + self.BUFFER/2]
        for p in self.interesting_cells:
            living_neighbors =  self.living_cells.intersection(self.neighbors(p))
            if p in self.living_cells:
                if 2 <= len(living_neighbors) <= 3:
                    new_cells.add(p)
            else:
                if len(living_neighbors) == 3:
                    new_cells.add(p)
        self.living_cells = new_cells

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

class ScreenPainter(object):
    def print_there(self, row, col, text):
        if 1 <= row + 1 <= self.HEIGHT and 1 <= col + 1 <= self.WIDTH:
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (row + 1, col + 1, text))
    def __init__(self):
        self.HEIGHT, self.WIDTH = map(int,os.popen('stty size', 'r').read().split())
    def clear(self):
        os.system("clear")
    def draw_state(self, game):
        for p in game.interesting_cells:
            if p in game.living_cells:
                char = "\u2593"
            else:
                char = " "
            s.print_there(p[1], p[0], char)
        sys.stdout.flush()

if __name__ == "__main__":
    s = ScreenPainter()
    a = ArgParser(s)
    initial_state = a.get_state(sys.argv)
    if initial_state == 'repl':
        run_repl(s)
    else:
        g = Game(s, initial_state=initial_state)
        run_game(s, g)
