class Game(object):
    """
    This class encapsulates the core game logic. Living cells with 2 or 3
    living neighbors live on in the next round, dead cells with precisely 3
    living neighbors get reborn next round, all other cells die or remain dead.
    The topology of the game board is encapsulated in 'neighbors', iteration
    is done by calling next()
    """
    def __init__(self, initial_state, screen=None, topology="Torus", height=24, width=80):
        self.topology = topology
        self.buffer = 20
        if screen:
            self.height, self.width = screen.height, screen.width
        else:
            self.height, self.width = height, width
        self.living_cells = initial_state
        self.interesting_cells = set().union(*[self.neighbors(p) for p in self.living_cells])
        self.interesting_cells = self.interesting_cells.union(self.living_cells)

    def from_file(filename, *args, **kwargs):
        try:
            with open("objects/" + filename, "r") as file:
                initial_state = set()
                for (row, line) in enumerate(file):
                        for (col, char) in enumerate(line):
                            if char == "*":
                                initial_state.add((col, row))
        except:
            print("Object {} not known.".format(filename))
        return Game(initial_state, *args, **kwargs)

    def neighbors(self, p):
        if self.topology == "Torus":
            l = [((u+p[0]) % self.width, (v+p[1]) % self.height) for u in
                                            range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q != p)
        elif self.topology == "Cylinder":
            l = [((u+p[0]) % self.width, v+p[1]) for u in range(-1, 2) for v in
                                                                    range(-1, 2)]
            return set(q for q in l if q[1] in range(self.height + self.buffer)
                                                                    and q != p)
        elif self.topology == "MoebiusBand":
            l = [((u+p[0]) % self.width, self.mirror("y",p[0]+u, v+p[1])) for
                                        u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q[1] in range(self.height + self.buffer)
                                                                    and q != p)
        elif self.topology == "KleinBottle":
            l = [(self.mirror("x",p[1]+v, u+p[0]) % self.width, self.mirror("y",
                                            p[0]+u, v+p[1]) % self.height) for
                                    u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q != p)
        else: # "Plane"
            l = [(u+p[0], v+p[1]) for u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q[0] in range(-self.buffer, self.width
                                                     + self.buffer+1) and q[1]
                                                     in range(self.height +
                                                     self.buffer+1) and q != p)
    def mirror(self, axis, x, y):
        if axis == "y":
            h, w = self.height, self.width
        else:
            h, w = self.width, self.height
        if x == -1 or x == w:
            return  h - y
        else:
            return y
    def next(self):
        new_cells = set()
        self.interesting_cells = set().union(*[self.neighbors(p) for p in self.living_cells])
        self.interesting_cells = self.interesting_cells.union(self.living_cells)
        if self.topology == None:
            self.interesting_cells = (c for c in self.interesting_cells if
                                  -self.buffer/2 < c[0] < self.width + self.buffer/2
                                  and -self.buffer/2 < c[1] < self.height + self.buffer/2)
        for p in self.interesting_cells:
            living_neighbors =  self.living_cells.intersection(self.neighbors(p))
            if p in self.living_cells:
                if 2 <= len(living_neighbors) <= 3:
                    new_cells.add(p)
            else:
                if len(living_neighbors) == 3:
                    new_cells.add(p)
        self.living_cells = new_cells
