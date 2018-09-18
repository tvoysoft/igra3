from unittest.test.test_result import __init__
import world as worldpack


class Cell:
    __counter = 0

    def __init__(self, layer_agent, name=None):
        Cell.__counter += 1
        self.__id = Cell.__counter
        self.name = name
        self.layer_agent = layer_agent  # type: worldpack.PhysicalAgent
        self.ag = layer_agent

    @property
    def id(self):
        return self.__id

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return super().__str__()

    def next_move(self):
        pass

    def destroy(self):
        self.layer_agent.kill(self)


class PhysicalCell(Cell):
    def __init__(self, layer_agent, name=None):
        super().__init__(layer_agent, name=name)
        self.weight = 1

    def get_my_group(self):
        return self.layer_agent.get_group(self)

    @property
    def position(self):
        return self.layer_agent.position(self)


class SimplePhysicalCell(PhysicalCell):
    def __init__(self, layer, color: tuple, directions: list, name=None):
        super().__init__(layer, name=name)
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
    MAX_SINGLE_CLONES = 3
    MAX_TOTAL_CLONES = 500
    TOTAL_CLONES_COUNT = 0

    def __init__(self, layer_agent, color: tuple, directions: list, name=None):
        super().__init__(layer_agent, name=name)
        self.color = color
        if directions is not None:
            self.directions = directions
        else:
            self.directions = []
        self.directions_count = len(directions)
        self.cur_dir_no = -1

        self.__clones_count = 0

    def get_next_direction(self):
        if len(self.directions) == 0:
            return worldpack.Direction.NO
        self.cur_dir_no += 1
        if self.cur_dir_no >= self.directions_count:
            self.cur_dir_no = 0
        return self.directions[self.cur_dir_no]

    def clone(self, direction, is_linked):
        """

        :param direction:
        :param is_linked:
        :return:
        :rtype: SimplePhysicalCell2
        """
        if SimplePhysicalCell2.TOTAL_CLONES_COUNT >= SimplePhysicalCell2.MAX_TOTAL_CLONES:
            return None
        new_name = self.name + '_' + str(self.__clones_count)
        c = self.__class__(self.layer_agent, self.color, self.directions, name=new_name)
        if is_linked:
            added = self.layer_agent.add_linked(c, self, direction)
        else:
            added = self.layer_agent.add_relative(c, self, direction)
        if added:
            self.__clones_count += 1
            SimplePhysicalCell2.TOTAL_CLONES_COUNT += 1
            return c
        else:
            return None

    def next_move(self):
        super().next_move()

        next_direction = self.get_next_direction()
        if next_direction != 9:
            self.layer_agent.move_linked(self, next_direction)  # !!!!!!!!!!!!!!!!!!!!!!!!!!!
        elif self.__clones_count < SimplePhysicalCell2.MAX_SINGLE_CLONES:
            if self.__clones_count == 0:
                clone = self.clone(worldpack.Direction.UP, True)
                # if clone is not None:
                #     clone.color = (255, 0, 0)
            elif self.__clones_count == 1:
                clone = self.clone(worldpack.Direction.DOWN, False)
                if clone is not None:
                    # make clone look brighter
                    clone.color = worldpack.change_brigness(self.color, 40 +
                                                            60
                                                            * SimplePhysicalCell2.TOTAL_CLONES_COUNT
                                                            / SimplePhysicalCell2.MAX_TOTAL_CLONES)

            else:
                for cell in self.get_my_group():
                    if cell != self:
                        self.layer_agent.unlink(self, cell)
                        # print('%s unlinked %s' % (self, cell))
                        self.color = (255, 0, 0)
