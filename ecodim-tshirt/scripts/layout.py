"""Compute the layout once (unit L = chest width) and render the transparent black print files.
Usage: python layout.py <dir> [L_cm=50] [dpi=150]"""
import sys, os, json, numpy as np
from PIL import Image
D = sys.argv[1]; L_CM = float(sys.argv[2]) if len(sys.argv) > 2 else 50; DPI = int(sys.argv[3]) if len(sys.argv) > 3 else 150
EL = os.path.join(D, 'out', 'elements')
el = {k[:-4]: Image.open(os.path.join(EL, k)) for k in os.listdir(EL)}
W = lambda k: el[k].width; H = lambda k: el[k].height

def layout():
    """Boxes (x, y, w, h) in L units; y=0 is the top of the print area, just under the shoulder seam."""
    f, b = {}, {}
    # chest left of the image: town + star
    w = 0.25; f['ville'] = (0.05, 0.03, w, w * H('ville') / W('ville'))
    # chest right of the image: text stack (right-aligned) + gap + symbol at far right
    s_over_t = 0.55 * 152 / 97              # stack height (97 px at scale 1) = 55 % of symbol diameter
    gap = 0.02; total = 0.37
    t = (total - gap) / (357 * s_over_t + 152)  # L per logo px for the symbol
    s = t * s_over_t                           # L per logo px for the text
    Dm = 152 * t; right = 1 - 0.04; top = 0.06
    f['symbole'] = (right - Dm, top, Dm, Dm)
    stack_top = top + (Dm - 97 * s) / 2; text_right = right - Dm - gap
    for k, y in (('ecodim', 58), ('ce', 88), ('extension', 134)):
        f[k] = (text_right - W(k) * s, stack_top + (y - 58) * s, W(k) * s, H(k) * s)
    chest_bottom = max(v[1] + v[3] for v in f.values())
    # centre column
    y = chest_bottom + 0.09
    sc = 0.45 / W('titre1')
    f['titre1'] = (0.5 - W('titre1') * sc / 2, y, W('titre1') * sc, H('titre1') * sc)
    f['titre2'] = (0.5 - W('titre2') * sc / 2, y + 86 * sc, W('titre2') * sc, H('titre2') * sc)
    y = f['titre2'][1] + f['titre2'][3] + 0.06
    f['coeur'] = (0.5 - 0.17, y, 0.34, 0.34)
    y += 0.34 + 0.05
    sq = 0.37 / W('question1')
    f['question1'] = (0.5 - W('question1') * sq / 2, y, W('question1') * sq, H('question1') * sq)
    f['question2'] = (0.5 - W('question2') * sq / 2, y + 46 * sq, W('question2') * sq, H('question2') * sq)
    # back: only the reference, centred high between the shoulders
    wb = 0.62; b['apocalypse'] = (0.5 - wb / 2, 0.08, wb, wb * H('apocalypse') / W('apocalypse'))
    return {'front': f, 'back': b}

def render(boxes, Lpx, height_L):
    a = np.zeros((int(round(height_L * Lpx)), int(Lpx)), np.float32)
    for k, (x, y, w, h) in boxes.items():
        im = el[k].resize((max(1, round(w * Lpx)), max(1, round(h * Lpx))), Image.LANCZOS)
        m = np.asarray(im, np.float32) / 255
        x0, y0 = round(x * Lpx), round(y * Lpx)
        sub = a[y0:y0 + m.shape[0], x0:x0 + m.shape[1]]
        np.maximum(sub, m[:sub.shape[0], :sub.shape[1]], out=sub)
    return a

if __name__ == '__main__':
    lay = layout()
    json.dump(lay, open(os.path.join(D, 'out', 'layout.json'), 'w'), indent=1)
    Lpx = round(L_CM / 2.54 * DPI)
    for side in ('front', 'back'):
        hL = max(v[1] + v[3] for v in lay[side].values()) + 0.03
        a = render(lay[side], Lpx, hL)
        rgba = np.zeros(a.shape + (4,), np.uint8); rgba[..., 3] = (a * 255).astype(np.uint8)
        name = {'front': 'impression_devant', 'back': 'impression_dos'}[side]
        Image.fromarray(rgba).save(os.path.join(D, 'out', f'{name}_{int(L_CM)}cm_{DPI}dpi.png'), dpi=(DPI, DPI))
        prev = Image.fromarray((255 - a * 255).astype(np.uint8)); prev.thumbnail((1000, 2000))
        prev.save(os.path.join(D, 'out', f'_apercu_{name}.png'))
        print(side, a.shape, f'{a.shape[1]/DPI*2.54:.1f} x {a.shape[0]/DPI*2.54:.1f} cm')
    # effective source resolution of the most enlarged element
    for side in lay:
        for k, (x, y, w, h) in lay[side].items():
            print(f'  {k:11s} {w*L_CM:5.1f} cm wide, source {W(k)} px -> {W(k)/(w*L_CM/2.54):5.0f} dpi effective')
