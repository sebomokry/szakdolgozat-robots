from .constants import DIRECTION_DELTAS

def compute_move(board, state, robot_idx, direction):
    """Kiszámolja, hogy a robot hova fog érkezni az adott irányba indulva."""
    x, y = state.robots[robot_idx]
    dx, dy = DIRECTION_DELTAS[direction]

    while True:
        # 1. Ellenőrizzük, van-e fal az adott irányban az aktuális mezőn
        if board.walls[y][x][direction]:
            break
        
        nx, ny = x + dx, y + dy
        
        # 2. Ellenőrizzük, áll-e ott másik robot
        if state.is_robot_at(nx, ny):
            break
            
        # 3. Ha nincs akadály, lépünk tovább
        x, y = nx, ny
        
    return (x, y)
