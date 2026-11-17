# Places the chosen takes on the reference music: start of each line = AT[i] (time of the first voiced sample).
# Writes audio/la/places.json (for motion_mix.py), lines.json [[start,end]] and words.json [[w,s,e,line]] in film time.
import json, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = json.load(open(f"{SP}/audio/la/pick.json"))
AT = [0.45, 5.55, 8.38, 10.75, 13.9, 16.8, 21.4, 27.2, 30.6]
places, lines, words = [], [], []
for i in range(9):
    p = P[str(i)]; a, sr = sf.read(p["file"], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
    idx = np.where(np.abs(a) > 0.01)[0]; on, off = idx[0] / sr, idx[-1] / sr
    pre = 800 / 48000                       # motion_mix keeps 800 samples before the onset
    places.append([p["file"], round(AT[i] - pre, 3)])
    sh = AT[i] - on
    lines.append([round(AT[i], 3), round(off + sh, 3)])
    words += [[w, round(s + sh, 3), round(e + sh, 3), i] for w, s, e in p["words"]]
json.dump(places, open(f"{SP}/audio/la/places.json", "w"))
json.dump(lines, open(f"{SP}/audio/la/lines.json", "w")); json.dump(words, open(f"{SP}/audio/la/words.json", "w"), ensure_ascii=False)
for i, (a, b) in enumerate(lines): print(i, a, b, round(b - a, 2), "gap->", round(lines[i + 1][0] - b, 2) if i < 8 else "")
