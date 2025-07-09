import os
from PIL import Image

# 🔧 Manually set your input and output folders here:
input_folder = r"D:\Personal\AI\Pillow\JPEG"
output_folder = r"D:\Personal\AI\Pillow\Flipped"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Flip each JPG/JPEG image
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.jpg', '.jpeg')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with Image.open(input_path) as img:
            flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
            flipped.save(output_path, format='JPEG')

print(f"✅ All JPG images flipped and saved to: {output_folder}")
