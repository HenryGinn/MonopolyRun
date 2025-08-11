import os


base_path = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(base_path, "Data")
base_source_path = os.path.join(data_path, "map.osm")
geometry_path = os.path.join(data_path, "geometry.csv")
test_path = os.path.join(data_path, "test.csv")
tikz_path = os.path.join(base_path, "TeX", "Map.tikz")
