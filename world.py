from common import TwoWayLinkSet

class Direction:
    UP_LEFT = LEFT_UP = 1
    UP = 2
    UP_RIGHT = RIGHT_UP = 3
    LEFT = 4
    RIGHT = 5
    DOWN_LEFT = LEFT_DOWN = 6
    DOWN = 7
    DOWN_RIGHT = RIGHT_DOWN = 8

    NO = 0

    HORIZONTAL = (LEFT, RIGHT)
    VERTICAL = (UP, DOWN)
    DIAGONAL = (LEFT_UP, RIGHT_UP, LEFT_DOWN, RIGHT_DOWN)
    ANY = tuple(range(1, 9))

    _ALL_UP = (LEFT_UP, UP, RIGHT_UP)
    _ALL_DOWN = (LEFT_DOWN, DOWN, RIGHT_DOWN)
    _ALL_LEFT = (LEFT_UP, LEFT, LEFT_DOWN)
    _ALL_RIGHT = (RIGHT_UP, RIGHT, RIGHT_DOWN)

    @classmethod
    def apply(cls, point, direction):
        """
        :param point:
        :param direction:
            1 2 3
            4 0 5
            6 7 8
        :return: point
        """
        if point is None:
            return None
        x, y = point
        if direction in Direction._ALL_UP:
            y += 1
        elif direction in Direction._ALL_DOWN:
            y -= 1
        if direction in Direction._ALL_LEFT:
            x -= 1
        elif direction in Direction._ALL_RIGHT:
            x += 1
        return x, y


class Layer:
    def __init__(self, world, width, height, concatenated):
        self.world = world
        self.width = width
        self.height = height
        self.concatenated = concatenated

    def has_cell(self, cell):
        return False

    def norm(self, point):
        if point is None:
            return None
        elif (0 <= point[0] < self.width) and (0 <= point[1] < self.height):
            return point
        elif self.concatenated:
            return (point[0] + self.width) % self.width, (point[1] + self.height) % self.height
        else:
            return None

    def direction_to_point(self, current_point, direction):
        return self.norm(Direction.apply(current_point, direction))


class PhysicalLayer(Layer):
    def __init__(self, world, width, height):
        super().__init__(world, width, height, True)

        self.__cell_to_point = {}
        self.__point_to_cell = {}

        self.agent = PhysicalAgent(self)

    @property
    def cell_pos_iter(self):
        for cell, position in self.__cell_to_point.items():
            yield cell, position

    def has_cell(self, cell):
        return cell is not None and cell in self.__cell_to_point

    def is_point_occupied(self, point):
        return self.norm(point) in self.__point_to_cell

    def add(self, cell, point):
        p = self.norm(point)
        if p in self.__point_to_cell or cell in self.__cell_to_point:
            return False
        else:
            self.__point_to_cell[p] = cell
            self.__cell_to_point[cell] = p
            self.world.add_cell_callback(cell, self)
            return True

    def position(self, cell):
        return self.__cell_to_point.get(cell, None)

    def move(self, cell, point):
        if not self.has_cell(cell):
            return False
        to_point = self.norm(point)
        if to_point is None:
            return self.remove(cell)

        if to_point in self.__point_to_cell:
            return False
        cur_point = self.__cell_to_point[cell]
        self.__cell_to_point[cell] = to_point
        self.__point_to_cell[to_point] = cell
        del self.__point_to_cell[cur_point]
        return True

    def move_in_direction(self, cell, direction):
        cur_point = self.__cell_to_point.get(cell, None)
        to_point = self.direction_to_point(cur_point, direction)
        if to_point is None:
            return False
        else:
            return self.move(cell, to_point)

    def remove(self, cell):
        if self.has_cell(cell):
            point = self.__cell_to_point[cell]
            del self.__cell_to_point[cell]
            del self.__point_to_cell[point]
            return True
        else:
            return False


class PhysicalAgent:

    def __init__(self, layer: PhysicalLayer):
        self.layer = layer
        self.__links = TwoWayLinkSet()
        self.move_impulses = []

    def add_cell(self, cell, point):
        add_to_layer = self.layer.add(cell, point)
        print('Add to layer: ', add_to_layer)
        return add_to_layer

    def link_cell(self, cell1, cell2):
        self.__links.set(cell1, cell2)

    def add_linked_cell(self, cell1, cell2, direction):
        point1 = self.layer.position(cell1)
        point2 = self.layer.direction_to_point(point1, direction)
        if point2 is None:
            return False
        if self.add_cell(cell2, point2):
            self.link_cell(cell1, cell2)
            return True
        else:
            return False

    def move_simple(self, cell, direction):
        self.layer.move_in_direction(cell, direction)


    def _new_cycle(self):
        self.move_impulses.clear()

    def impulse(self, cell, direction, power):
        """ Cell wants to move in some direction with some power """
        self.move_impulses.append((cell, direction, power))






class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.physical_layer = PhysicalLayer(self, width=width, height=height)
        self.energy_layer = None
        self.info_layer = None

        # store every cell of every layer here
        self.layer_cells = {
            self.physical_layer: []
        }

    def add_cell_callback(self, cell, layer):
        self.layer_cells[layer].append(cell)

    def add_physical_cell(self, cell, point):
        self.physical_layer.agent.add_cell(cell, point)


    def next_move(self):
        """
            Make next move of each cell of each layer if they are still present there.
        """

        # TODO: sort cells of layers to determine their move order

        # make moves

        for layer, cells in self.layer_cells.items():
            for cell in cells:
                if layer.has_cell(cell):
                    cell.next_move()

        # remove dead cells
        for layer, cells in self.layer_cells.items():
            self.layer_cells[layer] = [cell for cell in cells if layer.has_cell(cell)]

    def physical_cells_iter(self):
        """
            Just to test
        """
        for cell, point in self.physical_layer.cell_pos_iter:
            # convert Y-Axis
            yield self.height - point[0], point[1], cell.color
