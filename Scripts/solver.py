from itertools import permutations
import json
import os
import random

from cvxopt.glpk import ilp
from cvxopt import matrix
import numpy as np
import pandas as pd


class Solver():

    # Initialisation of useful quantities and structures
    
    def __init__(self, monopoly):
        self.monopoly = monopoly
        self.places = self.monopoly.places
        self.groups = self.monopoly.groups

    def set_quantities(self):
        self.set_squares()
        self.set_edges()
        self.set_type_counts()

    def set_squares(self):
        self.squares = (
            self.places
            .loc[:, ["Square", "Group ID", "Value"]]
            .drop_duplicates()
            .reset_index(drop=True))

    def set_edges(self):
        self.edges = pd.DataFrame(self.monopoly.routes)
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


    # Tools for constructing constraints

    def initialise_constraint_blocks(self, rows):
        self.group_constraints = np.zeros((rows, self.group_count))
        self.square_constraints = np.zeros((rows, self.square_count))
        self.vertex_constraints = np.zeros((rows, self.vertex_count))
        self.edge_constraints = np.zeros((rows, self.edge_count))
        self.limits = np.zeros((rows, 1))

    def gather_constraint_components(self):
        constraints = np.concatenate((
            self.group_constraints,
            self.square_constraints,
            self.vertex_constraints,
            self.edge_constraints,
            self.limits), axis=1)
        return constraints


    # Constructing the constraints    

    def set_group_indicator_constraints(self):
        self.initialise_constraint_blocks(self.group_count)
        for group_id in self.groups.index:
            self.set_group_indicator_constraint(group_id)
        self.group_indicator_constraints = self.gather_constraint_components()
        # The start and end group constraint is unnecessary
        self.group_indicator_constraints = self.group_indicator_constraints[1:, :]

    def set_group_indicator_constraint(self, group_id):
        squares = self.squares.loc[self.squares["Group ID"] == group_id]
        self.group_constraints[group_id, group_id] = squares.index.size
        self.square_constraints[group_id, squares.index] = -1

    def set_square_indicator_constraints(self):
        self.initialise_constraint_blocks(self.square_count)
        for square_id in self.squares.index:
            self.set_square_indicator_constraint(square_id)
        self.square_indicator_constraints = self.gather_constraint_components()

    def set_square_indicator_constraint(self, square_index):
        square = self.squares.loc[square_index, "Square"]
        vertices = self.places.reset_index().loc[self.places["Square"] == square]
        self.square_constraints[square_index, square_index] = vertices.index.size
        self.vertex_constraints[square_index, vertices.index] = -1

    def set_entering_constraints(self):
        self.initialise_constraint_blocks(self.vertex_count)
        for vertex_index in self.places.index:
            edge_indexes = self.edges.loc[self.edges["End ID"] == vertex_index].index
            self.edge_constraints[vertex_index, edge_indexes] = -1
            self.vertex_constraints[vertex_index, vertex_index] = 1
        self.entering_constraints = self.gather_constraint_components()

    def set_exiting_constraints(self):
        self.initialise_constraint_blocks(self.vertex_count)
        for vertex_index in self.places.index:
            edge_indexes = self.edges.loc[self.edges["Start ID"] == vertex_index].index
            self.edge_constraints[vertex_index, edge_indexes] = -1
            self.vertex_constraints[vertex_index, vertex_index] = 1
        self.exiting_constraints = self.gather_constraint_components()

    def set_start_finish_constraint(self):
        self.initialise_constraint_blocks(1)
        index = self.places.loc[self.places["Place"] == self.monopoly.terminal].index.values
        self.vertex_constraints[0, index] = -1
        self.limits[0] = -1
        self.start_finish_constraint = self.gather_constraint_components()

    def set_total_cost_constraint(self):
        self.initialise_constraint_blocks(1)
        self.edge_constraints[0, :] = self.edges["Weight"].values
        self.limits[0] = self.monopoly.time_limit
        self.cost_constraint = self.gather_constraint_components()


    # Putting everything together and solving
    
    def add_constraints(self):
        self.set_group_indicator_constraints()
        self.set_square_indicator_constraints()
        self.set_entering_constraints()
        self.set_exiting_constraints()
        self.set_start_finish_constraint()
        #self.set_total_cost_constraint()
        
    def gather_constraints(self):
        self.constraints = np.concatenate((
            self.group_indicator_constraints,
            self.square_indicator_constraints,
            self.entering_constraints,
            self.exiting_constraints,
            self.start_finish_constraint,
            #self.cost_constraint
            ), axis=0)

    def set_objective_function(self):
        self.c = np.concatenate((
            self.squares.groupby("Group ID").sum()["Value"].values,
            self.squares["Value"].values,
            np.zeros((self.vertex_count)),
            np.zeros((self.edge_count))))

    def solve(self):
        self.find_solution()
        path = os.path.join(self.monopoly.data_path, "Solution.csv")
        #np.savetxt(path, self.values)
        #self.values = np.loadtxt(path)
        self.parse_solution()
        
    def find_solution(self):
        # Maximises c^Tx subject to Ax <= b
        self.A = self.constraints[:, :-1]
        self.b = self.constraints[:, -1]
        (self.status, self.values) = ilp(
            matrix(-self.c), matrix(self.A), matrix(self.b),
            B=set(range(self.variables)))
        self.values = np.array(self.values)


    # Output and postprocessing
    
    def output_constraints(self, constraints):
        columns = np.concatenate((
            self.groups["Group Name"].values,
            self.squares["Square"].values,
            self.places["Place"].values,
            list(range(self.edge_count)),
            ["Limit"]))
        constraints = pd.DataFrame(constraints, columns=columns)
        path = os.path.join(self.monopoly.data_path, "Constraints.csv")
        constraints.to_csv(path)

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

    def solution(self):
        print(self.groups_solution)
        print(self.squares_solution)
        print(self.vertices_solution)
        print(self.edges_solution.drop(columns="Nodes"))
