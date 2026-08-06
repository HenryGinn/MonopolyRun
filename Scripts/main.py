import numpy as np
import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.speed = 1
m = monopoly

monopoly.set_graph()
monopoly.graph.set_graph()
monopoly.graph.set_places()
monopoly.graph.set_elevation_map()
monopoly.set_routes()

monopoly.set_solver()
s = monopoly.solver
g = monopoly.graph
self = g
monopoly.solver.set_quantities()
monopoly.construct_problem()
monopoly.solve()


monopoly.load_style()
monopoly.draw()
monopoly.set_server()
monopoly.server.run()
