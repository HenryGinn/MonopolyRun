import os

import osmnx as ox
import networkx as nx
import pandas as pd


class Graph():

    def __init__(self, monopoly):
        self.monopoly = monopoly
        self.set_routes_path()


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
            dist=7000, network_type="walk")
        ox.save_graphml(self.graph, self.graph_path)

    def load_graph(self):
        self.graph = ox.load_graphml(self.graph_path)


    # Initialising place data
    
    def set_places(self):
        path = os.path.join(self.monopoly.data_path, "Places.csv")
        if os.path.exists(path):
            self.places = pd.read_csv(path, index_col=0)
        else:
            self.generate_places()

    def generate_places(self):
        self.load_places_source()
        groups = self.get_groups()
        self.places = self.places.join(groups, on="Group ID")
        self.set_place_coordinates()
        self.save_places()

    def load_places_source(self):
        path = os.path.join(self.monopoly.data_path, "PlacesSource.csv")
        self.places = pd.read_csv(path, index_col=0)

    def get_groups(self):
        path = os.path.join(self.monopoly.data_path, "Groups.csv")
        groups = pd.read_csv(path, index_col=0)
        return groups

    def save_places(self):
        path = os.path.join(self.monopoly.data_path, "Places.csv")
        self.places.to_csv(path)


    # Getting coordinates that align to nodes in the graph

    def set_place_coordinates(self):
        self.places["Node"] = (
            self.places.apply(
                self.get_nearest_node, axis=1))

    def get_nearest_node(self, place):
        nearest_node = ox.distance.nearest_nodes(
            self.graph, place["Latitude"], place["Longitude"])
        return nearest_node

    def set_routes_path(self):
        self.routes_path = os.path.join(
            self.monopoly.source_path, "Routes.json")


    # Building a json of all route information
    
    def construct_routes(self):
        self.routes = {
            (start, end): self.get_route(start, end)
            for start in self.places.index
            for end in self.places.index[:1]
            if self.valid_start_and_end(start, end)}

    def valid_start_and_end(self, start, end):
        is_valid = (
            self.places.loc[start, "Square"] !=
            self.places.loc[end, "Square"])
        return is_valid

    def get_route(self, start, end):
        print(start, end)
