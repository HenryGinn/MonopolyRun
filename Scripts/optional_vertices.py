"""
The purpose of this script is to analyse which place was visited when
there were multiple places that could be visited to achieve a given
square.
"""

import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.setup()
monopoly.load()

m = monopoly
place_to_square_lookup = dict(monopoly.places[["Place", "Square"]].values)
routes = monopoly.solution_routes
routes["Square"] = routes["Place"].map(place_to_square_lookup)

monopoly.set_solution(8)
monopoly.draw()
monopoly.run()
