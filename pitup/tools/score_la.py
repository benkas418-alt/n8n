# Score every take in audio/la: text match (whisper, word timings), median pitch, duration. Picks best per line.
# usage: score_la.py  -> writes audio/la/pick.json {line: {file, dur, words:[[w,s,e]]}}
import glob, json, re, difflib, os, subprocess, unicodedata
import numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
TX = ["Découvre PitUp : les boutiques de Lubumbashi, réunies dans ton téléphone.",
      "Tu cherches des baskets, une robe, un téléphone ?", "Tu trouves, tu compares, tu choisis.",
      "Mais nous ne faisons pas que te montrer des articles.", "Tu commandes, la boutique confirme, et nous te livrons.",
      "Tu vends ? Ouvre ta propre boutique, depuis ton téléphone.", "Plus de cent boutiques locales, et le paiement à la livraison.",
      "Tes achats. Ta boutique. Ta ville.", "Découvre PitUp. Le commerce, simplement."]
def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("pit up", "pitup").replace("pitt up", "pitup"); return re.sub(r"[^a-z0-9 ]", " ", t).split()
def pitch(a, sr):
    # autocorrelation per 40 ms frame, voiced frames only
    n = int(0.04 * sr); f = []; lo, hi = int(sr / 400), int(sr / 120)
    for i in range(0, len(a) - n, n // 2):
        x = a[i:i + n] - a[i:i + n].mean()
        if np.sqrt((x ** 2).mean()) < 0.02: continue
        c = np.correlate(x, x, "full")[n - 1:]; k = lo + np.argmax(c[lo:hi])
        if c[k] > 0.4 * c[0]: f.append(sr / k)
    return float(np.median(f)) if f else 0
from faster_whisper import WhisperModel
m = WhisperModel("medium", compute_type="int8"); out = {}; rep = []
for i, t in enumerate(TX):
    best = None
    for f in sorted(glob.glob(f"{SP}/audio/la/p*_{i}.wav")):
        a, sr = sf.read(f, dtype="float32"); a = a if a.ndim == 1 else a.mean(1); d = len(a) / sr
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "16000", "-ac", "1", f"{SP}/audio/la_tmp.wav"])
        b, _ = sf.read(f"{SP}/audio/la_tmp.wav", dtype="float32")
        segs, _ = m.transcribe(b, language="fr", word_timestamps=True, initial_prompt="PitUp, Lubumbashi")
        ws = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]
        heard = " ".join(w[0] for w in ws); tr = difflib.SequenceMatcher(None, norm(t), norm(heard)).ratio()
        p = pitch(b, 16000); pen = 0 if 190 <= p <= 225 else min(abs(p - 207) / 40, 1)
        sc = 3 * tr - pen - (2 if d > 0.11 * len(t) + 1.6 else 0)
        rep.append(f"{os.path.basename(f):9s} {d:5.2f}s txt {tr:.2f} f0 {p:5.0f} sc {sc:.2f} | {heard}")
        if best is None or sc > best[0]: best = (sc, f, d, ws, tr)
    out[i] = {"file": best[1], "dur": best[2], "words": best[3], "txt": best[4]}
    rep.append(f"  -> {i}: {os.path.basename(best[1])}")
json.dump(out, open(f"{SP}/audio/la/pick.json", "w"), ensure_ascii=False, indent=1)
print("\n".join(rep))
