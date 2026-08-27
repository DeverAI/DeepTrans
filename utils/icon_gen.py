import os
from PIL import Image, ImageDraw, ImageFont

def generate_icon(size=(256, 256), output_path="assets/icon.ico"):
    # Create a new image with transparency
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw a rounded rectangle background (gradient-ish or solid elegant color)
    # DeepSeek Blue-ish/Purple theme
    bg_color = (60, 110, 240, 255)  # Deep Blue
    
    # Draw circle/rounded rect
    margin = 20
    bbox = [margin, margin, size[0] - margin, size[1] - margin]
    draw.ellipse(bbox, fill=bg_color)

    # Draw text "T" or "AI"
    # Try to load a font, fallback to default
    try:
        # Windows usually has arial or segoe ui
        font = ImageFont.truetype("arial.ttf", 120)
    except IOError:
        font = ImageFont.load_default()

    text = "AI"
    text_color = (255, 255, 255, 255)
    
    # Center text
    # textbbox not available in older PIL, using simplistic centering
    # For simplicity in this script, just estimating
    w = 120  # approx
    h = 100
    
    # Modern PIL
    if hasattr(draw, "textbbox"):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        w = right - left
        h = bottom - top
        
    text_x = (size[0] - w) / 2
    text_y = (size[1] - h) / 2 - 20 # slight adjustment
    
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as ICO
    image.save(output_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Icon generated at {output_path}")

if __name__ == "__main__":
    # Adjust path relative to script if run directly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_path = os.path.join(project_root, "assets", "icon.ico")
    generate_icon(output_path=output_path)
