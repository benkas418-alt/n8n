"""Photo mockups: recolour each supplied front photo and screen-print the design on it.
Usage: python mockup.py <dir>   (run extract.py and layout.py first)"""
import sys, os, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from geom import shirt_mask, geometry
from layout import render

D = sys.argv[1]; OUT = os.path.join(D, 'out'); os.makedirs(OUT, exist_ok=True)
LAY = json.load(open(os.path.join(OUT, 'layout.json')))
UP = 4            # working scale vs the supplied photo (x4 ESRGAN photos when present)
TOP_OFFSET = 0.27 # print area starts 0.27 L under the top of the collar (clears the neckline)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

VARIANTS = [  # photo, fabric name, fabric hex, ink name, ink hex, labels to inpaint (photo px)
 ('v1_vert.jpg',   'VERT FONCÉ', '#1F3A2B', 'CHAMPAGNE', '#EADEC0', []),
 ('v2_marine.jpg', 'BLEU MARINE', '#1B2540', 'CRÈME',     '#F2E8D0', [(494, 82, 527, 108)]),
 ('v3_noir.jpg',   'NOIR',        '#181818', 'IVOIRE',    '#F3EEDF', []),
 ('v4_rouge.jpg',  'ROUGE',       '#961A21', 'CRÈME',     '#F4EAD3', [(480, 62, 518, 106)]),
 ('v5_brun.jpg',   'BRUN CAFÉ',   '#4A3022', 'CRÈME',     '#F0E3C8', []),
 ('v6_gris.jpg',   'GRIS',        '#A8AAAC', 'BLEU NUIT', '#14213D', [(494, 66, 521, 113)]),
]
hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
lumf = lambda a: a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
rng = np.random.default_rng(7)

def recolour(rgb, m, target):
    lum = lumf(rgb.astype(np.float32))
    med = np.median(lum[m])
    shade = np.clip(lum / max(med, 1), 0.4, 1.7)
    dark = lumf(target[None])[0] < 90
    if dark:  # gentle curve + small additive lift so folds read on dark fabric
        s = shade ** 0.85
        out = target * s[..., None] + (s[..., None] - 1) * 22
    else:
        out = target * shade[..., None]
    out = np.clip(out, 0, 255)
    soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)[..., None]
    return rgb * (1 - soft) + out * soft, shade

def print_ink(fab, shade, m, alpha, ink, dark_ink, displace=True):
    # displacement map from the fabric luminance: the print follows the folds
    lb = cv2.GaussianBlur(shade.astype(np.float32), (0, 0), 3 * UP)  # folds only, not the knit texture
    gy, gx = np.gradient(lb)
    h, w = alpha.shape
    X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    k = 1.2 * UP / max(1e-6, np.percentile(np.abs(np.r_[gx[m], gy[m]]), 99)) if displace else 0.0
    a = cv2.remap(alpha, X + gx * k, Y + gy * k, cv2.INTER_LINEAR)
    a = cv2.GaussianBlur(a, (0, 0), 0.3 * UP) * m * 0.95
    p = 1.0 if dark_ink else 0.45  # multiply for dark ink, partial shading for light ink
    sh = np.clip(shade, 0.3, 1.6) ** p
    grain = 1 + cv2.GaussianBlur(rng.normal(0, 0.05, a.shape).astype(np.float32), (0, 0), UP / 4)
    printed = np.clip(ink * (sh * grain)[..., None], 0, 255)
    return fab * (1 - a[..., None]) + printed * a[..., None]

def make(v):
    fn, fname, fhex, iname, ihex, labels = v
    sr = os.path.join(D, 'photos_x4', fn[:-4] + '.png')
    if os.path.exists(sr):  # labels already removed, x4 ESRGAN (scripts/sr_photos.py)
        rgb = np.asarray(Image.open(sr).convert('RGB')).astype(np.float32)
    else:
        im = Image.open(os.path.join(D, 'photos', fn)).convert('RGB')
        rgb = np.asarray(im).copy()
        if labels:  # remove neck labels (brand/size): excluded from the fabric
            lm = np.zeros(rgb.shape[:2], np.uint8)
            for x0, y0, x1, y1 in labels: lm[y0:y1, x0:x1] = 1
            rgb = cv2.inpaint(rgb, lm, 5, cv2.INPAINT_TELEA)
        rgb = np.asarray(Image.fromarray(rgb).resize((im.width * UP, im.height * UP), Image.LANCZOS)).astype(np.float32)
    m, _ = shirt_mask(rgb.astype(np.uint8)); g = geometry(m)
    fab, shade = recolour(rgb, m, hexrgb(fhex))
    L = g['L']; x0 = int(round(g['cx'] - L / 2)); y0 = int(round(g['top'] + TOP_OFFSET * L))
    hL = max(b[1] + b[3] for b in LAY['front'].values()) + 0.03
    art = render(LAY['front'], L, hL)
    alpha = np.zeros(m.shape, np.float32)
    alpha[y0:y0 + art.shape[0], x0:x0 + art.shape[1]] = art[:alpha.shape[0] - y0, :alpha.shape[1] - x0]
    ink = hexrgb(ihex); dark_ink = lumf(ink[None])[0] < 90
    final = print_ink(fab, shade, m, alpha, ink, dark_ink).astype(np.uint8)
    # check: no ink outside the fabric
    assert (alpha * ~m).max() < 0.05, 'design leaves the shirt'
    boxes = {k: (x0 + b[0] * L, y0 + b[1] * L, b[2] * L, b[3] * L) for k, b in LAY['front'].items()}
    # flat back panel (no back photo supplied): fabric swatch with the back print at the same L scale
    bh = int(0.45 * L); bw = int(1.25 * L)
    back_fab = np.ones((bh, bw, 3), np.float32) * hexrgb(fhex)
    bshade = np.ones((bh, bw), np.float32) * (1 + rng.normal(0, 0.02, (bh, bw)).astype(np.float32))
    barr = render(LAY['back'], L, 0.45)
    ba = np.zeros((bh, bw), np.float32); bx = int((bw - L) / 2)
    ba[:barr.shape[0], bx:bx + barr.shape[1]] = barr[:bh]
    back = print_ink(back_fab, bshade, np.ones((bh, bw), bool), ba, ink, dark_ink, displace=False).astype(np.uint8)
    return dict(final=Image.fromarray(final), back=Image.fromarray(back), boxes=boxes, L=L, g=g,
                title=f'{fname} / IMPRESSION {iname}', fhex=fhex, ihex=ihex, fname=fname, iname=iname)

def fit(img, w, h):
    c = img.copy(); c.thumbnail((w, h), Image.LANCZOS); return c

def crop_box(img, box, pad):
    x, y, w, h = box
    return img.crop((int(x - pad), int(y - pad), int(x + w + pad), int(y + h + pad)))

def board(i, r):
    W = 2000; bg = (244, 242, 238); pad = 40
    ft = ImageFont.truetype(FONT, 46); fs = ImageFont.truetype(FONT, 26); fr = ImageFont.truetype(FONT_R, 22)
    b = Image.new('RGB', (W, 2650), bg); d = ImageDraw.Draw(b)
    d.text((pad, 40), f'VARIANTE 0{i} — T-SHIRT {r["title"]}', font=ft, fill=(25, 25, 25))
    y = 130
    front = fit(r['final'], 1180, 1180); b.paste(front, (pad, y))
    d.text((pad, y + front.height + 8), 'DEVANT — photo réelle, impression incrustée', font=fr, fill=(90, 90, 90))
    back = fit(r['back'], W - 1180 - 3 * pad, 1000); bx = 1180 + 2 * pad
    d.text((bx, y), 'DOS', font=fs, fill=(25, 25, 25))
    b.paste(back, (bx, y + 40))
    d.multiline_text((bx, y + 60 + back.height), 'Aucune photo de dos fournie :\nplacement à plat, même échelle\n(largeur L = poitrine).', font=fr, fill=(150, 40, 40), spacing=6)
    # swatches
    sy = y + 300 + back.height
    for j, (lab, hx) in enumerate((('TISSU ' + r['fname'], r['fhex']), ('ENCRE ' + r['iname'], r['ihex']))):
        yy = sy + j * 140
        d.rounded_rectangle((bx, yy, bx + 110, yy + 110), 55, fill=hx, outline=(120, 120, 120), width=2)
        d.text((bx + 130, yy + 25), lab, font=fs, fill=(25, 25, 25)); d.text((bx + 130, yy + 62), hx, font=fr, fill=(90, 90, 90))
    # 4 close-ups from the final image
    L = r['L']; bx_ = r['boxes']; img = r['final']
    def union(keys):
        xs = [bx_[k][0] for k in keys]; ys = [bx_[k][1] for k in keys]
        x1 = [bx_[k][0] + bx_[k][2] for k in keys]; y1 = [bx_[k][1] + bx_[k][3] for k in keys]
        return (min(xs), min(ys), max(x1) - min(xs), max(y1) - min(ys))
    crops = [('POITRINE GAUCHE (image)', crop_box(img, bx_['ville'], 0.04 * L)),
             ('LOGO', crop_box(img, union(['ecodim', 'ce', 'extension', 'symbole']), 0.04 * L)),
             ('COMPOSITION CENTRALE', crop_box(img, union(['titre1', 'titre2', 'coeur', 'question1', 'question2']), 0.04 * L)),
             ('DOS', r['back'])]
    cy = 130 + 1180 + 70; cw = (W - 5 * pad) // 4
    for j, (lab, c) in enumerate(crops):
        t = fit(c, cw, 1100) if j == 2 else fit(c, cw, 520)
        if j != 2 and t.width < cw: t = c.resize((cw, int(c.height * cw / c.width)), Image.LANCZOS)
        cx = pad + j * (cw + pad)
        d.text((cx, cy), lab, font=fs, fill=(25, 25, 25))
        b.paste(t, (cx, cy + 40))
        d.rectangle((cx - 1, cy + 39, cx + t.width, cy + 40 + t.height), outline=(180, 180, 180))
    bottom = cy + 40 + max(fit(c, cw, 1100 if j == 2 else 520).height for j, (_, c) in enumerate(crops)) + 30
    return b.crop((0, 0, W, max(bottom, sy + 300)))

if __name__ == '__main__':
    res = []
    for i, v in enumerate(VARIANTS, 1):
        r = make(v); res.append(r)
        slug = v[0][3:-4]
        r['final'].save(os.path.join(OUT, f'variante_0{i}_{slug}_devant.png'))
        r['back'].save(os.path.join(OUT, f'variante_0{i}_{slug}_dos_a_plat.png'))
        board(i, r).save(os.path.join(OUT, f'planche_variante_0{i}_{slug}.png'))
        g = r['g']; print(i, slug, 'L=%.0f' % r['L'], 'top=%d' % g['top'])
    # overview of the 6 variants
    tw = 1240; ft = ImageFont.truetype(FONT, 44); fr = ImageFont.truetype(FONT_R, 36)
    ov = Image.new('RGB', (3 * tw + 4 * 50, 2 * 1880 + 200), (244, 242, 238)); d = ImageDraw.Draw(ov)
    d.text((50, 50), 'ECODIM — T-SHIRTS DE NOËL : LES 6 VARIANTES (DEVANT + DOS À PLAT)', font=ImageFont.truetype(FONT, 64), fill=(25, 25, 25))
    for i, r in enumerate(res):
        x = 50 + (i % 3) * (tw + 50); y = 180 + (i // 3) * 1880
        d.text((x, y), f'0{i+1} — {r["title"]}', font=ft, fill=(25, 25, 25))
        f = fit(r['final'], tw, tw); ov.paste(f, (x, y + 70))
        bk = fit(r['back'], tw, 520); ov.paste(bk, (x, y + 90 + f.height))
        d.text((x, y + 100 + f.height + bk.height), 'dos (à plat)', font=fr, fill=(110, 110, 110))
    ov.save(os.path.join(OUT, 'apercu_6_variantes_HD.png'))
    small = ov.copy(); small.thumbnail((2000, 2000), Image.LANCZOS); small.save(os.path.join(OUT, 'apercu_6_variantes.png'))
