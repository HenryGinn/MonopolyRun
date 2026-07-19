from flask import Flask, send_from_directory, jsonify
import networkx as nx
import osmnx as ox
import json


app = Flask(__name__)

start = (51.32920605938939, -0.2676814081931653)
end = (51.334231337665436, -0.2682810902816036)

STYLE_PATH = "style.json"
_route_geojson = None


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/style.json")
def style():
    with open(STYLE_PATH) as f:
        merged = json.load(f)

    merged["sources"]["route"] = {
        "type": "geojson",
        "data": _route_geojson,
    }
    return jsonify(merged)


@app.route("/<path:f>")
def files(f):
    # Serves region.pmtiles and anything else in the directory.
    # Flask matches the more specific "/style.json" route above first,
    # so this never intercepts style requests.
    return send_from_directory(".", f)


def build_route():
    G = ox.load_graphml("region.graphml")

    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])

    route = nx.shortest_path(G, start_node, end_node, weight="length")

    coordinates = [(G.nodes[n]["x"], G.nodes[n]["y"]) for n in route]  # [lon, lat]

    distance_m = sum(
        G.edges[route[i], route[i + 1], 0]["length"]
        for i in range(len(route) - 1)
    )

    print(f"Route distance: {distance_m:.1f} m ({len(route)} nodes)")

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"distance_m": distance_m},
                "geometry": {"type": "LineString", "coordinates": coordinates},
            },
            {
                "type": "Feature",
                "properties": {"role": "start"},
                "geometry": {"type": "Point", "coordinates": [start[1], start[0]]},
            },
            {
                "type": "Feature",
                "properties": {"role": "end"},
                "geometry": {"type": "Point", "coordinates": [end[1], end[0]]},
            },
        ],
    }


if __name__ == "__main__":
    _route_geojson = build_route()
    app.run(host="localhost", port=8000)
