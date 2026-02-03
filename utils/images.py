# utils/images.py

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_image_from_prompt(prompt: str, topic: str) -> str:
    """Generate a simple placeholder image locally instead of downloading."""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    img_path = outputs_dir / f"{topic.replace(' ', '_')}_{hash(prompt)}.png"

    # Simple placeholder image with prompt text
    img = Image.new("RGB", (600, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    d.text((10, 180), prompt, fill=(0, 0, 0), font=font)
    img.save(img_path)
    return str(img_path)


#🤖 AI agents are building your teaching resources...

#st.set_page_config(page_title="Intelligent Teaching Assistant", layout="wide")