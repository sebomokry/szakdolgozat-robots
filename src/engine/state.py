class GameState:
    def __init__(self, robot_positions):
        # robot_positions: [(x1, y1), (x2, y2), ...]
        # Az első robot (index 0) általában a célrobot.
        self.robots = list(robot_positions)

    def is_robot_at(self, x, y):
        return (x, y) in self.robots
