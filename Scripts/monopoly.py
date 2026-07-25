import os

from server import Server


class Monopoly():

    def __init__(self):
        self.set_source_path()

    def set_source_path(self):
        self.source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "Sources")

    def set_server(self):
        self.server = Server(self)
