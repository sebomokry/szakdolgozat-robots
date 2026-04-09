import heapq
from collections import deque
from src.engine.logic import compute_move
from src.engine.state import GameState
from src.engine.constants import NORTH, SOUTH, EAST, WEST, DIRECTION_DELTAS

def calculate_heuristic(board, target_pos):
    """
    Kiszámolja a célmezőből kiindulva visszafele haladva, hogy 
    ha minden fal és minden segédrobot ideális helyen lenne, 
    minimálisan hány lépésbe telne eljutni az adott mezőről a célba.
    Ez kiváló és elfogadható (admissible) heurisztika az A* algoritmushoz.
    """
    size = board.size
    inf = float('inf')
    H = [[inf for _ in range(size)] for _ in range(size)]
    
    tx, ty = target_pos
    H[ty][tx] = 0
    
    queue = deque([(tx, ty)])
    
    while queue:
        cx, cy = queue.popleft()
        current_cost = H[cy][cx]
        
        # Minden irányban haladunk visszafelé, amíg falba nem ütközünk
        for direction, (dx, dy) in DIRECTION_DELTAS.items():
            x, y = cx, cy
            while True:
                # Van-e fal ebbe az irányba?
                if board.walls[y][x][direction]:
                    break
                
                x += dx
                y += dy
                
                # Ha ezen a vonalon olyan mezőre értünk, ahol a 
                # heurisztika érték még nem a legkisebb
                if H[y][x] > current_cost + 1:
                    H[y][x] = current_cost + 1
                    queue.append((x, y))
                    
    return H

def find_solution_astar(board, current_state, robot_idx, target_pos, max_depth=20):
    """
    A* algoritmus a Ricochet Robots megoldásához.
    """
    print(f"[{robot_idx}. robot] A* Útvonalkeresés a {target_pos} kordinátára... (max mélység: {max_depth})")
    
    # 1. Heurisztika tábla kiszámítása a célhoz
    H = calculate_heuristic(board, target_pos)
    
    start_positions = tuple(current_state.robots)
    
    # A kiinduló pozíció heurisztikája
    start_tx, start_ty = start_positions[robot_idx]
    start_h = H[start_ty][start_tx]
    
    if start_h == float('inf'):
        print("A cél elérhetetlen a heurisztika alapján (teljesen elzárt)!")
        return None
        
    pq = []
    counter = 0  # Sorrend megtartásához
    
    # A sor felépítése: (f_score, main_robot_penalty, g_score, counter, positions, path)
    # main_robot_penalty 0, ha a fő robot lépett legutóbb, különben 1. (Előnyben részesítjük)
    heapq.heappush(pq, (start_h, 0, 0, counter, start_positions, []))
    
    # Visited dict tárolja, hogy egy állapotot mennyi a legkisebb g_score-ral értünk el
    visited = {}
    visited[start_positions] = 0
    
    directions = [NORTH, SOUTH, EAST, WEST]
    
    while pq:
        f_score, main_robot_penalty, g_score, _, current_positions, path = heapq.heappop(pq)
        
        # Ha célhoz ért a kiválasztott robot
        if current_positions[robot_idx] == target_pos:
            print(f"{counter} db állapotot vizsgáltunk meg.")
            return path
            
        # Túlléptük a g_score határt
        if g_score >= max_depth:
            continue
            
        # Összes robot vizsgálata minden irányba
        for r_idx in range(len(current_positions)):
            for direction in directions:
                temp_state = GameState(list(current_positions))
                new_pos = compute_move(board, temp_state, r_idx, direction)
                
                # Ha nem tud mozdulni
                if new_pos == current_positions[r_idx]:
                    continue
                    
                new_positions_list = list(current_positions)
                new_positions_list[r_idx] = new_pos
                new_positions = tuple(new_positions_list)
                
                new_g = g_score + 1
                
                # Ha új állapot
                if new_positions not in visited:
                    visited[new_positions] = new_g
                    
                    # Heurisztika csak a kiválasztott fő robot távolságától függ!
                    rx, ry = new_positions[robot_idx]
                    h_score = H[ry][rx]
                    
                    new_f = new_g + h_score
                    
                    new_path = list(path)
                    new_path.append({"robot": r_idx, "dir": direction})
                    
                    # 0 a büntetés, ha a mi fő robotunk lépett, különben 1
                    main_robot_penalty = 0 if r_idx == robot_idx else 1
                    
                    counter += 1
                    heapq.heappush(pq, (new_f, main_robot_penalty, new_g, counter, new_positions, new_path))
    
    
    return None
