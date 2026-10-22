# Cursed Collection — promo video

A vertical (1080×1920, 60 fps) motion design ad for two engraved silicone
bracelets: Toji Zen'in and Satoru Gojo. The cuts follow the beat grid of the
opening "Kaikai Kitan" (~123 BPM, first hit at 2.76 s, drop at 5.97 s).

- V2 (current): `index.html` → `out/cursed-collection-promo-v2.mp4`
- V1: `index-v1.html` → `out/cursed-collection-promo.mp4`

## What is in V2

- Type: JJK font for names, Poppins for information, Instrument Serif italic for the voice.
- Real-time 3D bracelets (`bracelet3d.js`, three.js): 202 × 12 × 2 mm band with rounded
  edges, debossed engraving (bump map), silicone material, studio light, depth of field.
  The camera skims the outside engraving, the inside quote, then a turntable.
- Story order: Toji → the fight (one manga page, panels on the beat) → Hollow Purple
  (drawn in code) → Gojo → the two rings linked → call to action.

## Edit the texts

Open `index.html` and change `CONFIG` (brand, call to action, contact).

## Preview and render

Run from this folder:

```bash
npm install
python3 -m http.server 8000                      # open http://localhost:8000 to preview the loop
node scripts/render.mjs --music <song.mp3> --out out/cursed-collection-promo-v2.mp4
node scripts/render.mjs --stills 8.6,12.6,26.6   # quick still frames
```

`render.mjs` uses Chromium at `/opt/pw-browsers/...` with SwiftShader for WebGL.
Set `CHROME_PATH` on another machine. A full 60 fps render takes about 20–30 minutes
on a CPU-only machine.

## Assets

- `scripts/key.py` removes the green and orange screens from the clips (WebP sequences in `assets/seq/`).
- `scripts/prep_textures.py` makes the silicone colour maps and the icon and logo masks (`assets/tex/`).
- `scripts/prep_images.py` makes the crops and rotations.
- Fonts: Poppins and Instrument Serif (SIL Open Font License, see `assets/fonts/OFL-*.txt`),
  JJK font (free for commercial use, per its readme).

| Time (s) | Scene |
|---|---|
| 0 – 2.76 | Intro: 呪, "Deux légendes. Gravées." |
| 2.76 – 5.97 | Domain expansion, zoom into the hands |
| 5.97 – 7.92 | Toji: keyed clip, name, kanji |
| 7.92 – 13.77 | Toji bracelet 3D: outside macro, inside quote, turntable |
| 13.77 – 15.72 | The fight: manga page, panels on the beat |
| 15.72 – 17.67 | Hollow Purple: red and blue merge |
| 17.67 – 19.62 | Gojo: keyed clip, name, kanji |
| 19.62 – 25.48 | Gojo bracelet 3D: outside macro, inside quote, turntable |
| 25.48 – 29.38 | The two rings linked, features |
| 29.38 – 33.98 | Call to action |
