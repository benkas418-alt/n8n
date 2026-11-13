# Lubumbashi voice v25: pieces from the original take + regenerated lines, joined at silences, then pauses + room tone.
import json, subprocess, numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
A = f"{S}/audio"; sr = 48000
def rd(f): x, s = sf.read(f, dtype="float32"); assert s == sr; return x if x.ndim == 1 else x.mean(1)
def med(x):
    F = int(.01 * sr); E = 20 * np.log10(np.array([np.sqrt((x[k:k + F] ** 2).mean()) for k in range(0, len(x) - F, F)]) + 1e-9); return np.median(E[E > -30])
def level(x, ref_db, name):   # match speech level to the original take, peaks through a soft limiter
    g = 10 ** ((ref_db - med(x)) / 20); sf.write("/tmp/lv.wav", x * g, sr, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/lv.wav", "-af", "alimiter=limit=0.89:attack=2:release=50:level=disabled", "-c:a", "pcm_f32le", "/tmp/lv2.wav"], check=True)
    y = rd("/tmp/lv2.wav"); print(f"{name}: gain {20*np.log10(g):+.1f} dB, peak {abs(y).max():.2f}"); return y
def trim_in(x, t, fade=0.02):
    y = x[int(t * sr):].copy(); n = int(fade * sr); y[:n] *= np.sin(np.linspace(0, np.pi / 2, n)) ** 2; return y
raw = rd(f"{A}/v8/v14_ciel.wav"); REF = med(raw)
emb = rd(f"{A}/v20/emb2L.wav").copy(); a, b = int(.07 * sr), int(.095 * sr); emb[:a] = 0; emb[a:b] *= np.sin(np.linspace(0, np.pi / 2, b - a)) ** 2
raw2 = raw.copy(); raw2[int(5.21 * sr):int(5.21 * sr) + len(emb)] = emb          # embouteillages line, unclipped (v24)
i0, i1 = int(0.600 * sr), int(0.655 * sr); raw2[i0:i1] *= np.cos(np.linspace(0, np.pi / 2, i1 - i0)) ** 2; raw2[i1:int(1.0 * sr)] = 0   # "Ah," natural release
notre = level(trim_in(rd(f"{A}/v20/notreC_4.wav"), 0.16), REF, "notre take4")
alors = level(trim_in(rd(f"{A}/v20/alorsC_0.wav"), 0.07), REF, "alors take0")
seul = level(trim_in(rd(f"{A}/v20/seulC_4.wav"), 0.015, 0.012), REF, "seul take4"); n_ = int(.12 * sr); seul[-n_:] *= np.exp(-np.arange(n_) / sr / 0.03)   # "temps." was cut short by the generator: give it a natural exponential release
livre = trim_in(rd(f"{A}/v20/livreL_0.wav"), 2.515, 0.008)
g_ = np.ones(len(livre), np.float32); k1, k2 = int(.13 * sr), int(.16 * sr); g_[:k1] = 10 ** (4 / 20); g_[k1:k2] = np.linspace(10 ** (4 / 20), 1, k2 - k1); livre = livre * g_   # 'on' was 9 dB under the voice
# pieces: (audio, internal cuts [(t_in_piece, add)], pause after the piece)
P = [(raw2[:int(2.50 * sr)], [], 0.0),                                  # Ah, Lubumbashi ! (+ its silence)
     (notre, [(1.00 - 0.16 + 0.08, 0.25)], 0.55),                       # Notre ville bouge, | et ses boutiques aussi.
     (seul, [(0.70 - 0.015, .30), (3.03 - 0.015, .30)], 0.58),   # Seulement, | entre ... retours, | trouver ... temps. (new take 4; cuts at the start of each silence)
     (alors, [(0.43 - 0.07, 0.2)], 0.58),                               # Alors, | on a réuni ... appli.
     (raw2[int(12.63 * sr):int(15.10 * sr)], [(14.09 - 12.63, .3)], 0.44),     # Tu choisis ton article, | la boutique confirme,
     (livre, [(3.24 - 2.515, .18)], 0.45),                               # on te le livre, | et tu ne paies qu'à la livraison.
     (raw2[int(18.10 * sr):], [(19.38 - 18.10, .38), (20.84 - 18.10, .65), (21.93 - 18.10, .33)], 0.0)]
R, plan, t, starts_at = [], [], 0.0, []
for x, cuts, after in P:
    starts_at.append(t); R.append(x); plan += [[round(t + c, 3), a] for c, a in cuts]; t += len(x) / sr
    if after: plan.append([round(t, 3), after])
R = np.concatenate(R); sf.write(f"{A}/v20/v26_ciel.wav", R, sr)
plan.sort(); cum = lambda tt: sum(a for c, a in plan if c <= tt); newP = lambda tt: tt + cum(tt)
# anchors (first word of each scene, in R time) -> keep each scene's old lead before its first word
old = json.load(open(f"{A}/v8/v14_cielP.wav.map.json")); oldP = lambda tt: tt + sum(a for c, a in old if c <= tt)
st = [0.03, 2.55, 6.64, 12.1, 16.36, 21.22, 23.41]
anc_old = [None, 2.64, 5.42, 9.64, 12.94, 16.48, 18.52]
sh = starts_at[6] - 18.10
anc_new = [None, starts_at[1] + 0.02, starts_at[2] + 0.01, starts_at[3] + 0.03, starts_at[4] + (12.94 - 12.63), starts_at[5] + (3.36 - 2.515), 18.52 + sh]
ns = [st[0]] + [round(newP(n) + (st[i] - oldP(o)), 2) for i, (o, n) in enumerate(zip(anc_old, anc_new)) if i]
ec = round(newP(22.64 + sh) + (28.89 - oldP(22.64)), 2); ve = round(newP(23.26 + sh) + (29.67 - oldP(23.26)), 2)
json.dump({"plan": plan, "starts": ns, "end_card_at": ec, "vo_end": ve}, open(f"{A}/v20/plan26.json", "w"))
print("starts", ns, "end_card", ec, "vo_end", ve)
