# Smooth scroll videos of the real pi-tup.com pages, panned with sub-pixel precision from one tall capture (no jitter).
import subprocess, sys
from PIL import Image
def ease(u): return u * u * (3 - 2 * u)
def pan(out, head, body, foot, W, H, y0, y1, secs, fps=30):
    vh = H - head.height - (foot.height if foot else 0)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(secs * fps)
    for i in range(n):
        y = y0 + (y1 - y0) * ease(i / (n - 1))
        fr = Image.new("RGB", (W, H), "white")
        fr.paste(body.resize((W, vh), Image.LANCZOS, box=(0, y, body.width, y + vh * body.width / W)), (0, head.height))
        fr.paste(head, (0, 0))
        if foot: fr.paste(foot, (0, H - foot.height))
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print(out)
R = "real"; V = sys.argv[1]
mv, mt = Image.open(f"{R}/m_view.png").convert("RGB"), Image.open(f"{R}/m_tall.png").convert("RGB")
head, foot = mv.crop((0, 0, 780, 112)), mv.crop((0, 1688 - 130, 780, 1688))
body = mt.crop((0, 112, 780, mt.height - 130))
for name, a, b, s in [("phs_a", 0, 900, 2.4), ("phs_b", 900, 1700, 1.6), ("phs_c", 1700, 2800, 2.4), ("phs_full", 0, 3000, 5.0)]:
    pan(f"{V}/{name}.mp4", head, body, foot, 780, 1688, a, b, s)
d = Image.open(f"{R}/site_desk_market.png").convert("RGB"); k = 1832 / d.width
dh = d.crop((0, 0, d.width, 96)).resize((1832, int(96 * k)), Image.LANCZOS)
db = d.crop((0, 96, d.width, d.height))
pan(f"{V}/lapscroll.mp4", dh, db, None, 1832, 1136, 0, 2600, 5.0)
