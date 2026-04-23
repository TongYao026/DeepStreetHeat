import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

# Configuration
OUTPUT_FILE = 'data/lst_mean.tif'
# Yau Tsim Mong extent approx
WEST = 114.14
NORTH = 22.33
EAST = 114.19
SOUTH = 22.29
PIXEL_SIZE = 0.00027 # Approx 30m at equator, rough estimate

def generate_dummy_lst():
    if not os.path.exists('data'):
        os.makedirs('data')

    width = int((EAST - WEST) / PIXEL_SIZE)
    height = int((NORTH - SOUTH) / PIXEL_SIZE)
    
    transform = from_origin(WEST, NORTH, PIXEL_SIZE, PIXEL_SIZE)
    
    # Generate dummy data: Gradient + Random noise
    # Simulating UHI: hotter in center/dense areas (approx)
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xv, yv = np.meshgrid(x, y)
    
    # Simple pattern: Center is hotter
    center_x, center_y = 0.5, 0.5
    dist = np.sqrt((xv - center_x)**2 + (yv - center_y)**2)
    
    # Base temp 30C, max temp 35C in center, plus random noise
    lst_data = 35 - (dist * 10) + np.random.normal(0, 1, (height, width))
    lst_data = lst_data.astype(np.float32)

    with rasterio.open(
        OUTPUT_FILE,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=lst_data.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(lst_data, 1)

    print(f"Dummy LST data generated at {OUTPUT_FILE}")
    print("Value range: {:.2f} - {:.2f} Celsius".format(np.min(lst_data), np.max(lst_data)))

if __name__ == "__main__":
    generate_dummy_lst()
