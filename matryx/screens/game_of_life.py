import colorsys
import math
import random
import time

import cairo

from matryx.screen import Screen, SCREEN_WIDTH, SCREEN_HEIGHT
from matryx.utils import iterate_2d

NEIGHBOUR_PATTERN = [(x, y) for x in range(-1, 2) for y in range(-1, 2)]


def create_empty_grid():
    return [[None for y in range(SCREEN_HEIGHT)] for x in range(SCREEN_WIDTH)]


def create_random_grid():
    return [
        [random.choice([None, None, None, random.random()]) for y in range(SCREEN_HEIGHT)]
        for x in range(SCREEN_WIDTH)
    ]


def hex_to_rgb(hex_str):
    hex_str = hex_str[1:]

    hex_rgb_str = [
        hex_str[x : x + 2] for x in range(0, len(hex_str), int(len(hex_str) / 3))
    ]

    hex_rgb = [int(x, 16) for x in hex_rgb_str]
    hex_rgb_norm = [x / 255 for x in hex_rgb]

    return hex_rgb_norm


GRADIENT = [
    hex_to_rgb("#FFFFFF"),

]


def lerp(a, b, x):
    return (1 - x) * a + x * b


def lerp_seq(a, b, x):
    return tuple([lerp(a2, b2, x) for a2, b2 in zip(a, b)])


def lerp_circular(a, b, x):
    a2 = a * 2 * math.pi
    b2 = b * 2 * math.pi

    x2 = (1 - x) * math.cos(a2) + x * math.cos(b2)
    y2 = (1 - x) * math.sin(a2) + x * math.sin(b2)

    v = math.atan2(y2, x2)
    v = v / (math.pi)

    return v


def lerp_color(a, b, x):
    x = x % 1

    hsv_a = a
    hsv_b = b
    #hsv_a = colorsys.rgb_to_hsv(*a)
    #hsv_b = colorsys.rgb_to_hsv(*b)

    hsv_v = (
        math.sqrt(lerp(hsv_a[0] ** 2, hsv_b[0] ** 2, x)),
        math.sqrt(lerp(hsv_a[1] ** 2, hsv_b[1] ** 2, x)),
        math.sqrt(lerp(hsv_a[2] ** 2, hsv_b[2] ** 2, x)),
    )

    #return colorsys.hsv_to_rgb(*hsv_v)
    return hsv_v


def lerp_gradient_map(gradient_map, x):
    x = x % 1

    gradient_map = gradient_map + list(reversed(gradient_map))
    if x == 0:
        return gradient_map[0]
    elif x == 1:
        return gradient_map[:-1]

    gradients_len = len(gradient_map)
    final_step_index = gradients_len - 1

    max_x = final_step_index / gradients_len
    x = x * max_x

    step_index = int(x * gradients_len)
    next_step_index = step_index + 1

    min_x = step_index * (1 / gradients_len)
    max_x = (step_index + 1) * (1 / gradients_len)

    x = (x - min_x) / (1 / gradients_len)

    #return lerp_color(gradient_map[step_index], gradient_map[next_step_index], x)
    return gradient_map[int(x * len(gradient_map))]


class Timer:
    def __init__(self, interval):
        self.interval = interval
        self.reset()

    @property
    def has_ticked(self):
        return True if time.perf_counter() >= self.next_tick else False

    def reset(self):
        self.next_tick = time.perf_counter() + self.interval


class Clock(Screen):
    def __init__(self, matrix):
        super().__init__(matrix)

        self.grid = None
        self.sim_timer = Timer(0.025)
        self.reset_timer = Timer(10)

    def prepare(self):
        self.grid = create_random_grid()

    def update(self):
        self.matrix.ctx.save()
        self.matrix.ctx.set_operator(cairo.Operator.MULTIPLY)

        fade = 0.75
        self.matrix.ctx.set_source_rgb(fade, fade, fade)
        self.matrix.ctx.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.matrix.ctx.fill()
        self.matrix.ctx.restore()

        for x, y in iterate_2d(SCREEN_WIDTH, SCREEN_HEIGHT):
            if self.grid[x][y]:
                rgb = lerp_gradient_map(GRADIENT, self.grid[x][y])
                self.matrix.ctx.set_source_rgb(*rgb)
                self.matrix.ctx.rectangle(x, y, 1, 1)
                self.matrix.ctx.fill()

        if self.reset_timer.has_ticked:
            self.grid = create_random_grid()
            self.reset_timer.reset()

        if self.sim_timer.has_ticked:
            new_grid = create_empty_grid()

            for x, y in iterate_2d(SCREEN_WIDTH, SCREEN_HEIGHT):
                neighbours, hue_avg = self.calculate_neighbhours(x, y)

                if self.grid[x][y] and (neighbours < 2 or neighbours > 3):
                    new_grid[x][y] = None
                elif not self.grid[x][y] and neighbours == 3:
                    new_grid[x][y] = hue_avg
                else:
                    new_grid[x][y] = self.grid[x][y]

            self.grid = new_grid
            self.sim_timer.reset()

    def calculate_neighbhours(self, x, y):
        neighbours = 0
        hue_avg = None

        for u, v in NEIGHBOUR_PATTERN:
            n_x = (x + u) % SCREEN_WIDTH
            n_y = (y + v) % SCREEN_HEIGHT

            if n_x == x and n_y == y:
                continue

            if self.grid[n_x][n_y]:
                neighbours += 1

                if not hue_avg:
                    hue_avg = self.grid[n_x][n_y]
                else:
                    hue_avg = lerp_circular(hue_avg, self.grid[n_x][n_y], 0.5)

        #if neighbours > 0:
        #    hue_avg = hue_sum / neighbours
        #else:
        #    hue_avg = 0
        return neighbours, hue_avg


screen_class = Clock
