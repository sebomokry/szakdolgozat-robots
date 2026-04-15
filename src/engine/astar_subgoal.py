import heapq
from collections import deque
from src.engine.logic import compute_move
from src.engine.state import GameState
from src.engine.constants import NORTH, SOUTH, EAST, WEST, DIRECTION_DELTAS

def calculate_heuristic_subgoal(board, target_pos):
    """
    Kiszámolja a célmezőből kiindulva visszafele haladva, hogy 
    ha minden fal és minden segédrobot ideális helyen lenne, 
    minimálisan hány lépésbe telne eljutni az adott mezőről a célba.
    Továbbá ('Sub-goal' logika): Minden mezőhöz eltárolja, hogy ehhez a 
    minimális útra MELYIK koordinátákon volt feltétlenül szükség 
    egy "képzeletbeli" segédrobotra (pattanási pontra).
    """
    size = board.size
    inf = float('inf')
    H = [[inf for _ in range(size)] for _ in range(size)]
    Helpers = [[set() for _ in range(size)] for _ in range(size)]
    
    tx, ty = target_pos
    H[ty][tx] = 0
    
    queue = deque([(tx, ty)])
    
    OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
    
    while queue:
        cx, cy = queue.popleft()
        current_cost = H[cy][cx]
        current_helpers = Helpers[cy][cx]
        
        for direction, (dx, dy) in DIRECTION_DELTAS.items():
            
            has_wall = board.walls[cy][cx][direction]
            
            needed_helper = None
            if not has_wall:
                hx, hy = cx + dx, cy + dy
                
                if 0 <= hx < size and 0 <= hy < size:
                    needed_helper = (hx, hy)
                    
            new_helpers = set(current_helpers)
            if needed_helper:
                new_helpers.add(needed_helper)
                
            new_cost = current_cost + 1
            
            x, y = cx, cy
            opp_dir = OPPOSITE[direction]
            
            while True:
                if board.walls[y][x][opp_dir]:
                    break
                
                x -= dx
                y -= dy
                
                if H[y][x] > new_cost:
                    H[y][x] = new_cost
                    Helpers[y][x] = new_helpers
                    queue.append((x, y))
                elif H[y][x] == new_cost:
                    if len(new_helpers) < len(Helpers[y][x]):
                        Helpers[y][x] = new_helpers
                        queue.append((x, y))
                        
    return H, Helpers

def find_solution_astar_subgoal(board, current_state, robot_idx, target_pos, max_depth=20):
    """
    A* algoritmus a Ricochet Robots megoldásához, intelligens Alcél(Sub-goal) heurisztikával.
    """
    print(f"[{robot_idx}. robot] A* (Subgoal) Útvonalkeresés a {target_pos} kordinátára... (max mélység: {max_depth})")
    
    H, Helpers = calculate_heuristic_subgoal(board, target_pos)
    
    start_positions = tuple(current_state.robots)
    
    start_tx, start_ty = start_positions[robot_idx]
    start_h = H[start_ty][start_tx]
    
    if start_h == float('inf'):
        print("A cél elérhetetlen a heurisztika alapján (teljesen elzárt)!")
        return None
        
    pq = []
    counter = 0  
    
    heapq.heappush(pq, (start_h, 0, 0, counter, start_positions, []))
    
    visited = {}
    visited[start_positions] = 0
    
    directions = [NORTH, SOUTH, EAST, WEST]
    
    while pq:
        f_score, main_robot_penalty, g_score, _, current_positions, path = heapq.heappop(pq)
        
        if current_positions[robot_idx] == target_pos:
            print(f"{counter} db állapotot vizsgáltunk meg (A* Subgoal).")
            return path
            
        if g_score >= max_depth:
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
                
                new_g = g_score + 1
                
                if new_positions not in visited or new_g < visited[new_positions]:
                    visited[new_positions] = new_g
                    
                    rx, ry = new_positions[robot_idx]
                    base_h = H[ry][rx]
                    
                    required_helpers = Helpers[ry][rx]
                    missing_helpers = 0
                    
                    if required_helpers:
                        other_robots = set(new_positions)
                        other_robots.remove((rx, ry))
                        
                        for req_h in required_helpers:
                            if req_h not in other_robots:
                                missing_helpers += 1
                                
                    h_score = base_h + missing_helpers
                    new_f = new_g + h_score
                    
                    new_path = list(path)
                    new_path.append({"robot": r_idx, "dir": direction})
                    
                    main_robot_penalty = 0 if r_idx == robot_idx else 1
                    
                    counter += 1
                    heapq.heappush(pq, (new_f, main_robot_penalty, new_g, counter, new_positions, new_path))
                    
    return None
