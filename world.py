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
        """
        :param current_point:
        :param direction:
            1 2 3
            4 0 5
            6 7 8
        :return: point
        """
        if current_point is None:
            return None
        x, y = current_point
        if direction in (1, 2, 3):
            y -= 1
        elif direction in (6, 7, 8):
            y += 1
        if direction in (1, 4, 6):
            x -= 1
        elif direction in (3, 5, 8):
            x += 1
        return self.norm((x, y))


class PhysicalLayer(Layer):
    def __init__(self, world, width, height):
        super().__init__(world, width, height, True)

        self.cell_to_point = {}
        self.point_to_cell = {}

    def has_cell(self, cell):
        return cell is not None and cell in self.cell_to_point

    def is_point_occupied(self, point):
        return self.norm(point) in self.point_to_cell

    def add(self, cell, point):
        p = self.norm(point)
        if p in self.point_to_cell or cell in self.cell_to_point:
            return False
        else:
            self.point_to_cell[p] = cell
            self.cell_to_point[cell] = p
            return True

    def position(self, cell):
        return self.cell_to_point.get(cell, None)

    def move(self, cell, point):
        if not self.has_cell(cell):
            return False
        to_point = self.norm(point)
        if to_point is None:
            return self.remove(cell)

        if to_point in self.point_to_cell:
            return False
        cur_point = self.cell_to_point[cell]
        self.cell_to_point[cell] = to_point
        self.point_to_cell[to_point] = cell
        del self.point_to_cell[cur_point]
        return True

    def move_in_direction(self, cell, direction):
        cur_point = self.cell_to_point.get(cell, None)
        to_point = self.direction_to_point(cur_point, direction)
        if to_point is None:
            return False
        else:
            return self.move(cell, to_point)

    def remove(self, cell):
        if self.has_cell(cell):
            point = self.cell_to_point[cell]
            del self.cell_to_point[cell]
            del self.point_to_cell[point]
            return True
        else:
            return False


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

    def add_physical_cell(self, cell, point):
        if self.physical_layer.add(cell, point):
            self.layer_cells[self.physical_layer].append(cell)

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
        for point, cell in self.physical_layer.point_to_cell.items():
            yield point[0], point[1], cell.color
