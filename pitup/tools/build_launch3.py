# PitUp launch film v3 (17 Nov. 2026): music "Visa" (Sam Recks, instrumental), 2D logo, no phone sales,
# founder's products cut out on white, realistic 3D phone (layered titanium body, real thickness, turns in 3D).
# v2 notes:: kinetic typography in the PitUp art direction (light / blue #1f88c9 gradients,
# Poppins), the rhythm of the "congolais" motion: 1 to 3 words on screen, replaced at once by the next ones, each entry with
# its own movement and its own sound. Ideas taken from the reference (typed name, chat bubble, highlighted word, word swap,
# orbit) as movements only; real product photos and app recordings only as short illustrations.
# usage: build_launch2.py   (reads audio/la/words.json, places.json; writes the project hf/videos/pitup-launch2)
import json, subprocess, numpy as np, soundfile as sf, librosa
from scipy.signal import butter, sosfilt
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"; P = f"{SP}/hf/videos/pitup-launch3"
W = json.load(open(f"{SP}/audio/la/words.json")); PL = json.load(open(f"{SP}/audio/la/places.json"))
D = float(__import__("os").environ.get("DUR", "35.4")); sr = 48000; n = int(D * sr)
def wt(line, word, k=0):
    h = [w for w in W if str(w[3]) == str(line) and w[0].lower().strip(",.?") .startswith(word.lower())]
    return round(h[k][1], 3)
# ---------------------------------------------------------------- chunks: (start, html, bg, how, extra)
#   how: pop (kick: rises at once) | cam (dry click: whole phrase at once + flash) | type (letter by letter, one key per letter)
#        swap (slides up through a mask, swish) | mark (highlight sweeps behind the word)
#   bg: l = light gradient, b = PitUp blue gradient. <a>..</a> = accent colour.
E = lambda t: round(t - 0.04, 3)
# category words (no voice): on the beats just before line 7
BEATS = json.load(open(f"{SP}/audio/la/beats.json")); L7 = json.load(open(f"{SP}/audio/la/lines.json"))["7"][0]
k7 = min(range(len(BEATS)), key=lambda j: abs(BEATS[j] - L7)); CAT = [BEATS[k7 - 4], BEATS[k7 - 3], BEATS[k7 - 2]]
C = [
 (E(wt(0, "Découvre")), "Découvre", "l", "pop", ""),
 (E(wt(0, "PitUp")), "PitUp", "l", "type", "icon"),
 (E(wt(0, "les")), "les boutiques", "b", "pop", ""),
 (E(wt(0, "de")), "de <a>Lubumbashi</a>", "l", "cam", ""),
 (E(wt(0, "réunies")), "réunies", "b", "pop", ""),
 (E(wt(0, "dans")), "dans ton<br><a>téléphone.</a>", "l", "swap", "phone:phs_full"),
 (E(wt(1, "Tu")), "Tu cherches", "b", "pop", "bubble"),
 (E(wt(1, "des")), "des <a>baskets,</a>", "l", "cam", "card:basket"),
 (E(wt(1, "une")), "une <a>robe,</a>", "l", "cam", "card:robe"),
 (E(wt(1, "des", 1)), "des <a>accessoires ?</a>", "l", "cam", "card:montre"),
 (E(wt(2, "Tu")), "Tu trouves.", "b", "pop", ""),
 (E(wt(2, "tu", 1)), "tu compares.", "l", "pop", "pair"),
 (E(wt(2, "tu", 2)), "tu <a>choisis.</a>", "l", "pop", "pick"),
 (E(wt(3, "Mais")), "Mais", "l", "mark", ""),
 (E(wt(3, "nous")), "nous ne faisons pas", "l", "pop", ""),
 (E(wt(3, "que")), "que te montrer", "l", "pop", ""),
 (E(wt(3, "des")), "des articles.", "l", "swap", "fly"),
 (E(wt(4, "Tu")), "Tu commandes,", "b", "cam", ""),
 (E(wt(4, "la")), "la boutique<br><a>confirme,</a>", "l", "cam", "check"),
 (E(wt(4, "et")), "et nous<br>te livrons.", "b", "pop", "ring"),
 (E(wt("4b", "et")), "Et tu paies", "l", "pop", ""),
 (E(wt("4b", "à")), "à la <a>livraison.</a>", "l", "cam", "glass"),
 (E(wt(5, "tu")), "Tu vends ?", "l", "pop", ""),
 (E(wt(5, "ouvre")), "Ouvre ta", "b", "pop", ""),
 (E(wt(5, "propre")), "propre<br>boutique", "b", "type", ""),
 (E(wt(5, "depuis")), "depuis ton<br><a>téléphone.</a>", "l", "swap", "phone:phapp"),
 (E(wt(6, "Plus")), "+100", "b", "pop", "big"),
 (E(wt(6, "boutiques")), "boutiques<br>locales", "b", "type", "orbit"),
 (E(wt(6, "nous")), "nous ont déjà<br><a>rejoints.</a>", "l", "swap", ""),
 # no voice here: the music carries the words (kicks), like the "congolais" motion
 *[(c, w_, b_, "pop", "") for c, (w_, b_) in zip(CAT, [("Habillement", "b"), ("Chaussures", "l"), ("Accessoires", "b")])],
 (E(wt(7, "Tes")), "Tes <a>achats.</a>", "l", "swap", "sw"),
 (E(wt(7, "ta")), "Ta <a>boutique.</a>", "l", "swap", "sw"),
 (E(wt(7, "ta", 1)), "Ta <a>ville.</a>", "l", "swap", "sw"),
]
I = round(wt(8, "Découvre") - 0.05, 3)          # end: the P lands, the arrow rises into it
ARR0, ARR1 = I + 0.2, round(wt(8, "PitUp") - 0.05, 3)
TAG = wt(8, "commerce") - 0.1
ends = [c[0] for c in C[1:]] + [I]
# letter times for typed chunks: even steps across the spoken word(s)
TYPES = {}
for i, (a, h, bg, how, ex) in enumerate(C):
    if how == "type":
        txt = h.replace("<br>", ""); b = min(ends[i] - 0.12, a + 0.075 * len(txt) + 0.2)
        TYPES[i] = [round(a + (b - a) * j / max(1, len(txt) - 1), 3) for j in range(len(txt))]
# ---------------------------------------------------------------- audio
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).reshape(-1, 2)
import os
BED = os.environ.get("BED", f"{SP}/audio/la_bed.wav"); FULL = os.environ.get("FULL") == "1"
mus = load(BED)[:n].copy(); mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))
vox = np.zeros_like(mus); spans = []
for f, at in PL:
    v = load(f); e = np.abs(v).max(1); idx = np.where(e > 0.01)[0]; v = v[max(0, idx[0] - 800): idx[-1] + 2400]
    v = v * (10 ** (-17 / 20) / max(1e-6, np.sqrt((v[np.abs(v).max(1) > 0.02] ** 2).mean())))
    i = int(at * sr); v = v[: n - i]; vox[i:i + len(v)] += v; spans.append((at, at + len(v) / sr))
t = np.arange(n) / sr; w = np.zeros(n)
for a, b in spans:   # music dips under the voice (-9 dB), comes back in the gaps longer than 1.2 s
    up = np.clip((t - (a - 0.3)) / 0.3, 0, 1); dn = np.clip(((b + 0.5) - t) / 0.5, 0, 1); w = np.maximum(w, np.minimum(up, dn))
for (a0, b0), (a1, b1) in zip(spans, spans[1:]):
    if a1 - b0 < 1.2: w[int(b0 * sr):int(a1 * sr)] = 1
if FULL:   # the song stays low (lyrics audible in the back) and rises to full on the logo sound
    # -17 dB under the film; on the logo it jumps to -8 dB (the last line stays clear), then to -2 dB once the voice ends
    vend = spans[-1][1]; up = np.clip((t - (I + 0.15)) / 0.45, 0, 1); up2 = np.clip((t - (vend + 0.05)) / 0.4, 0, 1)
    g = -17.0 * (1 - up) + float(os.environ.get("LOGO_DB", "-8")) * up; g = g * (1 - up2) + -2.0 * up2
    mus *= (10 ** (g / 20))[:, None]
else:
    mus *= (10 ** (-14 * w / 20))[:, None]
fx = np.zeros(n, np.float32); rng = np.random.default_rng(7)
def add(at, s, g):
    i = int(at * sr); s = s[: max(0, n - i)]; fx[i:i + len(s)] += g * s
def thock(f0, dur=0.2, tau=0.05):
    tt = np.arange(int(dur * sr)) / sr; f = f0 + 1.6 * f0 * np.exp(-tt / 0.018)
    body = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt / tau)
    nz = np.convolve(rng.standard_normal(len(tt)) * np.exp(-tt / 0.004), np.ones(12) / 12, "same")
    return (body + 0.35 * nz).astype(np.float32)
def click():   # dry shutter-like click: two short filtered noise bursts
    L = int(0.09 * sr); o = np.zeros(L, np.float32); s2 = butter(2, [1800, 7000], "bandpass", fs=sr, output="sos")
    for d in (0, int(0.045 * sr)):
        b = rng.standard_normal(int(0.012 * sr)).astype(np.float32) * np.exp(-np.arange(int(0.012 * sr)) / (0.003 * sr)); o[d:d + len(b)] += sosfilt(s2, b)
    return o / (np.abs(o).max() + 1e-6)
def swish(dur, f1, f2):
    L = int(dur * sr); nz = rng.standard_normal(L).astype(np.float32); o = np.zeros(L, np.float32)
    for j in range(0, L, 1200):
        fc = f1 + (f2 - f1) * j / L; s2 = butter(2, [fc * 0.7, fc * 1.4], "bandpass", fs=sr, output="sos"); o[j:j + 1200] = sosfilt(s2, nz[j:j + 1200])
    return o * np.sin(np.linspace(0, np.pi, L)) ** 2 / (np.abs(o).max() + 1e-6)
k, _ = librosa.load(f"{SP}/sfx/kb/1387.mp3", sr=sr); on = librosa.onset.onset_detect(y=k, sr=sr, units="samples", backtrack=True)
strokes = []
for i, o in enumerate(on[:-1]):
    if on[i + 1] - o > int(0.16 * sr) and (i == 0 or o - on[i - 1] > int(0.1 * sr)):
        s = k[o:o + int(0.13 * sr)].copy(); s[-400:] *= np.linspace(1, 0, 400); s /= np.abs(s).max() + 1e-6; strokes.append(s)
for i, (a, h, bg, how, ex) in enumerate(C):
    if how == "pop": add(a, thock(80 if bg == "b" else 95), 0.22 if a < CAT[0] - 0.05 or a > L7 - 0.1 else 0.30)
    if how == "cam": add(a, click(), 0.22); add(a, thock(120, 0.12, 0.03), 0.12)
    if how == "swap": add(a - 0.12, swish(0.32, 900, 3200), 0.16)
    if how == "mark": add(a, thock(70), 0.3); add(a + 0.12, swish(0.3, 2000, 5000), 0.12)
    if how == "type":
        for j, tt_ in enumerate(TYPES[i]): add(tt_, strokes[(j * 5 + 2) % len(strokes)], 0.26)
add(ARR0 - 0.05, swish(0.6, 600, 3500), 0.22); add(ARR1, thock(110, 0.15, 0.03), 0.28)
mix = mus + vox + fx[:, None]
sf.write(f"{SP}/audio/la2_raw.wav", mix, sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/la2_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/la2_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000", "-c:a", "pcm_s16le", f"{P}/assets/mix.wav"], check=True)
# ---------------------------------------------------------------- html
def size(h):
    lines = h.replace("<a>", "").replace("</a>", "").split("<br>"); L = max(4, max(len(x) for x in lines))
    return int(min(220, 960 / (0.58 * L)))
def letters(h, sid):
    out, j, acc = [], 0, False
    for part in h.replace("<br>", "\n").replace("<a>", "\x01").replace("</a>", "\x02"):
        if part == "\n": out.append("<br>"); continue
        if part == "\x01": acc = True; continue
        if part == "\x02": acc = False; continue
        cls = " a" if acc else ""
        out.append(f'<span class="k{cls}" id="{sid}k{j}">{"&nbsp;" if part == " " else part}<i class="cur" id="{sid}c{j}"></i></span>'); j += 1
    return "".join(out)
def extra(ex, sid):
    if ex == "icon": return '<div class="tile" id="%sx"><img src="assets/icon_white.png" alt=""></div>' % sid
    if ex.startswith("phone:"):
        return ""
    if ex.startswith("card:"):
        return f'<div class="pc" id="{sid}x"><img src="assets/art/{ex[5:]}.png" alt=""></div>'
    if ex == "bubble": return f'<div class="bub" id="{sid}x"><i></i><i></i><i></i></div>'
    if ex == "pair": return f'<div class="pair" id="{sid}x"><img src="assets/art/robeA.png" alt=""><span>ou</span><img src="assets/art/robeB.png" alt=""></div>'
    if ex == "pick": return f'<div class="pc ok" id="{sid}x"><img src="assets/art/robeB.png" alt=""><b>✓</b></div>'
    if ex == "check": return f'<div class="chk" id="{sid}x">✓</div>'
    if ex == "ring": return f'<div class="ring" id="{sid}x">' + "".join(f'<i style="--a:{j * 15}deg"></i>' for j in range(24)) + '</div>'
    if ex == "fly": return f'<div class="fly" id="{sid}x">' + "".join(f'<img src="assets/art/{p}.png" style="--x:{x}px;--y:{y}px;--r:{r}deg" alt="">' for p, x, y, r in [("robeC", -300, -560, -8), ("montre", 300, -580, 7), ("basket", -290, 480, 6), ("robeA", 310, 460, -7)]) + '</div>'
    if ex == "orbit": return f'<div class="orb" id="{sid}x">' + "".join(f'<img src="assets/img/{s}.png" style="--a:{j * 40}deg" alt="">' for j, s in enumerate(["s03", "s10", "s11", "s15", "s16", "s24", "s28", "s29", "s30"])) + '</div>'
    if ex == "glass": return f'<div class="gl" id="{sid}x"><div class="glc"><b>Paiement</b><span>à la livraison</span></div></div>'
    return ""
slides = []
for i, (a, h, bg, how, ex) in enumerate(C):
    sid = f"s{i}"; fs = 330 if ex == "big" else 118 if ex == "orbit" else size(h)
    body = letters(h, sid) if how == "type" else h
    cls = "w" + (" mk" if how == "mark" else "")
    word = f'<div class="{cls}" style="font-size:{fs}px"><span class="in">{body}</span></div>' if how != "mark" else f'<div class="{cls}" style="font-size:{fs}px"><span class="hl"></span><span class="in">{body}</span></div>'
    slides.append(f'<div class="s {bg} x-{ex.split(":")[0]}" id="{sid}">{extra(ex, sid)}{word}</div>')
PW, PH, PR, DZ, PX, PY, BZ = 430, 900, 70, 38, 325, 800, 16   # phone size, corner radius, thickness, position, bezel
NL = 20
def phone(i, a, b, src):
    import math
    def tone(j):   # titanium band: bright in the middle of the edge, darker toward the glass and the back
        v = int(120 + 95 * math.sin(math.pi * j / (NL - 1))); return f"rgb({v},{v + 2},{v + 6})"
    lay = "".join(f'<i class="ly" style="transform:translateZ({-DZ / 2 + DZ * j / (NL - 1):.2f}px);background:{tone(j)}"></i>' for j in range(NL))
    return (f'<div class="sh3" id="H{i}"></div><div class="p3" id="P{i}">{lay}'
            f'<div class="bk" style="transform:translateZ({-DZ / 2 - .5}px) rotateY(180deg)"><b class="cam"><i></i><i></i><i></i></b></div>'
            f'<b class="btn" style="top:200px;transform:translateX(-3px) rotateY(-90deg)"></b><b class="btn" style="top:300px;height:80px;transform:translateX(-3px) rotateY(-90deg)"></b>'
            f'<b class="btn r" style="top:270px;height:130px;transform:translateX({PW - DZ * .6 + 3}px) rotateY(90deg)"></b>'
            f'<div class="fr" style="transform:translateZ({DZ / 2 + .5}px)"></div></div>'
            f'<video id="v{i}" class="clip scr3" src="assets/scr/{src}.mp4" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{2 + i % 3}"></video>'
            f'<div class="g3" id="G{i}"><b class="isl"></b></div>')
VIDS = "".join(phone(i, a, ends[i], ex[6:]) for i, (a, h, bg, how, ex) in enumerate(C) if ex.startswith("phone:"))
PHV = {}
cues = [[c[0], e, c[2], c[3], c[4]] for c, e in zip(C, ends)]
S_ = 0.25
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920"><script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f5f8fb;font-family:P,sans-serif}}
.bg{{position:absolute;inset:0}}
#bgl{{background:radial-gradient(110% 70% at 80% 0%,#ffffff 0%,#f3f7fb 50%,#e4eef7 100%)}}
#bgb{{background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
.s{{position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:60px}}
.l{{color:#0d1b2a}}.l .a{{color:#1f88c9}} .l a,.l .k.a{{color:#1f88c9}} a{{text-decoration:none;color:inherit}} .b{{color:#fff}}
.w{{position:relative;font-weight:700;letter-spacing:-.045em;line-height:1.06;text-align:center;white-space:nowrap}}
.w .in{{display:inline-block;position:relative}}
.k{{position:relative;display:inline-block;opacity:0}}.cur{{position:absolute;right:-.1em;top:.06em;width:.065em;height:.9em;background:#1f88c9;border-radius:4px;opacity:0}}
.b .cur{{background:#fff}}
.mk .hl{{position:absolute;left:-.12em;right:-.12em;top:.12em;bottom:.02em;background:#1f88c9;border-radius:.12em;transform-origin:0 50%}}
.mk .in{{color:#0d1b2a}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;z-index:20;pointer-events:none}}
.tile{{width:190px;height:190px;border-radius:52px;background:#1f88c9;display:flex;align-items:center;justify-content:center}} .tile img{{width:112px}}
.x-phone{{justify-content:flex-start;padding-top:300px}}
.p3{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PH}px;transform-style:preserve-3d;opacity:0;z-index:7}}
.ly{{position:absolute;inset:0;border-radius:{PR}px;background:linear-gradient(90deg,#4d5057 0%,#b9bcc2 12%,#8b8e95 35%,#e1e3e7 62%,#9a9da3 85%,#4a4d53 100%)}}
.bk{{position:absolute;inset:0;border-radius:{PR}px;background:linear-gradient(160deg,#5a5d63,#2f3136 60%,#45474c)}}
.bk .cam{{position:absolute;left:28px;top:28px;width:170px;height:170px;border-radius:44px;background:#3a3c41;box-shadow:inset 0 0 0 2px #6b6e74}}
.bk .cam i{{position:absolute;width:62px;height:62px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#3b4a63,#05070b 60%);box-shadow:0 0 0 6px #1b1c20}}
.bk .cam i:nth-child(1){{left:16px;top:16px}} .bk .cam i:nth-child(2){{left:16px;top:92px}} .bk .cam i:nth-child(3){{left:92px;top:54px}}
.btn{{position:absolute;left:0;width:{DZ * .6:.0f}px;height:60px;border-radius:4px;background:linear-gradient(#9fa2a8,#d9dbdf,#8c8f95);transform-origin:0 50%}}
.btn.r{{left:0}}
.fr{{position:absolute;inset:0;border-radius:{PR}px;background:#050506;box-shadow:inset 0 0 0 4px #c9ccd1,inset 0 0 0 6px #6d7076,inset 0 0 0 8px #0a0a0c}}
.scr3,.g3{{position:absolute;left:{PX + BZ}px;top:{PY + BZ}px;width:{PW - 2 * BZ}px;height:{PH - 2 * BZ}px;border-radius:{PR - BZ}px;opacity:0;z-index:8;transform-origin:{PW / 2 - BZ}px {PH / 2 - BZ}px}}
.scr3{{object-fit:cover;object-position:top;background:#fff}}
.g3{{z-index:9;background:linear-gradient(115deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.22) 42%,rgba(255,255,255,0) 55%);background-size:300% 100%}}
.g3 .isl{{position:absolute;left:50%;top:16px;width:126px;height:36px;margin-left:-63px;border-radius:18px;background:#050506}}
.sh3{{position:absolute;left:{PX + 30}px;top:{PY + PH - 20}px;width:{PW - 60}px;height:60px;border-radius:50%;background:rgba(13,40,70,.35);filter:blur(24px);opacity:0;z-index:6}}
.ph{{position:absolute;inset:0;border-radius:56px;background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,6px 4px 0 #1c1d21,40px 60px 80px rgba(13,40,70,.28)}}
.scr{{position:absolute;opacity:0;object-fit:cover;object-position:top;border-radius:46px;background:#fff;z-index:6}}
.pc{{position:relative;width:600px;height:600px;order:2}} .pc img{{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 26px 26px rgba(13,40,70,.16))}}
.pc.ok b{{position:absolute;right:22px;top:22px;width:96px;height:96px;border-radius:50%;background:#1f88c9;color:#fff;font-size:58px;display:flex;align-items:center;justify-content:center;border:6px solid #fff}}
.pair{{display:flex;align-items:center;gap:26px;order:2}} .pair img{{width:360px;height:480px;object-fit:contain;filter:drop-shadow(0 22px 22px rgba(13,40,70,.16))}} .pair span{{font-weight:700;font-size:56px;color:#1f88c9}}
.bub{{display:flex;gap:18px;padding:34px 46px;border-radius:60px;background:rgba(255,255,255,.18);border:3px solid rgba(255,255,255,.6)}} .bub i{{width:30px;height:30px;border-radius:50%;background:#fff}}
.chk{{width:200px;height:200px;border-radius:50%;background:#1f88c9;color:#fff;font-size:120px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 24px 50px rgba(22,114,171,.35)}}
.ring{{position:absolute;left:540px;top:960px;width:0;height:0}} .ring i{{position:absolute;left:-12px;top:-12px;width:24px;height:24px;border-radius:50%;background:#fff;transform:rotate(var(--a)) translateY(-470px)}}
.fly{{position:absolute;left:540px;top:960px;width:0;height:0}} .fly img{{position:absolute;left:-170px;top:-170px;width:340px;height:340px;object-fit:contain;filter:drop-shadow(0 20px 20px rgba(13,40,70,.16));transform:translate(var(--x),var(--y)) rotate(var(--r))}}
.orb{{position:absolute;left:540px;top:960px;width:0;height:0}} .orb img{{position:absolute;left:-80px;top:-80px;width:160px;height:160px;border-radius:50%;border:5px solid #fff;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:rotate(var(--a)) translateY(-470px) rotate(calc(-1 * var(--a)))}}
.gl{{order:2}} .glc{{padding:36px 64px;border-radius:28px;background:#1f88c9;color:#fff;text-align:center}} .glc b{{display:block;font-size:72px;letter-spacing:-.03em}} .glc span{{font-weight:600;font-size:48px;opacity:.92}}
#end{{position:absolute;inset:0;opacity:0}}
#cv{{position:absolute;left:{540 - 1040 * S_ * 1.6:.1f}px;top:{820 - 450 * S_ * 1.6:.1f}px;width:1500px;height:1900px;transform-origin:0 0;transform:scale({S_ * 1.6})}}
#cv img,#cv .m{{position:absolute;left:0;top:0;width:1500px;height:1900px}}
#ps{{-webkit-mask-image:url(assets/arrow_white.png),linear-gradient(#000,#000);-webkit-mask-size:1500px 1900px,100% 100%;-webkit-mask-repeat:no-repeat;-webkit-mask-position:0px 0px,0 0;-webkit-mask-composite:xor;mask-composite:exclude}}
#mo{{-webkit-mask-image:url(assets/mask_out.png);mask-image:url(assets/mask_out.png);-webkit-mask-size:100% 100%;mask-size:100% 100%}}
#word{{position:absolute;left:50%;top:1010px;width:470px;margin-left:-235px;opacity:0}}
#tag{{position:absolute;left:50%;top:1210px;width:520px;margin-left:-260px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1330px;text-align:center;color:#fff;font-weight:600;font-size:40px;letter-spacing:.02em;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1398px;text-align:center;color:#fff;font-weight:600;font-size:34px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1462px;display:flex;gap:28px;justify-content:center;opacity:0}}#stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div class="bg" id="bgl"></div><div class="bg" id="bgb" style="opacity:0"></div>
{chr(10).join(slides)}
{VIDS}
<div id="end">
 <div id="cv"><img id="ps" src="assets/p_solid.png" alt=""><div class="m" id="mo"><img id="aw" src="assets/arrow_white.png" alt=""></div></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/gplay.png" alt=""></div>
</div>
<div id="flash"></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const cues={json.dumps(cues)}, TYPES={json.dumps(TYPES)}, PHV={json.dumps(PHV)};
cues.forEach(([a,b,bg,how,ex],i)=>{{
  const s="#s"+i, w=s+" .w .in", x="#s"+i+"x";
  tl.set(s,{{opacity:1}},a); tl.set(s,{{opacity:0}},b); tl.set("#bgb",{{opacity:bg==="b"?1:0}},a);
  if(how==="pop"){{ tl.fromTo(w,{{y:60,scale:1.1,opacity:0}},E({{y:0,scale:1,opacity:1,duration:.22,ease:"expo.out"}}),a);
                    tl.to(w,{{scale:1.04,duration:Math.max(.05,b-a-.22),ease:"none"}},a+.22); }}
  if(how==="cam"){{ tl.fromTo(w,{{scale:1.08}},E({{scale:1,duration:.3,ease:"expo.out"}}),a);
                    tl.fromTo("#flash",{{opacity:.7}},E({{opacity:0,duration:.16,ease:"power2.out"}}),a); }}
  if(how==="swap"){{ tl.fromTo(w,{{yPercent:70,opacity:0,clipPath:"inset(0 0 100% 0)"}},E({{yPercent:0,opacity:1,clipPath:"inset(0 0 0% 0)",duration:.32,ease:"expo.out"}}),a);
                     tl.to(w,{{yPercent:-40,opacity:0,duration:.14,ease:"power2.in"}},b-.14); }}
  if(how==="mark"){{ tl.fromTo(s+" .hl",{{scaleX:0}},E({{scaleX:1,duration:.28,ease:"expo.out"}}),a+.1);
                     tl.fromTo(w,{{scale:1.15,opacity:0}},E({{scale:1,opacity:1,duration:.2,ease:"expo.out"}}),a);
                     tl.to(s+" .in",{{color:"#ffffff",duration:.12}},a+.18); }}
  if(how==="type"){{ (TYPES[i]||[]).forEach((t,j)=>{{
      tl.fromTo(s+"k"+j,{{opacity:0,y:14,scale:.86}},E({{opacity:1,y:0,scale:1,duration:.1,ease:"power2.out"}}),t);
      if(j) tl.set(s+"c"+(j-1),{{opacity:0}},t); tl.set(s+"c"+j,{{opacity:1}},t); }}); }}
  // illustrations: short, they arrive just after the words
  if(ex==="icon") tl.fromTo(x,{{scale:0,rotation:-20}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),a);
  if(ex.startsWith("card:")||ex==="pick"||ex==="glass") tl.fromTo(x,{{y:260,scale:.7,rotation:-6,opacity:0}},E({{y:0,scale:1,rotation:0,opacity:1,duration:.4,ease:"back.out(1.6)"}}),a+.04);
  if(ex==="pair"){{ tl.fromTo(x+" img",{{x:(k)=>k?160:-160,opacity:0}},E({{x:0,opacity:1,duration:.35,ease:"expo.out"}}),a); tl.fromTo(x+" span",{{scale:0}},E({{scale:1,duration:.3,ease:"back.out(2)"}}),a+.15); }}
  if(ex==="pick") tl.fromTo(x+" b",{{scale:0}},E({{scale:1,duration:.3,ease:"back.out(2.5)"}}),a+.25);
  if(ex==="bubble"){{ tl.fromTo(x,{{scale:0}},E({{scale:1,duration:.35,ease:"back.out(2)"}}),a); tl.fromTo(x+" i",{{y:0}},E({{y:-14,duration:.22,yoyo:true,repeat:5,ease:"sine.inOut",stagger:.09}}),a+.2); }}
  if(ex==="check") tl.fromTo(x,{{scale:0,rotation:-40}},E({{scale:1,rotation:0,duration:.4,ease:"back.out(2.4)"}}),a+.1);
  if(ex==="ring"){{ tl.fromTo(x+" i",{{scale:0}},E({{scale:1,duration:.3,ease:"back.out(2)",stagger:.012}}),a); tl.fromTo(x,{{rotation:0}},E({{rotation:60,duration:b-a,ease:"none"}}),a); }}
  if(ex==="fly") tl.fromTo(x+" img",{{scale:0,opacity:0}},E({{scale:1,opacity:1,duration:.4,ease:"back.out(1.8)",stagger:.06}}),a);
  if(ex==="orbit"){{ tl.fromTo(x+" img",{{scale:0}},E({{scale:1,duration:.35,ease:"back.out(2)",stagger:.05}}),a); tl.fromTo(x,{{rotation:0}},E({{rotation:50,duration:b-a,ease:"none"}}),a); }}
  if(ex==="big") tl.fromTo(w,{{scale:1.6}},E({{scale:1,duration:.3,ease:"expo.out"}}),a);
}});
// app recordings sit inside the phones (positions are read from the layout once the fonts are in)
// realistic 3D phone: one state drives the body, the screen recording and the glass, so they stay locked together
const phones={json.dumps({str(i): [c[0], e] for i, (c, e) in enumerate(zip(C, ends)) if c[4].startswith("phone:")})};
Object.entries(phones).forEach(([i,[a,b]])=>{{
  const P=document.getElementById("P"+i), V=document.getElementById("v"+i), G=document.getElementById("G"+i), H=document.getElementById("H"+i);
  const st={{y:1000,rx:16,ry:-40,rz:-7,sc:.94}};
  const T=()=>"perspective(2600px) translate3d(0,"+st.y+"px,0) rotateX("+st.rx+"deg) rotateY("+st.ry+"deg) rotateZ("+st.rz+"deg) scale("+st.sc+")";
  const put=()=>{{ const t=T(); P.style.transform=t; V.style.transform=t+" translateZ({DZ / 2 + 1}px)"; G.style.transform=t+" translateZ({DZ / 2 + 1.5}px)";
                   G.style.backgroundPosition=(110-(st.ry+40)*2.2)+"% 0"; H.style.transform="translateY("+st.y*0.9+"px) scaleX("+(1-Math.abs(st.ry)/160)+")"; }};
  [P,V,G,H].forEach((el)=>{{ tl.set(el,{{opacity:1}},a); tl.set(el,{{opacity:0}},b); }});
  tl.fromTo(st,{{y:1000,rx:16,ry:-40,rz:-7,sc:.94}},E({{y:0,rx:8,ry:-26,rz:0,sc:1,duration:.65,ease:"expo.out",onUpdate:put}}),a);
  tl.fromTo(st,{{rx:8,ry:-26}},E({{rx:4,ry:22,duration:Math.max(.3,b-a-.65),ease:"sine.inOut",onUpdate:put}}),a+.65);
  put();
}});
const I={I}; tl.set("#end",{{opacity:1}},I); tl.set("#bgb",{{opacity:1}},I);
tl.fromTo("#ps",{{scale:.8,opacity:0,transformOrigin:"1040px 450px"}},E({{scale:1,opacity:1,duration:.4,ease:"expo.out"}}),I);
const dx=-0.496*1150, dy=0.868*1150, ps=document.getElementById("ps"), aw=document.getElementById("aw"), o={{x:dx,y:dy}};
const put=()=>{{aw.style.transform="translate("+o.x+"px,"+o.y+"px)"; ps.style.webkitMaskPosition=o.x+"px "+o.y+"px, 0px 0px";}};
tl.set(o,{{x:dx,y:dy,onUpdate:put}},I); tl.set("#aw",{{opacity:0}},I); tl.set("#aw",{{opacity:1}},{ARR0:.3f});
tl.fromTo(o,{{x:dx,y:dy}},E({{x:0,y:0,duration:{ARR1 - ARR0:.3f},ease:"back.out(1.35)",onUpdate:put}}),{ARR0:.3f});
tl.to("#cv",{{y:-90,duration:.5,ease:"power3.inOut"}},{ARR1:.3f});
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.5,ease:"expo.out"}}),{ARR1 + 0.1:.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.5,ease:"expo.out"}}),{TAG:.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.5}}),{TAG + 0.5:.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{TAG + 0.7:.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.5,ease:"expo.out"}}),{TAG + 0.8:.3f});
tl.set({{}},{{}},{D}); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc.replace(" ?", " ?"))
for c, e in zip(C, ends): print(f"{c[0]:6.2f}-{e:6.2f} {c[3]:5s} {c[1]}")
print("end", I, ARR0, ARR1, TAG)
