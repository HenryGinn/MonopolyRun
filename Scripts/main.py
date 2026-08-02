import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.speed = 2
#monopoly.load_style()
m = monopoly
monopoly.set_graph()
monopoly.graph.set_graph()
monopoly.graph.set_places()
#monopoly.graph.set_elevation_map()
#monopoly.set_server()
#monopoly.server.run()
monopoly.set_routes()
monopoly.set_solver()
s = monopoly.solver
monopoly.solver.set_quantities()
monopoly.construct_problem()
monopoly.solve()

