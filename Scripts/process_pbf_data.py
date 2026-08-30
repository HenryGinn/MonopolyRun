"""
The main program works using region.json as a source of data and this
file is included in the repository. This file was generated based on
data from https://download.geofabrik.de/
"""

import json

import networkx as nx
from pyrosm import OSM


pbf = "../Sources/surrey-260819.osm.pbf"
bounding_box = [
    -0.28806753851261246,
    51.3108083757216,
    -0.20961773045511717,
    51.366453861007706]
osm = OSM(pbf, bounding_box=bounding_box)

nodes, edges = osm.get_network(
    network_type="walking",
    nodes=True)

G = osm.to_graph(
    nodes,
    edges,
    graph_type="networkx")

data = nx.node_link_data(G)
for node in data["nodes"]:
    if node.get("geometry") is not None:
        node["geometry"] = node["geometry"].wkt

for edge in data["edges"]:
    if edge.get("geometry") is not None:
        edge["geometry"] = edge["geometry"].wkt

with open("../Sources/region.json", "w") as f:
    json.dump(data, f)
