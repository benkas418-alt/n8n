# Lubumbashi voice v32: the SISTER's voice, one full take (soeurT_6). Narrative pauses at the script's punctuation,
# placed in the take's own silences (target total silence minus what is already there). No cut inside a word.
import json, re, difflib, numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"; A = f"{S}/audio"
REF = ("Ah… Lubumbashi ! Notre ville bouge, et ses boutiques aussi. Seulement, entre les embouteillages et les allers-retours, "
       "trouver la bonne pièce prend souvent du temps. Alors, on a réuni les boutiques de la ville dans une seule appli. "
       "Tu choisis ton article, la boutique confirme, on te le livre, et tu ne paies qu'à la livraison. Sur l'appli PitUp, "
       "ta prochaine pièce t'attend déjà. Passe ta première commande, et laisse la ville venir à toi.")
TGT = {"…": .80, "!": .80, ",": .45, ".": .90}; TGT_WORD = {"commande": .35}
a, sr = sf.read(f"{A}/v32/soeurV_6.wav", dtype="float32")
W = json.load(open(f"{A}/v32/words6.json"))                       # whisper words of the take: [word, start, end, prob]
T0 = 0.08; AH_END = 0.38
a = a[int(T0 * sr):].copy(); n = int(.005 * sr); a[:n] *= np.linspace(0, 1, n)
F = int(.01 * sr); E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
norm = lambda t: re.sub(r"[^a-zà-ÿ]", "", t.lower())
ref_tok = [(norm(w), w) for w in REF.replace(" !", "!").replace("-", " ").replace("'", "' ").split()]; ref_tok = [t for t in ref_tok if t[0]]
W = [w2 for w in W for w2 in ([[x, w[1], w[2], w[3]] for x in w[0].split("-") if x] if "-" in w[0] else [w])]
hyp = [norm(w[0]) for w in W]
sm = difflib.SequenceMatcher(None, [t[0] for t in ref_tok], hyp, autojunk=False)
pos = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size): pos[blk.a + k] = blk.b + k
plan = []
for i, (tok, raw) in enumerate(ref_tok[:-1]):
    p = raw[-1]; tgt = TGT.get(p) or TGT_WORD.get(tok)
    if not tgt or i not in pos or i + 1 not in pos: continue
    if tok == "seulement": print("  skip  Seulement,     liaison 'seulement-entre' (the silence is the t closure of 'entre')"); continue
    w0, w1 = W[pos[i]], W[pos[i + 1]]
    if tok == "ah": k = int(round((AH_END - T0) * 100)); lv = E[k]
    else:
        # first real silence (>= 40 ms under -40 dB) after the previous word ends: never a gap inside the next word
        i0, i1 = int((w0[2] - 0.08 - T0) * 100), int((w1[1] + 0.05 - T0) * 100) + 1
        k = None; j = i0
        while j < i1:
            if E[j] < -40:
                r = j
                while r < len(E) and E[r] < -40: r += 1
                if r - j >= 4: k = j; break
                j = r
            else: j += 1
        if k is None: print(f"  skip  {raw:14s} no silence"); continue
        lv = E[k:k + 4].min()
    if tok == "lubumbashi": k = int(round((1.045 - T0) * 100))   # -shi ends in the 1.045 s dip; the N of Notre starts right after (never cut in the t closure)
    if tok == "article": k = int(round((10.77 - T0) * 100))   # skip the creaky onset (4 glottal pulses at 10.68-10.765 s) before 'la'
    q0 = q1 = k
    while q0 > 0 and E[q0 - 1] < -45: q0 -= 1
    while q1 < len(E) - 1 and E[q1 + 1] < -45: q1 += 1
    have = (q1 - q0 + 1) / 100 if E[k] < -45 else 0.0; add = round(max(0.0, tgt - have), 2)
    plan.append([round(k / 100, 3), add]); print(f"  pause after {raw:14s} cut {k/100:.2f}s ({lv:.0f} dB) had {have:.2f}s +{add}")
sf.write(f"{A}/v32/v34_ciel.wav", a, sr); json.dump({"plan": plan, "trim": T0}, open(f"{A}/v32/plan34.json", "w"))
