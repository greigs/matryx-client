from matryx.matrix import MATRIX_WIDTH, MATRIX_HEIGHT


SCREEN_WIDTH = MATRIX_WIDTH
SCREEN_HEIGHT = MATRIX_HEIGHT


class Screen:
    def __init__(self, matrix):
        self.matrix = matrix

    def prepare(self):
        pass

    def update(self):
        pass
