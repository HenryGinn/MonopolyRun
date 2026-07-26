import os

from graph import Graph
from server import Server


class Monopoly():

    def __init__(self):
        self.set_paths()

    def set_paths(self):
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.source_path = os.path.join(self.base_path, "Sources")
        self.data_path = os.path.join(self.base_path, "Data")

    def set_server(self):
        self.server = Server(self)

    def set_graph(self):
        self.graph = Graph(self)

