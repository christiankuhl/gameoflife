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
        elif self.MODE == "MoebiusBand":
            l = [((u+p[0]) % self.WIDTH, self.mirror("y",p[0]+u, v+p[1])) for
                                        u in range(-1, 2) for v in range(-1, 2)]
            return set(q for q in l if q[1] in range(self.HEIGHT + self.BUFFER)
                                                                    and q != p)
        elif self.MODE == "KleinBottle":
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
