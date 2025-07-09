import os
import re
from PIL import Image

# 🔧 Set input and output paths
input_folder = r"D:\Personal\AI\Pillow\Flipped"
output_pdf = r"D:\Personal\AI\Pillow\PDF_output\combined_output.pdf"

# Natural sort key to sort like slide1, slide2, ..., slide10
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# Get all JPG/JPEG images sorted naturally
image_files = sorted([
    f for f in os.listdir(input_folder)
    if f.lower().endswith(('.jpg', '.jpeg'))
], key=natural_sort_key)

# Ensure images are found
if not image_files:
    print("❌ No JPG images found in the folder.")
    exit()

# Load and convert images
image_list = []
for filename in image_files:
    path = os.path.join(input_folder, filename)
    img = Image.open(path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    image_list.append(img)

# Save all images into one PDF
first_image = image_list.pop(0)
first_image.save(output_pdf, save_all=True, append_images=image_list)

print(f"✅ PDF created successfully: {output_pdf}")
