# Removes the DJEUDY watermark (signature + Instagram badge, top-right or bottom-left) from every frame of the
# 720x1280 source: only the bright watermark pixels inside the known zones are masked, then LaMa redraws them.
import sys, os, glob, subprocess, shutil, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
sess = ort.InferenceSession("/root/.cache/lama/lama.onnx", providers=["CPUExecutionProvider"])
ZONES = [((208, 0), [(550, 82, 690, 136), (617, 296, 674, 354), (532, 364, 674, 402)]),   # window origin, rects
         ((0, 700), [(80, 838, 215, 940)])]
def run(win, mask):
    x = (np.asarray(win, dtype=np.float32) / 255.0).transpose(2, 0, 1)[None]
    out = sess.run(None, {"image": x, "mask": mask[None, None].astype(np.float32)})[0][0].transpose(1, 2, 0)
    if out.max() <= 1.5: out = out * 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
def clean(im):
    a = np.asarray(im).astype(np.int32); lum = a.mean(2)
    for (ox, oy), rects in ZONES:
        m = np.zeros((512, 512), bool)
        for x0, y0, x1, y1 in rects:
            sub = lum[y0:y1, x0:x1] > 200                       # white watermark strokes only
            m[y0 - oy:y1 - oy, x0 - ox:x1 - ox] |= sub
        if m.sum() < 30: continue                              # no watermark in this zone on this frame
        m = ndi.binary_dilation(m, iterations=5)
        win = im.crop((ox, oy, ox + 512, oy + 512)); rec = run(win, m)
        feather = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
        win.paste(rec, (0, 0), feather); im.paste(win, (ox, oy))
    return im
if __name__ == "__main__":
    src, out, tmp = sys.argv[1], sys.argv[2], sys.argv[3]
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-t", "27.43", "-an", f"{tmp}/%05d.png"], check=True)
    fs = sorted(glob.glob(f"{tmp}/*.png"))
    for k, f in enumerate(fs):
        clean(Image.open(f).convert("RGB")).save(f)
        if k % 50 == 0: print(k, len(fs), flush=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{tmp}/%05d.png", "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", out], check=True)
    shutil.rmtree(tmp); print("done", out)
