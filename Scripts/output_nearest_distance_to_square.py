import os

import pandas as pd

from monopoly import Monopoly


def save_minimum_distance_to_nearest_place(name):
    monopoly = Monopoly(name)
    monopoly.setup()

    place_lookup = monopoly.graph.places.set_index("Place", drop=True)
    df = monopoly.solver.edges
    df["Start Square"] = df["Start"].map(place_lookup["Square"])
    df["End Square"] = df["End"].map(place_lookup["Square"])
    indexes = df.groupby("Start Square")["Weight"].idxmin()
    df = (
        df.loc[indexes,
               ["Start Square",
                "End Square",
                "Start",
                "End",
                "Weight"]]
        .reset_index(drop=True)
        .sort_values("Weight"))

    path = os.path.join(
        monopoly.output_path,
        "MinimumDistanceToNearestPlace.csv")
    df.to_csv(path, index=False)
    

names = ["2025", "2026"]
for name in names:
    save_minimum_distance_to_nearest_place(name)

