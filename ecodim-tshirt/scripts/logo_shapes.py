"""Dove and book of the ECODIM logo as tapered strokes, drawn on the neon reference (1536 x 1024 space).
Each stroke: cubic Bezier centre line (p0, c1, c2, p3) and widths (start, max, end)."""
import numpy as np

DOVE = [
    ((357, 30), (440, 125), (565, 228), (770, 287), (13, 18, 15)),     # left wing, upper feather
    ((363, 92), (378, 200), (480, 330), (740, 402), (12, 22, 4)),      # left wing, lower feather
    ((1004, 22), (950, 66), (915, 150), (926, 252), (9, 17, 11)),      # right wing, outer feather
    ((916, 150), (884, 182), (864, 232), (870, 274), (5, 15, 11)),     # right wing, inner feather
    ((904, 306), (948, 270), (1028, 268), (1061, 320), (6, 17, 3)),    # head, ending in the beak
    ((1000, 306), (930, 330), (880, 430), (690, 500), (14, 15, 3)),    # neck and body, ending in the tail
]
BOOK = [
    ((996, 408), (1090, 352), (1260, 330), (1356, 404), (10, 17, 12)),  # top edge of the right page
    ((1356, 404), (1300, 520), (1180, 760), (1062, 888), (12, 11, 10)), # fore edge 1
    ((1356, 446), (1305, 560), (1200, 790), (1092, 934), (10, 11, 10)), # fore edge 2
    ((1364, 424), (1300, 590), (1200, 860), (1104, 996), (12, 18, 22)), # fore edge 3 (page block)
    ((1104, 996), (1080, 1004), (1045, 980), (1026, 948), (22, 16, 4)), # curl at the bottom corner
    ((231, 800), (360, 830), (500, 860), (612, 886), (24, 16, 10)),     # bottom edge, left page
    ((612, 884), (700, 790), (880, 790), (1062, 888), (10, 11, 10)),    # bottom curve, upper
    ((616, 892), (720, 810), (900, 820), (1092, 934), (10, 11, 10)),    # bottom curve, lower
]

def _bez(p0, c1, c2, p3, t):
    t = t[:, None]; p0, c1, c2, p3 = map(np.array, (p0, c1, c2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3

def stroke_path(p0, c1, c2, p3, widths, n=64):
    w0, wm, w1 = widths
    t = np.linspace(0, 1, n)
    pts = _bez(p0, c1, c2, p3, t)
    d = np.gradient(pts, axis=0); d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    base = w0 * (1 - t) + w1 * t
    w = (base + (wm - base) * np.sin(np.pi * t)) / 2
    left = pts + nrm * w[:, None]; right = pts - nrm * w[:, None]
    poly = np.vstack([left, right[::-1]])
    path = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in poly) + ' Z'
    for (x, y), r in ((pts[0], w[0]), (pts[-1], w[-1])):   # round ends
        if r > 1.2:
            path += f' M{x - r:.1f} {y:.1f} a{r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0 a{r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0 Z'
    return path

def paths(group):
    return ' '.join(stroke_path(*s[:4], s[4]) for s in group)
