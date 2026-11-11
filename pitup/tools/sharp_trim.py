# Keeps only the longest sharp stretch of each clip (drops crossfades and blurry frames). Originals go to story/v/_orig.
import cv2, numpy as np, subprocess, sys, os, shutil
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"; V = f"{SP}/story/v"
os.makedirs(f"{V}/_orig", exist_ok=True)
for name in sys.argv[1:]:
    src = f"{V}/_orig/{name}.mp4"
    if not os.path.exists(src): shutil.copy(f"{V}/{name}.mp4", src)
    c = cv2.VideoCapture(src); fps = c.get(5) or 30; s = []
    while True:
        ok, x = c.read()
        if not ok: break
        g = cv2.cvtColor(x, cv2.COLOR_BGR2GRAY); g = cv2.resize(g, (540, int(540 * g.shape[0] / g.shape[1]))); s.append(cv2.Laplacian(g, cv2.CV_64F).var())
    s = np.array(s); thr = 0.6 * np.median(s); ok = s >= thr; best, run, st = (0, 0), 0, 0
    for i, v in enumerate(ok):
        run = run + 1 if v else 0
        if run > best[0]: best = (run, i - run + 1)
    a, n = best[1], best[0]
    if n == len(s): print(name, "already sharp", len(s)); continue
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a / fps:.3f}", "-t", f"{n / fps:.3f}", "-i", src, "-c:v", "libx264", "-crf", "14", "-an", f"{V}/{name}.mp4"], check=True)
    print(name, f"kept {a / fps:.2f}s..{(a + n) / fps:.2f}s of {len(s) / fps:.2f}s")
