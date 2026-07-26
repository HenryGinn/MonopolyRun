import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.load_style()
m = monopoly
monopoly.set_graph()
monopoly.graph.set_graph()
monopoly.graph.set_places()
monopoly.set_server()

for place in monopoly.graph.places.index:
    monopoly.graph.add_node(place)

monopoly.server.run()
#monopoly.graph.construct_routes()
