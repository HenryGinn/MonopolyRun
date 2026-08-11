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
    print("")
    print(speed)
    try:
        monopoly.speed = round(speed, 2)
        monopoly.reset()
        monopoly.solve()
        monopoly.update_outputs()
    except:
        print(f"Speed {speed} failed")

s = monopoly.solver
monopoly.save()
"""
monopoly.load()
monopoly.set_solution(2.0)
monopoly.draw()
monopoly.run()
