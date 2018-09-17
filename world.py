from common import TwoWayLinkSet
import colorsys

Point = tuple

class Direction:
    MAX = 8
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
    def apply(cls, position: Point, direction):
        """
        :param position:
        :param direction:
            1 2 3
            4 0 5
            6 7 8
        :return: point
        """
        if position is None:
            return None
        x, y = position
        if direction in Direction._ALL_UP:
            y += 1
        elif direction in Direction._ALL_DOWN:
            y -= 1
        if direction in Direction._ALL_LEFT:
            x -= 1
        elif direction in Direction._ALL_RIGHT:
            x += 1
        return x, y

def change_brigness(rgb, brightness):  # TODO: very slow, make faster
    '''

    :param rgb: tuple 0..255
    :param brightness: 0..100
    :return: tuple 0..255
    '''
    rgb01 = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    hsv = colorsys.rgb_to_hsv(*rgb01)
    new_rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], 0.01 * brightness)
    return new_rgb[0] * 255, new_rgb[1] * 255, new_rgb[2] * 255

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

    def apply_direction(self, point, direction):
        return self.norm(Direction.apply(point, direction))


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

    def get_cell(self, position, direction=None):
        if direction is None:
            return self.__point_to_cell.get(position, None)
        else:
            return self.__point_to_cell.get(self.norm(Direction.apply(position, direction)), None)

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

    def position(self, cell, direction=None):
        if direction is None:
            return self.__cell_to_point.get(cell, None)
        else:
            return self.norm(Direction.apply(self.__cell_to_point.get(cell, None), direction))

    def move(self, cell, point):
        if point is None or cell is None:
            return False
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
        return self.move(cell, self.position(cell, direction))

    def move_multiple_in_direction(self, cells, direction):
        overlapped = []
        for cell in cells:
            ov = self.get_cell(self.position(cell, direction))
            if ov is not None:
                overlapped.append(ov)
        if len(overlapped) == 0:
            can_move = True
        else:
            can_move = set(overlapped).issubset(set(cells))
        if can_move:
            # hmmm....
            current_points = [(cell, self.position(cell)) for cell in cells]
            for cell, position in current_points:
                del self.__point_to_cell[position]
            for cell, position in current_points:
                new_position = self.norm(Direction.apply(position, direction))
                self.__cell_to_point[cell] = new_position
                self.__point_to_cell[new_position] = cell
            return True
        else:
            return False

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

    def add(self, cell, position: Point, direction=Direction.NO):
        return self.layer.add(cell, Direction.apply(position, direction))

    def add_relative(self, cell, base_cell, direction):
        return self.add(cell, self.layer.position(base_cell), direction)

    def add_linked(self, cell_to_add, base_cell, direction):
        if self.add(cell_to_add, self.layer.position(base_cell), direction):
            self.link(base_cell, cell_to_add)
            return True
        else:
            return False

    def kill(self, cell):
        return self.layer.remove(cell)

    def link(self, cell1, cell2, **kwargs):
        self.__links.set(cell1, cell2, kwargs)

    def unlink(self, cell1, cell2):
        return self.__links.remove(cell1, cell2, True)

    @property
    def all_groups(self) -> tuple:
        '''

        :return: groups of cells
        '''
        return self.__links.get_groups()

    def get_nearby(self, cell, direction=None):
        '''

        :param cell:
        :param direction:
        :return: None, cell or list of cells
        '''
        if direction is not None:
            return self.layer.get_cell(self.layer.position(cell, direction))
        else:
            cells = []
            for d in Direction.ANY:
                c = self.layer.get_cell(self.layer.position(cell, d))
                if c is not None:
                    cells.append(c)
            return cells

    def get_group(self, cell) -> set:
        '''
        :return: cell's group (list with this cell and all linked)
        '''
        group = self.__links.get_single_group(cell)
        if group is not None:
            return group
        else:
            return {cell}

    def get_linked(self, cell) ->list:
        pass

    def move_simple(self, cell, direction):
        return self.layer.move_in_direction(cell, direction)

    def move_linked(self, cell, direction):
        self.layer.move_multiple_in_direction(self.get_group(cell), direction)

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
        return self.physical_layer.agent.add(cell, point)


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
            yield point[0], self.height - point[1], cell.color

    def groups_iter(self):
        """
            Just to test
        """
        groups = self.physical_layer.agent.all_groups
        cnt = len(groups)
        for cell, point in self.physical_layer.cell_pos_iter:
            cell_group_no = -1
            for num, group in enumerate(groups):
                if cell in group:
                    cell_group_no = num
                    break
            if cnt == 0 or cell_group_no < 0:
                color = cell.color
            else:
                color = (64, 64, 127 + 128 * cell_group_no // cnt)
            yield point[0], self.height - 1 - point[1], color
