"""
"""

import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.setup()
monopoly.load()

df = monopoly.solutions[["Speed (m/s)", "Squares Visited", "Groups Visited"]]
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots(1)
ax1.plot(df["Speed (m/s)"], df["Squares Visited"] / df["Groups Visited"])
plt.show()
#df.to_csv("../Essay/Data/PlacesCountsVsSpeed.csv")
