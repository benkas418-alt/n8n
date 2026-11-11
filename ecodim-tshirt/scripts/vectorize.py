"""Trace each design element with potrace and build the print files as SVG (units: mm).
Usage: python vectorize.py <dir> [L_mm=500]"""
import sys, os, re, json, subprocess, tempfile, numpy as np, cv2
from PIL import Image
D = sys.argv[1]; LMM = float(sys.argv[2]) if len(sys.argv) > 2 else 500
EL = os.path.join(D, 'out', 'elements'); OUT = os.path.join(D, 'out', 'svg'); os.makedirs(OUT, exist_ok=True)
LAY = json.load(open(os.path.join(D, 'out', 'layout.json')))
UPS = 8  # trace at 8x the source so the curves follow the shapes, not the pixels
SMOOTH = {'symbole': 0.3, 'extension': 0.4, 'ecodim': 0.45, 'ce': 0.45}  # thin details: less blur (in source px)

def trace(name):
    a = np.asarray(Image.open(os.path.join(EL, name + '.png')), np.float32) / 255
    h, w = a.shape
    big = cv2.resize(a, (w * UPS, h * UPS), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), UPS * SMOOTH.get(name, 0.6))
    ink = big > 0.5
    with tempfile.TemporaryDirectory() as t:
        Image.fromarray(np.where(ink, 0, 255).astype(np.uint8)).convert('1').save(os.path.join(t, 'i.pbm'))
        subprocess.run(['potrace', '-s', '--flat', '-t', str(3 * UPS * UPS // 4), '-O', '0.8', '-a', '1.1',
                        '-o', os.path.join(t, 'o.svg'), os.path.join(t, 'i.pbm')], check=True)
        svg = open(os.path.join(t, 'o.svg')).read()
    tr = re.search(r'<g transform="([^"]+)"', svg).group(1)
    paths = re.findall(r'<path d="([^"]+)"', svg, re.S)
    return dict(w=w * UPS, h=h * UPS, transform=tr, d=' '.join(p.replace('\n', ' ') for p in paths))

TR = {k[:-4]: trace(k[:-4]) for k in sorted(os.listdir(EL))}

def group(boxes, color):
    out = []
    for k, (x, y, w, h) in boxes.items():
        t = TR[k]; s = w * LMM / t['w']
        out.append(f'  <g id="{k}" transform="translate({x*LMM:.3f} {y*LMM:.3f}) scale({s:.6f})">'
                   f'<g transform="{t["transform"]}"><path fill="{color}" fill-rule="evenodd" d="{t["d"]}"/></g></g>')
    return '\n'.join(out)

def svg(side, color, bg=None):
    boxes = LAY[side]; hL = max(b[1] + b[3] for b in boxes.values()) + 0.03
    W, H = LMM, hL * LMM
    rect = f'  <rect width="100%" height="100%" fill="{bg}"/>\n' if bg else ''
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.3f} {H:.3f}">\n'
            f'  <title>ECODIM — {"devant" if side == "front" else "dos"} — largeur {W/10:.0f} cm</title>\n'
            f'{rect}{group(boxes, color)}\n</svg>\n')

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    for side, name in (('front', 'impression_devant'), ('back', 'impression_dos')):
        open(os.path.join(OUT, f'{name}_noir.svg'), 'w').write(svg(side, '#000000'))
    # one ink per variant (same layout), on a fabric-coloured background for viewing
    V = [('01_vert', '#1F3A2B', '#EADEC0'), ('02_marine', '#1B2540', '#F2E8D0'), ('03_noir', '#181818', '#F3EEDF'),
         ('04_rouge', '#961A21', '#F4EAD3'), ('05_brun', '#4A3022', '#F0E3C8'), ('06_gris', '#A8AAAC', '#14213D')]
    for slug, fab, ink in V:
        for side, name in (('front', 'devant'), ('back', 'dos')):
            open(os.path.join(OUT, f'variante_{slug}_{name}.svg'), 'w').write(svg(side, ink, fab))
    for k, t in TR.items(): print(f'{k:11s} {t["d"].count("c") + t["d"].count("l"):5d} segments')
