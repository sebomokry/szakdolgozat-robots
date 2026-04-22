from .constants import DIRECTION_DELTAS

def compute_move(board, state, robot_idx, direction):
    x, y = state.robots[robot_idx]
    dx, dy = DIRECTION_DELTAS[direction]

    while True:
        if board.walls[y][x][direction]:
            break
        
        nx, ny = x + dx, y + dy
        
        if state.is_robot_at(nx, ny):
            break
            
        x, y = nx, ny
        
    return (x, y)
