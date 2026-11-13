# Sister voice takes: filter C, cut the throwaway words ("Bon, alors." / "Voilà, merci.") in the silences around them,
# report median pitch (takes that fall to ~100 Hz are rejected). usage (fw python): prep_soeur.py in.wav out.wav
import sys, subprocess, numpy as np, soundfile as sf, re
from faster_whisper import WhisperModel
src, dst = sys.argv[1], sys.argv[2]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", "highpass=f=80,lowpass=f=8500,afftdn=nr=10:nf=-45,equalizer=f=3500:t=q:w=1.5:g=-2",
                "-ar", "48000", "-ac", "1", "-c:a", "pcm_f32le", "/tmp/ps_c.wav"], check=True)
a, sr = sf.read("/tmp/ps_c.wav", dtype="float32")
n = int(len(a) * 16000 / sr); y = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
r, _ = WhisperModel("medium", compute_type="int8").transcribe(y, language="fr", beam_size=5, word_timestamps=True)
W = [(w.word.strip(), w.start, w.end) for s in r for w in s.words]
F = int(.01 * sr); E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
norm = lambda t: re.sub(r"[^a-zà-ÿ]", "", t.lower())
def valley(t0, t1):
    i0, i1 = int(t0 * 100), max(int(t0 * 100) + 1, int(t1 * 100) + 1); k = i0 + int(np.argmin(E[i0:i1])); return k / 100, E[k]
ia = next((i for i, w in enumerate(W[:6]) if norm(w[0]) == "alors"), None)
iv = next((i for i in range(len(W) - 1, max(0, len(W) - 6), -1) if norm(W[i][0]).startswith("voil")), None)
if ia is None or iv is None: print("SKIP: throwaway words not found:", " ".join(w[0] for w in W[:5]), "...", " ".join(w[0] for w in W[-4:])); sys.exit(1)
c0, l0 = valley(W[ia][2] - 0.05, W[ia + 1][1] + 0.05); c1, l1 = valley(W[iv - 1][2] - 0.05, W[iv][1] + 0.05)
seg = a[int(c0 * sr):int(c1 * sr)].copy(); m = int(.01 * sr); seg[:m] *= np.linspace(0, 1, m); m = int(.04 * sr); seg[-m:] *= np.linspace(1, 0, m)
sf.write(dst, seg, sr)
x = seg; N = int(.04 * sr); f0 = []
for k in range(0, len(x) - N, int(.01 * sr)):
    s = x[k:k + N] - x[k:k + N].mean()
    if 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9) < -30: continue
    rr = np.correlate(s, s, "full")[N - 1:]; rr /= rr[0] + 1e-12; lo, hi = int(sr / 400), int(sr / 70); j = lo + int(np.argmax(rr[lo:hi]))
    if rr[j] > 0.5: f0.append(sr / j)
print(f"cut {c0:.2f}s ({l0:.0f} dB) .. {c1:.2f}s ({l1:.0f} dB) | median pitch {np.median(f0):.0f} Hz | {' '.join(w[0] for w in W[ia+1:iv])}")
