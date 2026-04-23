import torch
print("Torch imported")
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
print("Transformers imported")
import os

def test_model():
    print("Testing model load...")
    try:
        # Use a smaller model for testing
        model_name = "nvidia/segformer-b0-finetuned-cityscapes-512-512"
        processor = SegformerImageProcessor.from_pretrained(model_name)
        model = SegformerForSemanticSegmentation.from_pretrained(model_name)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
