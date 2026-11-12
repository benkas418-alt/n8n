"""Each visual alone, in black on white, at real size (300 dpi). Usage: python noir.py <dir>"""
import sys, os, shutil, subprocess, tempfile
from PIL import Image
sys.argv = [sys.argv[0], sys.argv[1], '500']
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize as V
D = sys.argv[1]; OUT = os.path.join(D, 'a_imprimer_noir'); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render_svg.js')
DPI = 300; M = 5  # margin in mm
GROUPS = [('01_ville_etoile', 'front', ['ville']),
          ('02_logo_complet', 'front', ['ecodim', 'ce', 'extension', 'symbole']),
          ('03_logo_rond', 'front', ['symbole']),
          ('04_logo_texte', 'front', ['ecodim', 'ce', 'extension']),
          ('05_titre_pas_de_place_a_bethleem', 'front', ['titre1', 'titre2']),
          ('06_coeur_porte', 'front', ['coeur']),
          ('07_question_trouvera_t_il', 'front', ['question1', 'question2']),
          ('08_dos_apocalypse_3_20', 'back', ['apocalypse'])]
for name, side, keys in GROUPS:
    boxes = {k: V.LAY[side][k] for k in keys}
    x0 = min(b[0] for b in boxes.values()) * V.LMM - M; y0 = min(b[1] for b in boxes.values()) * V.LMM - M
    x1 = max(b[0] + b[2] for b in boxes.values()) * V.LMM + M; y1 = max(b[1] + b[3] for b in boxes.values()) * V.LMM + M
    w, h = x1 - x0, y1 - y0
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}mm" height="{h:.1f}mm" viewBox="{x0:.3f} {y0:.3f} {w:.3f} {h:.3f}">'
           f'<rect x="{x0:.3f}" y="{y0:.3f}" width="{w:.3f}" height="{h:.3f}" fill="#ffffff"/>{V.group(boxes, "#000000")}</svg>')
    with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as f: f.write(svg)
    png = os.path.join(OUT, f'{name}_{(w - 2*M)/10:.1f}x{(h - 2*M)/10:.1f}cm.png'.replace('.', ',', 2).replace(',png', '.png'))
    subprocess.run(['node', JS, f.name, png, str(round(w / 25.4 * DPI))], check=True); os.remove(f.name)
    Image.open(png).convert('RGB').save(png, dpi=(DPI, DPI))
    print(os.path.basename(png), Image.open(png).size)
