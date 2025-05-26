import os
from PIL import Image

# Configure your paths
# input_root = r"C:\Path\To\Input\Images"
# output_root = r"C:\Path\To\Resized\Images"

input_root = r"C:\DOCS\kodachromes\RAJ"
output_root = r"C:\DOCS\kodachromes\RAJ"


# resize_size = (1024, 1024)  # Width x Height
resize_size = (300, 300)  # Width x Height

# Image extensions to process
valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

def resize_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            img.thumbnail(resize_size, Image.LANCZOS)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, optimize=True, quality=75)
            print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Failed: {input_path} ({e})")

for root, _, files in os.walk(input_root):
    for file in files:
        if file.lower().endswith(valid_extensions):
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(input_path, input_root)
            base, ext = os.path.splitext(relative_path)

            # Add _thumb suffix before the extension
            new_filename = base + "_thumb" + ext
            output_path = os.path.join(output_root, new_filename)

            resize_image(input_path, output_path)
