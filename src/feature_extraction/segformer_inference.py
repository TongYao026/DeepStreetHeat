
import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm
import sys

# Configuration
IMAGE_DIR = "data/svi_images"
OUTPUT_FILE = "data/segformer_features.csv"
MODEL_NAME = "nvidia/segformer-b0-finetuned-ade-512-512"
BATCH_SIZE = 4 # Small batch for CPU

def get_ade20k_mapping():
    mapping = {
        'seg_sky': [2],
        'seg_vegetation': [4, 9, 17],
        'seg_building': [0, 1, 8],
        'seg_road': [6, 11, 13]
    }
    return mapping

def run_segmentation():
    print("Starting SegFormer Segmentation...", flush=True)
    
    try:
        import torch
        from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
        print(f"Libraries imported. Torch: {torch.__version__}", flush=True)
    except ImportError as e:
        print(f"Import Error: {e}", flush=True)
        return

    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory {IMAGE_DIR} not found.", flush=True)
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}", flush=True)

    try:
        print(f"Loading model: {MODEL_NAME}...", flush=True)
        processor = SegformerImageProcessor.from_pretrained(MODEL_NAME)
        model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME).to(device)
        print("Model loaded successfully.", flush=True)
    except Exception as e:
        print(f"Failed to load model: {e}", flush=True)
        return

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('_0.jpg')]
    print(f"Found {len(image_files)} images.", flush=True)
    
    # Process a subset for testing if there are too many, or all if requested.
    # For now, let's do all.
    
    results = []
    mapping = get_ade20k_mapping()
    
    print("Starting inference...", flush=True)
    for i in tqdm(range(0, len(image_files), BATCH_SIZE)):
        batch_files = image_files[i:i+BATCH_SIZE]
        images = []
        valid_files = []
        
        for img_file in batch_files:
            try:
                img_path = os.path.join(IMAGE_DIR, img_file)
                image = Image.open(img_path).convert("RGB")
                images.append(image)
                valid_files.append(img_file)
            except Exception as e:
                print(f"Error reading {img_file}: {e}", flush=True)
                continue
        
        if not images:
            continue
            
        try:
            inputs = processor(images=images, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits
            pred_segs = logits.argmax(dim=1)
            
            for idx, pred_seg in enumerate(pred_segs):
                total_pixels = pred_seg.numel()
                row = {'filename': valid_files[idx]}
                pred_np = pred_seg.cpu().numpy()
                for cat, classes in mapping.items():
                    mask = np.isin(pred_np, classes)
                    row[cat] = np.sum(mask) / total_pixels
                results.append(row)
        except Exception as e:
            print(f"Inference error: {e}", flush=True)
            continue

    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"SegFormer features saved to {OUTPUT_FILE}", flush=True)
    else:
        print("No results generated.", flush=True)

if __name__ == "__main__":
    run_segmentation()
