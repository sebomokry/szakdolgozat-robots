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
    boardElement.innerHTML = '';

    const size = boardState.size;
    boardElement.style.gridTemplateColumns = `repeat(${size}, 32px)`;
    boardElement.style.gridTemplateRows = `repeat(${size}, 32px)`;

    // Render cells and walls
    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = `cell-${x}-${y}`;
            cell.addEventListener('click', () => selectTarget(x, y));

            const walls = boardState.walls[y][x];
            // [Észak, Dél, Kelet, Nyugati] - in the Python logic: NORTH=0, SOUTH=1, EAST=2, WEST=3
            if (walls[CONSTANTS.NORTH]) cell.classList.add('wall-top');
            if (walls[CONSTANTS.SOUTH]) cell.classList.add('wall-bottom');
            if (walls[CONSTANTS.EAST]) cell.classList.add('wall-right');
            if (walls[CONSTANTS.WEST]) cell.classList.add('wall-left');

            // Középső négyzet szinezése (Ricochet board közép 2x2 / 8,8 környéke)
            if ((x === size / 2 || x === size / 2 - 1) && (y === size / 2 || y === size / 2 - 1)) {
                cell.classList.add('center-block');
            }

            boardElement.appendChild(cell);
        }
    }

    // Render robots
    boardState.robots.forEach((pos, idx) => {
        const [x, y] = pos;
        const robotElement = document.createElement('div');
        robotElement.classList.add('robot', `robot-${idx}`);
        robotElement.id = `robot-${idx}`;

        const cell = document.getElementById(`cell-${x}-${y}`);
        if (cell) {
            cell.appendChild(robotElement);
        }
    });
}

function updateRobotPositions(newRobots) {
    boardState.robots = newRobots;

    // Smooth transition
    newRobots.forEach((pos, idx) => {
        const [x, y] = pos;
        const robotElement = document.getElementById(`robot-${idx}`);
        const cell = document.getElementById(`cell-${x}-${y}`);
        if (robotElement && cell) {
            cell.appendChild(robotElement);
        }
    });
}

async function move(direction) {
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

    // Add small delay to prevent spam
    setTimeout(() => { isMoving = false; }, 200);
}

// Keyboard controls handler
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
    }
});

function selectTarget(x, y) {
    if ((x === boardState.size / 2 || x === boardState.size / 2 - 1) && (y === boardState.size / 2 || y === boardState.size / 2 - 1)) {
        return; // Középső falra nem lehet célt tenni
    }

    // Előző cél törlése
    if (targetPos) {
        const oldCell = document.getElementById(`cell-${targetPos.x}-${targetPos.y}`);
        if (oldCell) oldCell.style.backgroundColor = '';
    }

    targetPos = { x, y };
    const newCell = document.getElementById(`cell-${x}-${y}`);
    if (newCell) newCell.style.backgroundColor = '#fef3c7'; // Sárgás/narancs szín jelöli a célt

    document.getElementById('target-coords').innerText = `(${x}, ${y})`;
    document.getElementById('solve-result').innerText = ''; // Eredmény törlése
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

            if (data.path === null) {
                document.getElementById('solve-result').innerText = 'Nem található megoldás a megadott lépésszámon belül.';
            } else if (data.path.length === 0) {
                document.getElementById('solve-result').innerText = 'A célba értünk! Nincs szükség további lépésre.';
            } else {
                const colors = { 0: "Zöld", 1: "Piros", 2: "Sárga", 3: "Kék", 4: "Fekete" };
                const dirs = { 0: "Észak", 1: "Dél", 2: "Kelet", 3: "Nyugat" };

                let resultHtml = `<div style="color: #059669;">Megoldás megtalálva! Lépésszám: ${data.path.length}</div>`;
                resultHtml += '<div style="margin-top: 10px; padding: 10px; background: white; border: 1px dashed #ccc; border-radius: 4px; max-height: 180px; overflow-y: auto; text-align: left; font-size: 14px; font-weight: normal; color: #333;">';

                data.path.forEach((step, idx) => {
                    const colorHtml = `<strong style="color: ${step.robot === 0 ? '#0a8754' : step.robot === 1 ? '#f64740' : step.robot === 2 ? '#ffb703' : step.robot === 3 ? '#000000' : '#8ecae6'}">${colors[step.robot]}</strong>`;
                    resultHtml += `<div>${idx + 1}. lépés: ${colorHtml} robot ➔ <strong>${dirs[step.dir]}</strong></div>`;
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

// Initialize on page load
initGame();
