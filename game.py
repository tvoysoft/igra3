from engine import Engine
from world import World, Direction
import cell

if __name__ == '__main__':
    width = 40
    height = 40


    world = World(width=width, height=height)
    cell1 = cell.SimplePhysicalCell(world.physical_layer.agent, (50, 100, 150), [4, 4, 4, 1, 1, 1])
    world.add_physical_cell(cell1, (25, 25))

    cell2 = cell.SimplePhysicalCell2(world.physical_layer.agent, (150, 100, 50),
                               [0,0, 5, 0, 9], name="Master")
    world.add_physical_cell(cell2, (20, 21))

    # cell3 = cell.SimplePhysicalCell2(world.physical_layer.agent, (0, 255, 255), [], name="Slave")
    # world.physical_layer.agent.add_linked_cell(cell3, cell2, Direction.DOWN)

    print([str(cell) for cell in world.physical_layer.agent.get_cell_group(cell2)])
    engine = Engine(width=width, height=height, cell_size_px=10, fps=150)
    engine.loop(move_fnc=world.next_move, cells_iter=world.groups_iter)
    for g in world.physical_layer.agent.get_all_cell_groups():
        print(len(g), g)
