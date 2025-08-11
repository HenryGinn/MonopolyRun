import os


data_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "Data")
base_source_path = os.path.join(data_path, "map.osm")
geometry_path = os.path.join(data_path, "geometry.csv")
test_path = os.path.join(data_path, "test.csv")
