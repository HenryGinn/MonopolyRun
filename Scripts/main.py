import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.setup()

"""
speeds = np.arange(0.5, 5.1, 0.1)
print(speeds)

for speed in speeds:
    print(f"\n{speed}")
    monopoly.speed = round(speed, 2)
    monopoly.reset()
    monopoly.solve()
    monopoly.update_outputs()

monopoly.save()
"""

monopoly.load()
monopoly.set_solution(4)
monopoly.draw()
monopoly.run()
