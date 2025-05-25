import os
import json
import torch
import open_clip
import random
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

IMAGE_DIR = "images"
OUTPUT_JSON = "temperament_scores.json"

# Load model and tokenizer
device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
tokenizer = open_clip.get_tokenizer("ViT-B-32")

# Define comparison prompts
prompts = [
    "chaotic energetic sharp angles straight warm hot ",
    "calm quiet chill relaxed soft cool curved  gentle"
]
text_tokens = tokenizer(prompts).to(device)

with torch.no_grad():
    text_features = model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

# Get similarity to "chaotic" prompt
def get_temperament_score(image_path):
    try:
        image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            similarity = (image_features @ text_features.T)[0][0].item()  # similarity to "chaotic"
            return similarity
    except Exception as e:
        print(f"⚠️ Failed: {image_path} - {e}")
        return float("-inf")

def main():
    filenames = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    scores = []

    for filename in tqdm(filenames):
        score = get_temperament_score(os.path.join(IMAGE_DIR, filename))
        scores.append((filename, score))

    # Sort by score ascending (lowest = 1)
    scores.sort(key=lambda x: x[1])

    # Create ranked + randomized output
    ranked = {
        filename: {
            "temperament_score": rank + 1,
            "intimacy_score": random.randint(1, 10)
        }
        for rank, (filename, _) in enumerate(scores)
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(ranked, f, indent=2)

    print(f"✅ Done. Unique scores + intimacy saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
