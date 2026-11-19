# One colour look for every rush (19 Nov.: "le colorbranding doit être identique pour tous les rushs").
# 1) per clip, measure Lab mean / spread on sampled frames; 2) move each clip toward one shared target
#    (neutral white balance, same exposure, same contrast), with clip-level values so nothing flickers;
# 3) apply the same final grade to all (gentle S-curve, slight saturation, very light cool-clean tint).
# usage: match_grade.py in_dir out_dir name1 name2 ...
import sys, subprocess, numpy as np, cv2
src, dst, names = sys.argv[1], sys.argv[2], sys.argv[3:]
def frames(path, step=6):
    c = cv2.VideoCapture(path); i = 0; out = []
    while True:
        ok, f = c.read()
        if not ok: break
        if i % step == 0: out.append(cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)[::7])
        i += 1
    return np.concatenate(out)
stats = {}
for n in names:
    x = frames(f"{src}/{n}.mp4"); stats[n] = (x.mean(0), x.std(0)); print(n, np.round(stats[n][0]), np.round(stats[n][1]))
Lm = np.mean([s[0][0] for s in stats.values()]); Ls = np.mean([s[1][0] for s in stats.values()])
T_MEAN = np.array([max(Lm, 132.0), 128.0, 127.0]); T_STD_L = max(Ls, 52.0)      # neutral, slightly cool, never darker than the set
curve = np.arange(256) / 255.0
lut = np.clip(255 * (curve + 0.06 * (curve - 0.5) * (1 - abs(2 * curve - 1))), 0, 255).astype(np.uint8)   # gentle S-curve
for n in names:
    m, s = stats[n]; k = 0.8                          # 80 % of the way to the target: consistent but still natural
    gain_L = 1 + k * (T_STD_L / max(s[0], 1) - 1); off = m + k * (T_MEAN - m)
    c = cv2.VideoCapture(f"{src}/{n}.mp4"); fps = c.get(5); w, h = int(c.get(3)), int(c.get(4))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", f"{dst}/{n}.mp4"], stdin=subprocess.PIPE)
    while True:
        ok, f = c.read()
        if not ok: break
        lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[..., 0] = (lab[..., 0] - m[0]) * gain_L + off[0]
        lab[..., 1] = (lab[..., 1] - m[1]) * 1.06 + off[1]          # same slight saturation lift for all
        lab[..., 2] = (lab[..., 2] - m[2]) * 1.06 + off[2]
        out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
        enc.stdin.write(cv2.LUT(out, lut).tobytes())
    enc.stdin.close(); enc.wait(); print("ok", n)
