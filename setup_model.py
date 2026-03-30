import torch
from transformers import AutoProcessor, AutoModelForCausalLM
import os

MODEL_ID = "microsoft/Florence-2-base"
MODEL_PATH = "models/Florence-2-base"

def setup():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    print(f"Checking Florence-2 model... (Target: {MODEL_PATH})")
    
    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at {MODEL_PATH}")
    else:
        print(f"Downloading model {MODEL_ID} to {MODEL_PATH}...")
        print("This might take a few minutes (approx 400MB)...")
        # Load and save
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, 
            trust_remote_code=True, 
            torch_dtype=torch_dtype,
            attn_implementation="eager"
        )
        processor = AutoProcessor.from_pretrained(
            MODEL_ID, 
            trust_remote_code=True
        )
        
        os.makedirs(MODEL_PATH, exist_ok=True)
        model.save_pretrained(MODEL_PATH)
        processor.save_pretrained(MODEL_PATH)
        print("Model downloaded and saved locally.")

if __name__ == "__main__":
    setup()
