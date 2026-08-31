"""
This produces the data for a plot of points against the fraction of
those points that were achieved from the bonus for getting all squares
within a group.
"""

import os

import pandas as pd

from monopoly import Monopoly


def main(name):
    print(f"Generating csv showing proportion of points come from groups for {name}.")
    monopoly = Monopoly(name)
    monopoly.setup()
    monopoly.load()

    df = monopoly.indicators.xs("Group", level=0).T
    df.index.name = "Speed (m/s)"
    df["GroupPoints"] = df.dot(monopoly.groups["Value"].values).T
    df["Points"] = monopoly.solutions["Points"].values
    df["GroupFraction"] = df["GroupPoints"] / df["Points"]
    df = df.reset_index()
    df = df[["Points", "GroupFraction"]]
    path = os.path.join(monopoly.output_path, "GroupProportion.csv")
    df.to_csv(path, index=False)

