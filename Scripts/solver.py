from itertools import permutations
import json
import random

import numpy as np


class Solver():

    def __init__(self, monopoly):
        self.monopoly = monopoly
        self.set_quantities()

    def set_quantities(self):
        self.groups = self.monopoly.graph.places["Group ID"].unique().size
        self.squares = self.monopoly.graph.places["Square"].unique().size
        self.vertices = self.monopoly.graph.places.shape[0]
        self.edges = len(self.monopoly.routes)
        self.variables = self.groups + self.squares + self.vertices + self.edges
    
    def initialise_grid(self):
        self.grid = np.ones((self.vertices, self.vertices)) * np.inf
        for edge in self.monopoly.routes:
            start_index = places.index(edge["Start"])
            end_index = places.index(edge["End"])
            weight = edge["Distance"] / self.monopoly.speed + edge["Penalty"]
            self.grid[start_index, end_index] = weight

    def gather_constraints(self, groups=None, squares=None, vertices=None, edges=None):
        constraints = self.get_non_trivial_constraints(groups, squares, vertices, edges)
        rows = self.get_constraint_rows(constraints)

    def get_constraint_rows(self, constraints):
        rows = [constraint.shape[0] for constraint in constraints.values()]
        if len(set(rows)) > 1:
            raise ValueError(
                "Constraints must have the same number of rows to be gathered"
                f"Row counts: {rows}")
        else:
            return rows[0]

    def get_non_trivial_constraints(self, groups, squares, vertices, edges):
        constraints = {
            "Groups": groups,
            "Squares": squares,
            "Vertices": vertices,
            "Edges": edges}
        constraints = {
            key: value for key, value in constraints.items()
            if value is not None}
        return constraints

    def add_group_indicator_constraints(self):
        self.group_constraints = np.zeros((self.groups, self.groups), "int8")
        for group_id in self.monopoly.graph.groups.index:
            self.set_group_indicator_constraint(group_id)

    def set_group_indicator_constraint(self, group_id):
        
