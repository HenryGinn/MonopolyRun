"""
This script is used to produce a file containing the elevation map data
that pgfplots can parse.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from monopoly import Monopoly


print("Building data for elevation plotting.")

monopoly = Monopoly(None)
monopoly.set_graph()
monopoly.graph.set_graph()
elevation, x, y = monopoly.graph.set_elevation_map()

y_min, y_max = 51.30771633543569, 51.36825881543783
x_min, x_max = -0.3040750763933488, -0.2064156725876473
x_indexes = np.nonzero((x_min <= x) & (x <= x_max))[0]
y_indexes = np.nonzero((y_min <= y) & (y <= y_max))[0]
x = x[x_indexes]
y = y[y_indexes]
xx, yy = np.meshgrid(x, y)
elevation = elevation[y_indexes[:, None], x_indexes]

rows = np.stack([xx, yy, elevation]).T
rows = rows[::5, ::5, :]

path = os.path.join(monopoly.base_output_path, "Elevation.csv")
with open(path, "w+") as file:
    for row in rows:
        content = "\n".join([
            ",".join(
                str(i) for i in coordinate)
            for coordinate in row])
        file.write(content)
        file.write("\n\n")
