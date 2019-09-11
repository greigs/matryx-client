import time

import matryx.screens
from matryx.matrix import RGBMatrixCanvas

FPS = 60


def run():
    matrix = RGBMatrixCanvas()

    print(f"Screens: {list(matryx.screens.get_available_screens())}")

    screen = matryx.screens.get_screen_class("plasma")(matrix)
    screen.prepare()

    while True:
        screen.update()
        matrix.sync()

        time.sleep(1 / FPS)


if __name__ == "__main__":
    run()
