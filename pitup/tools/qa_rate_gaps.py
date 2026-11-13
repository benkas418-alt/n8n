# Voice QA 3c: speech rate per sentence (WARN if > 1.15 x median) and sounds outside words (gaps louder than the bed).
# usage: qa_rate_gaps.py voice.wav words.json
import sys, json, re, numpy as np, soundfile as sf
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1); W = json.load(open(sys.argv[2]))
F = int(.01 * sr); E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
sent, cur = [], []
for w in W:
    cur.append(w)
    if re.search(r"[.!?]$", w[0]): sent.append(cur); cur = []
if cur: sent.append(cur)
syl = lambda t: max(1, len(re.findall(r"[aeiouyàâéèêëîïôûùœ]+", t.lower())))
R = []
for s in sent:
    t0, t1 = s[0][1], s[-1][2]; v = (E[int(t0 * 100):int(t1 * 100)] > -40).sum() / 100
    R.append((t0, sum(syl(w[0]) for w in s) / max(v, .1), " ".join(w[0] for w in s[:4])))
med = float(np.median([r for _, r, _ in R])); fast = [(round(t, 2), round(r, 1), x) for t, r, x in R if r > med * 1.15]
print(("WARN" if fast else "ok  "), f"fast sentences (median {med:.1f} syl/s):", fast)
inw = np.zeros(len(E), bool)
for w, s0, e0, p in W: inw[max(0, int((s0 - .05) * 100)):int((e0 + .06) * 100)] = True
runs = []
for k in range(len(E)):
    if not inw[k] and E[k] > -45:
        if runs and k - runs[-1][1] <= 2: runs[-1][1] = k; runs[-1][2] = max(runs[-1][2], E[k])
        else: runs.append([k, k, E[k]])
runs = [(round(x / 100, 2), round((y + 1) / 100, 2), int(m)) for x, y, m in runs if y - x >= 4]
print(("WARN" if runs else "ok  "), "sounds >= 50 ms outside words (check each with phones.py):", runs)
F5 = int(.005 * sr); E5 = 20 * np.log10(np.array([np.sqrt((a[k:k + F5] ** 2).mean()) for k in range(0, len(a) - F5, F5)]) + 1e-9)
inw5 = np.repeat(inw, 2)[:len(E5)]; clicks = [round(k * .005, 3) for k in range(1, len(E5) - 1) if not inw5[k] and E5[k] > -50 and E5[k] > E5[k - 1] + 10 and E5[k] > E5[k + 1] + 8]
print(("FAIL" if clicks else "ok  "), "short clicks in silences:", clicks)
