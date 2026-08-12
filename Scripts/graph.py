import os

from hgutilities.utils import json
import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import rasterio as rs
from scipy.interpolate import RegularGridInterpolator


class Graph():

    def __init__(self, monopoly):
        self.monopoly = monopoly


    # Initialising graph data

    def set_graph(self):
        self.set_graph_path()
        if os.path.exists(self.graph_path):
            self.load_graph()
        else:
            self.save_graph()

    def set_graph_path(self):
        self.graph_path = os.path.join(
            self.monopoly.source_path, "region.graphml")

    def save_graph(self):
        self.graph = ox.graph.graph_from_point(
            (51.3349906493623, -0.26368503514735964),
            dist=6000, network_type="walk")
        ox.save_graphml(self.graph, self.graph_path)

    def load_graph(self):
        self.graph = ox.load_graphml(self.graph_path)


    # Elevation

    def set_elevation_map(self):
        elevation_source, width, height, transform = self.load_elevation()
        x, y = self.get_elevation_grid(width, height, transform)
        self.elevation = self.get_elevation_interpolator(elevation_source, x, y)

    def load_elevation(self):
        elevation_path = os.path.join(
            self.monopoly.source_path, "Elevation.tif")
        with rs.open(elevation_path) as file:
            elevation_source = file.read(1)
            width, height = file.width, file.height
            transform = file.transform
        return elevation_source, width, height, transform

    def get_elevation_grid(self, width, height, transform):
        x = np.arange(width) * transform.a + transform.c + transform.a / 2
        y = np.arange(height) * transform.e + transform.f + transform.e / 2
        return x, y

    def get_elevation_interpolator(self, elevation_source, x, y):
        interpolator = RegularGridInterpolator(
            (x, y[::-1]), elevation_source[::-1, :].T, method="linear")
        return interpolator

    
    # Initialising place data
    
    def set_board_data(self):
        self.load_groups()
        self.set_places()
        self.set_squares()
        self.groups["Value"] = self.squares.groupby("Group ID")["Value"].sum()
        self.places["Node"] = self.places["Node"].astype(int)
        self.monopoly.groups = self.groups
        self.monopoly.places = self.places

    def set_places(self):
        path = os.path.join(self.monopoly.data_path, "Places.csv")
        if os.path.exists(path):
            self.places = pd.read_csv(path, index_col=0)
        else:
            self.generate_places()

    def generate_places(self):
        self.load_places_source()
        self.places = self.places.join(self.groups, on="Group ID")
        self.places.reset_index(inplace=True)
        self.set_place_coordinates()
        self.save_places()

    def load_places_source(self):
        path = os.path.join(self.monopoly.data_path, "PlacesSource.csv")
        self.places = pd.read_csv(path, index_col=0)

    def load_groups(self):
        path = os.path.join(self.monopoly.data_path, "Groups.csv")
        self.groups = pd.read_csv(path, index_col=0)

    def save_places(self):
        path = os.path.join(self.monopoly.data_path, "Places.csv")
        self.places.to_csv(path)

    def set_squares(self):
        self.squares = (
            self.places
            .loc[:, ["Square", "Group ID", "Group Name", "Value"]]
            .drop_duplicates()
            .reset_index(drop=True))
        self.monopoly.squares = self.squares


    # Getting coordinates that align to nodes in the graph

    def set_place_coordinates(self):
        self.set_place_nodes()
        self.set_coordinates_from_nodes()
        self.places.drop(columns=["Longitude", "Latitude"], inplace=True)
        
    def set_place_nodes(self):
        self.places["Node"] = (
            self.places.apply(
                self.get_nearest_node, axis=1))

    def get_nearest_node(self, place):
        nearest_node = ox.distance.nearest_nodes(
            self.graph, place["Latitude"], place["Longitude"])
        return nearest_node
    
    def set_coordinates_from_nodes(self):
        self.places[["X", "Y"]] = (
            self.places.apply(
                self.get_coordinate_from_node, axis=1)).to_list()

    def get_coordinate_from_node(self, place):
        x = self.monopoly.graph.graph.nodes[place["Node"]]["x"]
        y = self.monopoly.graph.graph.nodes[place["Node"]]["y"]
        return x, y


    # Building a json of all route information

    def construct_routes(self):
        self.initialise_routes()
        self.add_other_route_data()
        self.save_routes()
    
    def initialise_routes(self):
        print("Initialising routes")
        self.monopoly.routes = [
            {"Start ID": start,
             "End ID": end,
             "Start": self.places.loc[start, "Place"],
             "End": self.places.loc[end, "Place"],
             "Nodes": self.get_route(start, end)}
            for start in self.places.index
            for end in self.places.index
            if self.valid_start_and_end(start, end)]

    def valid_start_and_end(self, start, end):
        is_valid = (
            self.places.loc[start, "Square"] !=
            self.places.loc[end, "Square"])
        return is_valid

    def get_route(self, start, end):
        start_node = self.places.loc[start, "Node"]
        end_node = self.places.loc[end, "Node"]
        route = nx.shortest_path(self.graph, start_node, end_node, weight="length")
        route = [int(i) for i in route]
        return route

    def add_other_route_data(self):
        print("Adding other route data")
        for route in self.monopoly.routes:
            # Distance in metres, elevation penalty in seconds
            route.update({
                "Distance": self.get_route_distance(route),
                "Elevation Penalty": self.get_route_elevation_penalty(route)})

    def get_route_distance(self, route):
        length = nx.shortest_path_length(
            self.graph,
            self.places.loc[route["Start ID"], "Node"],
            self.places.loc[route["End ID"], "Node"],
            weight="length")
        return length

    def get_route_elevation_penalty(self, route):
        coordinates = self.nodes_to_coordinates(route["Nodes"])
        elevations = np.array([self.elevation(coordinate) for coordinate in coordinates])
        deltas = elevations[1:] - elevations[:-1]
        penalty = self.get_penalty_from_elevation_deltas(deltas)
        return penalty

    def get_penalty_from_elevation_deltas(self, deltas):
        penalty = np.where(
            deltas >= 0,
            self.monopoly.elevation_gain_penalty * deltas,
            self.monopoly.elevation_loss_reward * deltas
            ).sum()
        return penalty

    def save_routes(self):
        with open(self.monopoly.routes_path, "w+") as file:
            json.dump(self.monopoly.routes, file)


    # Adding things to map

    def draw(self):
        self.draw_places()
        self.draw_edges()

    def draw_places(self):
        for place in self.monopoly.solver.vertices_solution.index:
            self.add_node(place)

    def draw_edges(self):
        self.set_routes_vertices()
        for route_vertices in self.routes_vertices:
            route = self.draw_route_from_vertices(route_vertices)

    def set_routes_vertices(self):
        self.edges_solution = self.monopoly.solver.edges_solution.copy()
        self.routes_vertices = []
        while self.edges_solution.size > 0:
            self.add_route_vertices()

    def add_route_vertices(self):
        starting_node = self.edges_solution.iloc[0]["Start"]
        route_vertices = [starting_node]
        while (route_vertices[-1] != starting_node) or (len(route_vertices) == 1):
            route_vertices.append(self.get_next_vertex(route_vertices[-1]))
        self.routes_vertices.append(route_vertices)

    def get_next_vertex(self, current_node):
        start_is_current = self.edges_solution["Start"] == current_node
        next_edge = self.edges_solution.loc[start_is_current].iloc[0]
        next_vertex = next_edge["End"]
        self.edges_solution = self.edges_solution.drop([next_edge.name])
        return next_vertex

    def draw_route_from_vertices(self, route_vertices):
        edges = self.monopoly.solver.edges_solution
        for start, end in zip(route_vertices[:-1], route_vertices[1:]):
            nodes = edges.loc[
                (edges["Start"] == start) &
                (edges["End"] == end)
                ].loc[:, "Nodes"].iloc[0]
            self.add_route(nodes)

    def add_node(self, place):
        self.monopoly.style["sources"]["route"]["data"]["features"].append(
            {"type": "Feature",
             "properties": {
                 "role": int(self.places.loc[place, "Group ID"]),
                 "label": self.places.loc[place, "Square"]},
             "geometry": {
                 "type": "Point",
                 "coordinates": list(self.places.loc[place, ["X", "Y"]])}})

    def add_route(self, route):
        coordinates = self.nodes_to_coordinates(route)
        self.monopoly.style["sources"]["route"]["data"]["features"].append(
            {"type": "Feature",
             "properties": {"role": "route-line"},
             "geometry": {
                 "type": "LineString",
                 "coordinates": coordinates}})
        
    def nodes_to_coordinates(self, route):
        route_gdf = ox.routing.route_to_gdf(self.graph, route)
        coordinates = [
            coord
            for geometry in route_gdf.geometry
            for coord in geometry.coords]
        return coordinates

