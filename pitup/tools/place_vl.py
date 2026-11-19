# Each spoken line starts on a beat of the music (beat list B below).
import json, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = json.load(open(f"{SP}/audio/vl/pick.json"))
B = [0.5, 0.93, 1.34, 1.76, 2.12, 2.48, 2.83, 3.18, 3.6, 4.02, 4.43, 4.85, 5.27, 5.69, 6.11, 6.52, 6.94, 7.36, 7.72, 8.08, 8.5, 8.92, 9.28, 9.64, 10.05, 10.47, 10.89, 11.31, 11.73, 12.14, 12.56, 12.98, 13.41, 13.84, 14.32, 14.81, 15.3, 15.79, 16.21, 16.63, 17.05, 17.46, 17.89, 18.32, 18.81, 19.3, 19.71, 20.13, 20.49, 20.85, 21.27, 21.69, 22.11, 22.52, 22.94, 23.36, 23.78, 24.2]   # Raindance (Dave & Tems) from 141.65 s, half-beat grid
B += [round(B[-1] + 0.42 * j, 2) for j in range(1, 14)]   # same grid continued to the end
# delivery video order (18 Nov.): "8" = the validated end line of the launch film
# spoken order (17 Nov.): "4b" = buyers' line after the delivery, "6" = sellers' line after "open your shop"
ORDER = ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "6", "8"]
GAP_BEFORE = {"v2": 1, "v3": 2, "v6": 1}   # let the city and the client breathe
places, lines, words = [], {}, []; prev = -1
for i in ORDER:
    p = P[i]; a, sr = sf.read(p["file"], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
    idx = np.where(np.abs(a) > 0.01)[0]; on, off = idx[0] / sr, idx[-1] / sr
    need = prev + 0.22
    k = next(j for j, b in enumerate(B) if b >= need) + GAP_BEFORE.get(i, 0)
    at = B[k]; places.append([p["file"], round(at - 800 / 48000, 3)]); sh = at - on
    lines[i] = [at, round(off + sh, 3)]; prev = off + sh
    words += [[w, round(s + sh, 3), round(e + sh, 3), i] for w, s, e in p["words"]]
json.dump(places, open(f"{SP}/audio/vl/places.json", "w")); json.dump(lines, open(f"{SP}/audio/vl/lines.json", "w"))
json.dump(words, open(f"{SP}/audio/vl/words.json", "w"), ensure_ascii=False); json.dump(B, open(f"{SP}/audio/vl/beats.json", "w"))
for i, (a, b) in lines.items(): print(i, a, b)
