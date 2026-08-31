import numpy as np

from monopoly import Monopoly


monopoly = Monopoly(2026)
monopoly.setup()
speeds = np.arange(0.1, 4.5, 0.1)

for speed in speeds:
    monopoly.speed = round(speed, 2)
    print(f"\n{monopoly.speed}")
    monopoly.reset()
    monopoly.solve()
    monopoly.update_outputs()

monopoly.save()

