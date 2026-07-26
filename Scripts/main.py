import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
m = monopoly
#monopoly.set_server()
#monopoly.server.run()
monopoly.set_graph()
monopoly.graph.set_graph()
monopoly.graph.set_places()
#monopoly.graph.construct_routes()
