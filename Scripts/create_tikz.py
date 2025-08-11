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
    try:
        coords = get_coords(row)
        coords_strings = [f"({x}, {y})" for (x, y) in coords]
        tikz.append(f"\\draw[fill=blue, fill opacity=0.25] {' -- '.join(coords_strings)};")
    except:
        print("Something went wrong uwu")

def get_coords(row):
    geometry = row["geometry"]
    if geometry.geom_type in ["Polygon", "MultiPolygon"]:
        geometry = geometry.boundary
    coords = np.array(geometry.xy).T
    return coords

tikz = []
data.apply(create_line, axis=1)
tikz = "\n".join(tikz)
with open(tikz_path, "w+") as file:
    file.write(tikz)
