"""Remove neck labels, then upscale each photo x4 with ESRGAN (UpscalerJS esrgan-medium, MIT) run by node.
Usage: python sr_photos.py <dir> <path to sr.js>"""
import sys, os, subprocess, numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from mockup import VARIANTS
D, SRJS = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(D, 'photos_x4'), exist_ok=True)
procs = []
for fn, *_, labels in VARIANTS:
    rgb = np.asarray(Image.open(os.path.join(D, 'photos', fn)).convert('RGB')).copy()
    if labels:
        lm = np.zeros(rgb.shape[:2], np.uint8)
        for x0, y0, x1, y1 in labels: lm[y0:y1, x0:x1] = 1
        rgb = cv2.inpaint(rgb, lm, 5, cv2.INPAINT_TELEA)
    base = os.path.join(D, 'photos_x4', fn[:-4])
    rgb.tofile(base + '.in.raw')
    procs.append((subprocess.Popen(['node', SRJS, base + '.in.raw', str(rgb.shape[1]), str(rgb.shape[0]), base + '.out.raw']), base, rgb.shape))
for p, base, (h, w, _) in procs:
    p.wait()
    a = np.fromfile(base + '.out.raw', np.uint8).reshape(h * 4, w * 4, 3)
    Image.fromarray(a).save(base + '.png')
    os.remove(base + '.in.raw'); os.remove(base + '.out.raw')
    print('ok', base)
