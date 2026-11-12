# ECODIM — t-shirt de Noël « Pas de place à Bethléem »

Run from this folder:

```bash
python3 -I scripts/extract.py .            # design elements -> out/elements/, out/planche_controle_decoupes.png
python3 -I scripts/layout.py . 50 150      # out/layout.json + print files (L = 50 cm, 150 dpi)
python3 -I scripts/sr_photos.py . <sr.js>   # optional: remove neck labels + x4 ESRGAN -> photos_x4/
python3 -I scripts/vectorize.py . 500      # SVG print files in out/svg/ (needs potrace; L = 500 mm)
python3 -I scripts/mockup.py .             # 6 photo mockups (4000 px), 6 boards, overview (+ _HD 3920 px)
```

- `affiche.jpg`, `logo.png`: official sources.
- `out/layout.json`: positions in units of L (chest width). The mockups must reuse it.
- `out/impression_devant_*.png`, `out/impression_dos_*.png`: transparent black print files.
- `photos/`: one front photo per variant (supplied by the owner, licence unknown: see `sources.txt`).
- No back photo was supplied: the back is shown flat at the same scale.

## Upscale (x4)

`scripts/sr_photos.py` runs the ESRGAN model `@upscalerjs/esrgan-medium` (MIT, npm) with
TensorFlow.js (wasm backend) through a small node script `sr.js` (tiles of 128 px). Setup:
`npm install --legacy-peer-deps @upscalerjs/esrgan-medium@1.0.0 @tensorflow/tfjs@4.22.0 @tensorflow/tfjs-backend-wasm@4.22.0`.
The model removes JPEG artefacts and sharpens edges. It does not add real fabric detail.

## SVG

`out/svg/impression_devant_noir.svg` and `impression_dos_noir.svg` are the print files: one black ink,
real size (width L = 50 cm), one group per element. `variante_XX_*_{devant,dos}.svg` show each variant
(ink colour on a fabric-colour background). The curves are an automatic trace (potrace) of small sources:
contours are slightly irregular at large size, and the thinnest lines of the round symbol are broken.

## Print folder (current)

`python3 -I scripts/symbole_logo.py .` redraws the round symbol (circles, dove, book, text in Open Sans)
and sets the three logo lines in Open Sans Condensed Bold. Then run `vectorize.py`, `mockup.py` and
`imprimer.py`: `a_imprimer/` holds the print PNGs per colour, a measurements sheet and the logo alone.
SVG rendering uses Chromium (`scripts/render_svg.js`) because the symbol uses an SVG mask.
