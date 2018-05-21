from engine import Engine

class Simulation1():

    def __init__(self):
        self.move_no = 0

        self.color_blue = 0
        self.y_shift = 0

    def next_move(self):

        self.color_blue += 16
        if self.color_blue > 255:
            self.color_blue = 0

        self.y_shift += 1
        if self.y_shift > 100:
            self.y_shift = 0

    def cells_iter(self):
        for x in range(10):
            for y in range(5):
                new_x = x * 10
                new_y = y * 10 + self.y_shift
                color = (x*y*5, new_y, self.color_blue)
                yield (new_x, new_y, color)


if __name__ == '__main__':
    sim1 = Simulation1()
    engine = Engine(width=100, height=100, cell_size_px=5, fps=25)
    engine.loop(move_fnc=sim1.next_move, cells_iter=sim1.cells_iter)
