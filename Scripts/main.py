import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.setup()

speeds = [8]

for speed in speeds:
    monopoly.speed = round(speed, 2)
    print(f"\n{monopoly.speed}")
    monopoly.reset()
    monopoly.solve()
    monopoly.update_outputs()

#monopoly.save()
#monopoly.load()
#monopoly.draw()
#monopoly.run()

