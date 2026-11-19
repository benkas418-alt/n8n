# Each spoken line starts on a beat of the music (beat list B below).
import json, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = json.load(open(f"{SP}/audio/cl/pick.json"))
B = [0.51, 1.04, 1.58, 2.11, 2.65, 3.18, 3.72, 4.25, 4.78, 5.32, 5.85, 6.39, 6.92, 7.48, 7.99, 8.54, 9.08, 9.61, 10.15, 10.68, 11.22, 11.75, 12.28, 12.82, 13.35, 13.89, 14.42, 14.98, 15.49, 16.04, 16.58, 17.11, 17.65, 18.18, 18.72, 19.25, 19.78, 20.32, 20.85, 21.39, 21.92, 22.45, 22.99, 23.55, 24.08, 24.61, 25.15, 25.68, 26.15]   # Tems "Me & U" from 43.97 s (112 BPM)
B += [round(B[-1] + 0.535 * j, 2) for j in range(1, 14)]   # same grid continued to the end
# delivery video order (18 Nov.): "8" = the validated end line of the launch film
# spoken order (17 Nov.): "4b" = buyers' line after the delivery, "6" = sellers' line after "open your shop"
ORDER = ["0a", "0b", "1", "2", "3", "4", "5", "6", "8"]
GAP_BEFORE = {"4": 6}    # beats without voice after "nous te livrons": the delivery rushes play
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
