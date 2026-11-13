# Voice QA 3d: word endings that stop dead before a pause (> 20 dB drop in 30 ms, then >= 200 ms of quiet).
import sys, numpy as np, soundfile as sf
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1); F = int(.005 * sr)
E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
sp = np.median(E[E > -40]); out = []
for k in range(6, len(E) - 40):
    if E[k - 6] > sp - 12 and E[k] < E[k - 6] - 20 and (E[k:k + 40] < sp - 25).all() and (not out or k * .005 - out[-1][0] > .3):
        out.append((round(k * .005, 2), round(float(E[k - 6] - E[k]), 1)))
print(("FAIL" if out else "ok  "), "dead word endings before pauses (t, dB dropped in 30 ms):", out)
