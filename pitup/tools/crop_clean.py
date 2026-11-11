# Sunset/aerial shots with a TikTok badge: zoom slightly, anchored on the side opposite the badge, so the badge leaves
# the frame; whatever thin part of it stays inside the crop is rebuilt with LaMa (a small edge area, invisible).
# usage: crop_clean.py src dst ss dur zoom anchor(TL|TR|BL|BR)
import sys, json, subprocess, numpy as np, onnxruntime as ort, cv2
src, dst, ss, du, zoom, anchor = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
W, H = [int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")]
BW, BH = int(W * 0.27), int(H * 0.108)
cw, ch = int(round(W / zoom)), int(round(H / zoom))
cx0 = 0 if anchor[1] == "L" else W - cw; cy0 = 0 if anchor[0] == "T" else H - ch
sess = ort.InferenceSession("/root/.cache/lama/lama.onnx", providers=["CPUExecutionProvider"])
def find_icon(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    cy = (g > 170) & (b > 170) & (r < 110); rd = (r > 170) & (g < 90) & (b > 60) & (b < 170); best = None
    for side, x0, x1 in (("L", 0, W // 3), ("R", 2 * W // 3, W)):
        c = cy[:, x0:x1]; d = rd[:, x0:x1]
        if (c.sum(1) >= 2).sum() < 6: continue
        for y in range(0, H - 40, 8):
            nc, nd = c[y:y + 40].sum(), d[y:y + 40].sum()
            if nc >= 25 and nd >= 25 and (best is None or nc + nd > best[0]): best = (nc + nd, side, y)
    return best
def lama(img, m):
    ys, xs = np.nonzero(m); cy, cx = int(ys.mean()), int(xs.mean())
    wx = min(max(0, cx - 256), W - 512); wy = min(max(0, cy - 256), H - 512)
    win = img[wy:wy + 512, wx:wx + 512].astype(np.float32) / 255.0; mm = (m[wy:wy + 512, wx:wx + 512] > 0).astype(np.float32)
    o = sess.run(None, {"image": win.transpose(2, 0, 1)[None], "mask": mm[None, None]})[0][0].transpose(1, 2, 0)
    o = o * 255 if o.max() <= 1.5 else o
    a = cv2.GaussianBlur(mm, (9, 9), 0)[..., None]; r = img.astype(np.float32).copy()
    r[wy:wy + 512, wx:wx + 512] = r[wy:wy + 512, wx:wx + 512] * (1 - a) + o * a
    return np.clip(r, 0, 255).astype(np.uint8)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(du), "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", "30", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
                        "-vf", "unsharp=5:5:0.5", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
last, n, inside = None, 0, 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); h = find_icon(a); last = h or last
    if last:
        _, side, y = last; top = max(0, y - 14); m = np.zeros((H, W), np.uint8)
        x0, x1 = (0, BW + 6) if side == "L" else (W - BW - 6, W); m[top:top + BH + 10, x0:x1] = 255
        crop_m = np.zeros_like(m); crop_m[cy0:cy0 + ch, cx0:cx0 + cw] = 1
        mi = m * crop_m
        if mi.any(): a = lama(a, cv2.dilate(mi, np.ones((7, 7), np.uint8))); inside += 1
    c = a[cy0:cy0 + ch, cx0:cx0 + cw]
    enc.stdin.write(cv2.resize(c, (1080, 1920), interpolation=cv2.INTER_LANCZOS4).tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "frames needing a small fill", inside, dst)
