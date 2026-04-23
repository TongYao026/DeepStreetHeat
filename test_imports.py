import torch
print("Torch imported")
try:
    from transformers import SegformerFeatureExtractor
    print("SegformerFeatureExtractor imported")
    from transformers import SegformerForSemanticSegmentation
    print("SegformerForSemanticSegmentation imported")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
