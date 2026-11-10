"""Shirt mask and geometry from a front photo."""
import numpy as np, cv2
from PIL import Image

def shirt_mask(rgb):
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[:4].reshape(-1, 3), rgb[-4:].reshape(-1, 3), rgb[:, :4].reshape(-1, 3), rgb[:, -4:].reshape(-1, 3)])
    bg = np.median(border, 0)
    d = np.sqrt(((rgb.astype(np.float32) - bg) ** 2).sum(-1))
    m = (d > 45).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    # second pass: keep pixels closer to the shirt colour than to the background (drops cast shadows)
    shirt = np.median(rgb[m.astype(bool)], 0)
    ds = np.sqrt(((rgb.astype(np.float32) - shirt) ** 2).sum(-1))
    m = (m.astype(bool) & (ds < d)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    # fill holes (inner collar etc.)
    ff = m.copy(); cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    m = m | (1 - ff)
    return m.astype(bool), bg

def geometry(m):
    ys, xs = np.nonzero(m)
    top, bot = ys.min(), ys.max()
    H = bot - top
    widths = m.sum(1)
    band = slice(top + int(0.55 * H), top + int(0.75 * H))
    L = float(np.median(widths[band]))
    cx = float(np.median([np.nonzero(m[y])[0].mean() for y in range(band.start, band.stop, 5)]))
    # armpit: first row from the top (after the sleeves) where width falls to body width
    rows = np.arange(top + int(0.15 * H), top + int(0.6 * H))
    arm = int(rows[np.argmax(widths[rows] < 1.08 * L)])
    return dict(top=int(top), bottom=int(bot), L=L, cx=cx, armpit=arm)
