import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW
import os

def run_gwr():
    print("Running GWR Analysis...")
    if not os.path.exists("data/aggregated_features.csv"):
        print("Data not found.")
        return

    df = pd.read_csv("data/aggregated_features.csv")
    
    # Coordinates
    coords = list(zip(df['lon'], df['lat']))
    
    # Variables
    # Standardize variables
    target = 'LST'
    # Adding 'poi_density' if it exists (for the next step)
    features = ['sky', 'shadow_ratio', 'h_std']
    if 'poi_density' in df.columns:
        features.append('poi_density')
        print("Including POI Density in GWR...")
    
    y = df[target].values.reshape((-1, 1))
    X = df[features].values
    
    # Handle NaNs
    if np.isnan(X).any() or np.isnan(y).any():
        print("Warning: NaNs found. Dropping missing values.")
        valid_mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y).flatten()
        X = X[valid_mask]
        y = y[valid_mask]
        coords = [coords[i] for i in range(len(coords)) if valid_mask[i]]
        df = df[valid_mask]

    X_std = (X - X.mean(axis=0)) / X.std(axis=0)
    y_std = (y - y.mean(axis=0)) / y.std(axis=0)
    
    # Bandwidth Selection
    print("Selecting Optimal Bandwidth...")
    try:
        # Try optimization first
        gwr_selector = Sel_BW(coords, y_std, X_std)
        gwr_bw = gwr_selector.search(bw_min=40)
        print(f"Optimal Bandwidth: {gwr_bw}")
    except Exception as e:
        print(f"Bandwidth selection failed/slow ({e}). Using fixed bandwidth = 100.")
        gwr_bw = 100
        
    # Train GWR
    print("Fitting GWR Model...")
    try:
        gwr_model = GWR(coords, y_std, X_std, gwr_bw)
        gwr_results = gwr_model.fit()
        
        print(f"Global R2: {gwr_results.R2:.4f}")
        
        # Add GWR results back to DataFrame
        df_gwr = df.copy()
        df_gwr['localR2'] = gwr_results.localR2
        df_gwr['gwr_pred'] = gwr_results.predy
        df_gwr['gwr_resid'] = gwr_results.resid_response
        
        # Visualize Local R2
        if not os.path.exists('data/spatial_analysis'):
            os.makedirs('data/spatial_analysis')
            
        # Export enhanced CSV for GIS
        gis_output = 'data/spatial_analysis/gwr_results.csv'
        df_gwr.to_csv(gis_output, index=False)
        print(f"Exported GWR results (CSV) to {gis_output} for GIS mapping.")
        
        # Export as Shapefile
        try:
            import geopandas as gpd
            gdf = gpd.GeoDataFrame(df_gwr, geometry=gpd.points_from_xy(df_gwr.lon, df_gwr.lat), crs="EPSG:4326")
            shp_output = 'data/spatial_analysis/gwr_results.shp'
            gdf.to_file(shp_output)
            print(f"Exported GWR results (Shapefile) to {shp_output} for GIS mapping.")
        except ImportError:
            print("Geopandas not installed. Skipping shapefile export.")
            
        plt.figure(figsize=(10, 8))
        # Use df['lon'] and df['lat'] which align with the results
        sc = plt.scatter(df['lon'], df['lat'], c=gwr_results.localR2, cmap='plasma', s=40, edgecolors='none', alpha=0.9)
        plt.colorbar(sc, label='Local R2')
        plt.title(f'GWR Local R2 (Bandwidth={int(gwr_bw)})')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.savefig('data/spatial_analysis/gwr_local_r2.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("GWR Local R2 map saved to data/spatial_analysis/gwr_local_r2.png")
        
    except Exception as e:
        print(f"GWR Fitting Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_gwr()
