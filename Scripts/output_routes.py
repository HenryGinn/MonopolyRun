"""
This script takes the solutions and produces a files that can be
accepted by pgfplots and plot the route. The plot will show the route
with places labelled.
"""

import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


class PlottedRoute():

    def __init__(self, name):
        self.monopoly = Monopoly(name)
        self.monopoly.setup()
        self.monopoly.load()
        self.set_paths()
        self.set_id_lookup()
        self.set_label_placement_tools()
        self.set_cluster()

    def set_paths(self):
        self.set_routes_path()
        self.set_places_path()

    def set_routes_path(self):
        self.routes_path = os.path.join(
            self.monopoly.output_path,
            "PlottingEdges")
        if not os.path.exists(self.routes_path):
            os.mkdir(self.routes_path)

    def set_places_path(self):
        self.places_path = os.path.join(
            self.monopoly.output_path,
            "PlottingPlaces")
        if not os.path.exists(self.places_path):
            os.mkdir(self.places_path)

    def set_id_lookup(self):
        self.id_lookup = dict(zip(*[
            self.monopoly.places["Place"].values,
            self.monopoly.places.index.values]))
        self.id_lookup[self.monopoly.terminal] = self.monopoly.terminal[0]

    def set_label_placement_tools(self):
        self.set_cluster()
        self.set_directions()

    def set_cluster(self):
        cluster = np.linspace(-1/2, 1/2, 21)
        self.cluster = 1/2 - np.sign(cluster) * (4 * (1/2 - np.abs(cluster))**3 - 1/2)
        self.cluster = self.cluster.reshape(-1, 1)

    def set_directions(self):
        angles = np.linspace(0, 2*np.pi, 19, endpoint=False)
        self.directions = np.stack(
            (np.sin(angles), np.cos(angles))
            ).T * 0.12


    def generate_routes(self):
        self.print_message()
        for speed in self.monopoly.solutions["Speed (m/s)"].values:
            print(speed)
            self.set_route(speed)

    def print_message(self):
        print(
            "Generating sensible locations for "
            f"{self.monopoly.name} place labels.")

    def set_route(self, speed):
        self.set_speed_paths(speed)
        self.monopoly.set_solution(speed)
        self.set_coordinates()
        self.set_vertices()
        self.set_line_points()
        self.set_label_positions()
        self.save()

    def set_speed_paths(self, speed):
        speed_str = str(speed).replace(".", "_")
        self.route_path = os.path.join(self.routes_path, f"{speed_str}.csv")
        self.place_path = os.path.join(self.places_path, f"{speed_str}.csv")

    def set_coordinates(self):
        self.monopoly.graph.set_routes_vertices()
        route = self.monopoly.graph.routes_vertices[0]
        nodes_list = self.monopoly.graph.get_nodes_list_from_vertices(route)
        self.coordinates = [self.monopoly.graph.nodes_to_coordinates(nodes) for nodes in nodes_list]
        self.coordinates = [coords[:-1] for coords in self.coordinates[:-1]] + [self.coordinates[-1]]
        self.coordinates = np.array([coord for coords in self.coordinates for coord in coords])
        self.normalise_coordinates()

    def normalise_coordinates(self):
        self.shift = self.coordinates.mean(axis=0)
        self.coordinates -= self.shift
        self.scale = self.coordinates.std()
        self.coordinates /= self.scale

    def set_vertices(self):
        self.vertices = self.monopoly.solver.vertices_solution[["X", "Y", "Place"]]
        self.vertices.drop_duplicates(subset=["X", "Y"], inplace=True)
        self.vertices["Place"] = self.vertices["Place"].map(self.id_lookup)
        self.vertices[["X", "Y"]] = (self.vertices[["X", "Y"]] - self.shift) / self.scale

    def set_line_points(self):
        self.line_points = np.concatenate((
            [point_1 + self.cluster * (point_2 - point_1)
             for point_1, point_2 in zip(self.coordinates, self.coordinates[1:])]))

    def set_label_positions(self):
        self.vertices[["LabelX", "LabelY"]] = np.stack(
            [self.get_label_position(label)
             for label in self.vertices[["X", "Y"]].values])

    def get_label_position(self, label):
        possibilities = self.directions + label
        differences = self.line_points[:, np.newaxis] - possibilities
        distances = np.linalg.norm(differences, axis=2)
        distances = 1 / np.where(distances < 0.5, distances, np.inf)**4
        index = distances.sum(axis=0).argmin()
        label_position = possibilities[index]
        return label_position

    def save(self):
        np.savetxt(self.route_path, self.coordinates, fmt='%f')
        self.vertices.to_csv(self.place_path, index=False)


def main(name):
    route = PlottedRoute(name)
    route.generate_routes()
