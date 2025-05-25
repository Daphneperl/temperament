import os
import json

# Folder where your images are
IMAGE_DIR = "images"

# File to write the list
OUTPUT_JSON = os.path.join(IMAGE_DIR, "images.json")

# Collect image filenames
image_files = [
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
]

# Save to JSON
with open(OUTPUT_JSON, 'w') as f:
    json.dump(image_files, f, indent=2)

print(f"✅ Saved {len(image_files)} image names to {OUTPUT_JSON}")
