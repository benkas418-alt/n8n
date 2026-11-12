"""Redraw the round ECODIM symbol as clean vectors (disc in ink, details knocked out to the fabric).
Coordinates: the 6x enlargement of the logo crop (0, 20, 165, 186) -> 990 x 996 units.
Usage: python symbol.py <dir>"""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
FD = '/usr/share/fonts/truetype/open-sans/'
CX, CY, R = 495, 500, 440          # disc
RING_R, RING_W = 408, 6            # inner circle (knocked out)
LINE = 7                           # line width of the dove and the book

def text_path(txt, font, x0, x1, base, cap):
    """Text as an outline path, scaled so it spans x0..x1 with the given cap height."""
    f = TTFont(FD + font); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    capH = f['OS/2'].sCapHeight or 0.714 * upm
    pens, x = [], 0
    for ch in txt:
        g = cmap[ord(ch)]; p = SVGPathPen(gs); gs[g].draw(p); pens.append((x, p.getCommands())); x += gs[g].width
    last = cmap[ord(txt[-1])]; bp = BoundsPen(gs); gs[last].draw(bp)
    width = x - gs[last].width + bp.bounds[2]           # ink width, no trailing side bearing
    sy = cap / capH; sx = (x1 - x0) / width
    return ''.join(f'<path transform="translate({x0 + dx * sx:.2f} {base}) scale({sx:.5f} {-sy:.5f})" d="{d}"/>' for dx, d in pens)

DOVE = [  # stroked lines (knocked out)
    'M262 206 C300 262 392 326 492 360',                      # left wing, top edge
    'M268 228 C305 282 385 336 478 382',                      # left wing, 2nd feather
    'M282 268 C320 312 392 360 470 402',                      # left wing, 3rd feather
    'M492 360 C512 372 530 372 546 352',                      # body under the left wing
    'M606 198 C582 238 548 282 546 330 C545 350 552 362 566 368',  # right wing, outer
    'M598 226 C576 262 560 296 560 330',                      # right wing, inner
    'M566 368 C584 366 600 358 612 360 C626 362 634 370 638 378',  # head top + beak
    'M638 378 C624 384 604 388 590 396 C560 414 520 446 488 476',   # throat, neck to tail
    'M470 402 C478 410 484 420 486 434',                      # wing joins body
    'M478 500 L478 456 C500 454 504 478 484 482',             # tail hook after ECODIM
]
BOOK = [
    'M604 440 C676 420 752 424 800 460',                      # right page, top edge
    'M800 460 L656 774',                                      # right page, fore edge
    'M786 482 L646 760',                                      # page thickness
    'M200 682 C282 690 360 700 420 712 C452 690 484 676 532 678 C584 690 624 730 656 774',  # bottom edge
]

def body(ink, mid='k'):
    """Mask + disc. The symbol fills the box (55, 60, 880, 880) of the 990 x 996 space."""
    lines = ''.join(f'<path d="{d}"/>' for d in DOVE + BOOK)
    txt = (text_path('ECODIM', 'OpenSans-Bold.ttf', 190, 458, 487, 42)
           + text_path('LA PAROLE', 'OpenSans-Semibold.ttf', 190, 682, 582, 66)
           + text_path('ÉTERNELLE', 'OpenSans-Semibold.ttf', 190, 680, 665, 66))
    return (f'<defs><mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="990" height="996">'
            f'<rect width="990" height="996" fill="#fff"/>'
            f'<circle cx="{CX}" cy="{CY}" r="{RING_R}" fill="none" stroke="#000" stroke-width="{RING_W}"/>'
            f'<g fill="none" stroke="#000" stroke-width="{LINE}" stroke-linecap="round" stroke-linejoin="round">{lines}</g>'
            f'<g fill="#000">{txt}</g></mask></defs>'
            f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{ink}" mask="url(#{mid})"/>')

def svg(ink, fabric=None, size_mm=None):
    dim = f' width="{size_mm}mm" height="{size_mm}mm"' if size_mm else ''
    bg = f'<rect x="55" y="60" width="880" height="880" fill="{fabric}"/>' if fabric else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg"{dim} viewBox="55 60 880 880">{bg}{body(ink)}</svg>'

def nested(ink, x, y, w):
    """The symbol as a nested <svg> placed at (x, y) with width w (parent units)."""
    return f'<svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{w:.3f}" viewBox="55 60 880 880">{body(ink, "sym")}</svg>'

# --- the three text lines of the logo, set in a real font fitted to the original ink bounds ---
LOGO_TEXT = {'ecodim': 'ECODIM', 'ce': 'C.E. LA PAROLE ÉTERNELLE', 'extension': 'EXTENSION DU GOLF PLATEAU'}
SC = 10  # element space: source crop pixels x 10

def _bounds(key, D):
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(os.path.join(D, 'out', 'elements_trace', key + '.png'))) > 100
    cols = np.nonzero(a.any(0))[0]; rows = np.nonzero(a.any(1))[0]
    first = a[:, cols[0]:cols[0] + 6]          # first letter (C or E): no accent -> cap height
    r1 = np.nonzero(first.any(1))[0]
    return a.shape, cols[0], cols[-1] + 1, r1[0], r1[-1] + 1

def text_body(key, ink, D):
    (h, w), x0, x1, top, base = _bounds(key, D)
    p = text_path(LOGO_TEXT[key], 'OpenSans-CondBold.ttf', x0 * SC, x1 * SC, base * SC, (base - top) * SC)
    return w * SC, h * SC, f'<g fill="{ink}">{p}</g>'

def text_nested(key, ink, x, y, wbox, D):
    W, H, body_ = text_body(key, ink, D)
    return f'<svg x="{x:.3f}" y="{y:.3f}" width="{wbox:.3f}" height="{wbox * H / W:.3f}" viewBox="0 0 {W} {H}">{body_}</svg>'

def write_text_elements(D):
    """Render the three lines as raster masks for the photo mockups."""
    import subprocess, numpy as np
    from PIL import Image
    for key in LOGO_TEXT:
        W, H, body_ = text_body(key, '#000', D)
        svgp = os.path.join(D, 'out', f'_{key}.svg'); png = svgp[:-4] + '.png'
        open(svgp, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body_}</svg>')
        subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'render_svg.js'), svgp, png, str(W)], check=True)
        Image.fromarray(np.asarray(Image.open(png).convert('RGBA'))[..., 3]).save(os.path.join(D, 'out', 'elements', key + '.png'))
        os.remove(svgp); os.remove(png)

if __name__ == '__main__':
    D = sys.argv[1]; os.makedirs(os.path.join(D, 'out', 'svg'), exist_ok=True)
    import shutil
    tr = os.path.join(D, 'out', 'elements_trace'); os.makedirs(tr, exist_ok=True)
    for k in ('ecodim', 'ce', 'extension', 'symbole'):
        if not os.path.exists(os.path.join(tr, k + '.png')):
            shutil.copy(os.path.join(D, 'out', 'elements', k + '.png'), os.path.join(tr, k + '.png'))
    out = os.path.join(D, 'out', 'svg', 'symbole_redessine.svg')
    open(out, 'w').write(svg('#000000', size_mm=60))
    # raster mask for the photo mockups (replaces the low-res crop in out/elements/)
    import subprocess, numpy as np
    from PIL import Image
    tmp = os.path.join(D, 'out', '_symbole.png')
    subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'render_svg.js'), out, tmp, '1520'], check=True)
    a = np.asarray(Image.open(tmp).convert('RGBA'))[..., 3]
    Image.fromarray(a).save(os.path.join(D, 'out', 'elements', 'symbole.png')); os.remove(tmp)
    write_text_elements(D)

