import osmnx as ox
import pandas as pd

locations = [
    "Yau Tsim Mong, Hong Kong",
    "Yau Tsim Mong District, Hong Kong",
    "Yau Tsim Mong, Kowloon, Hong Kong"
]

for loc in locations:
    print(f"Geocoding: {loc}")
    try:
        gdf = ox.geocode_to_gdf(loc)
        print(f"Success! Found geometry: {gdf.geometry.values[0]}")
    except Exception as e:
        print(f"Failed: {e}")
