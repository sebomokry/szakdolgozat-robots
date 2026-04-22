class GameState:
    def __init__(self, robot_positions):
        self.robots = list(robot_positions)

    def is_robot_at(self, x, y):
        return (x, y) in self.robots
