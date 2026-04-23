import cv2
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

# Configuration
IMAGE_DIR = "data/svi_images"
OUTPUT_FILE = "data/macro_features.csv"

def calculate_shadow_ratio(image):
    """
    Calculate shadow ratio using HSV color space.
    Shadows often have high saturation and low value.
    This is a simplified heuristic.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Thresholding for shadow detection (tweak these values based on empirical observation)
    # Shadows: Low Value (V), Higher Saturation (S) compared to illuminated areas
    # Simple approach: Otsu's thresholding on V channel
    _, shadow_mask = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    shadow_pixels = cv2.countNonZero(shadow_mask)
    total_pixels = image.shape[0] * image.shape[1]
    
    return shadow_pixels / total_pixels

def calculate_sky_brightness(image):
    """
    Calculate average sky brightness.
    Assumes sky is the brightest part (simplified).
    A better approach uses the semantic segmentation mask to identify sky pixels first.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Assume top 20% of image contains sky if we don't use segmentation mask here
    # But since we have segmentation, we should ideally merge these.
    # For standalone macro script, we'll just take the mean brightness of the top 1/3rd
    h, w = gray.shape
    sky_region = gray[0:int(h/3), :]
    return np.mean(sky_region)

def extract_macro_features():
    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory {IMAGE_DIR} does not exist.")
        return

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
    results = []

    print(f"Processing {len(image_files)} images for macro features...")

    for img_file in tqdm(image_files):
        img_path = os.path.join(IMAGE_DIR, img_file)
        try:
            image = cv2.imread(img_path)
            if image is None:
                continue
        except Exception as e:
            print(f"Error opening {img_file}: {e}")
            continue
            
        shadow_ratio = calculate_shadow_ratio(image)
        sky_brightness = calculate_sky_brightness(image)
        
        # Add more features as needed (e.g., color diversity, texture)
        
        results.append({
            'filename': img_file,
            'shadow_ratio': shadow_ratio,
            'sky_brightness': sky_brightness
        })
        
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Macro features saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_macro_features()
