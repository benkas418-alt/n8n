"""Make the source maps for the 3D bracelets.

- Cloudy silicone colour, seamless on both axes (FFT-filtered noise).
- Icon and logo masks (white = engraved) taken from the reference images.
"""
import numpy as np
from PIL import Image, ImageFilter

D = 'assets/img/'
T = 'assets/tex/'
rng = np.random.default_rng(7)


def cloud(w, h, beta, seed):
    """Seamless fractal noise in 0..1."""
    g = np.random.default_rng(seed).normal(size=(h, w))
    # The band is 202 x 12 mm, so a texel is twice as wide as it is tall.
    fy = np.fft.fftfreq(h)[:, None] / (12 / h)
    fx = np.fft.fftfreq(w)[None, :] / (202 / w)
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1
    # Cut frequencies below 1/20 mm so the blobs stay about a finger wide.
    n = np.real(np.fft.ifft2(np.fft.fft2(g) / f ** beta * (1 - np.exp(-(f * 20) ** 2))))
    n = (n - n.mean()) / n.std()
    return 1 / (1 + np.exp(-1.6 * n))


def mix(a, b, t):
    return a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]


W, H = 4096, 512
big = cloud(W, H, 1.6, 1)
fine = cloud(W, H, 1.0, 2)

# Gojo: black and violet tie-dye clouds.
t = np.clip((big - 0.45) * 2.2 + (fine - 0.5) * 0.35, 0, 1)
gojo = mix(np.array([10, 8, 14.]), np.array([118, 46, 196.]), t ** 1.2)
gojo += (np.clip(t - 0.75, 0, 1) * 4)[..., None] * np.array([70, 40, 90.])
Image.fromarray(gojo.clip(0, 255).astype(np.uint8)).save(T + 'gojo_base.jpg', quality=94)

# Toji: concrete grey with lighter worn patches.
t = np.clip((big - 0.45) * 2.0, 0, 1)
toji = mix(np.array([92, 92, 90.]), np.array([182, 174, 160.]), t)
toji *= (0.88 + 0.24 * fine)[..., None]
speck = cloud(W, H, 0.3, 3)
toji *= (1 - np.clip(speck - 0.82, 0, 1) * 1.5)[..., None]
Image.fromarray(toji.clip(0, 255).astype(np.uint8)).save(T + 'toji_base.jpg', quality=94)

# Silicone micro surface for the bump map.
Image.fromarray((cloud(1024, 1024, 0.15, 4) * 255).astype(np.uint8)).save(T + 'micro.png')


def mask_from(src, box, fn, size):
    a = np.asarray(Image.open(D + src).convert('RGB').crop(box)).astype(np.float32)
    m = fn(a[..., 0], a[..., 1], a[..., 2])
    img = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8))
    img = img.resize(size, Image.LANCZOS) if size else img
    return img


# Gojo hand sign: cyan line art inside the swatch of the spec sheet.
mask_from('gojo_sheet.png', (1395, 500, 1580, 668),
          lambda r, g, b: (b - r - 30) / 60, (740, 672)).save(T + 'icon_gojo.png')
# Logo: white outline of the kanji title; red drips go in a second mask.
mask_from('logo_kanji.jpg', (30, 240, 706, 500), lambda r, g, b: (np.minimum(r, np.minimum(g, b)) - 90) / 90,
          None).save(T + 'logo_line.png')
mask_from('logo_kanji.jpg', (30, 240, 706, 500), lambda r, g, b: (r - g - 40) / 60,
          None).save(T + 'logo_red.png')
# Toji blade: light metal on black.
mask_from('toji_blade_chain.jpg', (230, 370, 470, 1000), lambda r, g, b: (r - 50) / 80,
          None).save(T + 'icon_toji.png')
print('ok')
