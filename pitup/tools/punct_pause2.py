# Punctuation pauses with verified cut points. For each pause, the candidates are the energy valleys near the word
# boundary; a candidate is kept only if whisper hears the expected last word on its left and the expected next word on
# its right (so no word is ever split). Silence is then inserted there (never time-stretching).
# usage: punct_pause2.py in.wav words.json out.wav '[[word_index, pause, "left", "right"], ...]'   (run with fw python)
import json, sys, re, unicodedata, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
src, wj, dst, plan = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
a, sr = sf.read(src, dtype="float32"); a = a if a.ndim == 2 else a[:, None]; mono = a.mean(1)
W = json.load(open(wj)); FR = int(0.01 * sr)
E = np.array([np.sqrt((mono[k:k + FR] ** 2).mean()) for k in range(0, len(mono) - FR, FR)])
Es = np.convolve(E, np.ones(3) / 3, "same")
M = WhisperModel("medium", compute_type="int8")
def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z]+", " ", t).split()
def hear(x0, x1):
    i0, i1 = max(0, int(x0 * sr)), min(len(mono), int(x1 * sr)); seg = mono[i0:i1]
    n16 = int(len(seg) * 16000 / sr); seg16 = np.interp(np.linspace(0, len(seg) - 1, n16), np.arange(len(seg)), seg).astype(np.float32)
    s, _ = M.transcribe(seg16, language="fr", initial_prompt="Lubumbashi. PitUp.", beam_size=5)
    return norm(" ".join(x.text for x in s))
cuts = []
for item in plan:
    i, target, L, R = item[:4]
    if len(item) > 4:                      # cut checked by ear-test with a wider window
        c = item[4]; k = int(round((c - 0.005) * 100)); ok = (c, k); print(f'  «{L}|{R}» forced {c:.2f}')
    else: ok = None
    if ok is None:
     wb = (W[i][2] + W[i + 1][1]) / 2; lo, hi = int((wb - 0.32) * 100), int((wb + 0.32) * 100)
     mins = [k for k in range(lo + 1, hi - 1) if Es[k] <= Es[k - 1] and Es[k] <= Es[k + 1]]
     mins.sort(key=lambda k: Es[k] * (1 + 2.5 * abs(k / 100 - wb)))
     for k in mins[:7]:
         c = k / 100 + 0.005; left, right = hear(c - 1.3, c), hear(c, c + 1.3)
         good = left and right and left[-1] == norm(L)[-1] and right[0] == norm(R)[0]
         print(f"  «{L}|{R}» try {c:.2f} E={Es[k]:.3f} heard ...{' '.join(left[-2:])} | {' '.join(right[:2])}... {'OK' if good else 'no'}", flush=True)
         if good: ok = (c, k); break
    if not ok: print(f"!! no clean cut for «{L}|{R}»: left as it is"); continue
    c, k = ok; q = 0.12 * np.median(E[E > 0.01]); l = r = k
    while l > 0 and E[l - 1] < q: l -= 1
    while r < len(E) - 1 and E[r + 1] < q: r += 1
    have = (r - l + 1) / 100 if E[k] < q else 0.0
    cuts.append((c, max(0.0, target - have)))
# smooth pauses: a 45 ms fade-out into the pause, a 30 ms fade-in after it, and the pause filled with the take's own
# room tone (never digital silence, which sounds like the voice is cut off)
FO, FI = int(0.045 * sr), int(0.03 * sr)
floor = float(np.percentile(E[E > 0], 8)); rng = np.random.default_rng(1)
def tone(n_):
    nz = rng.standard_normal((n_, a.shape[1])).astype(np.float32)
    k = np.ones(24) / 24; nz = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 0, nz)
    return nz / (np.sqrt((nz ** 2).mean()) + 1e-9) * floor * 0.8
out, last = [], 0
for c, add in sorted(cuts):
    j = int(c * sr); seg = a[last:j].copy()
    if add > 0:
        seg[-FO:] *= (np.cos(np.linspace(0, np.pi / 2, FO)) ** 2)[:, None]; out.append(seg); out.append(tone(int(add * sr)))
        a[j:j + FI] *= (np.sin(np.linspace(0, np.pi / 2, FI)) ** 2)[:, None]
    else: out.append(seg)
    last = j
out.append(a[last:]); y = np.concatenate(out); sf.write(dst, y if y.shape[1] > 1 else y[:, 0], sr)
json.dump(sorted(cuts), open(dst + ".map.json", "w")); print("in", round(len(mono) / sr, 2), "out", round(len(y) / sr, 2))
