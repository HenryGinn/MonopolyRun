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
        self.set_paths()
        self.route_geojson = None
        self.register_routes()
        self.set_graph()

    def set_paths(self):
        self.style_path = os.path.join(self.monopoly.source_path, "style.json")

    def register_routes(self):
        self.app.add_url_rule("/", "home", self.home)
        self.app.add_url_rule("/style.json", "style", self.style)
        self.app.add_url_rule("/<path:file>", "files", self.files)

    def home(self):
        return send_from_directory(self.monopoly.source_path, "index.html")

    def style(self):
        with open(self.style_path) as file:
            style = json.load(file)

        style["sources"]["route"] = {
            "type": "geojson",
            "data": self.route_geojson,
        }
        return style

    def files(self, file):
        return send_from_directory(self.monopoly.source_path, file)

    def build_route(self):

        start_node = ox.distance.nearest_nodes(
            self.graph, start[1], start[0]
        )
        end_node = ox.distance.nearest_nodes(
            self.graph, end[1], end[0]
        )

        route = nx.shortest_path(
            self.graph,
            start_node,
            end_node,
            weight="length"
        )

        coordinates = [
            (self.graph.nodes[n]["x"], self.graph.nodes[n]["y"])
            for n in route
        ]

        distance_m = sum(
            self.graph.edges[route[i], route[i + 1], 0]["length"]
            for i in range(len(route) - 1)
        )

        print(f"Route distance: {distance_m:.1f} m ({len(route)} nodes)")

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
        #self.route_geojson = self.build_route()
        self.app.run(host="localhost", port=8000)
