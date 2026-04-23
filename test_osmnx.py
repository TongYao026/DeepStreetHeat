import osmnx as ox

locations = [
    "Yau Tsim Mong, Hong Kong",
    "Yau Tsim Mong District, Hong Kong",
    "Yau Tsim Mong, Kowloon, Hong Kong"
]

for loc in locations:
    print(f"Testing location: {loc}")
    try:
        G = ox.graph_from_place(loc, network_type='drive')
        print(f"Success! Found {len(G.nodes)} nodes.")
        break
    except Exception as e:
        print(f"Failed: {e}")
