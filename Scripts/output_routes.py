"""
This script takes the solutions and produces a files that can be
accepted by pgfplots and plot the route. The plot will show the route
with places labelled.
"""

import argparse
import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


class PlottedRoute():

    label_distance_from_point = 0.025
    labels_too_close_threshold = 0.04

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
            ).T * self.label_distance_from_point


    def generate_routes(self):
        for speed in self.monopoly.solutions["Speed (m/s)"].values:
            self.set_route(speed)

    def set_route(self, speed):
        self.set_speed_paths(speed)
        self.monopoly.set_solution(speed)
        self.set_coordinates()
        self.set_vertices()
        self.set_line_points()
        self.set_label_positions()
        self.filter_label_positions()
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
        self.scale = np.max(self.coordinates.max(axis=0) - self.coordinates.min(axis=0))
        self.coordinates /= self.scale

    def set_vertices(self):
        self.vertices = self.monopoly.solver.vertices_solution[["X", "Y", "Place"]]
        self.vertices.drop_duplicates(subset=["X", "Y"], inplace=True)
        self.vertices["Label"] = self.vertices["Place"].map(self.id_lookup)
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


    # Sometimes labels are too close to each other or overlap. We solve
    # this problem by removing some labels.
    
    def filter_label_positions(self):
        self.set_terminal_lable_index()
        self.remove_labels_nearer_to_other_points()
        self.remove_overlapping_labels()

    def set_terminal_lable_index(self):
        self.terminal_lable_index = self.monopoly.places.loc[
            self.monopoly.places["Square"] == self.monopoly.terminal].index[0]

    def remove_labels_nearer_to_other_points(self):
        differences = (
            self.vertices[["LabelX", "LabelY"]].values[:, None, :]
            - self.vertices[["X", "Y"]].values[None, :, :])
        distances = np.linalg.norm(differences, axis=2)
        np.fill_diagonal(distances, np.inf)
        min_distances = distances.min(axis=1)
        self.label_indexes = min_distances <= self.label_distance_from_point * 0.8
        self.vertices.loc[self.vertices.index[self.label_indexes], "Label"] = ""

    def remove_overlapping_labels(self):
        self.labels_too_close = True
        distances = self.get_distances_between_labels()
        problematic_labels = self.get_problematic_labels(distances)
        self.remove_problematic_labels(problematic_labels)

    def get_distances_between_labels(self):
        positions = self.vertices[["LabelX", "LabelY"]].values
        differences = positions[:, None, :] - positions[None, :, :]
        distances = np.linalg.norm(differences, axis=2)
        np.fill_diagonal(distances, np.inf)
        # Remove labels that were already removed in the previous step.
        for index in self.label_indexes:
            distances[index, :] = np.inf
            distances[:, index] = np.inf
        return distances

    def get_problematic_labels(self, distances):
        problematic_labels = []
        while self.labels_too_close:
            i, j = np.unravel_index(np.argmin(distances), distances.shape)
            if distances[i, j] < self.labels_too_close_threshold:
                problematic_labels.append((i, j))
                distances[i, j] = np.inf
                distances[j, i] = np.inf
            else:
                self.labels_too_close = False
        return problematic_labels

    def remove_problematic_labels(self, problematic_labels):
        # There is a more sophisticated way of doing this. For example,
        # if labels A, B, and C are in a line and are too close then the
        # problem may be solved by removing just the B in the middle.
        for label_index_pair in problematic_labels:
            # Do not want to remove the label for the terminal
            if label_index_pair[0] == self.terminal_lable_index:
                label_index = label_index_pair[1]
            else:
                label_index = label_index_pair[0]
            place_index = self.vertices.index[label_index]
            self.vertices.loc[place_index, "Label"] = ""

    def save(self):
        np.savetxt(self.route_path, self.coordinates, fmt='%f')
        self.vertices.to_csv(self.place_path, index=False)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Board to be displayed")
    args = parser.parse_args(argv)
    route = PlottedRoute(args.name)
    route.generate_routes()


if __name__ == "__main__":
    main()
