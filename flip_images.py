import os
from PIL import Image

def flip_images(input_folder, output_folder):
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
