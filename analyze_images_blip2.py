import os
import replicate
import pandas as pd
from PIL import Image
from colorthief import ColorThief
from pathlib import Path
from dotenv import load_dotenv

# Load API key
load_dotenv()
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def analyze_image_colors(image_path):
    color_thief = ColorThief(image_path)
    dominant = rgb_to_hex(color_thief.get_color(quality=1))
    palette = [rgb_to_hex(c) for c in color_thief.get_palette(color_count=5)]
    return dominant, palette

def generate_caption_blip2(image_path):
    try:
        output = replicate_client.run(
            "salesforce/blip",
            input={"image": open(image_path, "rb")}
        )
        return output
    except Exception as e:
        print(f"Replicate error for {image_path}: {e}")
        return "Error generating caption"

def process_images(folder_path="images", output_csv="image_analysis_blip2.csv"):
    folder = Path(folder_path)
    results = []

    for img_path in folder.glob("*.*"):
        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            print(f"Processing: {img_path.name}")
            try:
                mean_color, color_list = analyze_image_colors(str(img_path))
                caption = generate_caption_blip2(str(img_path))
                result = {
                    "file_name": img_path.name,
                    "Mean_color": mean_color,
                    "Color_list": ", ".join(color_list),
                    "Description": caption
                }
                results.append(result)
            except Exception as e:
                print(f"Error with image {img_path.name}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ Analysis saved to: {output_csv}")

if __name__ == "__main__":
    process_images()
