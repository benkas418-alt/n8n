# Pick one take per line for the duo voice-over (sister + young man) and write place.json for build_duo.py.
# step 1 (fw python):      pick_duo.py tr  <dir>          -> <dir>/tr.json  (whisper medium, word times)
# step 2 (voxcpm python):  pick_duo.py pick <dir> <script.json> <sister_ref.wav> <boy_ref.wav>
# script.json: [{"who": "f"|"g", "prefix": "f0"|"g_0", "text": "display text"}, ...]; takes are <prefix>_<k>.wav.
# Choice: exact text first (word error count), then for the sister a pitch near the film median (195-235 Hz),
# for the young man the closest timbre (resemblyzer); then the fewer short energy dips (less choppy).
import sys, glob, json, os, re, unicodedata
import numpy as np

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("pit-ap", "pitup").replace("pitapp", "pitup").replace("pit up", "pitup").replace("pitap", "pitup").replace("moccasin", "mocassin")
    return re.findall(r"[a-z0-9]+", s)

def wer(a, b):
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (a[i - 1] != b[j - 1]))
    return d[len(b)]

if sys.argv[1] == "tr":
    import subprocess
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", device="cpu", compute_type="int8"); out = {}
    for f in sorted(glob.glob(sys.argv[2] + "/*_*.wav")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
        segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language="fr", word_timestamps=True)
        ws = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]
        out[os.path.basename(f)] = ws; print(os.path.basename(f), " ".join(w[0] for w in ws), flush=True)
    json.dump(out, open(sys.argv[2] + "/tr.json", "w"), ensure_ascii=False, indent=0)
    sys.exit()

import librosa
from resemblyzer import VoiceEncoder, preprocess_wav
d, script, fref, gref = sys.argv[2:6]
TR = json.load(open(d + "/tr.json")); SC = json.load(open(script))
enc = VoiceEncoder("cpu"); emb = {"f": enc.embed_utterance(preprocess_wav(fref)), "g": enc.embed_utterance(preprocess_wav(gref))}

def merge(ws):                                    # whisper splits "c'est" into "c" + "'est": glue them back
    out = []
    for w, s, e in ws:
        if out and (w.startswith("'") or w.startswith("-")): out[-1] = [out[-1][0] + w, out[-1][1], e]
        else: out.append([w, s, e])
    return out

def dips(y, sr):
    e = librosa.feature.rms(y=y, frame_length=400, hop_length=160)[0]; db = 20 * np.log10(e + 1e-9); low = db < np.percentile(db, 90) - 15
    runs, k = [], 0
    for v in low:
        if v: k += 1
        else:
            if k: runs.append(k)
            k = 0
    short = sum(1 for r in runs if 5 <= r <= 25); return short / max(0.1, (~low).sum() * 160 / sr)

rows = []
for li, L in enumerate(SC):
    cands = []
    for f in sorted(glob.glob(f"{d}/{L['prefix']}_*.wav")):
        b = os.path.basename(f)
        if b not in TR: continue
        ws = merge(TR[b]); err = wer(norm(" ".join(w[0] for w in ws)), norm(L["text"]))
        y, sr = librosa.load(f, sr=16000)
        f0, _, _ = librosa.pyin(y, fmin=70, fmax=400, sr=sr); f0 = f0[~np.isnan(f0)]
        sim = float(np.dot(emb[L["who"]], enc.embed_utterance(preprocess_wav(f))))
        cands.append(dict(file=f, err=err, f0=float(np.median(f0)) if len(f0) else 0, sim=sim, chop=dips(y, sr), words=ws, dur=len(y) / sr))
    rows.append(cands)
fmed = np.median([c["f0"] for r, L in zip(rows, SC) if L["who"] == "f" for c in r if c["err"] == 0] or [210])
place = []
for L, cands in zip(SC, rows):
    def key(c):
        tone = abs(c["f0"] - fmed) / 25 if L["who"] == "f" else (1 - c["sim"]) * 10
        return (c["err"], round(tone + c["chop"], 3))
    cands.sort(key=key)
    for c in cands: print(f"{L['prefix']:5} {os.path.basename(c['file']):10} err={c['err']} f0={c['f0']:.0f} sim={c['sim']:.3f} chop={c['chop']:.2f} | {' '.join(w[0] for w in c['words'])}")
    best = cands[0]; disp = L["text"].split()
    ws = best["words"]
    # display words: the script's spelling on the voice's timing (same count after merging), else the transcript
    if len(disp) == len(ws): ws = [[x, s, e] for x, (_, s, e) in zip(disp, ws)]
    else: print("  ! word count differs, transcript words kept", len(disp), len(ws))
    t0 = ws[0][1]                                 # trim nothing: words are relative to the file start
    place.append({"who": L["who"], "file": best["file"], "words": ws})
    print("  ->", os.path.basename(best["file"]))
json.dump(place, open(d + "/place.json", "w"), ensure_ascii=False, indent=0)
