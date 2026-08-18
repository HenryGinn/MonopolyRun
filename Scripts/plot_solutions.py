"""
This script takes the solutions and produces a files that can be
accepted by pgfplots and plot the route. The plot will show the route
with places labelled.
"""

import os

from adjustText import adjust_text
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

def densify_line(coordinates, spacing=0.01):
    points = []
    for p1, p2 in zip(coordinates[:-1], coordinates[1:]):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = np.hypot(dx, dy)
        n = max(1, int(np.ceil(length / spacing)))
        t = np.linspace(0, 1, n, endpoint=False)
        points.extend(
            np.column_stack([
                p1[0] + t * dx,
                p1[1] + t * dy]))
    points.append(coordinates[-1])
    return np.asarray(points)

for speed in np.arange(0.1, 8.1, 0.1):
    print(speed)
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
    a = densify_line(coordinates)

    # Places on the route

    vertices = monopoly.solver.vertices_solution[["X", "Y", "Place"]]
    vertices[["X", "Y"]] = (vertices[["X", "Y"]] - shift) / scale
    vertices["Place"] = vertices["Place"].map(id_lookup)

    fig, ax = plt.subplots(1)
    obstacle = ax.scatter(
        a[:, 0],
        a[:, 1],
        s=50,
        alpha=1, color="tab:red")
    texts = [
        ax.text(*row.values)
        for _, row in vertices.iterrows()]
    new_texts = adjust_text(
        texts,
        objects=obstacle,
        force_text=(0.3, 0.3),
        force_static=(1, 1),
        force_pull=(0.2, 0.2),
        max_move=5,
        pull_threshold=10,
        force_explode=(0.01, 0.01),
        ax=ax,
        iter_lim=500)
    old_positions = vertices[["X", "Y"]].values
    new_positions = np.array([text.get_position() for text in new_texts[0]])
    new_postions = old_positions + (new_positions - old_positions) * 1.5
    vertices[["LabelX", "LabelY"]] = new_positions
    vertices.to_csv(place_path, index=False)
    plt.close("all")
    
