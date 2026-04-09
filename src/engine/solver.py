from collections import deque
from src.engine.logic import compute_move
from src.engine.state import GameState
from src.engine.constants import NORTH, SOUTH, EAST, WEST

def find_solution(board, current_state, robot_idx, target_pos, max_depth=10):
    """
    BFS (Szélességi Keresés) algoritmus a legrövidebb útvonal megtalálására.
    """
    print(f"[{robot_idx}. robot] Útvonalkeresés a {target_pos} kordinátára... (max mélység: {max_depth})")
    
    # A kiinduló állapot tuple formában (hogy hash-elhető legyen a Set-hez)
    start_positions = tuple(current_state.robots)
    
    # queue: tartalmazza a (jelenlegi_pozíciók, addigi_lépések_listája) párosokat
    queue = deque([(start_positions, [])])
    
    # visited: az eddig vizsgált állapotok halmaza, hogy ne kerüljünk végtelen ciklusba
    visited = set()
    counter = 0
    visited.add(start_positions)
    
    directions = [NORTH, SOUTH, EAST, WEST]
    
    while queue:
        current_positions, path = queue.popleft()
        
        # Sikerült-e a kiválasztott robotot a célba juttatni?
        if current_positions[robot_idx] == target_pos:
            print(f"{counter} db állapotot vizsgáltunk meg.")
            return path
            
        # Ha elértük a maximális lépésszámot ezen az ágon, nem megyünk mélyebbre
        if len(path) >= max_depth:
            continue
            
        # Különben kipróbáljuk mind a 4(vagy ahány felé lehet) irányt az összes robotra
        for r_idx in range(len(current_positions)):
            for direction in directions:
                # Létrehozunk egy átmeneti állapotot, amit a compute_move használni tud
                temp_state = GameState(list(current_positions))
                
                # Kiszámoljuk, hova érkezne a robot
                new_pos = compute_move(board, temp_state, r_idx, direction)
                
                # Ha a robot nem tud mozdulni abba az irányba (mert egyből falnak vagy társnak ütközik)
                if new_pos == current_positions[r_idx]:
                    continue
                    
                # Új állapot generálása
                new_positions_list = list(current_positions)
                new_positions_list[r_idx] = new_pos
                new_positions = tuple(new_positions_list)
                
                # Ha ezt az elrendezést még nem vizsgáltuk
                if new_positions not in visited:
                    visited.add(new_positions)
                    
                    # Új útvonal elkészítése
                    new_path = list(path)
                    new_path.append({"robot": r_idx, "dir": direction})
                    
                    counter += 1
                    queue.append((new_positions, new_path))
                    
    # Ha kiürült a queue és nincs megoldás
    print("Nem található megoldás a megadott lépésszám korláton belül.")
    return None
