# Word leveler: lift only the words that sit far under the voice median (TTS prosody dips the music would mask).
# Gain per word = clip(median - 4 dB - word level, 0, 6 dB), applied with 40 ms ramps. Silences and other words untouched.
# usage (fw python): level_words.py in.wav out.wav
import sys, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
n = int(len(a) * 16000 / sr); y = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
r, _ = WhisperModel("medium", compute_type="int8").transcribe(y, language="fr", beam_size=5, word_timestamps=True, initial_prompt="Lubumbashi. PitUp.")
W = [(w.word.strip(), w.start, w.end) for s in r for w in s.words]
def lv(s, e):
    x = a[int(s * sr):int(e * sr)]; F = int(.06 * sr)
    if len(x) < F: return -99
    return max(20 * np.log10(np.sqrt((x[k:k + F] ** 2).mean()) + 1e-9) for k in range(0, len(x) - F + 1, F // 3))
L = [lv(s, e) for _, s, e in W]; med = float(np.median([l for l in L if l > -60]))
g = np.zeros(len(a), np.float32); R = int(.04 * sr)
for (w, s, e), l in zip(W, L):
    d = float(np.clip(med - 4 - l, 0, 6))
    if d < 0.5 or l < -60: continue
    i0, i1 = max(0, int((s - .02) * sr)), min(len(a), int((e + .02) * sr))
    env = np.full(i1 - i0, d, np.float32); k = min(R, (i1 - i0) // 2)
    env[:k] *= np.linspace(0, 1, k); env[-k:] *= np.linspace(1, 0, k); g[i0:i1] = np.maximum(g[i0:i1], env)
    print(f"  +{d:.1f} dB  {w} @{s:.2f}")
out = a * 10 ** (g / 20)
pk = float(np.abs(out).max()); out = out * (0.95 / pk) if pk > 0.95 else out
sf.write(sys.argv[2], out, sr); print("median", round(med, 1), "peak", round(float(np.abs(out).max()), 3))
