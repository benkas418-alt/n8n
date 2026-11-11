# After a build: every clip shorter than the time it stays on screen is slowed down to fill it (never frozen or black).
import re, sys, subprocess, json
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/{sys.argv[1]}"; html = open(f"{P}/index.html").read(); need = {}
for m in re.finditer(r'<video[^>]*src="assets/v/([^"]+)\.mp4"[^>]*data-duration="([0-9.]+)"', html):
    need[m.group(1)] = max(need.get(m.group(1), 0), float(m.group(2)))
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
for n, d in sorted(need.items()):
    src = f"{SP}/story/v/{n}.mp4"; have = dur(src); k = (d + 0.15) / have
    if k <= 1.0: continue
    if k > 1.8: print("TOO SHORT", n, round(have, 2), "for", round(d, 2)); continue
    # repeated frames keep every image sharp (blending would smear handheld shots)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"setpts={k:.4f}*PTS,fps=30", "-an", "-c:v", "libx264", "-crf", "14", f"{P}/assets/v/{n}.mp4"], check=True)
    print("slowed", n, f"x{k:.2f}", round(have, 2), "->", round(d, 2))
