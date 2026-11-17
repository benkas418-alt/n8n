# PitUp kinetic typography v3: PitUp art direction (blue #1f88c9, light background, Poppins), instrumental music taken
# from the founder's reference, real keyboard keystrokes on "simplement.", signature logo animation (the arrow rises into the P).
import json, subprocess, numpy as np, soundfile as sf, librosa
from scipy.signal import butter, sosfilt, fftconvolve
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"; P = f"{SP}/hf/videos/pitup-md4c"
REF = f"{SP}/dup/refsep/sep/htdemucs/cf82f77a/no_vocals.wav"
sr = 44100
# music: only the real track (the reference ends with the Instagram outro jingle from 26.7 s: never use it)
# [7.26, 16.40) words, real break 16.40-17.95 typing, drop at 18.0 logo
y, _ = librosa.load(REF, sr=sr, mono=False); y = y.T.astype(np.float32)
A0 = 7.26; seg = lambda src: src - A0
IMPACT = seg(18.0); SIL = seg(16.40)
D = round(IMPACT + 4.4, 2); n = int(D * sr)
mus = y[int(A0 * sr):int(A0 * sr) + n].copy()
t = np.arange(n) / sr; g = np.ones(n, np.float32); fo = t > D - 1.2; g[fo] = np.linspace(1, 0, fo.sum()) ** 1.5
mus *= g[:, None]
fx = np.zeros(n, np.float32)
def add(at, s, gain):
    i = int(at * sr); s = s[: max(0, n - i)]; fx[i:i + len(s)] += gain * s
# real keystrokes (Mixkit 1387, warm mechanical keyboard): isolated strokes only
k, _ = librosa.load(f"{SP}/sfx/kb/1387.mp3", sr=sr)
on = librosa.onset.onset_detect(y=k, sr=sr, units="samples", backtrack=True)
strokes = []
for i, o in enumerate(on[:-1]):
    if on[i + 1] - o > int(0.16 * sr) and (i == 0 or o - on[i - 1] > int(0.1 * sr)):
        s = k[o:o + int(0.13 * sr)].copy(); s[-400:] *= np.linspace(1, 0, 400); s /= np.abs(s).max() + 1e-6; strokes.append(s)
print("strokes", len(strokes))
# soft low "thock" on each cut
rng = np.random.default_rng(7)
def thock(f0, dur=0.2, tau=0.05):
    tt = np.arange(int(dur * sr)) / sr; f = f0 + 1.6 * f0 * np.exp(-tt / 0.018)
    body = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt / tau)
    nz = np.convolve(rng.standard_normal(len(tt)) * np.exp(-tt / 0.004), np.ones(12) / 12, "same")
    return (body + 0.35 * nz).astype(np.float32)
def swish(dur, f1, f2):
    L = int(dur * sr); nz = rng.standard_normal(L).astype(np.float32); o = np.zeros(L, np.float32)
    for j in range(0, L, 1102):
        fc = f1 + (f2 - f1) * j / L; s2 = butter(2, [fc * 0.7, fc * 1.4], "bandpass", fs=sr, output="sos"); o[j:j + 1102] = sosfilt(s2, nz[j:j + 1102])
    return o * np.sin(np.linspace(0, np.pi, L)) ** 2
# ---- words placed on the sounds of the music (v3, 17 Nov.): "pop" = on a kick, "cam" = on a dry click (camera),
# "type" = letter by letter on the real clicks of the music's typing passage
BT = 0.5585; L_, B_ = "l", "b"
HI = [0.51,0.64,0.78,1.21,1.31,1.49,1.63,1.77,2.04,2.19,2.33,2.47,2.61,2.74,2.89,3.03,3.17,3.31,3.45,3.59,3.70,3.87,4.02,4.11,4.28,4.43,
      4.71,4.85,4.99,5.13,5.24,5.41,5.56,5.69,5.83,5.97]          # high-band onsets measured in the music
def typed(txt, a, b):
    n = len(txt.replace("|", "")); out = []
    for i in range(n):
        t0 = a + (b - a) * i / max(1, n - 1); near = min(HI, key=lambda h: abs(h - t0))
        out.append(round(near if abs(near - t0) < 0.035 else t0, 3))
    for i in range(1, n): out[i] = max(out[i], out[i - 1] + 0.06)
    return out
seq = [(0.08, "Et si", L_, "", "pop", None), (0.92, "tout", B_, "", "pop", None), (1.77, "Lubumbashi", L_, "", "cam", None),
       (2.33, "tenait dans|ta poche ?", B_, "poche ?", "type", typed("tenait dans|ta poche ?", 2.33, 4.43)),
       (4.56, "+100|boutiques.", L_, "+100", "type2", typed("boutiques.", 4.85, 5.97)),
       (6.03, "tu commandes.", B_, "", "cam", None), (6.40, "on livre.", L_, "", "cam", None),
       (6.87, "tu paies|à la livraison.", B_, "livraison.", "cam", None),
       (7.43, "notre application|de vente en ligne", L_, "vente en ligne", "cam", None),
       (8.22, "fièrement", B_, "", "pop", None), (8.65, "congolaise.", L_, "congolaise.", "pop", None)]
word = "simplement."; T0 = SIL + 0.08; step = (IMPACT - 0.12 - T0) / len(word)
TY = [round(T0 + i * step + (0.012 if i % 3 == 1 else 0), 3) for i in range(len(word))]
for j, tt_ in enumerate(TY):
    st_ = strokes[(j * 5 + 2) % len(strokes)]; add(tt_, st_, 0.5 if j == len(word) - 1 else 0.38)
for at, txt, bg, acc, how, lt in seq:
    if how in ("pop", "cam") and at > 0.05: add(at, thock(80 if bg == B_ else 95), 0.22)
    if how == "type2": add(at, thock(95), 0.22)        # "+100" lands on the kick; "boutiques." is typed on the music's clicks
# logo: the arrow rises into the P (swish), locks in (small thock)
ARR0, ARR1 = IMPACT + 0.45, IMPACT + 1.0
add(ARR0 - 0.05, swish(0.65, 600, 3500), 0.30); add(ARR1, thock(110, 0.15, 0.03), 0.30)
mix = mus + fx[:, None]; sf.write("/tmp/md3_raw.wav", mix, sr, subtype="FLOAT")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/md3_raw.wav", "-af", "alimiter=limit=0.89:attack=2:release=60:level=disabled", "-c:a", "pcm_s16le", f"{P}/assets/bgm.wav"], check=True)
print("D", D, "impact", round(IMPACT, 3), "silence", round(SIL, 3), "music ends at src", round(A0 + D, 2))
# ---- html
def size(s): return int(min(230, 950 / (0.56 * max(4, max(len(x) for x in s.split('|'))))))
def letters_html(txt, acc, sid, first=0):
    out = []; j = first; acc_from = len(txt.replace("|", "")) - len(acc.replace("|", "")) if acc else 10**6; k = 0
    for c in txt:
        if c == "|": out.append("<br>"); continue
        cls = ' a' if k >= acc_from else ''
        out.append(f'<span class="k{cls}" id="{sid}k{j}">{"&nbsp;" if c == " " else c}<i class="cur" id="{sid}c{j}"></i></span>'); j += 1; k += 1
    return "".join(out)
slides = []; TYPES = []
for i, (at, txt, bg, acc, how, lt) in enumerate(seq):
    sid = f"s{i}"
    if how == "type":
        inner = f'<div class="w" style="font-size:{size(txt)}px">{letters_html(txt, acc, sid)}</div>'; TYPES.append([sid, lt])
    elif how == "type2":
        top, low = txt.split("|")
        inner = (f'<div class="w big" style="font-size:{size(top)}px"><span class="a">{top}</span></div>'
                 f'<div class="w" style="font-size:{size(low)}px">{letters_html(low, "", sid)}</div>'); TYPES.append([sid, lt])
    else:
        html = txt.replace(acc, f'<span class="a">{acc}</span>') if acc else txt
        inner = f'<div class="w" style="font-size:{size(txt)}px">{html.replace("|", "<br>")}</div>'
    slides.append(f'<div class="s {bg}" id="{sid}"><div class="col">{inner}</div></div>')
letters = "".join(f'<span class="k" id="k{j}">{c}<i class="cur" id="c{j}"></i></span>' for j, c in enumerate(word))
slides.append(f'<div class="s l" id="st"><div class="col"><div class="pre" id="pre">Le commerce</div>'
              f'<div class="w" style="font-size:{size(word)}px"><i class="cur" id="c_"></i>{letters}</div></div></div>')
ends = [x[0] for x in seq[1:]] + [SIL]
cues = [[x[0], e, x[4]] for x, e in zip(seq, ends)]
S_ = 0.25   # logo canvas scale (1500x1900 canvas, icon 800x900 at x=640)
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920"><script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f5f8fb;font-family:P,sans-serif}}
.bg{{position:absolute;inset:0}}
#bgl{{background:radial-gradient(110% 70% at 80% 0%,#ffffff 0%,#f3f7fb 50%,#e4eef7 100%)}}
#bgb{{background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
.s{{position:absolute;inset:0;opacity:0;display:flex;align-items:center;justify-content:center}}
.l{{color:#0d1b2a}}.l .a{{color:#1f88c9}}
.b{{color:#ffffff}}.col{{display:flex;flex-direction:column;align-items:center;gap:26px}}.pre{{font-weight:600;font-size:86px;letter-spacing:-.03em;color:#1f88c9}}
.w{{font-weight:700;letter-spacing:-.04em;line-height:1.08;white-space:pre;text-align:center}}
.k{{position:relative;display:inline-block;opacity:0}}.cur{{position:absolute;right:-.1em;top:.06em;width:.065em;height:.9em;background:#1f88c9;border-radius:4px;opacity:0}}#c_{{position:relative;display:inline-block;right:auto;vertical-align:-.08em;margin-right:-.065em}}
#end{{position:absolute;inset:0;opacity:0}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;z-index:5;pointer-events:none}}
.big{{margin-bottom:-10px}}
#avail{{position:absolute;left:0;right:0;top:1398px;text-align:center;color:#ffffff;font-weight:600;font-size:34px;letter-spacing:.01em;opacity:0}}
#cv{{position:absolute;left:{540 - 1040 * S_ * 1.6:.1f}px;top:{820 - 450 * S_ * 1.6:.1f}px;width:1500px;height:1900px;transform-origin:0 0;transform:scale({S_ * 1.6})}}
#cv img,#cv .m{{position:absolute;left:0;top:0;width:1500px;height:1900px}}
#ps{{-webkit-mask-image:url(assets/arrow_white.png),linear-gradient(#000,#000);-webkit-mask-size:1500px 1900px,100% 100%;-webkit-mask-repeat:no-repeat;-webkit-mask-position:0px 0px,0 0;-webkit-mask-composite:xor;mask-composite:exclude}}
#mo{{-webkit-mask-image:url(assets/mask_out.png);mask-image:url(assets/mask_out.png);-webkit-mask-size:100% 100%;mask-size:100% 100%}}
#word{{position:absolute;left:50%;top:1010px;width:470px;margin-left:-235px;opacity:0}}
#tag{{position:absolute;left:50%;top:1210px;width:520px;margin-left:-260px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1462px;display:flex;gap:28px;justify-content:center;opacity:0}}#stores img{{height:100px}}
#url{{position:absolute;left:0;right:0;top:1330px;text-align:center;color:#ffffff;font-weight:600;font-size:40px;letter-spacing:.02em;opacity:0}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/bgm.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div class="bg" id="bgl"></div><div class="bg" id="bgb" style="opacity:0"></div>
<div id="flash"></div>
{chr(10).join(slides)}
<div id="end">
 <div id="cv"><img id="ps" src="assets/p_solid.png" alt="">
  <div class="m" id="mo"><img id="aw" src="assets/arrow_white.png" alt=""></div></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div>
 <div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/gplay.png" alt=""></div>
</div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const D={D}; const cues={json.dumps(cues)}; const bgs={json.dumps([s_[2] for s_ in seq])}; const TYPES={json.dumps(TYPES)};
cues.forEach(([a,b,how],i)=>{{
  const s="#s"+i, w=s+" .w";
  tl.set(s,{{opacity:1}},a); tl.set(s,{{opacity:0}},b); tl.set("#bgb",{{opacity:bgs[i]==="b"?1:0}},a);
  if(how==="pop" && i>0){{   // on a kick: the word lands at once with a short rise
    tl.fromTo(w,{{y:50,scale:1.08,opacity:0}},{{y:0,scale:1,opacity:1,duration:.22,ease:"expo.out",immediateRender:false}},a);
    tl.to(w,{{scale:1.035,duration:Math.max(.05,b-a-.22),ease:"none"}},a+.22);
  }} else if(how==="cam"){{  // on a dry click: the whole phrase appears at once, like a photo (short flash, slight zoom out)
    tl.fromTo(w,{{scale:1.07,opacity:1}},{{scale:1,duration:.3,ease:"expo.out",immediateRender:false}},a);
    tl.fromTo("#flash",{{opacity:.75}},{{opacity:0,duration:.16,ease:"power2.out",immediateRender:false}},a);
  }} else if(how==="type2"){{ // "+100" lands on the kick, then "boutiques." is typed
    tl.fromTo(s+" .big",{{y:50,scale:1.08,opacity:0}},{{y:0,scale:1,opacity:1,duration:.22,ease:"expo.out",immediateRender:false}},a);
  }}
}});
TYPES.forEach(([sid,ts])=>{{   // letter after letter, on the clicks of the music, with the cursor after the last letter
  ts.forEach((t,j)=>{{
    tl.fromTo("#"+sid+"k"+j,{{opacity:0,y:14,scale:.86}},{{opacity:1,y:0,scale:1,duration:.11,ease:"power2.out",immediateRender:false}},t);
    if(j) tl.set("#"+sid+"c"+(j-1),{{opacity:0}},t); tl.set("#"+sid+"c"+j,{{opacity:1}},t);
  }});
}});
const TY={json.dumps(TY)}, S0={SIL:.3f};
tl.set("#st",{{opacity:1}},S0); tl.set("#bgb",{{opacity:0}},S0);
tl.fromTo("#pre",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.3,ease:"expo.out",immediateRender:false}},S0);
tl.set("#c_",{{opacity:1}},S0);
TY.forEach((t,j)=>{{
  tl.fromTo("#k"+j,{{opacity:0,y:14,scale:.86}},{{opacity:1,y:0,scale:1,duration:.11,ease:"power2.out",immediateRender:false}},t);
  tl.set(j?"#c"+(j-1):"#c_",{{opacity:0}},t); tl.set("#c"+j,{{opacity:1}},t);
}});
const last="#c{len(word)-1}"; for(let b=0;b<4;b++){{tl.set(last,{{opacity:0}},TY[TY.length-1]+0.25+b*0.5); tl.set(last,{{opacity:1}},TY[TY.length-1]+0.5+b*0.5);}}
tl.set("#st",{{opacity:0}},{IMPACT:.3f});
const I={IMPACT:.3f};
tl.set("#end",{{opacity:1}},I); tl.set("#bgb",{{opacity:1}},I);
// the P lands on the impact, then the arrow rises from below along its shaft and locks into the P
tl.fromTo("#ps",{{scale:.8,opacity:0,transformOrigin:"1040px 450px"}},{{scale:1,opacity:1,duration:.5,ease:"expo.out",immediateRender:false}},I);
// one value drives both the white arrow outside the P and the transparent cut it makes inside the P
const dx=-0.496*1150, dy=0.868*1150, ps=document.getElementById("ps"), aw=document.getElementById("aw"), o={{x:dx,y:dy}};
const put=()=>{{aw.style.transform="translate("+o.x+"px,"+o.y+"px)"; ps.style.webkitMaskPosition=o.x+"px "+o.y+"px, 0px 0px";}};
tl.set(o,{{x:dx,y:dy,onUpdate:put}},I); tl.set("#aw",{{opacity:0}},I); tl.set("#aw",{{opacity:1}},{ARR0:.3f});
tl.fromTo(o,{{x:dx,y:dy}},{{x:0,y:0,duration:.85,ease:"back.out(1.35)",immediateRender:false,onUpdate:put}},{ARR0:.3f});
tl.to("#cv",{{y:-90,duration:.6,ease:"power3.inOut"}},{ARR1 + 0.45:.3f});
tl.fromTo("#word",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.55,ease:"expo.out",immediateRender:false}},{ARR1 + 0.6:.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.5,ease:"expo.out",immediateRender:false}},{ARR1 + 0.85:.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45,ease:"expo.out",immediateRender:false}},{ARR1 + 1.18:.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.5,ease:"expo.out",immediateRender:false}},{ARR1 + 1.25:.3f});
tl.fromTo("#url",{{opacity:0}},{{opacity:.9,duration:.5,immediateRender:false}},{ARR1 + 1.1:.3f});
tl.set({{}},{{}},D); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc); print(len(seq), "slides; arrow", ARR0, ARR1); print(json.dumps(TYPES))
