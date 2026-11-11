# Removes TikTok badges by rebuilding the hidden area from REAL pixels of neighbouring frames:
# the camera moves, so what the badge hides at frame t is visible at t±k. For each frame, a local homography is fitted
# on the optical flow in a ring around the badge, the neighbour frame is warped onto t, colour-matched on the ring,
# and pasted where it is clean. LaMa only fills what no neighbour ever showed.
# usage: tiktok_fill.py src dst ss dur [extra_boxes_json]
import sys, json, subprocess, numpy as np, cv2
src, dst, ss, du = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
extra = json.loads(sys.argv[5]) if len(sys.argv) > 5 else []
W, H = [int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")]
BW, BH, PAD = int(W * 0.27), int(H * 0.108), 6.0     # badge box; PAD seconds of extra source frames on each side

def frames(t0, t1):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(max(0, t0)), "-t", str(t1 - max(0, t0)), "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", "30", "-"], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, H, W, 3)
t0 = max(0.0, ss - PAD); F = frames(t0, ss + du + PAD); off = int(round((ss - t0) * 30)); N = int(round(du * 30))

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
# badge position per frame (kept where it was last seen, and back-filled before the first sighting)
pos, last = [], None
for a in F:
    h = find_icon(a); last = h if h else last; pos.append(last)
first = next((p for p in pos if p), None); pos = [p or first for p in pos]
def mask_of(i):
    m = np.zeros((H, W), np.uint8)
    if pos[i]:
        _, side, y = pos[i]; top = max(0, y - 10)
        if side == "L": m[top:top + BH, 0:BW] = 255
        else: m[top:top + BH, W - BW:W] = 255
    for a, b, c, e in extra: m[b:e, a:c] = 255
    return m
M = [mask_of(i) for i in range(len(F))]
G = [cv2.cvtColor(a, cv2.COLOR_RGB2GRAY) for a in F]
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
K5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
# shots: sources must come from the same continuous shot
dif = [0.0] + [float(np.abs(cv2.resize(G[i], (72, 128)).astype(np.float32) - cv2.resize(G[i - 1], (72, 128)).astype(np.float32)).mean()) for i in range(1, len(G))]
thr = max(18.0, 4 * float(np.median(dif))); shot = np.cumsum([1 if d > thr else 0 for d in dif])
# consecutive full-frame homographies (frame i -> i+1), badges excluded, chained for far-away sources
rng = np.random.default_rng(0); HC = []
for i in range(len(G) - 1):
    fl = dis.calc(G[i], G[i + 1], None); ok = (M[i] == 0) & (M[i + 1] == 0); ys, xs = np.nonzero(ok)
    sel = rng.choice(len(xs), min(4000, len(xs)), replace=False); p0 = np.stack([xs[sel], ys[sel]], 1).astype(np.float32)
    Hm, _ = cv2.findHomography(p0, p0 + fl[ys[sel], xs[sel]], cv2.RANSAC, 1.0); HC.append(Hm if Hm is not None else np.eye(3))
def chain(t, s):                     # maps points of frame t to frame s
    Hm = np.eye(3)
    if s > t:
        for i in range(t, s): Hm = HC[i] @ Hm
    else:
        for i in range(t - 1, s - 1, -1): Hm = np.linalg.inv(HC[i]) @ Hm
    return Hm
import onnxruntime as ort
LAMA = ort.InferenceSession("/root/.cache/lama/lama.onnx", providers=["CPUExecutionProvider"])
def lama(img, m):
    ys, xs = np.nonzero(m); cy, cx = int(ys.mean()), int(xs.mean())
    wx = min(max(0, cx - 256), W - 512); wy = min(max(0, cy - 256), H - 512)
    win = img[wy:wy + 512, wx:wx + 512].astype(np.float32) / 255.0; mm = (m[wy:wy + 512, wx:wx + 512] > 0).astype(np.float32)
    o = LAMA.run(None, {"image": win.transpose(2, 0, 1)[None], "mask": mm[None, None]})[0][0].transpose(1, 2, 0)
    o = o * 255 if o.max() <= 1.5 else o; r = img.copy(); r[wy:wy + 512, wx:wx + 512][mm > 0] = o[mm > 0]; return r

def fill_frame(t):
    mt = M[t]; hole = cv2.dilate(mt, K5, iterations=1) > 0
    ring = (cv2.dilate(mt, np.ones((121, 121), np.uint8)) > 0) & ~(cv2.dilate(mt, np.ones((17, 17), np.uint8)) > 0)
    out = F[t].astype(np.float32).copy(); todo = hole.copy()
    cands = sorted([s for s in range(len(F)) if s != t and shot[s] == shot[t]], key=lambda s: abs(s - t))
    tried = 0
    for s in cands:
        if not todo.any(): break
        if abs(s - t) > 3 and (abs(s - t) % 3): continue          # every 3rd frame further away is enough
        Hc = chain(t, s)
        # quick check: does this source uncover anything still to do?
        wm = cv2.warpPerspective(M[s], Hc, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
        ok = todo & (cv2.dilate(wm, K5, iterations=2) == 0)
        if ok.sum() < 20: continue
        warped = cv2.warpPerspective(F[s], Hc, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        # residual local correction on the ring (parallax, chaining drift)
        gw = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY); fl = dis.calc(G[t], gw, None)
        rs = ring & (wm == 0); ys, xs = np.nonzero(rs)
        if len(xs) > 200:
            sel = np.random.default_rng(t * 1000 + s).choice(len(xs), min(3000, len(xs)), replace=False)
            p0 = np.stack([xs[sel], ys[sel]], 1).astype(np.float32); Hr, inl = cv2.findHomography(p0, p0 + fl[ys[sel], xs[sel]], cv2.RANSAC, 1.0)
            if Hr is not None and inl.mean() > 0.6:
                Hc2 = Hr @ Hc if False else None
                warped = cv2.warpPerspective(warped, Hr, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
                wm = cv2.warpPerspective(wm, Hr, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
                ok = todo & (cv2.dilate(wm, K5, iterations=2) == 0)
        warped = warped.astype(np.float32); rr = ring & (wm == 0)
        if rr.sum() > 100:
            g = (out[rr].mean(0) + 1) / (warped[rr].mean(0) + 1); warped *= np.clip(g, 0.85, 1.15)
        out[ok] = warped[ok]; todo &= ~ok; tried += 1
    left = int(todo.sum())
    if left: out = lama(np.clip(out, 0, 255).astype(np.uint8), cv2.dilate(todo.astype(np.uint8), K5, iterations=1)).astype(np.float32)
    alpha = cv2.GaussianBlur(hole.astype(np.float32), (7, 7), 0); alpha[mt > 0] = 1.0
    res = F[t].astype(np.float32) * (1 - alpha[..., None]) + out * alpha[..., None]
    return np.clip(res, 0, 255).astype(np.uint8), left, int(hole.sum())

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
log = []
prev = None
for t in range(off, off + N):
    img, left, tot = fill_frame(t)
    # temporal smoothing inside the rebuilt area only: blend with the previous output, motion-compensated
    if prev is not None:
        hole = cv2.dilate(M[t], K5, iterations=1) > 0
        pw = cv2.warpPerspective(prev, HC[t - 1], (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        a_ = cv2.GaussianBlur(hole.astype(np.float32), (7, 7), 0)[..., None] * 0.45
        img = np.clip(img.astype(np.float32) * (1 - a_) + pw.astype(np.float32) * a_, 0, 255).astype(np.uint8)
    prev = img
    enc.stdin.write(img.tobytes()); log.append((t - off, pos[t][1] if pos[t] else None, left, tot))
enc.stdin.close(); enc.wait()
json.dump(log, open(dst + ".log.json", "w"))
print("frames", N, "unfilled px (mean)", round(float(np.mean([l[2] for l in log])), 1), "of", round(float(np.mean([l[3] for l in log]))), dst)
