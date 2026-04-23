import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

IMAGE_DIR = "data/svi_images"
OUTPUT_FILE = "data/model_results/segmentation_qc.png"

def generate_masks():
    if not os.path.exists(IMAGE_DIR):
        print("Image directory not found.")
        return
    
    files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
    if not files:
        print("No images found.")
        return
        
    # Pick a random image (or a specific one if known to be good)
    # Using the first one for consistency
    img_file = files[0]
    img_path = os.path.join(IMAGE_DIR, img_file)
    print(f"Processing image: {img_file}")
    image = cv2.imread(img_path)
    
    if image is None:
        print("Failed to load image.")
        return

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    h, w, _ = image.shape

    # 1. Vegetation
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask_veg = cv2.inRange(hsv, lower_green, upper_green)

    # 2. Sky
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    sky_region_mask = np.zeros((h, w), dtype=np.uint8)
    sky_region_mask[0:int(h/2.5), :] = 255
    mask_bright = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 50, 255]))
    mask_sky = cv2.bitwise_or(mask_blue, cv2.bitwise_and(mask_bright, sky_region_mask))

    # 3. Road
    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 50, 150])
    mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
    road_region_mask = np.zeros((h, w), dtype=np.uint8)
    road_region_mask[int(h/2):, :] = 255
    mask_road = cv2.bitwise_and(mask_gray, road_region_mask)

    # 4. Shadow (Macro)
    v = hsv[:, :, 2]
    _, mask_shadow = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Plot
    fig, axes = plt.subplots(1, 5, figsize=(25, 6))
    
    # Define style
    title_font = {'fontsize': 20, 'fontweight': 'bold'}
    
    axes[0].imshow(image)
    axes[0].set_title("Original Image", **title_font)
    axes[0].axis('off')
    
    axes[1].imshow(mask_veg, cmap='Greens')
    axes[1].set_title("Vegetation Mask", **title_font)
    axes[1].axis('off')
    
    axes[2].imshow(mask_sky, cmap='Blues')
    axes[2].set_title("Sky Mask", **title_font)
    axes[2].axis('off')
    
    axes[3].imshow(mask_road, cmap='gray')
    axes[3].set_title("Road Mask", **title_font)
    axes[3].axis('off')
    
    axes[4].imshow(mask_shadow, cmap='gray')
    axes[4].set_title("Shadow Mask (Otsu)", **title_font)
    axes[4].axis('off')
    
    plt.tight_layout(pad=2.0)
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"Saved QC masks to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_masks()
