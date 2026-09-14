import argparse
import math
import os

from pmtiles.reader import Reader, MmapSource
from pmtiles.writer import Writer
from pmtiles.tile import zxy_to_tileid


def lon_to_x(lon, z):
    return int((lon + 180) / 360 * (1 << z))


def lat_to_y(lat, z):
    lat = max(-85.05112878, min(85.05112878, lat))
    return int(
        (1 - math.asinh(math.tan(math.radians(lat))) / math.pi)
        / 2 * (1 << z)
    )


def main():

    parser = argparse.ArgumentParser(
        description="Crop a PMTiles archive by bbox and zoom."
    )

    parser.add_argument("input")
    parser.add_argument("output")

    parser.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        required=True,
        metavar=("WEST", "SOUTH", "EAST", "NORTH"),
    )

    parser.add_argument("--minzoom", type=int)
    parser.add_argument("--maxzoom", type=int)

    args = parser.parse_args()

    west, south, east, north = args.bbox

    # --------------------------------------------------------
    # Open source
    # --------------------------------------------------------

    with open(args.input, "rb") as f:

        reader = Reader(MmapSource(f))

        header = reader.header()
        metadata = reader.metadata()

        source_minzoom = header["min_zoom"]
        source_maxzoom = header["max_zoom"]

        minzoom = (
            args.minzoom
            if args.minzoom is not None
            else source_minzoom
        )

        maxzoom = (
            args.maxzoom
            if args.maxzoom is not None
            else source_maxzoom
        )

        minzoom = max(minzoom, source_minzoom)
        maxzoom = min(maxzoom, source_maxzoom)

        print()
        print("Source:")
        print(
            f"  bounds: "
            f"{header['min_lon_e7'] / 1e7}, "
            f"{header['min_lat_e7'] / 1e7}, "
            f"{header['max_lon_e7'] / 1e7}, "
            f"{header['max_lat_e7'] / 1e7}"
        )
        print(
            f"  zoom: {source_minzoom}–{source_maxzoom}"
        )

        print()
        print("Crop:")
        print(
            f"  bounds: "
            f"{west}, {south}, {east}, {north}"
        )
        print(
            f"  zoom: {minzoom}–{maxzoom}"
        )

        # ----------------------------------------------------
        # Find tiles
        # ----------------------------------------------------

        tiles = []

        for z in range(minzoom, maxzoom + 1):

            xmin = lon_to_x(west, z)
            xmax = lon_to_x(east, z)

            ymin = lat_to_y(north, z)
            ymax = lat_to_y(south, z)

            tile_count = (
                (xmax - xmin + 1)
                * (ymax - ymin + 1)
            )

            print(
                f"  z{z}: "
                f"x {xmin}–{xmax}, "
                f"y {ymin}–{ymax} "
                f"({tile_count:,} possible tiles)"
            )

            for x in range(xmin, xmax + 1):

                for y in range(ymin, ymax + 1):

                    # pmtiles 3.7.0 uses reader.get()
                    tile_data = reader.get(z, x, y)

                    if tile_data is None:
                        continue

                    tile_id = zxy_to_tileid(z, x, y)

                    tiles.append(
                        (tile_id, tile_data)
                    )

        print()
        print(
            f"Found {len(tiles):,} tiles."
        )

        if not tiles:
            raise RuntimeError(
                "No tiles matched the requested "
                "bbox/zoom range."
            )

        # ----------------------------------------------------
        # Write cropped archive
        # ----------------------------------------------------
        with open("Sources/cropped.pmtiles", "wb") as output:

            writer = Writer(output)

            for tile_id, tile_data in tiles:

                writer.write_tile(
                    tile_id,
                    tile_data
                )

            new_header = dict(header)

            new_header["min_zoom"] = minzoom
            new_header["max_zoom"] = maxzoom

            new_header["min_lon_e7"] = int(west * 1e7)
            new_header["min_lat_e7"] = int(south * 1e7)
            new_header["max_lon_e7"] = int(east * 1e7)
            new_header["max_lat_e7"] = int(north * 1e7)

            new_header["center_lon_e7"] = int(
                ((west + east) / 2) * 1e7
            )

            new_header["center_lat_e7"] = int(
                ((south + north) / 2) * 1e7
            )

            new_header["center_zoom"] = minzoom

            writer.finalize(
                new_header,
                metadata
            )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    input_size = os.path.getsize(args.input)
    output_size = os.path.getsize(args.output)

    input_mb = input_size / 1024 / 1024
    output_mb = output_size / 1024 / 1024

    saved = (1 - output_size / input_size) * 100

    print()
    print("Done!")
    print(f"  Input:  {input_mb:.2f} MB")
    print(f"  Output: {output_mb:.2f} MB")
    print(f"  Saved:  {saved:.1f}%")


if __name__ == "__main__":
    main()
