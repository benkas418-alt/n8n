# Copies the classy product photos into story/img as card images, with crops that drop sizes, logos and phone numbers.
import sys, os
from PIL import Image
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
src = sys.argv[1] if len(sys.argv) > 1 else "hd"
CROP = {"555_0": (0, 0, 0.58, 0.86), "709_0": (0.15, 0.23, 1.0, 1.0)}   # fractions of width/height
for k in "708_2 452_0 555_0 737_3 735_0 648_1 709_0 679_0 783_3 737_1 681_1 235_0".split():
    p = f"{SP}/prod/classe/{src}/{k}.jpg"
    if not os.path.exists(p): p = f"{SP}/prod/classe/hd/{k}.jpg"
    im = Image.open(p).convert("RGB"); W, H = im.size
    if k in CROP: x0, y0, x1, y1 = CROP[k]; im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    im.save(f"{SP}/story/img/c_{k}.jpg", quality=93); print(k, p.split("/")[-2], im.size)
