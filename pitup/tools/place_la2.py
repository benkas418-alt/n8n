# Each spoken line starts on a beat of the music (beat list B below).
import json, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = json.load(open(f"{SP}/audio/la/pick.json"))
B = [0.5, 0.98, 1.47, 1.96, 2.42, 2.91, 3.38, 3.86, 4.35, 4.84, 5.33, 5.81, 6.28, 6.77, 7.23, 7.72, 8.18, 8.67, 9.16, 9.62, 10.09, 10.6, 11.08, 11.57, 12.04, 12.52, 12.99, 13.48, 13.94, 14.43, 14.92, 15.4, 15.87, 16.35, 16.82, 17.31, 17.79, 18.28, 18.75, 19.23, 19.72, 20.21, 20.67, 21.16, 21.65, 22.11, 22.6, 23.07, 23.55, 24.04, 24.51, 24.99, 25.48, 25.94, 26.43, 26.92, 27.38, 27.87, 28.36, 28.85, 29.31, 29.8, 30.26, 30.75, 31.24, 31.73, 32.19, 32.68, 33.14, 33.63, 34.12]   # "What Did I Miss?" (Drake), cut at 6.83 s: the stab lands on "Découvre"
B += [round(B[-1] + 0.4865 * j, 2) for j in range(1, 14)]   # same grid continued to the end
# spoken order (17 Nov.): "4b" = buyers' line after the delivery, "6" = sellers' line after "open your shop"
ORDER = ["0", "1", "2", "3", "4", "4b", "5", "6", "7", "8"]
GAP_BEFORE = {"7": 4}    # beats without voice before line 7 (category words)
places, lines, words = [], {}, []; prev = -1
for i in ORDER:
    p = P[i]; a, sr = sf.read(p["file"], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
    idx = np.where(np.abs(a) > 0.01)[0]; on, off = idx[0] / sr, idx[-1] / sr
    need = prev + 0.22
    k = next(j for j, b in enumerate(B) if b >= need) + GAP_BEFORE.get(i, 0)
    at = B[k]; places.append([p["file"], round(at - 800 / 48000, 3)]); sh = at - on
    lines[i] = [at, round(off + sh, 3)]; prev = off + sh
    words += [[w, round(s + sh, 3), round(e + sh, 3), i] for w, s, e in p["words"]]
json.dump(places, open(f"{SP}/audio/la/places.json", "w")); json.dump(lines, open(f"{SP}/audio/la/lines.json", "w"))
json.dump(words, open(f"{SP}/audio/la/words.json", "w"), ensure_ascii=False); json.dump(B, open(f"{SP}/audio/la/beats.json", "w"))
for i, (a, b) in lines.items(): print(i, a, b)
