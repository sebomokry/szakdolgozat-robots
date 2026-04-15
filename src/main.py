from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from src.engine.board import Board
from src.engine.state import GameState
from src.engine.logic import compute_move
from src.engine.solver import find_solution
from src.engine.astar import find_solution_astar
from src.engine.astar_subgoal import find_solution_astar_subgoal

app = FastAPI()

# Inicializálunk egy alap pályát és állapotot
board = Board(size=16)



# Példa robot pozíciók: 4 db robot (Pl. Piros, Kék, Zöld, Sárga)
initial_robots = [(5, 5), (9, 0), (10, 2), (7, 13), (1,1)]
game_state = GameState(initial_robots)

class MoveRequest(BaseModel):
    robot_idx: int
    direction: int

@app.get("/api/state")
def get_state():
    return {
        "size": board.size,
        "walls": board.walls,
        "robots": game_state.robots
    }

@app.post("/api/move")
def move(req: MoveRequest):
    new_pos = compute_move(board, game_state, req.robot_idx, req.direction)
    # Frissítjük a pozíciót
    game_state.robots[req.robot_idx] = new_pos
    return {"robots": game_state.robots}

class SolveRequest(BaseModel):
    robot_idx: int
    target_x: int
    target_y: int
    algorithm: str = "astar"

@app.post("/api/solve")
def solve_board(req: SolveRequest):
    target_pos = (req.target_x, req.target_y)
    
    if req.algorithm == "bfs":
        path = find_solution(board, game_state, req.robot_idx, target_pos, max_depth=10)
    elif req.algorithm == "astar":
        path = find_solution_astar(board, game_state, req.robot_idx, target_pos, max_depth=20)
    else:  # astar_subgoal
        path = find_solution_astar_subgoal(board, game_state, req.robot_idx, target_pos, max_depth=20)
        
    return {"path": path}

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
