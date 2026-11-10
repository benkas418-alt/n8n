# ECODIM — t-shirt de Noël « Pas de place à Bethléem »

Run from this folder:

```bash
python3 -I scripts/extract.py .            # design elements -> out/elements/, out/planche_controle_decoupes.png
python3 -I scripts/layout.py . 50 150      # out/layout.json + print files (L = 50 cm, 150 dpi)
```

- `affiche.jpg`, `logo.png`: official sources.
- `out/layout.json`: positions in units of L (chest width). The mockups must reuse it.
- `out/impression_devant_*.png`, `out/impression_dos_*.png`: transparent black print files.
- The photo mockups (steps 1, 4 and 5) are not done: see `sources.txt`.
