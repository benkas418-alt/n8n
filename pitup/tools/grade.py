# Uniform colour grade (method of the colour-grading repos the founder gave): measure each clip, correct it toward
# common targets (neutral white balance, median luminance ~0.45, black/white points), then apply one shared look.
# The correction is baked into a 33^3 .cube LUT per clip (one fit per clip: no flicker) and applied with ffmpeg lut3d.
# usage: grade.py in.mp4 out.mp4
import sys, subprocess, numpy as np
src, dst = sys.argv[1], sys.argv[2]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
fr = []
for k in range(8):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(dur * (k + 0.5) / 8), "-i", src, "-frames:v", "1", "-vf", "scale=270:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    if b: fr.append(np.frombuffer(b, np.uint8).astype(np.float32) / 255)
x = np.concatenate(fr).reshape(-1, 3)
# white balance: shades of gray (Minkowski p=6), applied at 70 % so the light keeps some warmth
g = (x ** 6).mean(0) ** (1 / 6); gains = g.mean() / g; gains = 1 + 0.7 * (gains - 1)
y = np.clip(x * gains, 0, 1); lum = y @ [0.2126, 0.7152, 0.0722]
lo, hi, med = np.percentile(lum, 1.5), np.percentile(lum, 99.2), np.median(lum)
def levels(v): return np.clip((v - lo) / max(1e-3, hi - lo) * 0.95 + 0.02, 0, 1)
m2 = levels(med); gamma = np.log(0.45) / np.log(max(1e-3, min(0.95, m2))); gamma = float(np.clip(gamma, 0.75, 1.35))
def look(rgb):
    v = levels(np.clip(rgb * gains, 0, 1)) ** gamma
    v = v + 0.06 * np.sin(np.pi * (v - 0.5)) * (1 - np.abs(2 * v - 1))          # gentle S-curve
    l = (v @ [0.2126, 0.7152, 0.0722])[..., None]
    v = l + (v - l) * 1.10                                                         # shared saturation
    v = v * [1.025, 1.0, 0.965]                                                    # shared sunny warmth
    return np.clip(v, 0, 1)
N = 33; r = np.linspace(0, 1, N); B, G, R = np.meshgrid(r, r, r, indexing="ij")
out = look(np.stack([R, G, B], -1).reshape(-1, 3))
cube = dst + ".cube"
with open(cube, "w") as f:
    f.write(f"LUT_3D_SIZE {N}\n"); f.writelines(f"{a:.6f} {b_:.6f} {c:.6f}\n" for a, b_, c in out)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"lut3d='{cube}':interp=tetrahedral", "-an", "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", dst], check=True)
print(f"{src.split('/')[-1]}: gains {np.round(gains, 3)} levels {lo:.2f}-{hi:.2f} gamma {gamma:.2f}")
