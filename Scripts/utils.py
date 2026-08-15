import numpy as np
import rasterio as rs


def load_elevation(path):
    with rs.open(path) as file:
        elevation_source = file.read(1)
        width, height = file.width, file.height
        transform = file.transform
    return elevation_source, width, height, transform

def get_elevation_grid(width, height, transform):
    x = np.arange(width) * transform.a + transform.c + transform.a / 2
    y = np.arange(height) * transform.e + transform.f + transform.e / 2
    return x, y
