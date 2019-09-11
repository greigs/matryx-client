import colorsys
import math

import cairo

from matryx.screen import Screen, SCREEN_WIDTH, SCREEN_HEIGHT


class Plasma(Screen):
    def __init__(self, matrix):
        super().__init__(matrix)

    def prepare(self):
        self.t = 0
        self.j = 0

    def update(self):
        self.matrix.identity_matrix()
        self.matrix.clear()

        self.t += 0.05
        self.j += 0.02

        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                px = x - SCREEN_WIDTH / 2
                py = y - SCREEN_HEIGHT / 2

                pixel = 1

                pixel = pixel * (
                    math.sin(0.3 * ((px * math.sin(self.t / 7))) * 0.5 + self.t)
                )

                pixel = pixel * (
                    math.sin(
                        0.5
                        * ((px * math.sin(self.t / 7)) + (py * math.cos(self.t / 5)))
                        * 0.5
                        + self.t
                    )
                )

                pixel = pixel * (
                    math.sin(
                        0.25
                        * math.sqrt(
                            (px + 16 * math.sin(self.t / 3)) ** 2
                            + (py + 16 * math.cos(self.t / 9)) ** 2
                            + 1
                        )
                        + self.t
                    )
                )

                self.matrix.ctx.set_source_rgb(
                    pixel * 2,
                    0, 0
                )
                self.matrix.fill_pixel(x, y)


screen_class = Plasma
