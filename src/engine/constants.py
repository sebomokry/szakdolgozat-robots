NORTH, SOUTH, EAST, WEST = 0, 1, 2, 3

# Irányoknak megfelelő elmozdulás vektorok: (dx, dy)
# NORTH = felfelé (y csökken)
# SOUTH = lefelé (y nő)
# EAST = jobbra (x nő)
# WEST = balra (x csökken)
DIRECTION_DELTAS = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST: (1, 0),
    WEST: (-1, 0)
}
