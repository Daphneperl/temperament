import os
import pandas as pd
from PIL import Image
from colorthief import ColorThief
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def analyze_image_colors(image_path):
    color_thief = ColorThief(image_path)
    dominant = rgb_to_hex(color_thief.get_color(quality=1))
    palette = [rgb_to_hex(c) for c in color_thief.get_palette(color_count=5)]
    return dominant, palette

def generate_ai_tags(file_name, mean_color, color_list):
    prompt = f"""
You are an art critic AI. Given an image with the following visual details:

- File name: {file_name}
- Mean color: {mean_color}
- Color palette: {color_list}

Generate the following information:
theme:
Art_medium:
vibe:
Description:
6_key_words:
Composition:
Atmosphere:
"""

    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        response = res.choices[0].message.content
        parts = {}
        for line in response.splitlines():
            if ':' in line:
                key, val = line.split(':', 1)
                parts[key.strip()] = val.strip()
        return parts
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {}

def process_images(folder_path="images", output_csv="image_analysis_ai.csv"):
    folder = Path(folder_path)
    results = []

    for img_path in folder.glob("*.*"):
        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            print(f"Processing: {img_path.name}")
            try:
                mean_color, color_list = analyze_image_colors(str(img_path))
                ai_data = generate_ai_tags(img_path.name, mean_color, color_list)
                result = {
                    "file_name": img_path.name,
                    "Mean_color": mean_color,
                    "Color_list": ", ".join(color_list),
                    **ai_data
                }
                results.append(result)
            except Exception as e:
                print(f"Error with image {img_path.name}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ Analysis saved to: {output_csv}")

if __name__ == "__main__":
    process_images()
