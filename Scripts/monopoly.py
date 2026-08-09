import json
import os

from graph import Graph
from server import Server
from solver import Solver


class Monopoly():

    time_limit = 70 * 60
    terminal = "Metropolis"
    stopping_at_place_penalty = 10
    elevation_gain_penalty = 0.5
    elevation_loss_reward = 0.3
    speed = 25/9 # 10 kmph

    def __init__(self):
        self.set_paths()

    def set_paths(self):
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.source_path = os.path.join(self.base_path, "Sources")
        self.data_path = os.path.join(self.base_path, "Data")
        self.output_path = os.path.join(self.base_path, "Output")
        self.style_path = os.path.join(self.source_path, "style.json")

    def setup(self):
        self.setup_graph()
        self.setup_solver()
        self.setup_server()

    def reset(self):
        self.solver.reset()


    # Graph

    def setup_graph(self):
        self.set_graph()
        self.graph.set_graph()
        self.graph.set_board_data()
        self.graph.set_elevation_map()
        self.set_routes()
        self.load_style()

    def set_graph(self):
        self.graph = Graph(self)

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

    def load_style(self):
        with open(self.style_path) as file:
            self.style = json.load(file)

    def draw(self):
        self.graph.draw()


    # Solver

    def setup_solver(self):
        self.set_solver()
        self.solver.set_quantities()
        self.solver.set_initial_constraints()

    def set_solver(self):
        self.solver = Solver(self)

    def solve(self):
        self.solver.solve()

    def get_solution_summary(self):
        summary = self.solver.get_summary()
        return summary


    # Drawing map

    # This is included only for consistency with other setup methods.
    def setup_server(self):
        self.set_server()

    def set_server(self):
        self.server = Server(self)

    def run(self):
        self.server.run()
