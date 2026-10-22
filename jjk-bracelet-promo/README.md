# Cursed Collection — promo video

A 32.5 s vertical (1080×1920, 30 fps) motion design ad for two engraved
silicone bracelets: Satoru Gojo and Toji Zen'in. The cuts follow the beat
grid of the opening "Kaikai Kitan" (~123 BPM, first hit at 2.76 s, drop at 5.97 s).

Output: `out/cursed-collection-promo.mp4`

## Edit the texts

Open `index.html` and change `CONFIG` (brand, call to action, contact).

## Preview and render

Run from this folder:

```bash
npm install
python3 -m http.server 8000                      # open http://localhost:8000 to preview the loop
node scripts/render.mjs --music <song.mp3> --out out/cursed-collection-promo.mp4
node scripts/render.mjs --stills 3.6,11.2,25.4   # quick still frames
```

`render.mjs` uses Chromium at `/opt/pw-browsers/...`. Set `CHROME_PATH` on another machine.

## Assets

- `scripts/key.py` removes the green and orange screens from the clips (WebP sequences in `assets/seq/`).
- `scripts/cutout.py` cuts the Gojo bracelet render out of its white background.
- `scripts/prep_images.py` makes the crops and rotations.

| Time (s) | Scene |
|---|---|
| 0 – 2.76 | Intro: 呪, red line |
| 2.76 – 5.97 | Domain expansion, "2 bracelets / 2 legends" |
| 5.97 – 13.77 | Gojo: clip, manga panels, product, inside engraving |
| 13.77 – 15.72 | Transition: blade and chain, 術師殺し |
| 15.72 – 23.52 | Toji: clip, manga panels, product, inside engraving |
| 23.52 – 27.42 | The pair and its features |
| 27.42 – 32.5 | Call to action |
