from .constants import NORTH, SOUTH, EAST, WEST

DEFAULT_LAYOUT = [
    [0, "R", 0, 0, "B", 0, 0, 0, "R", 0, 0, 0, 0, 0, 0, 0],
    [0, "B", 0, "R", 0, 0, 0, 0, 0, 0, 0, 0, 0, "L", 0, 0],
    [0, 0, "L", 0, 0, 0, 0, 0, 0, "R", 0, 0, "T", 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, "L", 0, 0, "T", 0, 0, 0, 0, "B"],
    [0, 0, 0, 0, 0, 0, "T", 0, 0, 0, 0, "B", 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "L", 0, "B", 0],
    [0, 0, "R", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "R", 0, 0],
    [0, 0, 0, "T", 0, 0, 0, "TL", "TR", "R", 0, 0, 0, 0, 0, 0],
    [0, 0, "B", 0, "R", 0, 0, "BL", "BR", 0, "T", 0, 0, 0, 0, 0],
    [0, "R", 0, 0, 0, "T", 0, 0, 0, 0, 0, 0, "R", 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "T", 0, 0],
    ["B", 0, 0, 0, 0, 0, 0, 0, 0, 0, "L", 0, 0, 0, 0, "B"],
    [0, 0, 0, 0, "B", 0, 0, 0, 0, "T", 0, 0, 0, 0, "B", 0],
    [0, 0, 0, 0, 0, "L", 0, 0, 0, 0, "B", 0, 0, 0, 0, "L"],
    [0, 0, "L", 0, 0, 0, 0, 0, 0, "R", 0, 0, 0, 0, 0, 0],
    [0, "T", 0, 0, 0, "R", 0, 0, 0, 0, 0, "R", 0, 0, 0, 0],
]

class Board:
    def __init__(self, size=16, layout=None):
        self.size = size
        self.walls = []
        for _ in range(size):
            row = []
            for _ in range(size):
                row.append([False, False, False, False])
            self.walls.append(row)
        self._setup_borders()
        
        if layout is None and size == 16:
            layout = DEFAULT_LAYOUT
            
        if layout:
            self._apply_layout(layout)

    def _setup_borders(self):
        for i in range(self.size):
            self.walls[0][i][NORTH] = True
            self.walls[self.size-1][i][SOUTH] = True
            self.walls[i][0][WEST] = True
            self.walls[i][self.size-1][EAST] = True

    def _apply_layout(self, layout):
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                if not isinstance(cell, str):
                    continue
                for char in cell:
                    if char == "T":
                        self.walls[y][x][NORTH] = True
                        if y > 0:
                            self.walls[y-1][x][SOUTH] = True
                    elif char == "B":
                        self.walls[y][x][SOUTH] = True
                        if y < self.size - 1:
                            self.walls[y+1][x][NORTH] = True
                    elif char == "R":
                        self.walls[y][x][EAST] = True
                        if x < self.size - 1:
                            self.walls[y][x+1][WEST] = True
                    elif char == "L":
                        self.walls[y][x][WEST] = True
                        if x > 0:
                            self.walls[y][x-1][EAST] = True
