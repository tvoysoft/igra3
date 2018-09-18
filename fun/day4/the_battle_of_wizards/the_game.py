'''
    Wizards move between sky and earth and throw fireballs.
    Fireballs fly strait and blow when touch anything.
'''

import world
import game
from cells import PhysicalCell

from world import Direction as D

bri = world.change_brigness


class BaseColors:
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)


class WizardGame(game.BaseGame):
    def __init__(self, width=40, height=40, cell_size_px=15, fps=24):
        super().__init__(width, height, cell_size_px, fps)
        self.wizards = []
        self.config = [
            {
                'name': 'First Wizard',
                'color': (30, 30, 120),
                'fireball': (180, 120, 255),
                'pos': (10, 3)
            },

            {
                'name': 'Second Wizard',
                'color': (30, 120, 30),
                'fireball': (30, 255, 30),
                'pos': (self.world.width - 10, 3)
            }
        ]

    def create_cells(self):

        for y in range(3):
            for x in range(self.world.width):
                c = Earth(self.ag, bri((90, 40, 10), 10 + 3 * y))
                self.world.add_physical_cell(cell=c, point=(x, y))

        for y in range(2):
            for x in range(self.world.width):
                self.world.add_physical_cell(cell=Sky(self.ag, (165, 225, 255)),
                                             point=(x, self.world.height - 1 - y))

        for cfg in self.config:
            cell = Wizard(self.ag,
                          name=cfg['name'],
                          color=cfg['color'],
                          fireball_color=cfg['fireball'],
                          )
            if self.world.add_physical_cell(cell=cell, point=cfg['pos']):
                self.wizards.append(cell)


class Wizard(PhysicalCell):
    def __init__(self, layer_agent, name=None, color=None, fireball_color=None):
        super().__init__(layer_agent, name)
        self.fireball_direction = D.NO

        if color is not None:
            self.color = color
        else:
            self.color = BaseColors.WHITE

        if fireball_color is not None:
            self.fireball_color = fireball_color
        else:
            self.fireball_color = BaseColors.RED

        self.dir = D.UP
        self.move_timer = 0
        self.fireball_timer = 0
        self.fireballs_count = 50

    def next_move(self):
        super().next_move()

        if self.move_timer >= 5:
            self.move_timer = 0
            if not self.layer_agent.move_simple(self, self.dir):
                self.change_dir()
        else:
            self.move_timer += 1

        if self.fireball_timer >= 25:
            self.fireball_timer = 0
            self.fire()
        else:
            self.fireball_timer += 1

    def change_dir(self):
        if self.dir == D.UP:
            self.dir = D.DOWN
        else:
            self.dir = D.UP

    def fire(self):
        self.fireball_direction += 1
        if self.fireball_direction > D.MAX:
            self.fireball_direction = D.NO

        fireball = Fireball(self.layer_agent, self.fireball_direction,
                            color=self.fireball_color,
                            lifetime=30,
                            wizard=self)
        if self.layer_agent.add_relative(fireball, self, self.fireball_direction):
            self.fireballs_count -= 1

            # if self.fireballs_count <= 0:
            #     self.destroy()


class Fireball(PhysicalCell):
    def __init__(self, layer_agent, direction=D.NO, color=BaseColors.YELLOW, wizard=None, lifetime=None):
        super().__init__(layer_agent, 'Fireball')
        self.lifetime = lifetime
        self.color = color
        self.moving = True
        self.direction = direction
        self.burn_timer = 0
        self.wizard = wizard

    def next_move(self):
        super().next_move()
        if self.moving:
            if not self.layer_agent.move_simple(self, self.direction):
                self.moving = False
                self.blow2()
            else:
                if self.lifetime is not None:
                    self.lifetime -= 1
                    if self.lifetime < 0:
                        self.burn()
        else:
            self.burn()

    def blow(self):
        self.color = BaseColors.RED
        cells = self.layer_agent.get_nearby(self)
        for cell in cells:
            if cell != self.wizard:
                cell.destroy()
        self.burn()

    def blow2(self):
        """
        blows only 3 cells in direction and near
        :return:
        """
        self.color = BaseColors.RED
        cells = [
            self.layer_agent.get_nearby(self, d)
            for d in (self.direction,) + world.Direction.near(self.direction)
        ]

        for cell in cells:
            if cell is not None:
                if cell != self.wizard:
                    pos = cell.position
                    cell.destroy()
                    flame = Fireball(self.layer_agent)
                    self.layer_agent.add(flame, pos)
                    flame.moving = False
                    flame.color = BaseColors.RED
                    flame.burn()

        self.destroy()

    def burn(self):
        self.burn_timer += 1
        self.color = bri(self.color, (100 - self.burn_timer * 2))
        if self.burn_timer >= 50:
            self.destroy()


class Earth(PhysicalCell):
    def __init__(self, layer_agent, color: tuple, name='Earth'):
        super().__init__(layer_agent, name=name)
        self.color = color


class Sky(PhysicalCell):
    def __init__(self, layer_agent, color: tuple, name='Sky'):
        super().__init__(layer_agent, name)
        self.color = color


if __name__ == '__main__':
    WizardGame(width=80, height=30, cell_size_px=10, fps=100).start()
