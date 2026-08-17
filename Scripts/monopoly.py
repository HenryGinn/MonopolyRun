import json
import os

import numpy as np
import pandas as pd

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
        self.set_input_paths()
        self.set_output_paths()

    def set_input_paths(self):
        self.source_path = os.path.join(self.base_path, "Sources")
        self.data_path = os.path.join(self.base_path, "Data")
        self.style_path = os.path.join(self.source_path, "style.json")

    def set_output_paths(self):
        self.output_path = os.path.join(self.base_path, "Output")
        self.indicators_path = os.path.join(self.output_path, "Indicators.csv")
        self.solutions_path = os.path.join(self.output_path, "Solutions.csv")
        self.solution_routes_path = os.path.join(self.output_path, "Routes.csv")

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
        self.initialise_outputs()

    def set_solver(self):
        self.solver = Solver(self)

    def solve(self):
        self.solver.solve()


    # Drawing map

    # This is included only for consistency with other setup methods.
    def setup_server(self):
        self.set_server()

    def set_server(self):
        self.server = Server(self)

    def run(self):
        self.server.run()


    # Output

    def initialise_outputs(self):
        self.indicators = pd.DataFrame(index=self.solver.columns[:-1])
        self.solutions = pd.DataFrame()
        route_columns = ["Speed (m/s)", "Order ID", "Place"]
        self.solution_routes = pd.DataFrame(columns=route_columns)

    def update_outputs(self):
        self.indicators.loc[:, self.speed] = self.solver.values
        self.solutions = pd.concat((self.solutions, self.solver.get_summary()))
        self.add_route_to_output()

    def add_route_to_output(self):
        route = self.graph.routes_vertices[0]
        route = pd.DataFrame({
            "Speed (m/s)": np.ones(len(route))*self.speed,
            "Order ID": np.arange(len(route)),
            "Place": route})
        self.solution_routes = pd.concat((self.solution_routes, route))

    def save(self):
        self.indicators.to_csv(self.indicators_path)
        self.solutions.sort_index().to_csv(self.solutions_path)
        self.solution_routes.sort_values(
            ["Speed (m/s)", "Order ID"]
            ).to_csv(self.solution_routes_path, index=False)

    def load(self):
        self.indicators = pd.read_csv(self.indicators_path, index_col=["Type", "Item"])
        self.indicators.columns = self.indicators.columns.astype("float64")
        self.solutions = pd.read_csv(self.solutions_path)
        self.solution_routes = pd.read_csv(self.solution_routes_path)

    def set_solution(self, speed):
        self.speed = speed
        self.solver.set_edge_weight()
        self.solver.values = self.indicators.loc[:, speed].values
        self.solver.parse_solution()
        self.graph.set_routes_vertices()
