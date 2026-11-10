"""Extract design elements as alpha masks (no redrawing). Usage: python extract.py <dir>"""
import sys, os, numpy as np
from PIL import Image, ImageDraw
D = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = os.path.join(D, 'out', 'elements')
os.makedirs(OUT, exist_ok=True)

def alpha(img, bg, off, rng):
    a = np.asarray(img.convert('RGB'), dtype=np.float32)
    d = np.sqrt(((a - np.array(bg, np.float32)) ** 2).sum(-1))
    return np.clip((d - off) / rng, 0, 1)

poster = Image.open(os.path.join(D, 'affiche.jpg'))
logo = Image.open(os.path.join(D, 'logo.png'))
ap = alpha(poster, (248, 244, 235), 22, 100)
al = alpha(logo, (243, 243, 243), 40, 110)

P = {
 'titre1': (63, 261, 512, 352), 'titre2': (65, 347, 511, 423),
 'question1': (71, 451, 482, 499), 'question2': (139, 497, 424, 536),
 'coeur': (220, 598, 635, 1013), 'ville': (459, 231, 839, 558),
 'apocalypse': (243, 1043, 611, 1069),
}
L = {
 'symbole': (6, 27, 158, 179), 'ecodim': (185, 58, 312, 87),
 'ce': (185, 88, 542, 124), 'extension': (186, 134, 518, 155),
}
els = {}
for k, (x0, y0, x1, y1) in P.items():
    m = ap[y0:y1, x0:x1].copy()
    if k == 'ville':  # erase title letters (poster coords x<522 and y<508)
        xs = np.arange(x0, x1)[None, :]; ys = np.arange(y0, y1)[:, None]
        m[(xs < 522) & (ys < 508)] = 0
    els[k] = m
import cv2
def drop_strays(m, keep):
    # remove glyph fragments cut by an overlapping box (pieces of the neighbouring line)
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.05).astype(np.uint8), connectivity=8)
    h = m.shape[0]
    for i in range(1, n):
        top, bot = st[i, 1], st[i, 1] + st[i, 3]
        if not keep(top / h, bot / h):
            m[lab == i] = 0
    return m
els['titre1'] = drop_strays(els['titre1'], lambda t, b: t < 0.7)   # line-2 tops at the bottom
els['titre2'] = drop_strays(els['titre2'], lambda t, b: b > 0.15)  # line-1 'p' descender at the top
for k, (x0, y0, x1, y1) in L.items():
    els[k] = al[y0:y1, x0:x1].copy()

for k, m in els.items():
    Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(OUT, k + '.png'))

# contact sheet: each element in black on white, with its name and bbox outline
pad, scale = 20, 2
tiles = []
for k, m in els.items():
    im = Image.fromarray((255 - m * 255).astype(np.uint8)).convert('RGB')
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    t = Image.new('RGB', (im.width + 2 * pad, im.height + 2 * pad + 24), 'white')
    t.paste(im, (pad, pad + 24))
    dr = ImageDraw.Draw(t)
    dr.rectangle([pad - 1, pad + 23, pad + im.width, pad + 24 + im.height], outline=(220, 0, 0))
    dr.text((pad, 4), f'{k} {m.shape[1]}x{m.shape[0]}', fill=(220, 0, 0))
    tiles.append(t)
W = 1800; x = y = rowh = 0; pos = []
for t in tiles:
    if x + t.width > W: x, y, rowh = 0, y + rowh, 0
    pos.append((x, y)); x += t.width; rowh = max(rowh, t.height)
sheet = Image.new('RGB', (W, y + rowh), (235, 235, 235))
for t, p in zip(tiles, pos): sheet.paste(t, p)
sheet.save(os.path.join(D, 'out', 'planche_controle_decoupes.png'))
print('ok', {k: m.shape for k, m in els.items()})
