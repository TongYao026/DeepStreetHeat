import ee
import geemap
import os
import sys

# Initialize Earth Engine
def init_ee():
    try:
        ee.Initialize(project='ninth-physics-489311-d2')
        return True
    except Exception as e:
        print(f"Earth Engine initialization failed: {e}")
        
        # Check for specific error messages
        if "not registered to use Earth Engine" in str(e):
            print("\nCRITICAL: Your project is enabled but NOT registered.")
            print("Please visit: https://signup.earthengine.google.com/")
            print("Select your project and register it for 'Non-commercial' use.\n")
        
        print("Trying to authenticate with forced refresh...")
        try:
            # Force re-authentication to pick up new project permissions
            ee.Authenticate(force=True, auth_mode='notebook')
            ee.Initialize(project='ninth-physics-489311-d2')
            return True
        except Exception as e2:
            print(f"Authentication failed: {e2}")
            return False

def get_lst_data(roi, start_date='2023-01-01', end_date='2023-12-31'):
    """
    Fetch Land Surface Temperature (LST) data from Landsat 8.
    """
    # Landsat 8 Collection 2 Level 2
    l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', 10))

    def calculate_lst(image):
        thermal = image.select('ST_B10')
        lst_kelvin = thermal.multiply(0.00341802).add(149.0)
        lst_celsius = lst_kelvin.subtract(273.15).rename('LST')
        return image.addBands(lst_celsius)

    l8_lst = l8.map(calculate_lst)
    mean_lst = l8_lst.select('LST').mean().clip(roi)
    return mean_lst

def export_lst(image, roi, filename='data/lst_mean.tif', scale=30):
    if not os.path.exists('data'):
        os.makedirs('data')
        
    geemap.ee_export_image(
        image, 
        filename=filename, 
        scale=scale, 
        region=roi, 
        file_per_band=False
    )
    print(f"Exported LST to {filename}")

if __name__ == "__main__":
    if init_ee():
        # Define ROI for Yau Tsim Mong, Hong Kong
        roi = ee.Geometry.Rectangle([114.14, 22.29, 114.19, 22.33])
        print("Fetching LST data...")
        lst_image = get_lst_data(roi)
        export_lst(lst_image, roi)
    else:
        print("\nSkipping GEE download. Please use the dummy data generator: src/data_collection/generate_dummy_lst.py")
