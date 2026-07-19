from graph import Graph

import openrouteservice as ors
import osmnx as ox


class Graph():

    def __init__(self):
        pass

    def save_graph():
        graph = ox.graph.graph_from_point(
            (51.3349906493623, -0.26368503514735964),
            dist=7000, network_type="walk")
        ox.save_graphml(graph, "region.graphml")

    def load_graph(self):
        self.graph = ox.load_graphml("region.graphml")


graph = Graph()
graph.load_graph()
graph.save_graph()
