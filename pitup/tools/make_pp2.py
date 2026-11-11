# Phone clips from fresh pi-tup.com mobile captures: blue price text found and erased, then a slow push-in.
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw
W, H = 780, 1688
def ease(u): return u * u * (3 - 2 * u)
def clean(png):
    im = Image.open(png).convert('RGB'); a = np.asarray(im).astype(int)
    blue = (a[..., 2] > 170) & (a[..., 0] < 100) & (a[..., 1] > 50) & (a[..., 1] < 150)
    blue[:900] = False; blue[1395:] = False                 # info card only, never the sticky buy bar
    rows = np.where(blue.sum(1) > 3)[0]; dr = ImageDraw.Draw(im); grp = []
    for r in rows:
        if grp and r - grp[-1][1] <= 4: grp[-1][1] = r
        else: grp.append([r, r])
    for y0, y1 in grp:
        if 20 <= y1 - y0 <= 90:                              # a line of big blue text = the price
            xs = np.where(blue[y0:y1 + 1].any(0))[0]; dr.rectangle((30, y0 - 8, min(560, xs.max() + 12), y1 + 8), fill='white')
    low = np.where(blue[1290:1395].sum(1) > 3)[0]           # price row half hidden under the buy bar
    if len(low): dr.rectangle((30, 1290 + low[0] - 8, 742, 1394), fill='white')
    return im
def clip(png, out, secs=4.0, fps=30, z=0.07):
    im = clean(png); p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "30", out], stdin=subprocess.PIPE)
    for k in range(int(secs * fps)):
        s = 1 + z * ease(k / (secs * fps - 1)); w, h = int(W / s), int(H / s); x = (W - w) // 2; y = int((H - h) * 0.3)
        p.stdin.write(im.crop((x, y, x + w, y + h)).resize((W, H), Image.LANCZOS).tobytes())
    p.stdin.close(); p.wait(); im.save(out.replace('.mp4', '_chk.png')); print(out)
for arg in sys.argv[1:]:
    src, out = arg.split('='); clip(src, out)
