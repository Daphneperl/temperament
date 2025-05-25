import os
import replicate
import pandas as pd
from PIL import Image
from colorthief import ColorThief
from pathlib import Path
from dotenv import load_dotenv

# Load and verify .env
load_dotenv()
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    print("❌ REPLICATE_API_TOKEN not found. Make sure your .env file exists and is named correctly (no .txt) and contains:")
    print("REPLICATE_API_TOKEN=your_actual_token")
    exit()

# Initialize Replicate client
replicate_client = replicate.Client(api_token=token)

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def analyze_image_colors(image_path):
    try:
        color_thief = ColorThief(image_path)
        dominant = rgb_to_hex(color_thief.get_color(quality=1))
        palette = [rgb_to_hex(c) for c in color_thief.get_palette(color_count=5)]
        return dominant, palette
    except Exception as e:
        print(f"⚠️ Color analysis failed for {image_path}: {e}")
        return "N/A", []

def generate_caption_llava(image_path):
    try:
        with open(image_path, "rb") as img_file:
            output = replicate_client.run(
                "haotian-liu/llava-13b",
                input={
                    "image": img_file,
                    "prompt": "Describe this image like an art critic. Focus on color, composition, emotion, and materiality. Be poetic."
                }
            )
        return output
    except Exception as e:
        print(f"⚠️ Replicate error for {image_path}: {e}")
        return "Error generating caption"

def process_images(folder_path="images", output_csv="image_analysis_llava.csv"):
    folder = Path(folder_path)
    results = []

    image_files = list(folder.glob("*.*"))
    print(f"🔍 Found {len(image_files)} files in folder '{folder_path}'")

    for img_path in image_files:
        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            print(f"🖼️ Processing: {img_path.name}")
            try:
                mean_color, color_list = analyze_image_colors(str(img_path))
                caption = generate_caption_llava(str(img_path))
                result = {
                    "file_name": img_path.name,
                    "Mean_color": mean_color,
                    "Color_list": ", ".join(color_list),
                    "Description": caption
                }
                results.append(result)
                print("✅ Added to results\n")
            except Exception as e:
                print(f"❌ Failed on {img_path.name}: {e}")
        else:
            print(f"⏭️ Skipped unsupported file: {img_path.name}")

    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False)
        print(f"📄 CSV saved to: {output_csv}")
    else:
        print("⚠️ No valid results to save. CSV was not created.")

if __name__ == "__main__":
    process_images()
