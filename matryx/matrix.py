import math

import cairo
import zmq


MATRIX_WIDTH = 128
MATRIX_HEIGHT = 128


class RGBMatrixClient:
    EXPECTED_BUFFER_SIZE = MATRIX_WIDTH * MATRIX_HEIGHT * 4

    def __init__(self, endpoint):
        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(endpoint)

    def send_frame(self, buffer):
        if len(buffer) != self.EXPECTED_BUFFER_SIZE:
            raise ValueError(
                f"Buffer length must be exactly {self.EXPECTED_BUFFER_SIZE}"
            )

        self._zmq_socket.send(buffer)
        self._zmq_socket.recv()


class RGBMatrixCanvas:
    def __init__(self, width=MATRIX_WIDTH, height=MATRIX_HEIGHT, supersample_ratio=1):
        self.width = width
        self.height = height
        self.supersample_ratio = supersample_ratio

        self._client = RGBMatrixClient("tcp://10.0.10.47:8182")

        self.canvas_surface = cairo.ImageSurface(
            cairo.Format.RGB24,
            self.width * self.supersample_ratio,
            self.height * self.supersample_ratio,
        )
        self._matrix_surface = cairo.ImageSurface(
            cairo.Format.RGB24, self.width, self.height
        )

        self.ctx = cairo.Context(self.canvas_surface)

        self._ctx_matrix = cairo.Context(self._matrix_surface)
        self._ctx_matrix.scale(1 / self.supersample_ratio, 1 / self.supersample_ratio)
        self._ctx_matrix.set_source_surface(self.canvas_surface)
        self._ctx_matrix.get_source().set_filter(cairo.Filter.GOOD)

        self.identity_matrix()

    def fill_pixel(self, x, y):
        self.ctx.rectangle(x, y, 1, 1)
        self.ctx.fill()

    def identity_matrix(self):
        self.ctx.identity_matrix()
        self.ctx.scale(self.supersample_ratio, self.supersample_ratio)

    def clear(self, color=(0, 0, 0)):
        self.ctx.save()
        self.ctx.set_source_rgb(*color)
        self.ctx.paint()
        self.ctx.restore()

    def sync(self):
        self._ctx_matrix.paint()
        self._client.send_frame(self._matrix_surface.get_data())
