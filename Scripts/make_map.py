import argparse
import base64
import json
from pathlib import Path

from monopoly import Monopoly


def main(argv=None):
    args = parse_args(argv)
    monopoly = Monopoly(args.name)
    monopoly.setup()
    monopoly.load()
    speeds = get_speeds(args, monopoly)
    make_maps(monopoly, speeds)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Board to be displayed")
    parser.add_argument("speed", type=float, nargs="?", default=None, help=
                        "Speed of runners. If left blank, processes all speeds.")
    args = parser.parse_args(argv)
    return args

def get_speeds(args, monopoly):
    if args.speed is None:
        speeds = monopoly.solutions.index
    else:
        speeds = [args.speed]
    return speeds

def make_maps(monopoly, speeds):
    for speed in speeds:
        make_map(monopoly, speed)

# Modify url line as the file is embedded in the html.
# We also use a smaller pmtiles to keep file sizes down.
def change_style_pmtiles(monopoly):
    for source in monopoly.style.get("sources", {}).values():
        if isinstance(source, dict):
            if source.get("url") == "pmtiles:///region.pmtiles":
                source["url"] = "pmtiles://cropped.pmtiles"

def make_map(monopoly, speed):
    set_speed(monopoly, speed)
    maps_path = BASE_DIR / "Output" / monopoly.name / "Maps"
    maps_path.mkdir(exist_ok=True)
    speed = str(speed).replace(".", "_")
    output_path = maps_path / f"{speed}.html"
    style_json = get_style_converted_to_javascript_json(monopoly)

    # Construct the standalone HTML
    html = f"""<!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
    {maplibre_css}

    html, body, #map {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
    }}
    </style>

    <script>
    {maplibre_js}
    </script>

    <script>
    {pmtiles_js}
    </script>

    </head>

    <body>

    <div id="map"></div>

    <script>

    // Embedded map style
    const MAP_STYLE = {style_json};

    // ------------------------------------------------------------
    // Embedded PMTiles archive
    // ------------------------------------------------------------
    //
    // The Python generator stored region.pmtiles as base64.
    // Convert it back into a browser File object.
    //
    // PMTiles provides a FileSource specifically for this use case.
    // ------------------------------------------------------------

    const PMTILES_BASE64 = "{pmtiles_base64}";

    function base64ToUint8Array(base64) {{
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);

        for (let i = 0; i < binary.length; i++) {{
            bytes[i] = binary.charCodeAt(i);
        }}

        return bytes;
    }}

    const pmtilesBytes = base64ToUint8Array(PMTILES_BASE64);

    const pmtilesFile = new File(
        [pmtilesBytes],
        "cropped.pmtiles",
        {{
            type: "application/octet-stream"
        }}
    );


    // PMTiles protocol
    const protocol = new pmtiles.Protocol();

    maplibregl.addProtocol(
        "pmtiles",
        protocol.tile
    );


    // ------------------------------------------------------------
    // Give the PMTiles protocol our embedded File.
    //
    // FileSource reads byte ranges directly from the File,
    // so MapLibre does not need an HTTP server.
    // ------------------------------------------------------------

    const pmtilesArchive = new pmtiles.PMTiles(
        new pmtiles.FileSource(pmtilesFile)
    );

    protocol.add(pmtilesArchive);


    // ------------------------------------------------------------
    // Create the map
    // ------------------------------------------------------------

    const map = new maplibregl.Map({{
        container: "map",
        style: MAP_STYLE,

        center: [
            -0.26425884971285996,
            51.33803794637353
        ],

        zoom: 14
    }});


    window.map = map;

    </script>

    </body>
    </html>
    """


    output_path.write_text(
        html,
        encoding="utf-8")
    print(f"Output to {output_path}")


def set_speed(monopoly, speed):
    monopoly.reset()
    change_style_pmtiles(monopoly)
    try:
        monopoly.set_solution(speed)
    except ValueError:
        raise f"Solution has not been generated for {speed}"
    monopoly.draw()

def get_style_converted_to_javascript_json(monopoly):
    style_json = json.dumps(
        monopoly.style,
        separators=(",", ":"),
        ensure_ascii=False)
    return style_json

def read_text(path):
    return path.read_text(encoding="utf-8")

def read_binary_base64(path):
    data = path.read_bytes()
    return base64.b64encode(data).decode("ascii")


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_DIR = BASE_DIR / "Sources"
INDEX_HTML = SOURCES_DIR / "index.html"
PMTILES_FILE = SOURCES_DIR / "cropped.pmtiles"
MAPLIBRE_JS = SOURCES_DIR / "maplibre-gl.js"
MAPLIBRE_CSS = SOURCES_DIR / "maplibre-gl.css"
PMTILES_JS = SOURCES_DIR / "pmtiles.js"

maplibre_js = read_text(MAPLIBRE_JS)
maplibre_css = read_text(MAPLIBRE_CSS)
pmtiles_js = read_text(PMTILES_JS)
pmtiles_base64 = read_binary_base64(PMTILES_FILE)

if __name__ == "__main__":
    main()
