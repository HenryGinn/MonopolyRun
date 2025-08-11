import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import xmltodict
from hgutilities.utils import json


data_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "Data")
base_source_path = os.path.join(data_path, "map.osm")
nodes_path = os.path.join(data_path, "nodes.csv")
ways_path = os.path.join(data_path, "ways.csv")
relations_path = os.path.join(data_path, "relations.csv")
test_path = os.path.join(data_path, "json_from_xml.json")


with open(base_source_path, "rb") as file:
    xml = file.read()

converted_json = xmltodict.parse(xml)
nodes = converted_json["osm"]["node"]
ways = converted_json["osm"]["way"]
relations = converted_json["osm"]["relation"]

keys_to_keep = {
    "@id": "ID",
    "@lat": "Latitude",
    "@lon": "Longitude",
    "nd": "Nodes",
    "tag": "Tags",
    "member": "Member"}


def process_node(node):
    node = process_entry(node)
    return node

def process_way(way):
    way = process_entry(way)
    way = flatten_quantity(way, "Nodes")
    return way

def process_relation(relation):
    relation = process_entry(relation)
    relation = flatten_quantity(relation, "Member")
    return relation

def process_entry(entry):
    entry = filter_and_rename_keys(entry)
    entry = flatten_dict(entry, "Tags")
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
relations = [process_relation(relation) for relation in relations]

with open(test_path, "w+") as file:
    json.dump(converted_json, file)
with open(nodes_path, "w+") as file:
    json.dump(nodes, file)
with open(ways_path, "w+") as file:
    json.dump(ways, file)
with open(relations_path, "w+") as file:
    json.dump(relations, file)
