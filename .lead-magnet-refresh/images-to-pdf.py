import os
import sys
from PIL import Image

input_dir, output_pdf = sys.argv[1], sys.argv[2]
files = []
for name in os.listdir(input_dir):
    if name.endswith(".png") and name.startswith("slide-"):
        stem = name[len("slide-"):-4]
        if stem.isdigit(): files.append((int(stem), os.path.join(input_dir, name)))
files.sort()
if not files: raise SystemExit(f"No slide PNGs found in {input_dir}")
images = [Image.open(path).convert("RGB") for _, path in files]
images[0].save(output_pdf, "PDF", resolution=144.0, save_all=True, append_images=images[1:])
print({"pages":len(images),"output":output_pdf})
