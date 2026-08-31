import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


monopoly = Monopoly(2026)
monopoly.setup()
monopoly.load()
monopoly.set_solution(3.2)
monopoly.draw()
monopoly.run()

