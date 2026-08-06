import json
import os

from graph import Graph
from server import Server
from solver import Solver


class Monopoly():

    time_limit = 70 * 60
    terminal = "Metropolis"

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

    def set_solver(self):
        self.solver = Solver(self)

    def load_style(self):
        with open(self.style_path) as file:
            self.style = json.load(file)

    def set_routes(self):
        self.set_routes_path()
        if os.path.exists(self.routes_path):
            self.load_routes()
        else:
            self.graph.construct_routes()

    def set_routes_path(self):
        self.routes_path = os.path.join(
            self.source_path, "Routes.json")

    def load_routes(self):
        with open(self.routes_path, "r") as file:
            self.routes = json.load(file)

    def construct_problem(self):
        self.solver.add_constraints()
        self.solver.gather_constraints()
        self.solver.set_objective_function()

    def draw(self):
        self.graph.draw()

    def solve(self):
        self.solver.solve()
