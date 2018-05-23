class Cell:
    def __init__(self, layer):
        self.layer = layer

    def next_move(self):
        pass


class PhysicalCell(Cell):
    def __init__(self, layer):
        super().__init__(layer)


class SimplePhysicalCell(PhysicalCell):
    def __init__(self, layer, color: tuple, directions: list):
        super().__init__(layer)
        self.color = color
        self.directions = directions
        self.directions_count = len(directions)
        self.cur_dir = -1

    def next_move(self):
        super().next_move()
        self.cur_dir += 1
        if self.cur_dir >= self.directions_count:
            self.cur_dir = 0
        direction = self.directions[self.cur_dir]
        self.layer.move_in_direction(self, direction)
