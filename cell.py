from unittest.test.test_result import __init__

import world as worldpack

class Cell:
    def __init__(self, layer_agent):
        self.layer_agent = layer_agent  # type: worldpack.PhysicalAgent

    def next_move(self):
        pass


class PhysicalCell(Cell):
    def __init__(self, layer_agent):
        super().__init__(layer_agent)
        self.weight = 1


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
        # use agent to move cell
        self.layer_agent.move_simple(self, direction)


class SimplePhysicalCell2(PhysicalCell):

    def __init__(self, layer_agent, color: tuple, directions: list):
        super().__init__(layer_agent)
        self.color = color
        self.directions = directions
        self.directions_count = len(directions)
        self.cur_dir_no = -1

        self.__clones_count = 0

    def get_next_direction(self):
        self.cur_dir_no += 1
        if self.cur_dir_no >= self.directions_count:
            self.cur_dir_no = 0
        return self.directions[self.cur_dir_no]

    def clone(self, direction):
        c = self.__class__(self.layer_agent, self.color, self.directions)
        if self.layer_agent.add_linked_cell(self, c, direction):
            self.__clones_count += 1
            return c
        else:
            return None

    def next_move(self):
        super().next_move()

        next_direction = self.get_next_direction()
        if next_direction != 9:
            self.layer_agent.move_simple(self, next_direction)
        elif self.__clones_count < 2:
            if self.__clones_count == 0:
                clone_dir = 2
            else:
                clone_dir = 7
            clone = self.clone(clone_dir)


