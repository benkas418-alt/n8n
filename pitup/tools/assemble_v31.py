# Lubumbashi voice v30: ONE full take (fullBC_0), no splicing inside the text. Only: cut the prompt residue before "Ah",
# and lengthen pauses at punctuation, placed in the take's own silences (skipped where the take has no silence).
import json, numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"; A = f"{S}/audio"
a, sr = sf.read(f"{A}/v30/fullBC_0.wav", dtype="float32")
T0 = 0.115; a = a[int(T0 * sr):].copy(); n = int(.005 * sr); a[:n] *= np.linspace(0, 1, n)    # start on the real "A"
F = int(.01 * sr); E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
# (end of word before the pause, start of next word, extra pause) in take time, from the take's word timing
# (end of word before the pause, start of next word, TARGET total silence, label): narrative pacing
P = [(0.40, 0.52, .60, "Ah | Lubumbashi"), (1.06, 1.24, .80, "Lubumbashi ! | Notre"), (1.88, 2.04, .45, "bouge, | et"),
     (2.90, 3.26, .90, "aussi. | Seulement"), (3.60, 3.66, .45, "Seulement, | entre"), (5.44, 5.60, .45, "retours, | trouver"),
     (7.36, 7.62, .95, "temps. | Alors"), (7.82, 8.00, .45, "Alors, | on"), (10.22, 10.42, .95, "appli. | Tu"),
     (11.36, 11.54, .45, "article, | la"), (12.40, 12.54, .45, "confirme, | on"), (13.10, 13.28, .45, "livre, | et"),
     (14.42, 14.56, .95, "livraison. | Sur"), (15.42, 15.60, .40, "PitUp, | ta"), (16.82, 16.96, .90, "déjà. | Passe"),
     (17.96, 18.08, .35, "commande | et")]
plan = []
for e0, s1, add, lab in P:
    i0, i1 = int((e0 - T0) * 100), int((s1 - T0) * 100) + 1
    k = i0 + int(np.argmin(E[i0:i1])); lv = E[k]
    if lv > -33 and not lab.startswith("Ah"): print(f"  skip  {lab:24s} no silence (min {lv:.0f} dB)"); continue
    # cut at the START of the quiet stretch, so the fade-in is over before the next word begins
    while k > i0 and E[k - 1] < lv + 3: k -= 1
    if lab.startswith("Ah"):   # "Ah" runs into "Lu-" with no silence: let "Ah" die away naturally (80 ms exponential) before the pause
        k = 19; j = int(k / 100 * sr); m_ = int(.06 * sr); a[j - m_:j] *= np.exp(-np.arange(m_) / sr / 0.02)   # Ah ends at 0.31 s in the take, the L starts there
    q0 = q1 = k   # silence already in the take around the cut (frames under -40 dB)
    while q0 > 0 and E[q0 - 1] < -40: q0 -= 1
    while q1 < len(E) - 1 and E[q1 + 1] < -40: q1 += 1
    have = (q1 - q0 + 1) / 100 if E[k] < -40 else 0.0
    tgt = add; add = round(max(0.0, tgt - have), 2)
    plan.append([round(k / 100, 3), add]); print(f"  pause {lab:24s} cut {k/100:.2f}s (min {lv:.0f} dB) had {have:.2f}s -> +{add} = {have+add:.2f}s")
sf.write(f"{A}/v30/v31_ciel.wav", a, sr); json.dump({"plan": plan, "trim": T0}, open(f"{A}/v30/plan31.json", "w"))
