"""Cut a product render out of a light studio background.

Pixels lighter than the threshold that connect to the seed points become
transparent. Their darkness is kept as a black soft shadow.

Usage: python3 cutout.py <src> <out.png> <crop x0,y0,x1,y1> <threshold> [seed x,y ...]
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, dst, crop, thr = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
seeds = [tuple(map(int, s.split(','))) for s in sys.argv[5:]]

img = Image.open(src).convert('RGB').crop(tuple(map(int, crop.split(','))))
arr = np.asarray(img).astype(np.float32)
lum = arr.mean(-1)

light = Image.fromarray(((lum > thr) * 255).astype(np.uint8)).copy()
w, h = light.size
for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), *seeds]:
    # A seed on a dark pixel would fill the product itself.
    if light.getpixel((x, y)) == 255:
        ImageDraw.floodfill(light, (x, y), 128)
    else:
        print('skip dark seed', x, y)
bg = np.asarray(light) == 128
bg = np.asarray(Image.fromarray(bg.astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(1.2))) / 255

# The background turns into a black shadow whose opacity follows how dark it was.
paper = np.percentile(lum[bg > 0.99], 95)
shadow = np.clip((paper - lum) / paper * 2.2, 0, 0.75)
alpha = (1 - bg) + bg * shadow
rgb = arr * (1 - bg[..., None])
out = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(dst)
print(dst, img.size)
