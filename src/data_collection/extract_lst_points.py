import rasterio
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# Configuration
SVI_METADATA = "data/svi_metadata.csv"
LST_TIFF = "data/lst_mean.tif"
OUTPUT_FILE = "data/lst_data.csv"

def extract_lst_values():
    if not os.path.exists(SVI_METADATA):
        print("SVI metadata file not found.")
        return
    if not os.path.exists(LST_TIFF):
        print("LST TIFF file not found.")
        return

    # Load SVI points
    df = pd.read_csv(SVI_METADATA)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
    )

    # Open LST raster
    with rasterio.open(LST_TIFF) as src:
        # Reproject points if necessary (rasterio handles this usually if crs matches)
        # Assuming TIFF is in WGS84 or similar. If not, reproject gdf.
        if src.crs != gdf.crs:
            gdf = gdf.to_crs(src.crs)
            
        # Sample raster values at points
        coords = [(x, y) for x, y in zip(gdf.geometry.x, gdf.geometry.y)]
        gdf['LST'] = [x[0] for x in src.sample(coords)]

    # Save to CSV
    gdf.drop(columns='geometry').to_csv(OUTPUT_FILE, index=False)
    print(f"LST values extracted to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_lst_values()
