from itertools import permutations
import json
import os
import random

from scipy import optimize

import numpy as np
import pandas as pd


class Solver():

    # Initialisation of useful quantities and structures
    
    def __init__(self, monopoly):
        self.monopoly = monopoly
        self.groups = self.monopoly.groups
        self.squares = self.monopoly.squares
        self.places = self.monopoly.places
        self.set_paths()

    def set_paths(self):
        self.constraints_path = os.path.join(
            self.monopoly.data_path, "Constraints.csv")
        self.solution_path = os.path.join(
            self.monopoly.data_path, "Solution.csv")

    def reset(self):
        self.set_edge_weight()

    def set_quantities(self):
        self.set_edges()
        self.set_type_counts()
        self.set_columns()

    def set_edges(self):
        self.edges = pd.DataFrame(self.monopoly.routes)
        self.set_edge_weight()

    def set_edge_weight(self):
        flat_time = self.edges["Distance"] / self.monopoly.speed
        elevation_penalty = self.edges["Elevation Penalty"]
        self.edges["Weight"] = flat_time + elevation_penalty

    def set_type_counts(self):
        self.group_count = self.groups.index.size
        self.square_count = self.squares.index.size
        self.vertex_count = self.places.index.size
        self.edge_count = self.edges.index.size
        self.counts = (
            0, self.group_count, self.square_count,
            self.vertex_count, self.edge_count)
        self.variables = sum(self.counts)

    def set_columns(self):
        level_0 = self.get_level_0()
        level_1 = self.get_level_1()
        self.columns = pd.MultiIndex.from_arrays(
            [level_0, level_1], names=["Type", "Item"])

    def get_level_0(self):
        level_0 = (
            ["Group"] * self.group_count +
            ["Square"] * self.square_count +
            ["Vertex"] * self.vertex_count +
            ["Edge"] * self.edge_count +
            ["Phantom"] * self.edge_count +
            ["Limit"])
        return level_0

    def get_level_1(self):
        level_1 = np.concatenate((
            self.groups["Group Name"].values,
            self.squares["Square"].values,
            self.places["Place"].values,
            list(range(self.edge_count)),
            list(range(self.edge_count)),
            ["Limit"]))
        return level_1


    # Tools for constructing constraints

    def initialise_constraint_blocks(self, rows):
        self.constraint_names = [""] * rows
        self.group_constraints = np.zeros((rows, self.group_count))
        self.square_constraints = np.zeros((rows, self.square_count))
        self.vertex_constraints = np.zeros((rows, self.vertex_count))
        self.edge_constraints = np.zeros((rows, self.edge_count))
        self.phantom_constraints = np.zeros((rows, self.edge_count))
        self.limits = np.zeros((rows, 1))

    def gather_constraint_components(self):
        constraints = np.concatenate((
            self.group_constraints,
            self.square_constraints,
            self.vertex_constraints,
            self.edge_constraints,
            self.phantom_constraints,
            self.limits), axis=1)
        constraints = pd.DataFrame(
            constraints,
            columns=self.columns,
            index=self.constraint_names)
        return constraints
    
    def set_initial_constraints(self):
        self.set_group_indicator_constraints()
        self.set_square_indicator_constraints()
        self.set_vertices_must_be_entered_constraints()
        self.set_vertices_must_be_exited_constraints()
        self.set_vertices_entered_once_constraints()
        self.set_vertices_left_once_constraints()
        self.set_start_finish_constraint()
        self.set_connected_constraints_no_flow()
        self.set_connected_constraints_flow_absorption()
        self.set_total_cost_constraint()
        
    def gather_initial_constraints(self):
        self.constraints = pd.concat((
            self.group_indicator_constraints,
            self.square_indicator_constraints,
            self.vertices_must_be_entered_constraints,
            self.vertices_must_be_exited_constraints,
            self.vertices_entered_once_constraints,
            self.vertices_left_once_constraints,
            self.start_finish_constraint,
            self.connected_constraints_no_flow,
            self.connected_constraints_flow_absorption,
            self.total_cost_constraint
            ), axis=0)


    # Constructing the constraints    

    def set_group_indicator_constraints(self):
        self.initialise_constraint_blocks(self.group_count)
        for group_id in self.groups.index:
            squares = self.squares.loc[self.squares["Group ID"] == group_id]
            self.group_constraints[group_id, group_id] = squares.index.size
            self.square_constraints[group_id, squares.index] = -1
            self.constraint_names[group_id] = f"Group {self.groups.loc[group_id, 'Group Name']}"
        self.group_indicator_constraints = self.gather_constraint_components()

    def set_square_indicator_constraints(self):
        self.initialise_constraint_blocks(self.square_count)
        for square_id in self.squares.index:
            self.set_square_indicator_constraint(square_id)
        self.square_indicator_constraints = self.gather_constraint_components()

    def set_square_indicator_constraint(self, square_index):
        square = self.squares.loc[square_index, "Square"]
        vertices = self.places.loc[self.places["Square"] == square]
        self.square_constraints[square_index, square_index] = 1
        self.vertex_constraints[square_index, vertices.index] = -1
        self.constraint_names[square_index] = f"Square {self.squares.loc[square_index, 'Square']}"

    def set_vertices_must_be_entered_constraints(self):
        self.initialise_constraint_blocks(self.vertex_count)
        for vertex_index in self.places.index:
            entering_indexes = self.edges.loc[self.edges["End ID"] == vertex_index].index
            self.edge_constraints[vertex_index, entering_indexes] = -1
            self.vertex_constraints[vertex_index, vertex_index] = 1
            self.constraint_names[vertex_index] = f"Vertex entered {self.places.loc[vertex_index, 'Place']}"
        self.vertices_must_be_entered_constraints = self.gather_constraint_components()

    def set_vertices_must_be_exited_constraints(self):
        self.initialise_constraint_blocks(self.vertex_count)
        for vertex_index in self.places.index:
            exiting_indexes = self.edges.loc[self.edges["Start ID"] == vertex_index].index
            self.edge_constraints[vertex_index, exiting_indexes] = -1
            self.vertex_constraints[vertex_index, vertex_index] = 1
            self.constraint_names[vertex_index] = f"Vertex exited {self.places.loc[vertex_index, 'Place']}"
        self.vertices_must_be_exited_constraints = self.gather_constraint_components()

    def set_vertices_entered_once_constraints(self):
        self.initialise_constraint_blocks(self.vertex_count)
        for vertex_index in self.places.index:
            entering_indexes = self.edges.loc[self.edges["End ID"] == vertex_index].index
            self.edge_constraints[vertex_index, entering_indexes] = 1
            self.vertex_constraints[vertex_index, vertex_index] = -1
            self.constraint_names[vertex_index] = f"Vertex entered once {self.places.loc[vertex_index, 'Place']}"
        self.vertices_entered_once_constraints = self.gather_constraint_components()

    def set_vertices_left_once_constraints(self):
        self.initialise_constraint_blocks(self.vertex_count)
        for vertex_index in self.places.index:
            exiting_indexes = self.edges.loc[self.edges["Start ID"] == vertex_index].index
            self.edge_constraints[vertex_index, exiting_indexes] = 1
            self.vertex_constraints[vertex_index, vertex_index] = -1
            self.constraint_names[vertex_index] = f"Vertex left once {self.places.loc[vertex_index, 'Place']}"
        self.vertices_left_once_constraints = self.gather_constraint_components()
    
    def set_start_finish_constraint(self):
        self.initialise_constraint_blocks(1)
        index = self.squares.loc[self.squares["Square"] == self.monopoly.terminal].index.values
        self.square_constraints[0, index] = -1
        self.limits[0] = -1
        self.constraint_names[0] = "Terminal"
        self.start_finish_constraint = self.gather_constraint_components()

    def set_connected_constraints_no_flow(self):
        self.initialise_constraint_blocks(self.edge_count)
        self.phantom_constraints = np.eye(self.edge_count)
        self.edge_constraints = np.eye(self.edge_count) * (1 - self.vertex_count)
        self.constraint_names = np.full(self.edge_count, "No flow through unincluded edges")
        self.connected_constraints_no_flow = self.gather_constraint_components()

    def set_connected_constraints_flow_absorption(self):
        self.initialise_constraint_blocks(self.vertex_count - 1)
        for index, vertex_index in enumerate(self.places.loc[self.places["Square"] != self.monopoly.terminal].index):
            self.phantom_constraints[index, self.edges.loc[self.edges["End ID"] == vertex_index].index] = -1
            self.phantom_constraints[index, self.edges.loc[self.edges["Start ID"] == vertex_index].index] = 1
            self.vertex_constraints[index, vertex_index] = 1
            self.constraint_names[index] = f"Flow is absorped {self.places.loc[vertex_index, 'Place']}"
        self.connected_constraints_flow_absorption = self.gather_constraint_components()

    def set_total_cost_constraint(self):
        self.initialise_constraint_blocks(1)
        self.edge_constraints[0, :] = self.edges["Weight"].values
        self.vertex_constraints[0, :] = self.monopoly.stopping_at_place_penalty
        self.limits[0] = self.monopoly.time_limit
        self.constraint_names[0] = "Total Cost"
        self.total_cost_constraint = self.gather_constraint_components()

    def set_enforced_items_constraints(self):
        self.initialise_constraint_blocks(1)
        self.group_constraints[0, self.groups_solution.index] = -1
        self.square_constraints[0, self.squares_solution.index] = -1
        self.limits[0] = -len(self.squares_solution) - len(self.groups_solution)
        self.constraint_names[0] = "Visit given items"
        self.enforced_items_constraints = self.gather_constraint_components()


    # Putting everything together and solving

    def set_objective_function_maximise_points(self):
        self.c = -np.concatenate((
            self.groups["Value"].values,
            self.squares["Value"].values,
            np.zeros((self.vertex_count)),
            np.zeros((self.edge_count)),
            np.zeros((self.edge_count))))

    def set_objective_function_minimise_distance(self):
        self.c = np.concatenate((
            np.zeros((self.group_count)),
            np.zeros((self.square_count)),
            np.zeros((self.vertex_count)),
            self.edges["Weight"].values,
            np.zeros((self.edge_count))))

    def solve(self):
        self.set_initial_constraints()
        self.find_solution_maximum_points()
        self.find_solution_minimum_distance()

    def find_solution_maximum_points(self):
        self.set_objective_function_maximise_points()
        self.gather_initial_constraints()
        self.find_tour()
        print("Found maximum points tour!")

    def find_solution_minimum_distance(self):
        self.set_objective_function_minimise_distance()
        self.gather_initial_constraints()
        self.set_minimum_distance_constraints()
        self.find_tour()
        print("Found maximum points tour of minimum length!")

    def set_minimum_distance_constraints(self):
        self.set_enforced_items_constraints()
        self.constraints = pd.concat(
            (self.constraints,
             self.enforced_items_constraints,),
            axis=0)

    def find_tour(self):
        self.find_integer_programming_solution()
        self.parse_solution()
        self.monopoly.graph.set_routes_vertices()
        
    def find_integer_programming_solution(self):
        # Minimise c^Tx subject to Ax <= b
        A = self.constraints.values[:, :-1]
        b = self.constraints.values[:, -1]
        lb = np.zeros((self.variables + len(self.edges)))
        ub = np.concatenate((np.ones(self.variables), np.ones(len(self.edges))*np.inf))
        bounds = optimize.Bounds(lb=lb, ub=ub)
        integrality = np.concatenate((np.ones(self.variables), np.zeros((len(self.edges)))))
        constraints = optimize.LinearConstraint(A, ub=b)
        self.res = optimize.milp(
            c=self.c, constraints=constraints,
            integrality=integrality, bounds=bounds)
        self.values = self.res.x.round(0).astype("int8")
        

    # Output and postprocessing
    
    def output(self):
        data = self.constraints.copy()
        data.loc["Solution", :] = np.concatenate((self.values.reshape(-1), [0]))
        data.to_csv(self.constraints_path)

    def parse_solution(self):
        indexes = self.get_solution_indexes()
        self.groups_solution = self.groups.iloc[indexes[0], :]
        self.squares_solution = self.squares.iloc[indexes[1], :]
        self.vertices_solution = self.places.iloc[indexes[2], :]
        self.edges_solution = self.edges.iloc[indexes[3], :]

    def get_solution_indexes(self):
        cum = np.cumsum(self.counts)
        indexes = [
            np.nonzero(self.values[count_lower:count_upper])[0]
            for count_lower, count_upper in zip(cum[:-1], cum[1:])]
        return indexes

    def get_summary(self):
        summary = {
            "Pace (min/km)": 60 / (1000 * self.monopoly.speed),
            "Distance": self.edges_solution["Distance"].sum(),
            "Points": self.get_points(),
            "Time": self.get_time()}
        return summary

    def get_points(self):
        points = (
            self.groups_solution["Value"].sum() +
            self.squares_solution["Value"].sum())
        return points

    def get_time(self):
        self.set_total_cost_constraint()
        time = round((
            self.edges_solution["Weight"].sum() +
            self.squares_solution.index.size * self.monopoly.stopping_at_place_penalty
            ) / 60, 2)
        return time
