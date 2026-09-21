import argparse

from monopoly import Monopoly


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Board to be displayed")
    args = parser.parse_args(argv)
    monopoly = Monopoly(args.name)
    monopoly.setup()


if __name__ == "__main__":
    main()
