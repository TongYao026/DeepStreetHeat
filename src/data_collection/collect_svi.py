import os
import requests
import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY or API_KEY == "YOUR_ACTUAL_API_KEY_HERE":
    print("Warning: GOOGLE_MAPS_API_KEY is not set in .env file.")

OUTPUT_DIR = "data/svi_images"
METADATA_FILE = "data/svi_metadata.csv"
LOCATION = "Yau Tsim Mong District, Hong Kong"
IMAGE_SIZE = "640x640"
FOV = 90
HEADING = [0, 90, 180, 270]  # 4 directions
PITCH = 0

def download_svi(location_name=LOCATION, num_points=700):
    """
    Download Street View Imagery for a given location.
    """
    if not API_KEY:
        print("Error: API Key is missing. Please set GOOGLE_MAPS_API_KEY in .env file.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Fetching street network for {location_name}...")
    try:
        G = ox.graph_from_place(location_name, network_type='drive')
    except Exception as e:
        print(f"Error fetching network: {e}")
        return

    # Convert graph to nodes and edges
    nodes, edges = ox.graph_to_gdfs(G)
    
    # Generate sample points along edges (simplified approach: use nodes or sample points on edges)
    # For better distribution, we can sample points along the edges.
    print("Generating sample points...")
    points = []
    
    # Simple sampling: use nodes for demonstration. In a real scenario, interpolate points along edges.
    # We will just take a subset of nodes to simulate the sampling.
    sample_nodes = nodes.sample(n=min(num_points, len(nodes)), random_state=42)
    
    metadata = []

    print("Downloading images...")
    for idx, row in tqdm(sample_nodes.iterrows(), total=len(sample_nodes)):
        lat = row.geometry.y
        lon = row.geometry.x
        point_id = idx

        for h in HEADING:
            # Check if image exists
            # URL for Google Street View Static API
            # https://maps.googleapis.com/maps/api/streetview?size=600x300&location=46.414382,10.013988&heading=151.78&pitch=-0.76&key=YOUR_API_KEY
            
            url = f"https://maps.googleapis.com/maps/api/streetview?size={IMAGE_SIZE}&location={lat},{lon}&heading={h}&pitch={PITCH}&fov={FOV}&key={API_KEY}"
            
            # Save path
            filename = f"{point_id}_{h}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # Skip if file exists
            if os.path.exists(filepath):
                continue
                
            # In a real scenario, uncomment the following lines to download
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                else:
                    print(f"Failed to download {filename}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
            
            # Record metadata
            metadata.append({
                'id': point_id,
                'lat': lat,
                'lon': lon,
                'heading': h,
                'filename': filename
            })

    # Save metadata
    df = pd.DataFrame(metadata)
    df.to_csv(METADATA_FILE, index=False)
    print(f"Metadata saved to {METADATA_FILE}")

if __name__ == "__main__":
    download_svi()
