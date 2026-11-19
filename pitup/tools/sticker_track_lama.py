# Sticker removal on a hand-held in-car clip: each sticker (or object) is followed frame to frame by template
# matching on its own texture (chained, local search), then the area is rebuilt with LaMa; a short temporal blend
# on the rebuilt pixels removes flicker.  usage: sticker_track_lama.py in.mp4 out.mp4 masks.json ref t0 t1
import sys, json, subprocess, numpy as np, cv2, onnxruntime as ort
src, dst, mfile, REF, T0, T1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
cap = cv2.VideoCapture(src); FPS = cap.get(5); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
a, b = int(T0 * FPS), int(T1 * FPS); H, W = F[0].shape[:2]
boxes = [p for k in ("glass", "both") for p in json.load(open(mfile))[k]]
boxes = [(min(x for x, y in p), min(y for x, y in p), max(x for x, y in p), max(y for x, y in p)) for p in boxes]
sess = ort.InferenceSession("/root/.cache/lama/lama.onnx", providers=["CPUExecutionProvider"])
gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in F]
pos = {REF: [(x0, y0) for x0, y0, x1, y1 in boxes]}
for order in (range(REF + 1, b), range(REF - 1, a - 1, -1)):
    prev = REF
    for t in order:
        cur = []
        for i, (x0, y0, x1, y1) in enumerate(boxes):
            w, h = x1 - x0, y1 - y0; px, py = pos[prev][i]
            tx0, ty0 = int(np.clip(px, 0, W - w)), int(np.clip(py, 0, H - h))
            tpl = gray[prev][ty0:ty0 + h, tx0:tx0 + w]
            R = 60; sx0, sy0 = max(0, tx0 - R), max(0, ty0 - R); sx1, sy1 = min(W, tx0 + w + R), min(H, ty0 + h + R)
            res = cv2.matchTemplate(gray[t][sy0:sy1, sx0:sx1], tpl, cv2.TM_CCOEFF_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(res)
            cur.append((sx0 + ml[0], sy0 + ml[1]) if mv > 0.35 else (px, py))
        pos[t] = cur; prev = t
def lama(img, mask):
    out = img.copy(); n, lab = cv2.connectedComponents((mask > 0).astype(np.uint8))
    for c in range(1, n):
        yy, xx = np.where(lab == c); cy, cx = (yy.min() + yy.max()) // 2, (xx.min() + xx.max()) // 2
        size = int(min(min(H, W), max(512, (yy.max() - yy.min()) * 2.2, (xx.max() - xx.min()) * 2.2)))
        y0 = int(np.clip(cy - size // 2, 0, H - size)); x0 = int(np.clip(cx - size // 2, 0, W - size))
        win = out[y0:y0 + size, x0:x0 + size]; mw = mask[y0:y0 + size, x0:x0 + size]
        wi = cv2.resize(win, (512, 512), interpolation=cv2.INTER_AREA); mi = cv2.resize(mw, (512, 512), interpolation=cv2.INTER_NEAREST)
        x = (cv2.cvtColor(wi, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        r = sess.run(None, {"image": x, "mask": (mi > 127).astype(np.float32)[None, None]})[0][0].transpose(1, 2, 0)
        if r.max() <= 1.5: r = r * 255
        r = cv2.resize(cv2.cvtColor(np.clip(r, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR), (size, size), interpolation=cv2.INTER_CUBIC)
        soft = cv2.GaussianBlur((cv2.dilate(mw, np.ones((15, 15), np.uint8)) > 0).astype(np.float32), (0, 0), 6)[..., None]
        win[:] = (win.astype(np.float32) * (1 - soft) + r.astype(np.float32) * soft).astype(np.uint8)   # feathered edge: no seam
    return out
outs, masks = [], []
for t in range(a, b):
    m = np.zeros((H, W), np.uint8)
    for (x0, y0, x1, y1), (px, py) in zip(boxes, pos[t]):
        cv2.rectangle(m, (int(px) - 6, int(py) - 6), (int(px) + x1 - x0 + 6, int(py) + y1 - y0 + 6), 255, -1)
    masks.append(m); outs.append(lama(F[t], m))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", dst], stdin=subprocess.PIPE)
for i in range(len(outs)):     # temporal blend of rebuilt pixels with neighbours (aligned by the sticker motion is small)
    nb = [outs[j].astype(np.float32) for j in range(max(0, i - 1), min(len(outs), i + 2))]
    avg = np.mean(nb, axis=0); soft = cv2.GaussianBlur(masks[i].astype(np.float32) / 255, (0, 0), 3)[..., None]
    img = (outs[i].astype(np.float32) * (1 - soft * 0.5) + avg * soft * 0.5).astype(np.uint8)
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait(); print("ok", a, b)
