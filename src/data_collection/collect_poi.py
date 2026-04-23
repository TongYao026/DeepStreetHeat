import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import numpy as np

# Config
PLACE_NAME = "Yau Tsim Mong District, Hong Kong"
BUFFER_DIST = 100  # meters

def collect_poi_data():
    print("Collecting POI data from OpenStreetMap...")
    
    if not os.path.exists("data/aggregated_features.csv"):
        print("Aggregated features not found.")
        return

    df = pd.read_csv("data/aggregated_features.csv")
    
    # Check for NaNs in lat/lon
    if df['lat'].isnull().any() or df['lon'].isnull().any():
        print("NaNs found in coordinates. Dropping...")
        df = df.dropna(subset=['lat', 'lon'])

    # 1. Download POIs (Restaurants, Shops, Amenities)
    tags = {'amenity': True, 'shop': True, 'leisure': True}
    try:
        print(f"Downloading POIs for {PLACE_NAME} using place name...")
        # Use features_from_place which is more robust
        try:
            pois = ox.features_from_place(PLACE_NAME, tags=tags)
        except Exception as e:
            print(f"features_from_place failed: {e}. Trying bbox...")
            north, south, east, west = df['lat'].max() + 0.01, df['lat'].min() - 0.01, df['lon'].max() + 0.01, df['lon'].min() - 0.01
            pois = ox.features_from_bbox(bbox=(north, south, east, west), tags=tags)
            
        print(f"Downloaded {len(pois)} POIs.")
        
        # Project to UTM (for distance calculation)
        # Hong Kong is UTM zone 50Q, EPSG:32650 usually works, or auto-project
        # ox.project_gdf is deprecated, use to_crs
        try:
            pois_proj = pois.to_crs(epsg=32650) 
        except:
            pois_proj = pois.to_crs(pois.estimate_utm_crs())

        # Create GeoDataFrame for our sample points
        geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
        gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        gdf_points_proj = gdf_points.to_crs(pois_proj.crs)
        
        # 2. Calculate POI Density (Count within buffer)
        print("Calculating POI density for each point...")
        poi_counts = []
        
        # Create spatial index for faster query
        sindex = pois_proj.sindex
        
        for idx, row in gdf_points_proj.iterrows():
            # Buffer the point
            buffer = row.geometry.buffer(BUFFER_DIST)
            # Find possible matches with spatial index
            possible_matches_index = list(sindex.intersection(buffer.bounds))
            possible_matches = pois_proj.iloc[possible_matches_index]
            # Precise intersection
            precise_matches = possible_matches[possible_matches.intersects(buffer)]
            poi_counts.append(len(precise_matches))
            
        df['poi_density'] = poi_counts
        
        print("POI Density calculated.")
        print(df[['id', 'poi_density']].head())
        
        # Save updated dataset
        df.to_csv("data/aggregated_features.csv", index=False)
        print("Data saved to data/aggregated_features.csv")
        
    except Exception as e:
        print(f"Error collecting POIs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    collect_poi_data()
