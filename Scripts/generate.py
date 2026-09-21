import argparse

import numpy as np

from monopoly import Monopoly


lookup = {
    "2025": {"Start": 0.1, "Stop": 8.1},
    "2026": {"Start": 0.1, "Stop": 5.1},
    "2026 Stoneleigh 40": {"Start": 2.1, "Stop": 5.1},

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Board to be displayed")
    args = parser.parse_args(argv)
    monopoly = Monopoly(args.name)
    monopoly.setup()
    monopoly.load()

    limits = lookup[monopoly.name]
    speeds = np.arange(limits["Start"], limits["Stop"], 0.1)

    for speed in speeds:
        monopoly.speed = round(speed, 2)
        print(f"\n{monopoly.speed}")
        monopoly.reset()
        monopoly.solve()
        monopoly.update_outputs()

    monopoly.save()


if __name__ == "__main__":
    main()


