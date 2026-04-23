const CONSTANTS = {
    NORTH: 0,
    SOUTH: 1,
    EAST: 2,
    WEST: 3
};

let boardState = null;
let isMoving = false;
let targetPos = null;

async function initGame() {
    try {
        const res = await fetch('/api/state');
        boardState = await res.json();
        renderBoard();
    } catch (e) {
        console.error("Failed to load initial state:", e);
    }
}

function renderBoard() {
    const boardElement = document.getElementById('game-board');
    const svgLayer = document.getElementById('arrow-layer');
    boardElement.innerHTML = '';
    if (svgLayer) boardElement.appendChild(svgLayer);

    const size = boardState.size;
    boardElement.style.gridTemplateColumns = `repeat(${size}, 32px)`;
    boardElement.style.gridTemplateRows = `repeat(${size}, 32px)`;

    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = `cell-${x}-${y}`;
            cell.addEventListener('click', () => selectTarget(x, y));

            cell.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });
            cell.addEventListener('drop', (e) => handleRobotDrop(e, x, y));

            const walls = boardState.walls[y][x];
            // NORTH=0, SOUTH=1, EAST=2, WEST=3
            if (walls[CONSTANTS.NORTH]) cell.classList.add('wall-top');
            if (walls[CONSTANTS.SOUTH]) cell.classList.add('wall-bottom');
            if (walls[CONSTANTS.EAST]) cell.classList.add('wall-right');
            if (walls[CONSTANTS.WEST]) cell.classList.add('wall-left');

            if ((x === size / 2 || x === size / 2 - 1) && (y === size / 2 || y === size / 2 - 1)) {
                cell.classList.add('center-block');
            }

            boardElement.appendChild(cell);
        }
    }

    boardState.robots.forEach((pos, idx) => {
        const [x, y] = pos;
        const robotElement = document.createElement('div');
        robotElement.classList.add('robot', `robot-${idx}`);
        robotElement.id = `robot-${idx}`;
        robotElement.setAttribute('draggable', 'true');
        robotElement.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', idx);
            e.dataTransfer.effectAllowed = 'move';
        });

        const cell = document.getElementById(`cell-${x}-${y}`);
        if (cell) {
            cell.appendChild(robotElement);
        }
    });
}

function updateRobotPositions(newRobots) {
    boardState.robots = newRobots;

    newRobots.forEach((pos, idx) => {
        const [x, y] = pos;
        const robotElement = document.getElementById(`robot-${idx}`);
        const cell = document.getElementById(`cell-${x}-${y}`);
        if (robotElement && cell) {
            cell.appendChild(robotElement);
        }
    });
}

async function handleRobotDrop(e, x, y) {
    clearArrows();
    e.preventDefault();
    const robotIdx = parseInt(e.dataTransfer.getData('text/plain'));
    if (isNaN(robotIdx)) return;

    if ((x === boardState.size / 2 || x === boardState.size / 2 - 1) && 
        (y === boardState.size / 2 || y === boardState.size / 2 - 1)) {
        return;
    }

    const isOccupied = boardState.robots.some(pos => pos[0] === x && pos[1] === y);
    if (isOccupied) {
        return;
    }

    try {
        const res = await fetch('/api/set_robot_pos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                robot_idx: robotIdx,
                x: x,
                y: y
            })
        });

        if (res.ok) {
            const data = await res.json();
            updateRobotPositions(data.robots);
            document.getElementById('solve-result').innerText = '';
        }
    } catch (e) {
        console.error("Set position failed:", e);
    }
}

async function move(direction) {
    clearArrows();
    if (isMoving) return;

    const selectedRobotInput = document.querySelector('input[name="robot"]:checked');
    if (!selectedRobotInput) return;

    const selectedRobotIdx = parseInt(selectedRobotInput.value);

    isMoving = true;
    try {
        const res = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                robot_idx: selectedRobotIdx,
                direction: direction
            })
        });

        if (res.ok) {
            const data = await res.json();
            updateRobotPositions(data.robots);
        }
    } catch (e) {
        console.error("Action failed:", e);
    }

    setTimeout(() => { isMoving = false; }, 200);
}

async function undoMove() {
    clearArrows();
    if (isMoving) return;
    isMoving = true;
    try {
        const res = await fetch('/api/undo', {
            method: 'POST'
        });
        if (res.ok) {
            const data = await res.json();
            updateRobotPositions(data.robots);
            document.getElementById('solve-result').innerText = '';
        }
    } catch (e) {
        console.error("Undo failed:", e);
    }
    setTimeout(() => { isMoving = false; }, 200);
}

// Keyboard
document.addEventListener('keydown', (e) => {
    switch (e.key.toLowerCase()) {
        case 'w':
        case 'arrowup':
            move(CONSTANTS.NORTH);
            break;
        case 's':
        case 'arrowdown':
            move(CONSTANTS.SOUTH);
            break;
        case 'd':
        case 'arrowright':
            move(CONSTANTS.EAST);
            break;
        case 'a':
        case 'arrowleft':
            move(CONSTANTS.WEST);
            break;
        case 'z':
            undoMove();
            break;
    }
});

function selectTarget(x, y) {
    clearArrows();
    if ((x === boardState.size / 2 || x === boardState.size / 2 - 1) && (y === boardState.size / 2 || y === boardState.size / 2 - 1)) {
        return;
    }

    // Delete previous target
    if (targetPos) {
        const oldCell = document.getElementById(`cell-${targetPos.x}-${targetPos.y}`);
        if (oldCell) oldCell.style.backgroundColor = '';
    }

    targetPos = { x, y };
    const newCell = document.getElementById(`cell-${x}-${y}`);
    if (newCell) newCell.style.backgroundColor = '#fef3c7';

    document.getElementById('target-coords').innerText = `(${x}, ${y})`;
    document.getElementById('solve-result').innerText = '';
}

async function solve() {
    if (!targetPos) {
        alert("Kérlek válassz ki egy célt a pályán (kattints egy mezőre)!");
        return;
    }
    const selectedRobotInput = document.querySelector('input[name="robot"]:checked');
    if (!selectedRobotInput) return;
    const selectedRobotIdx = parseInt(selectedRobotInput.value);
    const algorithm = document.getElementById('algorithm-select').value;

    document.getElementById('solve-result').innerText = 'Keresés folyamatban...';

    try {
        const res = await fetch('/api/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                robot_idx: selectedRobotIdx,
                target_x: targetPos.x,
                target_y: targetPos.y,
                algorithm: algorithm
            })
        });

        if (res.ok) {
            const data = await res.json();
            clearArrows();

            if (data.path === null) {
                document.getElementById('solve-result').innerHTML = `Nem található megoldás a megadott lépésszámon belül.<br><span style="font-size:13px;color:#666;">Kipróbált állapotok: ${data.states_evaluated} db</span>`;
            } else if (data.path.length === 0) {
                document.getElementById('solve-result').innerHTML = `A célba értünk! Nincs szükség további lépésre.<br><span style="font-size:13px;color:#666;">Kipróbált állapotok: ${data.states_evaluated} db</span>`;
            } else {
                const colors = { 0: "Zöld", 1: "Piros", 2: "Sárga", 3: "Kék", 4: "Fekete" };
                const hexColors = { 0: "#0a8754", 1: "#f64740", 2: "#ffb703", 3: "#8ecae6", 4: "#000000" };
                const dirs = { 0: "Észak", 1: "Dél", 2: "Kelet", 3: "Nyugat" };

                let resultHtml = `<div style="color: #059669;">Megoldás megtalálva! Lépésszám: ${data.path.length}</div>`;
                resultHtml += `<div style="font-size: 13px; color: #666; margin-top: 4px;">Kipróbált állapotok: ${data.states_evaluated} db</div>`;
                resultHtml += '<div style="margin-top: 10px; padding: 10px; background: white; border: 1px dashed #ccc; border-radius: 4px; max-height: 180px; overflow-y: auto; text-align: left; font-size: 14px; font-weight: normal; color: #333;">';

                data.path.forEach((step, idx) => {
                    const colorHtml = `<strong style="color: ${hexColors[step.robot]}">${colors[step.robot]}</strong>`;
                    resultHtml += `<div>${idx + 1}. lépés: ${colorHtml} robot ➔ <strong>${dirs[step.dir]}</strong></div>`;

                    if (step.start && step.end) {
                        const [sx, sy] = step.start;
                        const [ex, ey] = step.end;
                        const startX = sx * 33 + 16;
                        const startY = sy * 33 + 16;
                        const endX = ex * 33 + 16;
                        const endY = ey * 33 + 16;

                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', startX);
                        line.setAttribute('y1', startY);
                        line.setAttribute('x2', endX);
                        line.setAttribute('y2', endY);
                        line.setAttribute('stroke', hexColors[step.robot]);
                        line.setAttribute('stroke-width', '4');
                        line.setAttribute('marker-end', `url(#arrow-${step.robot})`);
                        line.setAttribute('opacity', '0.7');

                        document.getElementById('arrow-layer').appendChild(line);
                    }
                });

                resultHtml += '</div>';
                document.getElementById('solve-result').innerHTML = resultHtml;
            }
        }
    } catch (e) {
        console.error("Solve failed:", e);
        document.getElementById('solve-result').innerText = 'Hiba történt a keresés során.';
    }
}

function clearArrows() {
    const layer = document.getElementById('arrow-layer');
    if (!layer) return;
    const defs = layer.querySelector('defs');
    layer.innerHTML = '';
    if (defs) layer.appendChild(defs);
}

initGame();
