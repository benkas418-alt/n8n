# v3: each spoken line starts on a beat of "Visa" (instrumental, cut at 6.54 s so the drop lands on "Découvre").
import json, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = json.load(open(f"{SP}/audio/la/pick.json"))
B = [0.43, 1.03, 1.63, 2.26, 2.96, 3.65, 4.28, 4.88, 5.49, 6.3, 6.9, 7.53, 8.11, 8.74, 9.46, 10.16, 10.76, 11.36, 11.97, 12.78, 13.38, 14.01, 14.61, 15.22, 15.91, 16.63, 17.24, 17.86, 18.65, 19.28, 19.88, 20.49, 21.09, 21.72, 22.42, 23.11, 23.74, 24.34, 24.95, 25.76, 26.36, 26.97, 27.57, 28.2, 28.89, 29.61, 30.22, 30.82, 31.45, 32.24, 32.84, 33.47, 34.07, 34.68]
GAP_BEFORE = {7: 3}      # three beats without voice before line 7 (category words)
places, lines, words = [], [], []; prev = -1
for i in range(9):
    p = P[str(i)]; a, sr = sf.read(p["file"], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
    idx = np.where(np.abs(a) > 0.01)[0]; on, off = idx[0] / sr, idx[-1] / sr
    need = prev + 0.22
    k = next(j for j, b in enumerate(B) if b >= need) + GAP_BEFORE.get(i, 0)
    at = B[k]; places.append([p["file"], round(at - 800 / 48000, 3)]); sh = at - on
    lines.append([at, round(off + sh, 3)]); prev = off + sh
    words += [[w, round(s + sh, 3), round(e + sh, 3), i] for w, s, e in p["words"]]
json.dump(places, open(f"{SP}/audio/la/places.json", "w")); json.dump(lines, open(f"{SP}/audio/la/lines.json", "w"))
json.dump(words, open(f"{SP}/audio/la/words.json", "w"), ensure_ascii=False); json.dump(B, open(f"{SP}/audio/la/beats.json", "w"))
for i, (a, b) in enumerate(lines): print(i, a, b)
