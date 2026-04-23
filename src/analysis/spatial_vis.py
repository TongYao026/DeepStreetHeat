import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import os

def idw_interpolation(x, y, z, xi, yi, p=2):
    xi_flat = xi.flatten()
    yi_flat = yi.flatten()
    grid_points = np.vstack((xi_flat, yi_flat)).T
    data_points = np.vstack((x, y)).T
    dists = cdist(grid_points, data_points)
    dists[dists == 0] = 1e-10
    weights = 1.0 / (dists ** p)
    zi = np.sum(weights * z.values, axis=1) / np.sum(weights, axis=1)
    return zi.reshape(xi.shape)

def generate_spatial_plots():
    print("Generating spatial plots...")
    if not os.path.exists('data/aggregated_features.csv'):
        return

    df = pd.read_csv("data/aggregated_features.csv")
    if not os.path.exists('data/spatial_analysis'):
        os.makedirs('data/spatial_analysis')

    # 1. IDW (LST)
    x = df['lon']
    y = df['lat']
    z = df['LST']
    resolution = 0.0005
    xi = np.arange(x.min(), x.max(), resolution)
    yi = np.arange(y.min(), y.max(), resolution)
    xi, yi = np.meshgrid(xi, yi)
    
    zi = idw_interpolation(x, y, z, xi, yi, p=2)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(zi, extent=(x.min(), x.max(), y.min(), y.max()), origin='lower', cmap='RdYlBu_r', alpha=0.8)
    plt.scatter(x, y, c=z, s=20, cmap='RdYlBu_r', edgecolors='k', linewidth=0.5)
    plt.colorbar(label='LST (°C)')
    plt.title('LST Spatial Distribution (IDW)\nPower=2, Resolution=~50m, Search=All Points')
    plt.savefig('data/spatial_analysis/idw_interpolation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Hotspot
    threshold_hot = df['LST'].quantile(0.90)
    threshold_cold = df['LST'].quantile(0.10)
    plt.figure(figsize=(10, 8))
    plt.scatter(df['lon'], df['lat'], c='lightgray', s=10, alpha=0.5)
    plt.scatter(df[df['LST'] >= threshold_hot]['lon'], df[df['LST'] >= threshold_hot]['lat'], c='red', s=50, label='Hotspots (>90%)', edgecolors='white')
    plt.scatter(df[df['LST'] <= threshold_cold]['lon'], df[df['LST'] <= threshold_cold]['lat'], c='blue', s=50, label='Coldspots (<10%)', edgecolors='white')
    plt.legend()
    plt.title('LST Hotspot Analysis (Top/Bottom 10% Quantile)')
    plt.savefig('data/spatial_analysis/hotspot_map.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Residual Map
    if os.path.exists('data/model_results/residuals.csv'):
        print("Generating Residual Map...")
        res_df = pd.read_csv('data/model_results/residuals.csv')
        
        plt.figure(figsize=(10, 8))
        # Red = Positive Residual (True > Pred, Model Underestimated)
        # Blue = Negative Residual (True < Pred, Model Overestimated)
        sc = plt.scatter(res_df['lon'], res_df['lat'], c=res_df['residual'], cmap='coolwarm', s=30, edgecolors='k', linewidth=0.5, vmin=-3, vmax=3)
        plt.colorbar(sc, label='Residual (°C)')
        plt.title('Spatial Distribution of Residuals (True - Predicted)')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.savefig('data/spatial_analysis/residual_map.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print("Done.")

if __name__ == "__main__":
    generate_spatial_plots()
