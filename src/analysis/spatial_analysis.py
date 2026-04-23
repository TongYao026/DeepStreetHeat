import pandas as pd
import geopandas as gpd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from esda.getisord import G_Local
from libpysal.weights import DistanceBand
import os

# Configuration
DATA_FILE = "data/merged_data.csv"
OUTPUT_DIR = "data/spatial_analysis"
SHAPEFILE_OUTPUT = "data/spatial_analysis/results.shp"

def perform_spatial_analysis():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load data
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print("Merged data file not found. Please run data merging first.")
        # Create dummy data for demonstration
        N = 100
        df = pd.DataFrame({
            'lat': 22.3 + np.random.rand(N) * 0.05,
            'lon': 114.15 + np.random.rand(N) * 0.05,
            'LST': 30 + 5 * np.random.rand(N),
            'predicted_LST': 30 + 5 * np.random.rand(N)
        })

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
    )

    # 1. IDW Interpolation
    print("Performing IDW Interpolation...")
    
    # Define grid
    x_min, x_max = gdf.geometry.x.min(), gdf.geometry.x.max()
    y_min, y_max = gdf.geometry.y.min(), gdf.geometry.y.max()
    grid_x, grid_y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
    
    # Interpolate LST
    grid_z = griddata(
        (gdf.geometry.x, gdf.geometry.y), 
        gdf['LST'], 
        (grid_x, grid_y), 
        method='cubic'
    )
    
    plt.figure(figsize=(10, 8))
    plt.imshow(grid_z.T, extent=(x_min, x_max, y_min, y_max), origin='lower', cmap='hot')
    plt.colorbar(label='LST (C)')
    plt.title('LST Interpolation (IDW/Cubic)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.savefig(os.path.join(OUTPUT_DIR, "idw_interpolation.png"))
    plt.close()
    
    # 2. Hotspot Analysis (Getis-Ord Gi*)
    print("Performing Hotspot Analysis (Getis-Ord Gi*)...")
    
    # Define weights (distance-based)
    wq = DistanceBand.from_dataframe(gdf, threshold=0.01, binary=True, silence_warnings=True)
    
    # Calculate Gi*
    gi = G_Local(gdf['LST'], wq, transform='R')
    
    gdf['Gi_ZScore'] = gi.Zs
    gdf['Gi_PValue'] = gi.p_sim
    
    # Identify hotspots (Z > 1.96 for 95% confidence)
    gdf['Hotspot'] = np.where(gdf['Gi_ZScore'] > 1.96, 1, 0)
    gdf['Coldspot'] = np.where(gdf['Gi_ZScore'] < -1.96, 1, 0)
    
    # Save results to Shapefile for ArcGIS
    gdf.to_file(SHAPEFILE_OUTPUT)
    print(f"Spatial analysis results saved to {SHAPEFILE_OUTPUT}")
    
    # Plot Hotspots
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(column='Gi_ZScore', cmap='coolwarm', legend=True, ax=ax, markersize=5)
    plt.title('LST Hotspots (Getis-Ord Gi*)')
    plt.savefig(os.path.join(OUTPUT_DIR, "hotspot_map.png"))
    plt.close()

if __name__ == "__main__":
    perform_spatial_analysis()
