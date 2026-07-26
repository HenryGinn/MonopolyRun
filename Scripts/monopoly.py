import json
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
        self.style_path = os.path.join(self.source_path, "style.json")

    def set_server(self):
        self.server = Server(self)

    def set_graph(self):
        self.graph = Graph(self)

    def load_style(self):
        with open(self.style_path) as file:
            self.style = json.load(file)

