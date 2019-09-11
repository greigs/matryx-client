import cairo

from datetime import datetime
from matryx.screen import Screen


class Clock(Screen):
    def __init__(self, matrix):
        super().__init__(matrix)

        self._text_extents = None

    def prepare(self):
        fo = cairo.FontOptions()
        fo.set_antialias(cairo.Antialias.NONE)
        fo.set_hint_style(cairo.HintStyle.FULL)
        fo.set_hint_metrics(cairo.HintMetrics.ON)
        self.matrix.ctx.set_font_options(fo)

        self.matrix.ctx.select_font_face(
            "VCR OSD Mono", cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL
        )
        self.matrix.ctx.set_font_size(21)
        self._text_extents = self.matrix.ctx.text_extents("99:99")

    def update(self):
        self.matrix.identity_matrix()
        self.matrix.clear()

        self.matrix.ctx.translate(32, 16)
        self.matrix.ctx.move_to(
            -self._text_extents.x_bearing - self._text_extents.width / 2,
            -self._text_extents.y_bearing - self._text_extents.height / 2,
        )

        now = datetime.now()
        now_str = now.strftime("%H:%M")

        self.matrix.ctx.set_source_rgb(0.5, 0.25, 0)
        self.matrix.ctx.show_text(now_str)


screen_class = Clock
