"""Simple print folder: per variant the front and back print (transparent PNG, 300 dpi, real size)
and a photo preview; the redrawn symbol alone; one detail sheet with sizes. Usage: python imprimer.py <dir>"""
import sys, os, shutil, subprocess, tempfile, json
from PIL import Image, ImageDraw, ImageFont
sys.argv = [sys.argv[0], sys.argv[1], '500']
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize as V, symbole_logo as SY
D = sys.argv[1]; OUT = os.path.join(D, 'out'); A = os.path.join(D, 'a_imprimer')
shutil.rmtree(A, ignore_errors=True); os.makedirs(A)
JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render_svg.js')
DPI = 300; px = lambda mm: round(mm / 25.4 * DPI)
VAR = [('01', 'vert', 'VERT FONCÉ', '#1F3A2B', 'CHAMPAGNE', '#EADEC0'), ('02', 'marine', 'BLEU MARINE', '#1B2540', 'CRÈME', '#F2E8D0'),
       ('03', 'noir', 'NOIR', '#181818', 'IVOIRE', '#F3EEDF'), ('04', 'rouge', 'ROUGE', '#961A21', 'CRÈME', '#F4EAD3'),
       ('05', 'brun', 'BRUN CAFÉ', '#4A3022', 'CRÈME', '#F0E3C8'), ('06', 'gris', 'GRIS', '#A8AAAC', 'BLEU NUIT', '#14213D')]

def render(svg, out, width):
    with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as f: f.write(svg)
    subprocess.run(['node', JS, f.name, out, str(width)], check=True); os.remove(f.name)
    im = Image.open(out); im.save(out, dpi=(DPI, DPI))

for n, slug, fname, fh, iname, ih in VAR:
    d = os.path.join(A, f'{n}_{slug}'); os.makedirs(d)
    render(V.svg('front', ih), os.path.join(d, f'{n}_{slug}_DEVANT_encre_{iname.lower().replace(" ", "_").replace("è", "e")}.png'), px(V.LMM))
    render(V.svg('back', ih), os.path.join(d, f'{n}_{slug}_DOS_encre_{iname.lower().replace(" ", "_").replace("è", "e")}.png'), px(V.LMM))
    shutil.copy(os.path.join(OUT, f'planche_variante_{n}_{slug}.png'), os.path.join(d, f'{n}_{slug}_APERCU.png'))

# symbol alone, large (black and each ink)
render(SY.svg('#000000'), os.path.join(A, 'LOGO_rond_ECODIM_noir.png'), 3000)

# detail sheet: front + back in black with the width of each element in cm
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
FR = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
tmp = os.path.join(A, '_f.png'); tmpb = os.path.join(A, '_b.png')
render(V.svg('front', '#000000', '#ffffff'), tmp, 1600); render(V.svg('back', '#000000', '#ffffff'), tmpb, 1600)
f = Image.open(tmp).convert('RGB'); b = Image.open(tmpb).convert('RGB'); os.remove(tmp); os.remove(tmpb)
sc = 1600 / V.LMM
W, H = 2400, 140 + f.height + 120 + b.height + 120
im = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(im)
dr.text((60, 40), 'ECODIM — FICHE D\'IMPRESSION (mesures en cm, largeur de la zone = 50 cm)', font=F, fill=(0, 0, 0))
ox, oy = 60, 120; im.paste(f, (ox, oy)); dr.rectangle((ox, oy, ox + f.width, oy + f.height), outline=(180, 180, 180), width=2)
names = {'ville': 'Ville + étoile', 'symbole': 'Logo rond', 'ecodim': 'ECODIM', 'ce': 'C.E. LA PAROLE ÉTERNELLE',
         'extension': 'EXTENSION DU GOLF PLATEAU', 'titre1': 'Titre ligne 1', 'titre2': 'Titre ligne 2', 'coeur': 'Cœur',
         'question1': 'Question ligne 1', 'question2': 'Question ligne 2', 'apocalypse': 'APOCALYPSE 3:20'}
ty = oy
for k, (x, y, w, h) in V.LAY['front'].items():
    x0, y0 = ox + x * 1600, oy + y * 1600
    dr.rectangle((x0, y0, x0 + w * 1600, y0 + h * 1600), outline=(220, 40, 40), width=2)
    dr.text((ox + 1640, ty), f'{names[k]} : {w*50:.1f} × {h*50:.1f} cm', font=FR, fill=(0, 0, 0))
    dr.text((ox + 1640, ty + 30), f'   à {x*50:.1f} cm du bord gauche, {y*50:.1f} cm du haut', font=FR, fill=(110, 110, 110))
    ty += 76
dr.text((ox + 1640, ty + 20), 'DEVANT : le haut de la zone est à ~2 cm', font=FR, fill=(220, 40, 40))
dr.text((ox + 1640, ty + 50), 'sous la couture d\'épaule ; zone centrée.', font=FR, fill=(220, 40, 40))
by = oy + f.height + 80
dr.text((60, by - 45), 'DOS', font=F, fill=(0, 0, 0)); im.paste(b, (ox, by))
dr.rectangle((ox, by, ox + b.width, by + b.height), outline=(180, 180, 180), width=2)
x, y, w, h = V.LAY['back']['apocalypse']
dr.text((ox + 1640, by), f'APOCALYPSE 3:20 : {w*50:.1f} × {h*50:.1f} cm', font=FR, fill=(0, 0, 0))
dr.text((ox + 1640, by + 30), f'   centré, à {y*50:.1f} cm sous le col', font=FR, fill=(110, 110, 110))
im.save(os.path.join(A, 'FICHE_IMPRESSION_mesures.png'))
print(sum(len(x) for _, _, x in os.walk(A)), 'files')
