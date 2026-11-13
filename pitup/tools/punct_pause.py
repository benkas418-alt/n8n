# Gives a voice take the pauses its punctuation asks for: silence is inserted (never time-stretching) at the quietest
# point between the two words, so a period breathes ~0.75 s and a comma ~0.38 s. Writes the time map for the edit.
# usage: punct_pause.py in.wav words.json out.wav '[[word_index, target_pause(, cut_time)], ...]'
import json, sys, numpy as np, soundfile as sf
src, wj, dst, plan = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
a, sr = sf.read(src, dtype="float32"); mono = a if a.ndim == 1 else a.mean(1); a = a if a.ndim == 2 else a[:, None]
W = json.load(open(wj)); FR = int(0.01 * sr)
E = np.array([np.sqrt((mono[k:k + FR] ** 2).mean()) for k in range(0, len(mono) - FR, FR)])
cuts = []
for item in plan:
    i, target = item[0], item[1]
    e, s = W[i][2], W[i + 1][1]
    if len(item) > 2: e = s = item[2]          # a cut time measured by hand when whisper places the words badly
    lo, hi = int((min(e, s) - 0.06) * 100), int((max(e, s) + 0.06) * 100)
    k = lo + int(np.argmin(E[lo:hi])); c = k / 100 + 0.005
    # the silence already there (frames under the quiet floor around the cut)
    q = 0.12 * np.median(E[E > 0.01]); l = k; r = k
    while l > 0 and E[l - 1] < q: l -= 1
    while r < len(E) - 1 and E[r + 1] < q: r += 1
    have = (r - l + 1) / 100 if E[k] < q else 0.0
    add = max(0.0, target - have); cuts.append((c, add)); print(f"after «{W[i][0]}» cut {c:.2f}s had {have:.2f}s add {add:.2f}s")
out, last, F = [], 0, int(0.012 * sr)
for c, add in sorted(cuts):
    j = int(c * sr); seg = a[last:j].copy()
    if add > 0: seg[-F:] *= np.linspace(1, 0, F)[:, None]
    out.append(seg)
    if add > 0:
        out.append(np.zeros((int(add * sr), a.shape[1]), np.float32)); nxt = a[j:j + F].copy() * np.linspace(0, 1, F)[:, None]; a[j:j + F] = nxt
    last = j
out.append(a[last:]); y = np.concatenate(out); sf.write(dst, y if y.shape[1] > 1 else y[:, 0], sr)
json.dump(sorted(cuts), open(dst + ".map.json", "w")); print("in", round(len(mono) / sr, 2), "out", round(len(y) / sr, 2))
