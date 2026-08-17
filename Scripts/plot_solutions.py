"""
This script takes the solutions and produces a files that can be
accepted by pgfplots and plot the route. The plot will show the route
with places labelled.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.setup()
monopoly.load()

routes_path = os.path.join(
    monopoly.output_path,
    "PlottingEdges")
places_path = os.path.join(
    monopoly.output_path,
    "PlottingPlaces")

if not os.path.exists(routes_path):
    os.mkdir(routes_path)

if not os.path.exists(places_path):
    os.mkdir(places_path)

id_lookup = dict(zip(*[monopoly.places["Place"].values, monopoly.places.index.values]))
id_lookup[monopoly.terminal] = monopoly.terminal[0]

for speed in np.arange(0.1, 8.1, 0.1):
    speed = round(speed, 2)
    speed_str = str(speed).replace(".", "_")
    route_path = os.path.join(routes_path, f"{speed_str}.csv")
    place_path = os.path.join(places_path, f"{speed_str}.csv")
    monopoly.set_solution(speed)


    # Coordinates that trace the route

    monopoly.graph.set_routes_vertices()
    route = monopoly.graph.routes_vertices[0]
    nodes_list = monopoly.graph.get_nodes_list_from_vertices(route)
    coordinates = [monopoly.graph.nodes_to_coordinates(nodes) for nodes in nodes_list]
    coordinates = [coords[:-1] for coords in coordinates[:-1]] + [coordinates[-1]]
    coordinates = np.array([coord for coords in coordinates for coord in coords])

    shift = coordinates.mean(axis=0)
    coordinates -= shift
    scale = coordinates.std()
    coordinates /= scale
    np.savetxt(route_path, coordinates, fmt='%f')


    # Places on the route

    vertices = monopoly.solver.vertices_solution[["Place", "X", "Y"]]
    vertices[["X", "Y"]] = (vertices[["X", "Y"]] - shift) / scale
    # This swap is deliberate
    vertices[["X", "Y"]] = vertices[["Y", "X"]]
    vertices["Place"] = vertices["Place"].map(id_lookup)
    vertices.to_csv(place_path, index=False)
