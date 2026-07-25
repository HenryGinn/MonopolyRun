"""
This script generates a style.json file for MapLibre. This is for quick
testing of global modifications.
"""

import json
import os

import pandas as pd


base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
style_path = os.path.join(base_path, "style.json")
layers_path = os.path.join(base_path, "Layers.csv")
items_path = os.path.join(base_path, "Items.csv")

layers = pd.read_csv(layers_path, index_col=0)
items = pd.read_csv(items_path, index_col=0)

def get_filter(layer):
    if layers.loc[layer, "Filter"]:
        return {"filter": ["in", "class"] + list(items.loc[items["Layer"] == layer].index)}
    else:
        return {}

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
       "paint": {
           "text-color": "#ffffff",
           "text-halo-color": "rgba(0, 0, 0, 0.5)",
           "text-halo-width": 4,
           "text-halo-blur": 1}},
    **get_filter(layer))
     for layer in layers.loc[layers["Type"].isin(["symbol", "line"])].index]

style_json = {
  "version": 8,
  "sources": {
    "local": {
      "type": "vector",
      "url": "pmtiles:///region.pmtiles"
    }
  },
  "layers": background + fill_json + line_json + symbol_json
}

for layer in style_json["layers"]:
    if layer["id"] == "Rail":
        layer["paint"]["line-dasharray"] = [3, 3]

with open(style_path, "w+") as file:
    json.dump(style_json, file, indent=2)
