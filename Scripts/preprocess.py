import geopandas as gpd
from hgutilities.utils import json
import pandas as pd
from shapely import LineString, Polygon
import xmltodict

from global_vars import *


with open(base_source_path, "rb") as file:
    xml = file.read()

converted_json = xmltodict.parse(xml)
nodes = converted_json["osm"]["node"]
ways = converted_json["osm"]["way"]

bounds = converted_json["osm"]["bounds"]
bounds_keys = ["@minlon", "@minlat", "@maxlon", "@maxlat"]
bounds = [float(bounds[key]) for key in bounds_keys]

keys_to_keep = {
    "@id": "ID",
    "@lat": "latitude",
    "@lon": "longitude",
    "nd": "nodes",
    "tag": "tags",}

def process_node(node):
    node = process_entry(node)
    return node

def process_way(way):
    way = process_entry(way)
    way = flatten_quantity(way, "nodes")
    return way

def process_entry(entry):
    entry = filter_and_rename_keys(entry)
    entry = flatten_dict(entry, "tags")
    entry["ID"] = int(entry["ID"])
    return entry

def filter_and_rename_keys(entry):
    entry = {
        keys_to_keep[key]: value for key, value in entry.items()
        if key in keys_to_keep}
    return entry

def flatten_dict(entry, quantity):
    if quantity in entry:
        if isinstance(entry[quantity], list):
            for value in entry[quantity]:
                entry[value["@k"]] = value["@v"]
        else:
            entry[entry[quantity]["@k"]] = entry[quantity]["@v"]
        del entry[quantity]
    return entry

def flatten_quantity(entry, quantity):
    entry[quantity] = [int(value["@ref"]) for value in entry[quantity]]
    return entry


nodes = [process_node(node) for node in nodes]
ways = [process_way(way) for way in ways]

nodes = pd.DataFrame(nodes)
ways = pd.DataFrame(ways)
if "landuse" in ways.columns.values:
    ways = ways.loc[~ways["landuse"].notna()]

nodes = nodes.loc[:, ["ID", "latitude", "longitude", "name"]]
ways = ways.loc[:, ["ID", "nodes", "highway", "name"]]

nodes["latitude"] = pd.to_numeric(nodes["latitude"])
nodes["longitude"] = pd.to_numeric(nodes["longitude"])
nodes.set_index("ID", inplace=True)

ways["polygon"] = ways["nodes"].apply(lambda x: x[0] == x[-1])
way_nodes = ways.explode("nodes").reset_index(drop=True)

position = nodes.loc[way_nodes["nodes"], ["longitude", "latitude"]]
way_nodes["longitude"] = position["longitude"].values
way_nodes["latitude"] = position["latitude"].values
way_nodes.drop(columns="nodes", inplace=True)

polygons = (
    way_nodes
    .loc[way_nodes["polygon"]]
    .groupby("ID")[["longitude", "latitude"]]
    .apply(lambda x: Polygon(x.values)))
linestrings = (
    way_nodes
    .loc[~way_nodes["polygon"]]
    .groupby("ID")[["longitude", "latitude"]]
    .apply(lambda x: LineString(x.values)))
geometry = pd.concat((polygons, linestrings), axis=0)

ways.set_index("ID", inplace=True)
ways.drop(columns="nodes", inplace=True)
ways["geometry"] = geometry

ways = gpd.GeoDataFrame(ways, geometry="geometry")
ways["geometry"] = ways.clip_by_rect(*bounds)
ways.to_csv(geometry_path, index=False)














