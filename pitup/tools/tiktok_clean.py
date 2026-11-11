# Removes the TikTok badge (icon + "TikTok" + @handle) frame by frame and rebuilds the area with LaMa.
# The icon is found by its cyan + red fringes; left badges are left-aligned, right badges right-aligned.
import sys, json, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageDraw, ImageFilter
src, dst, ss, du = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
extra = json.loads(sys.argv[5]) if len(sys.argv) > 5 else []          # fixed boxes, e.g. a burned-in signature
W, H = [int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")]
sess = ort.InferenceSession("/root/.cache/lama/lama.onnx", providers=["CPUExecutionProvider"])
BW, BH = int(W * 0.27), int(H * 0.108)                              # badge box size (icon + two text lines)
def find_icon(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    cy = (g > 170) & (b > 170) & (r < 110); rd = (r > 170) & (g < 90) & (b > 60) & (b < 170)
    best = None
    for side, x0, x1 in (("L", 0, W // 3), ("R", 2 * W // 3, W)):
        c = cy[:, x0:x1]; d = rd[:, x0:x1]
        rows = np.where(c.sum(1) >= 2)[0]
        if len(rows) < 6: continue
        for y in range(0, H - 40, 8):                                # icon = cyan and red together in a 40 px band
            nc, nd = c[y:y + 40].sum(), d[y:y + 40].sum()
            if nc >= 25 and nd >= 25 and (best is None or nc + nd > best[0]): best = (nc + nd, side, y)
    return best
def inpaint(img, boxes):
    for (a, b, c, e) in boxes:
        a, b, c, e = max(0, a), max(0, b), min(W, c), min(H, e)
        wx = min(max(0, (a + c) // 2 - 256), W - 512); wy = min(max(0, (b + e) // 2 - 256), H - 512)
        win = img.crop((wx, wy, wx + 512, wy + 512)); m = Image.new("L", (512, 512), 0)
        ImageDraw.Draw(m).rectangle((a - wx, b - wy, c - wx, e - wy), fill=255)
        x = (np.asarray(win, dtype=np.float32) / 255.0).transpose(2, 0, 1)[None]
        out = sess.run(None, {"image": x, "mask": (np.asarray(m) > 127).astype(np.float32)[None, None]})[0][0].transpose(1, 2, 0)
        if out.max() <= 1.5: out = out * 255
        rec = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        win.paste(rec, (0, 0), m.filter(ImageFilter.GaussianBlur(4))); img.paste(win, (wx, wy))
    return img
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(du), "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "30", dst], stdin=subprocess.PIPE)
n, last, log = 0, None, []
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    a = np.frombuffer(buf, np.uint8).reshape(H, W, 3); hit = find_icon(a)
    if hit: last = hit
    boxes = [tuple(e) for e in extra]
    if last:                                                      # keep masking where the badge was seen last
        _, side, y = last; top = y - 10
        boxes.append((0, top, BW, top + BH) if side == "L" else (W - BW, top, W, top + BH))
    img = inpaint(Image.fromarray(a.copy()), boxes); enc.stdin.write(img.tobytes())
    log.append((n, last[1] if last else None, last[2] if last else None)); n += 1
enc.stdin.close(); enc.wait(); json.dump(log, open(dst + ".log.json", "w")); print("frames", n, dst)
