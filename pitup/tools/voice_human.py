# How close is a cloned take to the sister's REAL voice? Prints, for each file: intonation range (semitones, 5-95 %),
# median pitch, share of pauses (>= 0.2 s), longest pause, and spectral balance of the voiced frames.
# Real voice (her 99 s recording): range about 12 st, 200 Hz, almost no pause over 0.3 s, 4-8 kHz about -9 dB.
# usage (voxcpm python): voice_human.py a.wav b.wav ...
import sys, numpy as np, soundfile as sf, librosa
from scipy.signal import stft
for f in sys.argv[1:]:
    a, sr = sf.read(f, dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
    y = librosa.resample(a, orig_sr=sr, target_sr=16000)
    f0, _, _ = librosa.pyin(y, fmin=130, fmax=420, sr=16000, frame_length=1024); f0 = f0[~np.isnan(f0)]
    st = 12 * np.log2(f0 / np.median(f0))
    F = int(.02 * sr); E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
    sp = np.median(E[E > E.max() - 25]); sil = E < sp - 25; runs = []; k = 0
    while k < len(sil):
        if sil[k]:
            j = k
            while j < len(sil) and sil[j]: j += 1
            if (j - k) * .02 >= .2 and k > 10 and j < len(sil) - 10: runs.append((j - k) * .02)
            k = j
        else: k += 1
    fr, t, Z = stft(a, sr, nperseg=2048); P = np.abs(Z) ** 2; e = 10 * np.log10(P.sum(0) + 1e-12); m = P[:, e > e.max() - 25].mean(1)
    b = lambda lo, hi: 10 * np.log10(m[(fr >= lo) & (fr < hi)].sum() / m.sum() + 1e-12)
    print(f"{f.split('/')[-1]:22s} {len(a)/sr:5.1f}s f0 {np.median(f0):3.0f} Hz range {np.percentile(st,95)-np.percentile(st,5):4.1f} st | pauses {len(runs)}, {100*sum(runs)/(len(a)/sr):2.0f}% of time, longest {max(runs) if runs else 0:.2f}s | "
          f"<250 {b(0,250):5.1f} 250-1k {b(250,1000):5.1f} 1-2k {b(1000,2000):5.1f} 2-4k {b(2000,4000):5.1f} 4-8k {b(4000,8000):5.1f} 8-16k {b(8000,16000):5.1f} | voice-noise {sp-np.percentile(E,5):.0f} dB")
