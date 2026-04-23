import cv2
import numpy as np
import os
import pandas as pd
from tqdm import tqdm
from scipy.stats import entropy

# Configuration
IMAGE_DIR = "data/svi_images"
OUTPUT_FILE = "data/statistical_features.csv"

def calculate_entropy(image):
    """
    Calculate Shannon Entropy of the grayscale image.
    Higher entropy -> more texture/complexity.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist / hist.sum()
    return entropy(hist, base=2)[0]

def calculate_colorfulness(image):
    """
    Calculate colorfulness metric (Hasler & Suesstrunk, 2003).
    """
    (B, G, R) = cv2.split(image.astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    return stdRoot + (0.3 * meanRoot)

def extract_statistical_features():
    print("Starting statistical feature extraction (HSV Stats, Entropy, Colorfulness)...")
    
    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory {IMAGE_DIR} does not exist.")
        return

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
    if not image_files:
        print(f"No images found in {IMAGE_DIR}")
        return

    results = []

    for img_file in tqdm(image_files):
        img_path = os.path.join(IMAGE_DIR, img_file)
        try:
            image = cv2.imread(img_path)
            if image is None:
                continue
            
            # 1. HSV Statistics
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            h_mean, h_std = np.mean(h), np.std(h)
            s_mean, s_std = np.mean(s), np.std(s)
            v_mean, v_std = np.mean(v), np.std(v)
            
            # 2. Entropy (Texture/Complexity)
            img_entropy = calculate_entropy(image)
            
            # 3. Colorfulness
            colorfulness = calculate_colorfulness(image)
            
            results.append({
                'filename': img_file,
                'h_mean': h_mean, 'h_std': h_std,
                's_mean': s_mean, 's_std': s_std,
                'v_mean': v_mean, 'v_std': v_std,
                'entropy': img_entropy,
                'colorfulness': colorfulness
            })

        except Exception as e:
            print(f"Error processing {img_file}: {e}")
            continue

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Statistical features saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_statistical_features()
