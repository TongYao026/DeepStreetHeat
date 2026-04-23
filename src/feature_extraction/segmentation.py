import cv2
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

# Configuration
IMAGE_DIR = "data/svi_images"
OUTPUT_FILE = "data/micro_features.csv"

def extract_micro_features():
    """
    Extract micro features using color segmentation (OpenCV).
    This is a robust alternative when deep learning models fail to load.
    """
    print("Starting micro feature extraction (Color-based)...")
    
    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory {IMAGE_DIR} does not exist.")
        return

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
    if not image_files:
        print(f"No images found in {IMAGE_DIR}")
        return

    print(f"Processing {len(image_files)} images...")
    results = []

    for img_file in tqdm(image_files):
        img_path = os.path.join(IMAGE_DIR, img_file)
        try:
            image = cv2.imread(img_path)
            if image is None:
                continue
            
            # Convert to HSV color space
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            total_pixels = image.shape[0] * image.shape[1]

            # 1. Vegetation (Green)
            # Green range in HSV (approximate)
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            vegetation_ratio = cv2.countNonZero(mask_green) / total_pixels

            # 2. Sky (Blue/Bright)
            # Sky is often blue or very bright (white/gray)
            # Blue range
            lower_blue = np.array([90, 50, 50])
            upper_blue = np.array([130, 255, 255])
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Brightness (Value channel) > 200 often indicates sky or white buildings
            # We'll use a simple heuristic: top 1/3 of image + bright/blue
            h, w, _ = image.shape
            sky_region_mask = np.zeros((h, w), dtype=np.uint8)
            sky_region_mask[0:int(h/2.5), :] = 255 # Assume sky is mostly in top part
            
            # Combine blue OR very bright in the top region
            mask_bright = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 50, 255]))
            mask_sky_candidate = cv2.bitwise_or(mask_blue, mask_bright)
            mask_sky = cv2.bitwise_and(mask_sky_candidate, sky_region_mask)
            
            sky_ratio = cv2.countNonZero(mask_sky) / total_pixels

            # 3. Road/Pavement (Gray/Dark in lower part)
            # Low saturation, low-medium value
            lower_gray = np.array([0, 0, 50])
            upper_gray = np.array([180, 50, 150])
            mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
            
            road_region_mask = np.zeros((h, w), dtype=np.uint8)
            road_region_mask[int(h/2):, :] = 255 # Bottom half
            mask_road = cv2.bitwise_and(mask_gray, road_region_mask)
            
            road_ratio = cv2.countNonZero(mask_road) / total_pixels

            # 4. Building (Everything else roughly)
            # Simplified: 1 - (veg + sky + road)
            # Ensure non-negative
            building_ratio = max(0, 1.0 - (vegetation_ratio + sky_ratio + road_ratio))

            results.append({
                'filename': img_file,
                'vegetation': vegetation_ratio,
                'sky': sky_ratio,
                'road': road_ratio,
                'building': building_ratio,
                # Add dummy columns for other classes to match original schema if needed
                'sidewalk': 0.0, 'wall': 0.0, 'fence': 0.0, 'pole': 0.0, 
                'traffic light': 0.0, 'traffic sign': 0.0, 'terrain': 0.0, 
                'person': 0.0, 'rider': 0.0, 'car': 0.0, 'truck': 0.0, 
                'bus': 0.0, 'train': 0.0, 'motorcycle': 0.0, 'bicycle': 0.0
            })

        except Exception as e:
            print(f"Error processing {img_file}: {e}")
            continue

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Micro features (Color-based) saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_micro_features()
