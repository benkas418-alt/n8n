# Route that follows the streets drawn on the OSM map image (no API): road-colour mask + least-cost path.
import sys, json, numpy as np
from PIL import Image, ImageDraw
from skimage.graph import MCP_Geometric
from skimage.morphology import binary_closing, disk
from skimage.measure import approximate_polygon
a = np.asarray(Image.open('real/osm16.jpg').convert('RGB')).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
salmon = (R > 215) & (G > 120) & (R - G > 22) & (R - B > 30) & (G - B > -5)
yellow = (R > 232) & (G > 232) & (B < 215) & (R - B > 25)
white = (R > 243) & (G > 243) & (B > 243)
cost = np.full(R.shape, 1e6)
for m, c in ((binary_closing(white, disk(3)), 7.0), (binary_closing(yellow, disk(3)), 1.25), (binary_closing(salmon, disk(3)), 1.0)):
    cost[m] = np.minimum(cost[m], c)
def snap(p, mask):
    ys, xs = np.nonzero(mask); k = np.argmin((xs - p[0]) ** 2 + (ys - p[1]) ** 2); return int(xs[k]), int(ys[k])
road = cost < 1e5
A = snap(tuple(map(int, sys.argv[1].split(','))), road); Bp = snap(tuple(map(int, sys.argv[2].split(','))), road)
m = MCP_Geometric(cost); m.find_costs([A[::-1]], [Bp[::-1]]); path = np.array(m.traceback(Bp[::-1]))[:, ::-1]
simp = approximate_polygon(path.astype(float), tolerance=2.5)
d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in simp)
L = float(np.sum(np.hypot(*np.diff(simp, axis=0).T)))
json.dump({"d": d, "A": A, "B": [int(Bp[0]), int(Bp[1])], "len": L}, open('real/route/route.json', 'w'))
im = Image.open('real/osm16.jpg').convert('RGB'); dr = ImageDraw.Draw(im); dr.line([tuple(p) for p in simp], fill=(31, 136, 201), width=9)
im.resize((650, 1150)).save('dup/route_chk.jpg'); print(A, Bp, len(simp), round(L))
