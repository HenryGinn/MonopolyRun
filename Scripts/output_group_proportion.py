"""
This produces a plot of points against the fraction of those points that
were achieved from the bonus for getting all squares within a group.
"""

import pandas as pd

from monopoly import Monopoly


monopoly = Monopoly()
monopoly.setup()
monopoly.load()

df = monopoly.indicators.xs("Group", level=0).T
df.index.name = "Speed (m/s)"
df["GroupPoints"] = df.dot(monopoly.groups["Value"].values).T
df["Points"] = monopoly.solutions["Points"].values
df["GroupFraction"] = df["GroupPoints"] / df["Points"]
df = df.reset_index()
df = df[["Points", "GroupFraction"]]
df.to_csv("../Essay/Data/GroupProportion.csv", index=False)
