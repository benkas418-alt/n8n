"""Remove a flat screen colour from a video and write a WebP frame sequence.

Usage: python3 key.py <video> <out_dir> <green|orange>
"""
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image

src, out, mode = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
out.mkdir(parents=True, exist_ok=True)

probe = subprocess.run(
    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
     '-of', 'csv=p=0', src], capture_output=True, text=True, check=True).stdout.strip().split(',')
w, h = int(probe[0]), int(probe[1])
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'fps=30', '-f', 'rawvideo',
                      '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.float32)

for i, f in enumerate(frames):
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    if mode == 'green':
        # Green dominance works on grey manga art, where a chroma distance key fails.
        spill = g - np.maximum(r, b)
        alpha = 1 - np.clip((spill - 25) / 45, 0, 1)
        g = np.minimum(g, np.maximum(r, b) + 4)
    else:
        key = np.array([248, 178, 67], np.float32)
        dist = np.sqrt(((f - key) ** 2).sum(-1))
        alpha = np.clip((dist - 40) / 50, 0, 1)
    rgba = np.dstack([r, g, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(rgba, 'RGBA')
    img = img.resize((round(w * 900 / h), 900), Image.LANCZOS)
    img.save(out / f'{i + 1:03d}.webp', quality=88, method=4)
print(out.name, len(frames))
