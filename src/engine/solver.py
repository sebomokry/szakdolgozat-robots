from collections import deque
from src.engine.logic import compute_move
from src.engine.state import GameState
from src.engine.constants import NORTH, SOUTH, EAST, WEST

def find_solution(board, current_state, robot_idx, target_pos, max_depth=14):
    print(f"[{robot_idx}. robot] Útvonalkeresés a {target_pos} kordinátára... (max mélység: {max_depth})")
    
    start_positions = tuple(current_state.robots)
    
    queue = deque([(start_positions, [])])
    
    visited = set()
    counter = 0
    visited.add(start_positions)
    
    directions = [NORTH, SOUTH, EAST, WEST]
    
    while queue:
        current_positions, path = queue.popleft()
        
        if current_positions[robot_idx] == target_pos:
            print(f"{counter} db állapotot vizsgáltunk meg.")
            return path, counter
            
        if len(path) >= max_depth:
            continue
            
        for r_idx in range(len(current_positions)):
            for direction in directions:
                temp_state = GameState(list(current_positions))
                
                new_pos = compute_move(board, temp_state, r_idx, direction)
                
                if new_pos == current_positions[r_idx]:
                    continue
                    
                new_positions_list = list(current_positions)
                new_positions_list[r_idx] = new_pos
                new_positions = tuple(new_positions_list)
                
                if new_positions not in visited:
                    visited.add(new_positions)
                    
                    new_path = list(path)
                    new_path.append({"robot": r_idx, "dir": direction})
                    
                    counter += 1
                    queue.append((new_positions, new_path))
                    
    return None, counter
