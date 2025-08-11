import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
import numpy as np
import pandas as pd
from shapely import wkt

from global_vars import *


data = gpd.GeoDataFrame(pd.read_csv(geometry_path))
data = data.set_geometry(wkt.loads(data["geometry"].values))

colors = np.ones((len(data), 3))
colors[:, 0] = np.linspace(0, 1, len(data))
colors = mcol.hsv_to_rgb(colors)

fig = plt.figure(figsize=(5, 5), facecolor='#1c1e1f')
ax = fig.add_axes([0, 0, 1, 1], facecolor='#1c1e1f')
ax.axis("off")

def plot_name(row):
    point = row["geometry"].representative_point()
    ax.text(point.x, point.y, row["name"], color="white",
            ha="center", va="center")


paths = data.loc[~data["polygon"]]
paths.plot(ax=ax, color=colors)
named_paths = paths.loc[paths["name"].notna()].reset_index()
named_paths.loc[:, "label_location"] = (
    named_paths["geometry"]
    .apply(lambda x: x.representative_point()))

#for name, location in b.loc[:, ["name", "label_location"]].values:
#    ax.text(location.x, location.y, name, ha="center", va="center", color="white")

buildings = data.loc[data["polygon"]].reset_index()
buildings.plot(ax=ax, edgecolor="white", facecolor=colors, alpha=0.4)
buildings.loc[buildings["name"].notna()].apply(lambda x: plot_name(x), axis=1)
    

plt.show()
