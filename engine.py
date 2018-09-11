import pygame as pg


class Engine:
    def __init__(self, width, height, cell_size_px=2, fps=50):
        self.width = width
        self.height = height
        self.width_px = width * cell_size_px
        self.height_px = height * cell_size_px

        self.cell_size_px = cell_size_px
        self.fps = fps

        # Setup window and main surface
        pg.display.set_caption("Igra 3")
        size_px = (self.width_px, self.height_px)
        self.window = pg.display.set_mode(size_px)  # type: pg.Surface
        self.main_surface = pg.Surface(size_px)
        self.cell_surface = pg.Surface((cell_size_px, cell_size_px))

    def loop(self, move_fnc=None, cells_iter=None, max_turns=None):
        loop_no = 0
        # Start world
        current_turn = 0
        clock = pg.time.Clock()
        while True:
            clock.tick(self.fps)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

            # Check input
            self.input()

            # Make move
            if move_fnc is not None:
                move_fnc()
            current_turn += 1

            # Draw world
            self.draw_world(cells_iter)

            if max_turns is not None and current_turn >= max_turns:
                return

    def draw_world(self, cells_iter):
        self.main_surface.fill((0, 0, 0))
        for x, y, color in cells_iter():
            if x < self.width and y < self.height:
                _x = x * self.cell_size_px
                _y = y * self.cell_size_px
                self.cell_surface.fill(color)
                self.main_surface.blit(self.cell_surface, (_x, _y))
        self.window.blit(self.main_surface, (0, 0))
        pg.display.flip()

    def input(self):
        pass
