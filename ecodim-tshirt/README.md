# ECODIM — t-shirt de Noël « Pas de place à Bethléem »

Run from this folder:

```bash
python3 -I scripts/extract.py .            # design elements -> out/elements/, out/planche_controle_decoupes.png
python3 -I scripts/layout.py . 50 150      # out/layout.json + print files (L = 50 cm, 150 dpi)
python3 -I scripts/mockup.py .             # 6 photo mockups, 6 boards, out/apercu_6_variantes.png
```

- `affiche.jpg`, `logo.png`: official sources.
- `out/layout.json`: positions in units of L (chest width). The mockups must reuse it.
- `out/impression_devant_*.png`, `out/impression_dos_*.png`: transparent black print files.
- `photos/`: one front photo per variant (supplied by the owner, licence unknown: see `sources.txt`).
- No back photo was supplied: the back is shown flat at the same scale.
