# Cursed Collection — promo video

A vertical (1080×1920, 60 fps) motion design ad for two engraved silicone
bracelets: Toji Zen'in and Satoru Gojo. The cuts follow the beat grid of the
opening "Kaikai Kitan" (~123 BPM, first hit at 2.76 s, drop at 5.97 s).

- V4 (current): `index.html` → `out/otaku-drift-gojo-toji-v4.mp4`
- V3: `out/otaku-drift-gojo-toji-v3.mp4`
- V2: `out/cursed-collection-promo-v2.mp4` (source in git history)
- V1: `index-v1.html` → `out/cursed-collection-promo.mp4`

## What changed in V4: details a fan recognises

- 帳 (the curtain): black liquid drips from the sky and turns it to night while the chant
  「闇より出でて闇より黒く　その穢れを禊ぎ祓え」 appears, before the logo.
- 黒閃 (Black Flash): black lightning with red edges on the "Toji vs Gojo" hit and on the
  linked rings. It is not used on Toji alone, because he has no cursed energy.
- 無量空処 (Unlimited Void): Gojo's domain, an information storm, behind his jump.
- 天上天下唯我独尊: Gojo's awakening line against Toji, next to his inside quote.
- 猿 (monkey): a red seal on Toji's inside quote. 天逆鉾 names the spear panel.
- Ofuda talismans seal the screen and burn away before the call to action.
- 四つ巴: the four-comma emblem of the Jujutsu High uniform buttons signs Otaku Drift.

## What changed in V3

- Brand: Otaku Drift. The call to action shows a WhatsApp button with the number.
- Intro: the Jujutsu Kaisen logo with a moving light and rays.
- Edit style: hard cuts on every beat, one colour grade per character (red for Toji,
  violet-blue for Gojo), RGB split, two-frame negative hits, punch-ins, light leaks.
- Bracelets: names, icons and logos are taken from the reference renders
  (`scripts/make_bracelet_maps.py`). The engraving is cut 0.45 mm into the geometry,
  with groove walls, inner shadow and paint on the floor. A softbox sweeps across the band.

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
Set `CHROME_PATH` on another machine. A full 60 fps render takes about 1 h 40 min
on a CPU-only machine.

## Assets

- `scripts/key.py` removes the green and orange screens from the clips (WebP sequences in `assets/seq/`).
- `scripts/prep_textures.py` makes the silicone colour noise (`assets/tex/*_base.jpg`).
- `scripts/make_bracelet_maps.py` makes the colour, height, normal, roughness and glow maps of each face.
- `scripts/prep_images.py` makes the crops and rotations.
- Fonts: Poppins, Instrument Serif and Saira Condensed (SIL Open Font License, see `assets/fonts/OFL-*.txt`),
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
