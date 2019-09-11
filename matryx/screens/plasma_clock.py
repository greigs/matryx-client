import math
from datetime import datetime

import cairo

from matryx.screen import Screen


class PlasmaClock(Screen):
    def __init__(self, matrix):
        super().__init__(matrix)

    def prepare(self):
        self.t = 0
        self.j = 0
        self.u = 0

        fo = cairo.FontOptions()
        fo.set_antialias(cairo.Antialias.NONE)
        fo.set_hint_style(cairo.HintStyle.FULL)
        fo.set_hint_metrics(cairo.HintMetrics.ON)
        self.matrix.ctx.set_font_options(fo)

        self.matrix.ctx.select_font_face(
            "XLMonoAlt", cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL
        )
        self.matrix.ctx.set_font_size(40)
        self._text_extents = self.matrix.ctx.text_extents("28:88")

        self.blur_surf = cairo.ImageSurface(
            cairo.Format.RGB24, int(64 / 4), int(32 / 4)
        )
        self.blur_ctx = cairo.Context(self.blur_surf)

        self.sine_surf = cairo.ImageSurface(cairo.Format.RGB24, 64, 32)
        self.sine_ctx = cairo.Context(self.sine_surf)

    def update(self):
        self.matrix.identity_matrix()
        self.matrix.clear()

        self.t += 0.0125
        self.j += 0.005
        self.u += 0.03

        for y in range(32):
            for x in range(64):
                px = x - 64 / 2
                py = y - 32 / 2

                pixel = 0

                pixel = pixel + (
                    math.sin(0.3 * ((px * math.sin(self.t / 7))) * 0.5 + self.t)
                )

                pixel = pixel + (
                    math.sin(
                        0.5
                        * ((px * math.sin(self.t / 7)) + (py * math.cos(self.t / 5)))
                        * 0.5
                        + self.t
                    )
                )

                pixel = pixel + (
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
                    ((math.cos(2 * pixel + self.j) * 0.5 + 0.5) ** 1),
                    ((math.cos(2 * pixel + self.j) * 0.5 + 0.5) ** 1),
                    ((math.sin(2 * pixel + self.j) * 0.5 + 0.5) ** 1),
                )
                self.matrix.fill_pixel(x, y)

        self.matrix.ctx.translate(32, 16)
        self.matrix.ctx.move_to(
            -self._text_extents.x_bearing - self._text_extents.width / 2,
            -self._text_extents.y_bearing - self._text_extents.height / 2,
        )

        now = datetime.now()
        now_str = now.strftime("%H:%M")

        self.matrix.ctx.set_operator(cairo.Operator.DEST_IN)
        self.matrix.ctx.set_source_rgb(1.0, 1.0, 1.0)
        self.matrix.ctx.show_text(now_str)
        self.matrix.ctx.set_operator(cairo.Operator.OVER)

        self.sine_ctx.identity_matrix()
        self.sine_ctx.set_source_surface(self.matrix.canvas_surface)
        self.sine_ctx.paint()

        self.matrix.clear()
        self.matrix.identity_matrix()
        self.matrix.ctx.set_source_surface(self.sine_surf)
        # self.matrix.ctx.rectangle(0, 0, 64, 32)
        # self.matrix.ctx.fill()
        for x in range(64):
            m = cairo.Matrix(y0=(math.sin(x / 16 + self.u) * 2))
            self.matrix.ctx.get_source().set_matrix(m)
            self.matrix.ctx.rectangle(x, 0, 1, 32)
            self.matrix.ctx.fill()

        self.blur_ctx.identity_matrix()
        self.blur_ctx.scale(1 / 4, 1 / 4)
        self.blur_ctx.set_source_surface(self.matrix.canvas_surface)
        self.blur_ctx.get_source().set_filter(cairo.Filter.GOOD)
        self.matrix.canvas_surface.flush()
        self.blur_ctx.paint()
        self.blur_surf.flush()

        self.matrix.ctx.set_operator(cairo.Operator.SCREEN)
        self.matrix.identity_matrix()
        self.matrix.ctx.scale(4, 4)
        self.matrix.ctx.set_source_surface(self.blur_surf)
        self.matrix.ctx.paint()

        self.matrix.ctx.set_operator(cairo.Operator.OVER)


screen_class = PlasmaClock
