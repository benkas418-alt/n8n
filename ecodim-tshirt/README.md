# ECODIM — t-shirt de Noël « Pas de place à Bethléem »

Run from this folder:

```bash
python3 -I scripts/extract.py .            # design elements -> out/elements/, out/planche_controle_decoupes.png
python3 -I scripts/layout.py . 50 150      # out/layout.json + print files (L = 50 cm, 150 dpi)
python3 -I scripts/sr_photos.py . <sr.js>   # optional: remove neck labels + x4 ESRGAN -> photos_x4/
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
