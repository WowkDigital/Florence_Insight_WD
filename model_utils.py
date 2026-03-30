import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import os

MODEL_ID = "microsoft/Florence-2-base"
MODEL_PATH = "models/Florence-2-base"

class FlorenceModel:
    """Class to handle model loading, local caching, and inference using Florence-2."""
    
    def __init__(self):
        # Determine device and torch data type based on CUDA availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        print(f"Loading Florence-2 model on {self.device}...")
        
        # Check if the model is already downloaded locally to avoid unnecessary network traffic
        if os.path.exists(MODEL_PATH):
            print(f"Loading model from local path: {MODEL_PATH}")
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH, 
                trust_remote_code=True, 
                torch_dtype=self.torch_dtype,
                attn_implementation="eager"
            ).to(self.device)
            self.processor = AutoProcessor.from_pretrained(
                MODEL_PATH, 
                trust_remote_code=True
            )
        else:
            print(f"Downloading model {MODEL_ID} to local path {MODEL_PATH}...")
            # This handles initial download and model object creation
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID, 
                trust_remote_code=True, 
                torch_dtype=self.torch_dtype,
                attn_implementation="eager"
            ).to(self.device)
            self.processor = AutoProcessor.from_pretrained(
                MODEL_ID, 
                trust_remote_code=True
            )
            # Persist model and processor locally for offline use and faster subsequent startups
            os.makedirs(MODEL_PATH, exist_ok=True)
            self.model.save_pretrained(MODEL_PATH)
            self.processor.save_pretrained(MODEL_PATH)
            print(f"Model saved to {MODEL_PATH}")

    def generate_caption(self, image_path, task_prompt="<DETAILED_CAPTION>", max_new_tokens=1024, num_beams=3):
        """Generates an image description using the provided prompt and generation parameters."""
        image = Image.open(image_path).convert("RGB")
        
        # Pre-process image and prompt into tensors
        inputs = self.processor(text=task_prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)
        
        # Execute model inference
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=max_new_tokens,
            do_sample=False,
            num_beams=num_beams
        )
        
        # Decode and post-process generation results
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        
        parsed_answer = self.processor.post_process_generation(
            generated_text, 
            task=task_prompt, 
            image_size=(image.width, image.height)
        )
        
        return parsed_answer[task_prompt]

if __name__ == "__main__":
    # Small test suite to verify loading and hardware detection
    fm = FlorenceModel()
    print(f"Model successfully initialized on: {fm.device}")
