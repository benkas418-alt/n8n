# Each spoken line starts on a beat of the music (beat list B below).
import json, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = json.load(open(f"{SP}/audio/cl/pick.json"))
B = [0.51, 0.93, 1.35, 1.77, 2.18, 2.6, 3.02, 3.44, 3.85, 4.28, 4.71, 5.13, 5.55, 5.97, 6.39, 6.8, 7.22, 7.64, 8.06, 8.48, 8.89, 9.31, 9.73, 10.15, 10.57, 11.0, 11.42, 11.84, 12.26, 12.68, 13.1, 13.5, 13.91, 14.34, 14.77, 15.18, 15.6, 16.02, 16.44, 16.87, 17.3, 17.71, 18.13, 18.55, 18.97, 19.39, 19.81, 20.23, 20.64, 21.06, 21.48, 21.89, 22.31, 22.74, 23.17, 23.59, 24.01, 24.41, 24.82, 25.25, 25.68]   # "Obsessed With You" (Central Cee) from 13.04 s, half-beat grid (72 BPM)
B += [round(B[-1] + 0.418 * j, 2) for j in range(1, 14)]   # same grid continued to the end
# delivery video order (18 Nov.): "8" = the validated end line of the launch film
# spoken order (17 Nov.): "4b" = buyers' line after the delivery, "6" = sellers' line after "open your shop"
ORDER = ["0a", "0b", "1", "2", "3", "4", "5", "6", "8"]
GAP_BEFORE = {"4": 7}    # beats without voice after "nous te livrons": the delivery rushes play
places, lines, words = [], {}, []; prev = -1
for i in ORDER:
    p = P[i]; a, sr = sf.read(p["file"], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
    idx = np.where(np.abs(a) > 0.01)[0]; on, off = idx[0] / sr, idx[-1] / sr
    need = prev + 0.22
    k = next(j for j, b in enumerate(B) if b >= need) + GAP_BEFORE.get(i, 0)
    at = B[k]; places.append([p["file"], round(at - 800 / 48000, 3)]); sh = at - on
    lines[i] = [at, round(off + sh, 3)]; prev = off + sh
    words += [[w, round(s + sh, 3), round(e + sh, 3), i] for w, s, e in p["words"]]
json.dump(places, open(f"{SP}/audio/cl/places.json", "w")); json.dump(lines, open(f"{SP}/audio/cl/lines.json", "w"))
json.dump(words, open(f"{SP}/audio/cl/words.json", "w"), ensure_ascii=False); json.dump(B, open(f"{SP}/audio/cl/beats.json", "w"))
for i, (a, b) in lines.items(): print(i, a, b)
