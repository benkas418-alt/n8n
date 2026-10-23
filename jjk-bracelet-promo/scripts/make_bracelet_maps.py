"""Build the 3D maps of both bracelets from the reference renders.

Each face (outer, inner) gets:
  *_color.jpg   silicone colour with the paint in the engraving
  *_height.png  engraving mask (white = groove floor), used as displacement
  *_normal.png  tangent-space normals of the groove walls
  *_rough.png   roughness (paint is a little glossier than silicone)
  *_glow.jpg    emissive map (Gojo neon only)

The texture covers the full band: 202 mm around, 12 mm across.
Run from the project folder: python3 -I scripts/make_bracelet_maps.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = 'assets/img/'
T = 'assets/tex/'
W, H = 8192, 512
MM = W / 202     # texels per mm around the band
VMM = H / 12     # texels per mm across the band
DEPTH = 0.45     # engraving depth in mm


def img(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float32)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def tight(m, thr=0.5):
    ys, xs = np.where(m > thr)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def vectorise(m, h_px, w_px):
    """Upscale a low-res mask with clean edges: bicubic, soften, then threshold."""
    big = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((w_px, h_px), Image.BICUBIC)
    scale = h_px / m.shape[0]
    big = big.filter(ImageFilter.GaussianBlur(max(0.6, scale * 0.45)))
    return smoothstep(0.42, 0.58, np.asarray(big) / 255.0)


def place(canvas, m, x_mm, h_mm, y_mm=6.0):
    """Paste mask m on canvas, centred at x_mm, h_mm tall, keeping its physical aspect."""
    h_px = int(round(h_mm * VMM))
    w_px = int(round(m.shape[1] / m.shape[0] * h_mm * MM))
    v = vectorise(m, h_px, w_px)
    x0 = int(round(x_mm * MM - w_px / 2))
    y0 = int(round(y_mm * VMM - h_px / 2))
    canvas[y0:y0 + h_px, x0:x0 + w_px] = np.maximum(canvas[y0:y0 + h_px, x0:x0 + w_px], v)
    return canvas


def blur(a, r):
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))) / 255.0


def lum(a):
    return a.mean(-1)


# ---------- Masks from the references ----------
gw = img(D + 'gojo_bracelet_white.png')
tj = img(D + 'toji_bracelet.png')
lk = img(D + 'logo_kanji.jpg')

gojo_name = tight(smoothstep(140, 200, gw[625:715, 500:1040].min(-1)))
g = gw[565:765, 1680:1820]
gojo_hand = tight(smoothstep(30, 90, g[..., 1] - g[..., 0]))
toji_name = tight(smoothstep(32, 14, lum(tj[570:708, 480:1052])))
toji_icon = tight(smoothstep(110, 70, lum(tj[465:675, 305:390])))

lk = lk[200:540, 20:716]
logo_line = tight(smoothstep(80, 170, lk.min(-1)))
# Toji's logo is printed with a heavier line than Gojo's neon outline.
logo_fill = np.asarray(Image.fromarray((logo_line * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) / 255.0
red = lk[..., 0] - lk[..., 1]
logo_red_full = smoothstep(30, 90, red)
ys, xs = np.where(logo_line > 0.5)
logo_red = logo_red_full[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def base(path):
    b = Image.open(path).convert('RGB').resize((W, H), Image.BICUBIC)
    return np.asarray(b).astype(np.float32) / 255.0


def text_mask(text, cap_mm, font_path, max_mm):
    """Render text with the right physical size and return (mask, width in mm)."""
    size = 400
    font = ImageFont.truetype(font_path, size)
    box = font.getbbox(text)
    im = Image.new('L', (box[2] - box[0] + 40, box[3] - box[1] + 40), 0)
    ImageDraw.Draw(im).text((20 - box[0], 20 - box[1]), text, font=font, fill=255)
    m = tight(np.asarray(im) / 255.0, 0.3)
    w_mm = m.shape[1] / m.shape[0] * cap_mm
    if w_mm > max_mm:
        # Narrow the type rather than shrinking it, like a condensed cut.
        m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
            (int(m.shape[1] * max_mm / w_mm), m.shape[0]), Image.LANCZOS)) / 255.0
    return m


def finish(name, color, groove, paint, paint_rough, glow=None):
    """Write all maps of one face."""
    g = blur(groove, 0.8)                      # soft 0.02 mm bevel on the groove edges
    # Normals of the height field h = -DEPTH * g (in mm).
    h = -DEPTH * g
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * MM / 2
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * VMM / 2
    n = np.dstack([-dx, dy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(T + f'{name}_normal.png')
    Image.fromarray((g * 255).astype(np.uint8)).save(T + f'{name}_height.png')

    # Shadow along the inside of each wall, and a darker floor.
    wall = np.clip(g - blur(g, 2.5), 0, 1) * 1.3
    ao = 1 - np.clip(wall, 0, 0.45) - 0.08 * g
    rgb = color * (1 - g[..., None]) + paint * g[..., None]
    rgb *= ao[..., None]
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(T + f'{name}_color.jpg', quality=93)

    rough = 0.62 * (1 - g) + paint_rough * g
    Image.fromarray((rough * 255).astype(np.uint8)).save(T + f'{name}_rough.png')
    if glow is not None:
        Image.fromarray((np.clip(glow, 0, 1) * 255).astype(np.uint8)).save(T + f'{name}_glow.jpg', quality=92)


saira = 'assets/fonts/SairaCondensed-Medium.ttf'

# ---------- Gojo ----------
col = base(T + 'gojo_base.jpg')
white = np.zeros((H, W))
cyan = np.zeros((H, W))
place(white, gojo_name, 84, 5.4)
place(cyan, gojo_hand, 34, 9.6)
place(cyan, logo_line, 140, 7.6)
groove = np.maximum(white, cyan)
paint = col.copy()
paint[white > 0] = [0.95, 0.94, 0.97]
paint = np.where(cyan[..., None] > 0, np.array([0.34, 0.86, 1.0]), paint)
halo = blur(cyan, 10) * 1.4 + cyan
glow = halo[..., None] * np.array([0.2, 0.75, 1.0])
finish('gojo_outer', col, groove, paint, 0.42, glow)

inner = np.zeros((H, W))
place(inner, text_mask('Throughout heaven and earth, I alone am honored', 4.6, saira, 175), 92, 4.6)
paint = np.ones_like(col) * np.array([0.94, 0.93, 0.96])
finish('gojo_inner', col, inner, paint, 0.45)

# ---------- Toji ----------
col = base(T + 'toji_base.jpg')
black = np.zeros((H, W))
place(black, toji_name, 84, 5.4)
place(black, toji_icon, 30, 10.0)
place(black, logo_fill, 140, 7.6)
reds = np.zeros((H, W))
place(reds, logo_red, 140, 7.6)
reds = reds * black
paint = np.ones_like(col) * np.array([0.06, 0.06, 0.065])
paint = paint * (1 - reds[..., None]) + np.array([0.62, 0.05, 0.08]) * reds[..., None]
finish('toji_outer', col, black, paint, 0.5)

inner = np.zeros((H, W))
quote = 'A monkey like me, incapable of using occult energy, has just surpassed all the chosen ones'
place(inner, text_mask(quote, 4.0, saira, 180), 92, 4.0)
paint = np.ones_like(col) * np.array([0.07, 0.07, 0.075])
finish('toji_inner', col, inner, paint, 0.5)

# Previews of the masks, for checking.
prev = Image.new('L', (1600, 260))
x = 0
for m in [gojo_name, gojo_hand, toji_name, toji_icon, logo_fill]:
    p = Image.fromarray((m * 255).astype(np.uint8))
    p.thumbnail((400, 250))
    prev.paste(p, (x, 0))
    x += p.width + 10
prev.save(T + 'masks_preview.png')
print('ok')
