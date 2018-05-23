from engine import Engine
from world import World
from cell import SimplePhysicalCell

if __name__ == '__main__':
    width = 100
    height = 100

    engine = Engine(width=width, height=height, cell_size_px=5, fps=25)

    world = World(width=width, height=height)
    cell1 = SimplePhysicalCell(world.physical_layer, (50, 100, 150), [4, 4, 4, 1, 1, 1])
    cell2 = SimplePhysicalCell(world.physical_layer, (150, 100, 50),
                               [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 5, 5, 5, 5, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 4,
                                4, 4, 4, 0, 0, 0, 0])
    world.add_physical_cell(cell1, (50, 50))
    world.add_physical_cell(cell2, (50, 51))

    engine.loop(move_fnc=world.next_move, cells_iter=world.physical_cells_iter)
