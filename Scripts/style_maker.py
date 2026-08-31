"""
This script generates a style.json file for MapLibre.
"""

import json
import os

import pandas as pd

from monopoly import Monopoly


print("Building base style file.")

monopoly = Monopoly(2026)
monopoly.set_graph()
monopoly.graph.load_groups()


# Items.csv gathers mapping elements of a similar type together, for
# example to treat a neighbourhood and a town similarly.
# Layers.csv defines colours, sizes, and other necessary metadata for
# each of the different mapping layers.

style_path = os.path.join(monopoly.source_path, "style.json")
layers_path = os.path.join(monopoly.source_path, "Layers.csv")
items_path = os.path.join(monopoly.source_path, "Items.csv")

layers = pd.read_csv(layers_path, index_col=0)
items = pd.read_csv(items_path, index_col=0)

def get_filter(layer):
    if layers.loc[layer, "Filter"]:
        return {"filter": ["in", "class"] + list(items.loc[items["Layer"] == layer].index)}
    else:
        return {}

text_dict = {
    "text-color": "#ffffff",
    "text-halo-color": "rgba(0, 0, 0, 0.5)",
    "text-halo-width": 4,
    "text-halo-blur": 1}

background = [{
    "id": "Background",
    "type": "background",
    "source": "local",
    "layout": {"visibility": "visible"},
    "paint": {"background-color": "#262626"}}]

fill_json = [dict(
    **{"id": layer,
       "type": "fill",
       "source": "local",
       "source-layer": layers.loc[layer, "SourceLayer"],
       "minzoom": int(layers.loc[layer, "MinZoom"]),
       "layout": {"visibility": "visible"},
       "paint": {"fill-color": layers.loc[layer, "Color"]}},
    **get_filter(layer))
    for layer in layers.loc[layers["Type"] == "fill"].index]

line_json = [dict(
    **{"id": layer,
       "type": "line",
       "source": "local",
       "source-layer": layers.loc[layer, "SourceLayer"],
       "minzoom": int(layers.loc[layer, "MinZoom"]),
       "paint": {
           "line-color": layers.loc[layer, "Color"],
           "line-width": layers.loc[layer, "Width"]}},
    **get_filter(layer))
    for layer in layers.loc[layers["Type"] == "line"].index]

symbol_json = [dict(
    **{"id": f"{layer}Name",
       "type": "symbol",
       "source": "local",
       "source-layer": layers.loc[layer, "SourceLayerSymbol"],
       "minzoom": int(layers.loc[layer, "MinZoom"]),
       "layout": {
           "symbol-placement": layers.loc[layer, "SymbolPlacement"],
           "text-field": [
            "coalesce",
            ["get", "name:latin"],
            ["get", "name"]],
       "text-size": int(layers.loc[layer, "TextSize"]),
       "symbol-spacing": int(layers.loc[layer, "SymbolSpacing"]),
       "text-allow-overlap": False,
       "text-ignore-placement": False,
       "text-keep-upright": True},
       "paint": text_dict},
    **get_filter(layer))
     for layer in layers.loc[layers["Type"].isin(["symbol", "line"])].index]

route_json = [{
    "id": "route-line",
    "type": "line",
    "source": "route",
    "filter": ["==", "$type", "LineString"],
    "layout": {
      "line-cap": "round",
      "line-join": "round"},
    "paint": {
      "line-color": "#004cff",
      "line-width": 10,
      "line-opacity": 1}}]

route_colors = [
    i for group_id, group_data in monopoly.graph.groups.iterrows()
    for i in [group_id, group_data['Color']]]

route_points_json = [{
    "id": "route-points",
    "type": "circle",
    "source": "route",
    "filter": [
        "==",
        "$type",
	"Point"],
    "paint": {
        "circle-radius": 12,
        "circle-color": [
            "match",
            ["get", "role"],
            *route_colors,
            "#808080"]}}]

route_points_labels_json = [{
    "id": "route-point-labels",
    "type": "symbol",
    "source": "route",
    "layout": {
        "text-field": ["get", "label"],
        "text-size": 20,
        "text-offset": [0, 0.8],
        "text-anchor": "top"
    },
    "paint": text_dict}]

features = {
    "type": "geojson",
    "data": {
        "type": "FeatureCollection",
        "features": []}}

style_json = {
  "version": 8,
  "sources": {
    "local": {
      "type": "vector",
      "url": "pmtiles:///region.pmtiles"},
    "route": features},
  "layers": (
      background +
      fill_json +
      line_json +
      route_json +
      route_points_json +
      route_points_labels_json +
      symbol_json)
}

for layer in style_json["layers"]:
    if layer["id"] == "Rail":
        layer["paint"]["line-dasharray"] = [3, 3]

with open(style_path, "w+") as file:
    json.dump(style_json, file, indent=2)
