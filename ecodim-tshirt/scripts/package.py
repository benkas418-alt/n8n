"""Build livraison/ (all PNG): mockups, print files at 300 dpi, elements per ink, colour chart.
Usage: python package.py <dir>   (run vectorize.py and mockup.py first)"""
import sys, os, shutil, re, cairosvg
from PIL import Image, ImageDraw, ImageFont
sys.argv = [sys.argv[0], sys.argv[1], '500']
sys.path.insert(0, os.path.dirname(__file__))
import vectorize as V
D = sys.argv[1]; OUT = os.path.join(D, 'out'); LIV = os.path.join(D, 'livraison')
shutil.rmtree(LIV, ignore_errors=True)
DPI = 300; px = lambda mm: round(mm / 25.4 * DPI)
INKS = [('noir', '#000000'), ('01_vert_champagne', '#EADEC0'), ('02_marine_creme', '#F2E8D0'), ('03_noir_ivoire', '#F3EEDF'),
        ('04_rouge_creme', '#F4EAD3'), ('05_brun_creme', '#F0E3C8'), ('06_gris_bleu_nuit', '#14213D')]
VAR = [('01', 'vert', 'VERT FONCÉ', '#1F3A2B', 'CHAMPAGNE', '#EADEC0'), ('02', 'marine', 'BLEU MARINE', '#1B2540', 'CRÈME', '#F2E8D0'),
       ('03', 'noir', 'NOIR', '#181818', 'IVOIRE', '#F3EEDF'), ('04', 'rouge', 'ROUGE', '#961A21', 'CRÈME', '#F4EAD3'),
       ('05', 'brun', 'BRUN CAFÉ', '#4A3022', 'CRÈME', '#F0E3C8'), ('06', 'gris', 'GRIS', '#A8AAAC', 'BLEU NUIT', '#14213D')]
def mk(*p):
    d = os.path.join(LIV, *p); os.makedirs(d, exist_ok=True); return d

# 1. mockups
m = mk('01_maquettes')
shutil.copy(os.path.join(OUT, 'apercu_6_variantes_HD.png'), os.path.join(m, '00_apercu_6_variantes_HD.png'))
shutil.copy(os.path.join(OUT, 'apercu_6_variantes.png'), os.path.join(m, '00_apercu_6_variantes.png'))
for n, slug, *_ in VAR:
    shutil.copy(os.path.join(OUT, f'planche_variante_{n}_{slug}.png'), os.path.join(m, f'{n}_{slug}_planche.png'))
    shutil.copy(os.path.join(OUT, f'variante_{n}_{slug}_devant.png'), os.path.join(m, f'{n}_{slug}_devant_photo_4000px.png'))
    shutil.copy(os.path.join(OUT, f'variante_{n}_{slug}_dos_a_plat.png'), os.path.join(m, f'{n}_{slug}_dos_a_plat.png'))

# 2. print files: transparent, real size, 300 dpi, one per ink
for side, name in (('front', 'devant'), ('back', 'dos')):
    for ink, col in INKS:
        svg = V.svg(side, col)
        wmm = float(re.search(r'width="([\d.]+)mm"', svg).group(1))
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(mk('02_impression_300dpi'), f'{name}_{ink}.png'),
                         output_width=px(wmm), dpi=DPI)

# 3. elements: each element alone, transparent, at its printed size (300 dpi, at least 1200 px wide)
for side in ('front', 'back'):
    for k, (x, y, w, h) in V.LAY[side].items():
        t = V.TR[k]
        for ink, col in INKS:
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {t["w"]} {t["h"]}">'
                   f'<g transform="{t["transform"]}"><path fill="{col}" fill-rule="evenodd" d="{t["d"]}"/></g></svg>')
            cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(mk('03_elements', ink), f'{k}.png'),
                             output_width=max(1200, px(w * V.LMM)))

# 4. colour chart
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
im = Image.new('RGB', (2000, 1500), (244, 242, 238)); d = ImageDraw.Draw(im)
d.text((60, 50), 'ECODIM — NUANCIER DES 6 VARIANTES', font=ImageFont.truetype(F, 54), fill=(25, 25, 25))
for i, (n, slug, fn, fh, inn, ih) in enumerate(VAR):
    y = 170 + i * 215
    d.rounded_rectangle((60, y, 1940, y + 190), 24, fill=fh)
    d.text((100, y + 30), f'{n}', font=ImageFont.truetype(F, 90), fill=ih)
    d.text((300, y + 40), f'TISSU {fn}  {fh}', font=ImageFont.truetype(F, 40), fill=ih)
    d.text((300, y + 105), f'ENCRE {inn}  {ih}', font=ImageFont.truetype(FR, 40), fill=ih)
    d.ellipse((1720, y + 25, 1860, y + 165), fill=ih, outline=(255, 255, 255), width=3)
im.save(os.path.join(mk('04_couleurs'), 'nuancier.png'))

# 5. sources
for f in ('affiche.jpg', 'logo.png', 'sources.txt'):
    shutil.copy(os.path.join(D, f), os.path.join(mk('05_sources'), f))
n = sum(len(fs) for _, _, fs in os.walk(LIV)); print('files', n)
