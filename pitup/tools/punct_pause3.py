# Pauses without audible cuts. The cut points are already verified (punct_pause2 / ear test).
# v2 faded the voice into a synthetic hiss at -40 dB, while other gaps stayed digital silence: the background jumped
# and the ear heard every cut. Here: long cos fades into true silence at each cut, then ONE constant room-tone bed
# (mic-like pink noise, same level everywhere) under the whole take, so the background never stops or changes.
# usage: punct_pause3.py in.wav out.wav '[[cut_s, add_s], ...]' [bed_dbfs=-60]
import json, sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
src, dst, plan = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]); bed_db = float(sys.argv[4]) if len(sys.argv) > 4 else -60.0
a, sr = sf.read(src, dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
FO, FI = int(0.07 * sr), int(0.035 * sr)
out, last = [], 0
for c, add in sorted(plan):
    j = int(c * sr); seg = a[last:j].copy()
    if add > 0:
        q = 0; st = int(0.005 * sr)   # fade only over the quiet tail already there, so no word ending is eaten
        while q < FO and np.sqrt((seg[len(seg) - q - st:len(seg) - q] ** 2).mean()) < 0.018: q += st
        n = min(max(q, int(0.05 * sr)), len(seg)); seg[-n:] *= np.cos(np.linspace(0, np.pi / 2, n)) ** 2
        out += [seg, np.zeros(int(add * sr), np.float32)]
        m = min(FI, len(a) - j); a[j:j + m] *= np.sin(np.linspace(0, np.pi / 2, m)) ** 2
    else: out.append(seg)
    last = j
out.append(a[last:]); y = np.concatenate(out)
# room-tone bed: pink noise (1/f by summing octave-filtered white noise), band-limited like the voice chain
rng = np.random.default_rng(7); w = rng.standard_normal(len(y)).astype(np.float32)
f = np.fft.rfft(w); fr = np.fft.rfftfreq(len(w), 1 / sr); f[1:] /= np.sqrt(fr[1:]); f[0] = 0; p = np.fft.irfft(f, len(w)).astype(np.float32)
p = sosfilt(butter(2, [100, 7000], "bandpass", fs=sr, output="sos"), p).astype(np.float32)
p *= 10 ** (bed_db / 20) / (np.sqrt((p ** 2).mean()) + 1e-12)
r = int(0.25 * sr); p[:r] *= np.linspace(0, 1, r); p[-r:] *= np.linspace(1, 0, r)
y = y + p; sf.write(dst, y, sr)
json.dump(sorted(plan), open(dst + ".map.json", "w")); print("in", round(len(a) / sr, 2), "out", round(len(y) / sr, 2))
