import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import wkt

from global_vars import *


data = gpd.GeoDataFrame(pd.read_csv(geometry_path))
data = data.set_geometry(wkt.loads(data["geometry"].values))

x_min, y_min, x_max, y_max = data["geometry"].union_all().bounds
scale = 1/(x_max - x_min)
data["geometry"] = data["geometry"].translate(xoff=-x_min, yoff=-y_min)
data["geometry"] = data["geometry"].scale(xfact=scale, yfact=scale, origin=(0, 0))

def create_line(row):
    match row["geometry"].geom_type:
        case "Polygon": create_line_polygon(row)
        case "LineString": create_line_linestring(row)
        case _: create_line_exception(row)

def create_line_polygon(row):
    geometry = row["geometry"]
    geometry = geometry.boundary
    coords = np.array(geometry.xy).T[:-1, :]
    coords_strings = [f"({x}, {y})" for (x, y) in coords]
    tikz.append(f"\\draw[fill=black, fill opacity=0.25] {' -- '.join(coords_strings)};")

def create_line_linestring(row):
    geometry = row["geometry"]
    coords = np.array(geometry.xy).T
    coords_strings = [f"({x}, {y})" for (x, y) in coords]
    tikz.append(f"\\path[color=black] {' -- '.join(coords_strings)};")

def create_line_exception(row):
    raise ValueError(
        f"Unknown geometry type: {row['geometry'].geom_type}\n\n"
        f"Row:\n{row}")


tikz = []
data.apply(create_line, axis=1)
tikz = "\n".join(tikz)
with open(tikz_path, "w+") as file:
    file.write(tikz)
