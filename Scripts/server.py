import json
import os

from flask import Flask, send_from_directory, jsonify
import networkx as nx
import osmnx as ox


start = (51.32920605938939, -0.2676814081931653)
end = (51.334231337665436, -0.2682810902816036)

class Server():
    
    def __init__(self, monopoly):
        self.monopoly = monopoly
        self.app = Flask(__name__)
        self.route_geojson = None
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule("/", "home", self.home)
        self.app.add_url_rule("/<path:file>", "files", self.files)
        self.app.add_url_rule("/style.json", "style", lambda: jsonify(self.monopoly.style))

    def home(self):
        return send_from_directory(self.monopoly.source_path, "index.html")

    def files(self, file):
        return send_from_directory(self.monopoly.source_path, file)

    def build_route(self):

        start_node = ox.distance.nearest_nodes(
            self.monopoly.graph.graph, start[1], start[0]
        )
        end_node = ox.distance.nearest_nodes(
            self.monopoly.graph.graph, end[1], end[0]
        )

        route = nx.shortest_path(
            self.monopoly.graph.graph,
            start_node,
            end_node,
            weight="length"
        )

        coordinates = [
            (self.monopoly.graph.graph.nodes[n]["x"], self.monopoly.graph.graph.nodes[n]["y"])
            for n in route
        ]

        distance_m = sum(
            self.monopoly.graph.graph.edges[route[i], route[i + 1], 0]["length"]
            for i in range(len(route) - 1))

        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"distance_m": distance_m},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates,
                    },
                },
                {
                    "type": "Feature",
                    "properties": {"role": "start"},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [start[1], start[0]],
                    },
                },
                {
                    "type": "Feature",
                    "properties": {"role": "end"},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [end[1], end[0]],
                    },
                },
            ],
        }

    def run(self):
        self.route_geojson = self.build_route()
        self.app.run(host="localhost", port=8000)
