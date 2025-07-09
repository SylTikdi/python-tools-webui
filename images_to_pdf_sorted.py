import os
import re
from PIL import Image

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def images_to_pdf(input_folder, output_pdf_path):
    # Get all JPG/JPEG images sorted naturally
    image_files = sorted([
        f for f in os.listdir(input_folder)
        if f.lower().endswith(('.jpg', '.jpeg'))
    ], key=natural_sort_key)

    # Ensure images are found
    if not image_files:
        return None

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
    first_image.save(output_pdf_path, save_all=True, append_images=image_list)

    return output_pdf_path
