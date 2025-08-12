"""
This module is for processing the raw data from OpenStreetMaps into a
geopandas DataFrame.

    Nodes:     A single point. These define the real-world location of things.
    Ways:      A collection of nodes. These define paths and boundaries.
    Relations: An unused OpenStreetMaps structure.
"""


import geopandas as gpd
from hgutilities.utils import json
import pandas as pd
from shapely import LineString, Polygon
import xmltodict

from global_vars import *


keys_to_keep = {
    "@id": "ID",
    "@lat": "latitude",
    "@lon": "longitude",
    "nd": "nodes",
    "tag": "tags",}


def main():
    raw_json = get_raw_json()
    bounds = get_bounds(raw_json)
    nodes = get_nodes(raw_json)
    ways = get_ways(raw_json)
    geometry = get_geometry(nodes, ways)
    gdf = get_geo_dataframe(ways, geometry, bounds)
    return gdf


# Loading raw data

def get_raw_json():
    with open(base_source_path, "rb") as file:
        xml = file.read()
    raw_json = xmltodict.parse(xml)
    return raw_json

def get_bounds(raw_json):
    bounds = raw_json["osm"]["bounds"]
    bounds_keys = ["@minlon", "@minlat", "@maxlon", "@maxlat"]
    bounds = [float(bounds[key]) for key in bounds_keys]
    return bounds


# Nodes and ways

def get_nodes(raw_json):
    nodes = get_nodes_df(raw_json)
    nodes = process_nodes(nodes)
    return nodes

def get_nodes_df(raw_json):
    nodes = raw_json["osm"]["node"]
    nodes = [process_node(node) for node in nodes]
    nodes = pd.DataFrame(nodes)
    return nodes

def process_node(node):
    node = process_entry(node)
    return node

def process_way(way):
    way = process_entry(way)
    way = flatten_quantity(way, "nodes")
    return way

def get_ways(raw_json):
    ways = get_ways_df(raw_json)
    ways = process_ways(ways)
    return ways

def get_ways_df(raw_json):
    ways = raw_json["osm"]["way"]
    ways = [process_way(way) for way in ways]
    ways = pd.DataFrame(ways)
    return ways


# Conversion from json to pandas DataFrame

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


# Postprocessing nodes and ways

def process_nodes(nodes):
    nodes = nodes.loc[:, ["ID", "latitude", "longitude", "name"]]
    nodes = set_lat_long_types(nodes)
    nodes.set_index("ID", inplace=True)
    return nodes

def set_lat_long_types(df):
    df["latitude"] = pd.to_numeric(df["latitude"])
    df["longitude"] = pd.to_numeric(df["longitude"])
    return df

# Rows with "landuse" are removed because they do not indicate physical
# things like a path, building, or forest, etc. They indicate zoning
# information.

def process_ways(ways):
    ways = remove_rows_with_key(ways, "landuse")
    ways = ways.loc[:, ["ID", "nodes", "highway", "name"]]
    ways["polygon"] = ways["nodes"].apply(lambda x: x[0] == x[-1])
    return ways

def remove_rows_with_key(df, key):
    if key in df.columns.values:
        df = df.loc[df[key].isna()]
    return df


# Combining ways and nodes into a single geopandas DataFrame

def get_geometry(nodes, ways):
    way_nodes = get_way_nodes(ways, nodes)
    polygons = get_geometry_polygons(way_nodes)
    linestrings = get_geometry_linestrings(way_nodes)
    geometry = pd.concat((polygons, linestrings), axis=0)
    return geometry

def get_way_nodes(ways, nodes):
    way_nodes = ways.explode("nodes").reset_index(drop=True)
    position = nodes.loc[way_nodes["nodes"], ["longitude", "latitude"]]
    way_nodes["longitude"] = position["longitude"].values
    way_nodes["latitude"] = position["latitude"].values
    way_nodes.drop(columns="nodes", inplace=True)
    return way_nodes

def get_geometry_polygons(way_nodes):
    polygons = (
        way_nodes
        .loc[way_nodes["polygon"]]
        .groupby("ID")[["longitude", "latitude"]]
        .apply(lambda x: Polygon(x.values)))
    return polygons

def get_geometry_linestrings(way_nodes):
    linestrings = (
        way_nodes
        .loc[~way_nodes["polygon"]]
        .groupby("ID")[["longitude", "latitude"]]
        .apply(lambda x: LineString(x.values)))
    return linestrings

def get_geo_dataframe(ways, geometry, bounds):
    ways = convert_ways_to_use_geometry(ways, geometry)
    gdf = gpd.GeoDataFrame(ways, geometry="geometry")
    gdf["geometry"] = gdf.clip_by_rect(*bounds)
    return gdf

def convert_ways_to_use_geometry(ways, geometry):
    ways.set_index("ID", inplace=True)
    ways.drop(columns="nodes", inplace=True)
    ways["geometry"] = geometry
    return ways


if __name__ == "__main__":
    gdf = main()
    gdf.to_csv(geometry_path, index=False)
