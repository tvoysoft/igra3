from engine import Engine
from world import World, Direction
import cells


class BaseGame:

    def __init__(self, width=40, height=40, cell_size_px=15, fps=24):
        self.world = World(width=width, height=height)
        self.ag = self.world.physical_layer.agent
        self.engine = Engine(width=width, height=height, cell_size_px=cell_size_px, fps=fps)

    def start(self, move_fnc=None, cells_iter=None):
        self.create_cells()
        if move_fnc is None:
            move_fnc = self.world.next_move
        if cells_iter is None:
            cells_iter = self.world.groups_iter
        self.engine.loop(move_fnc=move_fnc, cells_iter=cells_iter)
        # for g in world.physical_layer.agent.all_groups:
        #     print(len(g), ','.join([str(c.id) for c in g]))

    def create_cells(self):
        raise NotImplementedError


class DebugGame(BaseGame):

    def create_cells(self):
        cell1 = cells.SimplePhysicalCell(
            self.world.physical_layer.agent,
            (50, 100, 150),
            [4, 4, 4, 1, 1, 1]
        )
        self.world.add_physical_cell(cell1, (25, 25))

        self.cell2 = cells.SimplePhysicalCell2(
            self.world.physical_layer.agent,
            (150, 100, 50),
            [0, 0, 2, 2, 2, 0, 4, 4, 9],
            name="Master"
        )
        self.world.add_physical_cell(self.cell2, (20, 21))


if __name__ == '__main__':

    # cell3 = cell.SimplePhysicalCell2(world.physical_layer.agent, (0, 255, 255), [], name="Slave")
    # world.physical_layer.agent.add_linked_cell(cell3, cell2, Direction.DOWN)
    game = DebugGame(fps=20)
    game.start()
    print([str(cell) for cell in game.world.physical_layer.agent.get_group(game.cell2)])

