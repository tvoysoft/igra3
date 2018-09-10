from engine import Engine
from world import World
import cell

if __name__ == '__main__':
    width = 40
    height = 40

    engine = Engine(width=width, height=height, cell_size_px=10, fps=25)

    world = World(width=width, height=height)
    cell1 = cell.SimplePhysicalCell(world.physical_layer.agent, (50, 100, 150), [4, 4, 4, 1, 1, 1])
    cell2 = cell.SimplePhysicalCell2(world.physical_layer.agent, (150, 100, 50),
                               [0, 0, 0, 0, 0, 0, 0, 0,
                                1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 5, 5, 5, 5,
                                8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 4, 4, 4, 4,
                                0, 0, 0, 9, 0, 0, 0, 0])
    world.add_physical_cell(cell1, (20, 20))
    world.add_physical_cell(cell2, (20, 21))

    engine.loop(move_fnc=world.next_move, cells_iter=world.physical_cells_iter)
