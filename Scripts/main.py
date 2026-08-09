import os

import numpy as np
import pandas as pd

from monopoly import Monopoly


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

monopoly = Monopoly()
monopoly.setup()

# Given in minutes per km, converted to metres per second
#paces = np.arange(1, 16, 15)
paces = np.array([10])

indicators = {}
solutions = {}
routes = {}

def a():
    global s
    s = monopoly.solver
    b = np.concatenate((s.values, [0]))
    B = np.concatenate((s.c, [0]))
    c = pd.DataFrame([b], index=["Solution"], columns=s.columns)
    d = pd.DataFrame([B], index=["Objective"], columns=s.columns)
    e = pd.concat((c, d, s.constraints), axis=0)
    e.to_csv(s.solution_path)

for pace in paces:
    monopoly.speed = 1000 / 60 / pace
    monopoly.reset()
    monopoly.solve()
    indicators[pace] = monopoly.solver.values.reshape(-1)
    solutions[pace] = monopoly.get_solution_summary()
    routes[pace] = monopoly.graph.routes_vertices[0]

s = monopoly.solver

indicators = pd.DataFrame(indicators, index=monopoly.solver.columns[:-1])
solutions = pd.DataFrame(solutions).transpose()
solutions.index.name = "Pace (min/km)"
routes = [
    [speed, order_id, place]
    for speed, solution in routes.items()
    for order_id, place in enumerate(solution)]
routes = pd.DataFrame(
    routes, columns=["Pace (min/km)", "Order ID", "Place"])

indicators_path = os.path.join(monopoly.output_path, "Indicators.csv")
solutions_path = os.path.join(monopoly.output_path, "Solutions.csv")
routes_path = os.path.join(monopoly.output_path, "Routes.csv")

indicators.to_csv(indicators_path)
solutions.to_csv(solutions_path)
routes.to_csv(routes_path)

monopoly.draw()
monopoly.run()
