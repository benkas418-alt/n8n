# PitUp simple motion design for buyers (27 Nov. 2026). Kinetic type in the art direction (light / PitUp blue, Poppins),
# 1 to 3 words at a time, each group lands on a beat of the music, no voice.
# Hook theory (founder's references, B. Storey): a specific promise for a specific problem, clear before clever,
# a clear call to action. Problem = looking for an item without going round the shops (the collaborator's own words).
# Sounds: real camera click on every other change of scene, real keyboard on the typed word (no code-made sound).
# usage: build_md.py   (env BED=<music wav> OFF=46.07 start of the music section, BPM grid read from the track)
import json, os, subprocess, numpy as np, soundfile as sf, librosa
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-md"; sr = 48000
BED = os.environ.get("BED", f"{SP}/audio/tems.wav"); OFF = float(os.environ.get("OFF", "46.07"))
y, _ = librosa.load(BED, sr=22050, offset=OFF, duration=24)
_, bf = librosa.beat.beat_track(y=y, sr=22050); B = [round(float(t), 3) for t in librosa.frames_to_time(bf, sr=22050)]
if B[0] > 0.2: B = [0.0] + B                       # beat 0 = the cut into the section
b = lambda k: B[k]
# groups: (beat, html, scene, entry). scene: l light | b blue | p phone (light, phone below) | e end
# entry: pop (rises) | swap (slides up through a mask) | type (letter by letter, keyboard) | mark (blue highlight) | cam (lands at once)
G = [(0, "Tu cherches", "l", "pop"), (2, "des<br><a>baskets</a> ?", "l", "pop"), (4, "à<br>Lubumbashi ?", "l", "type"),
     (6, "Sans faire", "b", "swap"), (7, "le tour", "b", "swap"), (8, "des<br><a>boutiques.</a>", "b", "pop"),
     (10, "Trouve-les", "p", "pop"), (12, "sur <a>PitUp</a>", "p", "cam"), (14, "Tu<br>commandes.", "p", "pop"),
     (16, "On te <a>livre.</a>", "p", "pop"), (18, "Tu paies", "b", "swap"), (19, "à la livraison.", "b", "mark")]
E0 = b(22); D = round(b(29) + 0.2, 2); n = int(D * sr)
T = [b(k) for k, *_ in G]; ENDS = T[1:] + [E0]
PH0, PH1 = b(10), b(18)
SCENE_CUTS = [b(6), b(10), b(18), E0]               # changes of scene
TYPES = {}
for i, (k, h, sc, how) in enumerate(G):
    if how == "type":
        h = h.replace("<br>", "\n"); a = T[i]; z = min(ENDS[i] - 0.25, a + 0.065 * len(h) + 0.1); TYPES[i] = [round(a + (z - a) * j / max(1, len(h) - 1), 3) for j in range(len(h))]

# ---------------------------------------------------------------- audio
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                                        capture_output=True).stdout, np.float32)
mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFF}", "-t", f"{D}", "-i", BED, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2)
mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))[:n]
tt = np.arange(n) / sr; mus = mus * np.clip((D - tt) / 1.0, 0, 1)[:, None] * np.clip(tt / 0.05, 0, 1)[:, None]
fx = np.zeros(n, np.float32)
def add(t0, s, g):
    i = int(t0 * sr); s = s[:max(0, n - i)]; fx[i:i + len(s)] += g * s
SH = load(f"{SP}/sfx/mk/1432.mp3")                  # real camera click, peak 0.31 s into the file
for x in SCENE_CUTS[::2]: add(x - 0.30, SH, 0.55)  # every other change of scene (founder, 26 Nov.)
kb, _ = librosa.load(f"{SP}/sfx/kb/1387.mp3", sr=sr); on = librosa.onset.onset_detect(y=kb, sr=sr, units="samples", backtrack=True)
strokes = []
for i, o in enumerate(on[:-1]):
    if on[i + 1] - o > int(0.16 * sr) and (i == 0 or o - on[i - 1] > int(0.1 * sr)):
        q = kb[o:o + int(0.13 * sr)].copy(); q[-400:] *= np.linspace(1, 0, 400); q /= np.abs(q).max() + 1e-6; strokes.append(q)
for i, ts in TYPES.items():
    for j, t_ in enumerate(ts):
        if G[i][1].replace("<br>", "\n")[j] not in " \n": add(t_, strokes[(j * 5 + 2) % len(strokes)], 0.22)
mix = mus + fx[:, None]
sf.write(f"{SP}/audio/md_raw.wav", mix, sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/md_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/md_raw.wav", "-af",
                f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000", "-c:a", "pcm_s16le", f"{P}/assets/mix.wav"], check=True)

# ---------------------------------------------------------------- html
def fs(h):
    L = max(len(x) for x in h.replace("<a>", "").replace("</a>", "").split("<br>"))
    return max(x for x in (55, 89, 144) if x <= max(55, min(144, 1000 / (0.53 * max(L, 4)))))   # golden scale, largest that fits
def body(h, i, how):
    if how != "type": return h
    return "".join("<br>" if ch == "\n" else f'<span class="k" id="g{i}k{j}">{"&nbsp;" if ch == " " else ch}</span>' for j, ch in enumerate(h.replace("<br>", "\n")))
WD = "".join(f'<div class="w s-{sc}{" mk" if how == "mark" else ""}" id="g{i}" style="font-size:{fs(h)}px">'
             f'{"<span class=hl></span>" if how == "mark" else ""}<span class="in">{body(h, i, how)}</span></div>' for i, (k, h, sc, how) in enumerate(G))
PW, PHH, PR, DZ, PX, PY, BZ, NL = 470, 984, 76, 40, 305, 700, 17, 20
import math
def tone(j):
    v = int(120 + 95 * math.sin(math.pi * j / (NL - 1))); return f"rgb({v},{v + 2},{v + 6})"
LAY = "".join(f'<i class="ly" style="transform:translateZ({-DZ / 2 + DZ * j / (NL - 1):.2f}px);background:{tone(j)}"></i>' for j in range(NL))
PHONE = (f'<div class="sh3" id="H"></div><div class="p3" id="Pp">{LAY}'
         f'<div class="bk" style="transform:translateZ({-DZ / 2 - .5}px) rotateY(180deg)"><b class="cam"><i></i><i></i><i></i></b></div>'
         f'<b class="btn" style="top:210px;transform:translateX(-3px) rotateY(-90deg)"></b><b class="btn" style="top:320px;height:84px;transform:translateX(-3px) rotateY(-90deg)"></b>'
         f'<b class="btn" style="top:290px;height:140px;transform:translateX({PW - DZ * .6 + 3}px) rotateY(90deg)"></b>'
         f'<div class="fr" style="transform:translateZ({DZ / 2 + .5}px)"></div></div>'
         f'<video id="Vp" class="clip scr3" src="assets/scr/app.mp4" muted playsinline data-start="{PH0:.3f}" data-duration="{PH1 - PH0:.3f}" data-track-index="2"></video>'
         f'<div class="g3" id="Gp"><b class="isl"></b></div>')
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f5f8fb;font-family:P,sans-serif}}
.bg{{position:absolute;inset:0}}
#bgl{{background:radial-gradient(110% 70% at 80% 0%,#ffffff 0%,#f3f7fb 50%,#e4eef7 100%)}}
#bgb{{background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0}}
.w{{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;font-weight:700;letter-spacing:-.045em;line-height:1.05;
   white-space:nowrap;opacity:0;z-index:12;color:#0d1b2a}}
.w .in{{display:inline-block;position:relative}} .w a{{color:#1f88c9;text-decoration:none}} .w .k{{display:inline-block;opacity:0}}
.w.s-b{{color:#fff}} .w.s-b a{{color:#bfe3ff}}
.w.s-p{{top:330px;transform:none}}
.mk .hl{{position:absolute;left:50%;top:50%;width:var(--hw);height:1.15em;margin-left:calc(var(--hw) / -2);margin-top:-.6em;background:#fff;border-radius:.14em;transform-origin:0 50%;transform:scaleX(0)}}
.mk .in{{z-index:1}}
#brand{{position:absolute;left:480px;top:90px;width:120px;height:120px;border-radius:34px;background:#1f88c9;display:flex;align-items:center;justify-content:center;z-index:13}}
#brand img{{width:70px}}
.p3{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PHH}px;transform-style:preserve-3d;opacity:0;z-index:7}}
.ly{{position:absolute;inset:0;border-radius:{PR}px}}
.bk{{position:absolute;inset:0;border-radius:{PR}px;background:linear-gradient(160deg,#5a5d63,#2f3136 60%,#45474c)}}
.bk .cam{{position:absolute;left:30px;top:30px;width:184px;height:184px;border-radius:48px;background:#3a3c41;box-shadow:inset 0 0 0 2px #6b6e74}}
.bk .cam i{{position:absolute;width:66px;height:66px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#3b4a63,#05070b 60%);box-shadow:0 0 0 6px #1b1c20}}
.bk .cam i:nth-child(1){{left:18px;top:18px}} .bk .cam i:nth-child(2){{left:18px;top:100px}} .bk .cam i:nth-child(3){{left:100px;top:59px}}
.btn{{position:absolute;left:0;width:{DZ * .6:.0f}px;height:64px;border-radius:4px;background:linear-gradient(#9fa2a8,#d9dbdf,#8c8f95);transform-origin:0 50%}}
.fr{{position:absolute;inset:0;border-radius:{PR}px;background:#050506;box-shadow:inset 0 0 0 4px #c9ccd1,inset 0 0 0 6px #6d7076,inset 0 0 0 8px #0a0a0c}}
.scr3,.g3{{position:absolute;left:{PX + BZ}px;top:{PY + BZ}px;width:{PW - 2 * BZ}px;height:{PHH - 2 * BZ}px;border-radius:{PR - BZ}px;opacity:0;z-index:8;transform-origin:{PW / 2 - BZ}px {PHH / 2 - BZ}px}}
.scr3{{object-fit:cover;object-position:top;background:#fff}}
.g3{{z-index:9;background:linear-gradient(115deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.22) 42%,rgba(255,255,255,0) 55%);background-size:300% 100%}}
.g3 .isl{{position:absolute;left:50%;top:16px;width:132px;height:38px;margin-left:-66px;border-radius:19px;background:#050506}}
.sh3{{position:absolute;left:{PX + 30}px;top:{PY + PHH - 20}px;width:{PW - 60}px;height:60px;border-radius:50%;background:rgba(13,40,70,.35);filter:blur(24px);opacity:0;z-index:6}}
#end{{position:absolute;inset:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0;z-index:20}}
#et{{position:absolute;left:390px;top:560px;width:300px;height:300px;display:flex;align-items:center;justify-content:center}} #et img{{width:178px}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div class="bg" id="bgl"></div><div class="bg" id="bgb"></div>
<div id="brand"><img src="assets/icon_white.png" alt=""></div>
{PHONE}{WD}
<div id="end"><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const G={json.dumps([[T[i], ENDS[i], sc, how] for i, (k, h, sc, how) in enumerate(G)])}, TYPES={json.dumps(TYPES)};
G.forEach(([a,b,sc,how],i)=>{{ const w="#g"+i, n=w+" .in";
  tl.set(w,{{opacity:1}},a); tl.set(w,{{opacity:0}},b); tl.set("#bgb",{{opacity:sc==="b"?1:0}},a);
  tl.set("#brand",{{background:sc==="b"?"rgba(255,255,255,.18)":"#1f88c9"}},a);
  if(how==="pop") tl.fromTo(n,{{y:80,scale:.86,opacity:0}},E({{y:0,scale:1,opacity:1,duration:.3,ease:"back.out(1.7)"}}),a);
  if(how==="cam") tl.fromTo(n,{{scale:1.12}},E({{scale:1,duration:.3,ease:"expo.out"}}),a);
  if(how==="swap"){{ tl.fromTo(n,{{yPercent:80,opacity:0,clipPath:"inset(0 0 100% 0)"}},E({{yPercent:0,opacity:1,clipPath:"inset(0 0 0% 0)",duration:.32,ease:"expo.out"}}),a);
                     tl.to(n,{{yPercent:-50,opacity:0,duration:.14,ease:"power2.in"}},b-.14); }}
  if(how==="mark"){{ const W=document.querySelector(w+" .in").offsetWidth; document.querySelector(w).style.setProperty("--hw",(W*1.12)+"px");
                     tl.fromTo(w+" .hl",{{scaleX:0}},E({{scaleX:1,duration:.3,ease:"expo.out"}}),a+.08);
                     tl.fromTo(n,{{scale:1.15,opacity:0}},E({{scale:1,opacity:1,duration:.22,ease:"expo.out"}}),a);
                     tl.to(n,{{color:"#1f88c9",duration:.12}},a+.18); }}
  if(how==="type") (TYPES[i]||[]).forEach((t,j)=>document.querySelector(w+"k"+j)&&tl.fromTo(w+"k"+j,{{opacity:0,y:16,scale:.86}},E({{opacity:1,y:0,scale:1,duration:.1,ease:"power2.out"}}),t));
}});
tl.fromTo("#brand",{{scale:0,rotation:-15}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),0.05);
// the app in a realistic 3D phone, below the words
const P0={PH0:.3f}, P1={PH1:.3f}, E0={E0:.3f};
const Pp=document.getElementById("Pp"), Vp=document.getElementById("Vp"), Gp=document.getElementById("Gp"), H=document.getElementById("H");
const st={{y:1200,rx:16,ry:-40,rz:-7,sc:.94}};
const TT=()=>"perspective(2600px) translate3d(0,"+st.y+"px,0) rotateX("+st.rx+"deg) rotateY("+st.ry+"deg) rotateZ("+st.rz+"deg) scale("+st.sc+")";
const put=()=>{{ const t=TT(); Pp.style.transform=t; Vp.style.transform=t+" translateZ({DZ / 2 + 1}px)"; Gp.style.transform=t+" translateZ({DZ / 2 + 1.5}px)";
  Gp.style.backgroundPosition=(110-(st.ry+40)*2.2)+"% 0"; H.style.transform="translateY("+st.y*0.9+"px) scaleX("+(1-Math.abs(st.ry)/160)+")"; }};
[Pp,Vp,Gp,H].forEach((el)=>{{ tl.set(el,{{opacity:1}},P0); tl.set(el,{{opacity:0}},P1); }});
tl.fromTo(st,{{y:1200,rx:16,ry:-40,rz:-7,sc:.94}},E({{y:0,rx:6,ry:-18,rz:0,sc:1,duration:.6,ease:"expo.out",onUpdate:put}}),P0);
tl.fromTo(st,{{rx:6,ry:-18}},E({{rx:3,ry:14,duration:Math.max(.3,P1-P0-.6),ease:"sine.inOut",onUpdate:put}}),P0+.6); put();
// end
tl.set("#end",{{opacity:1}},E0); tl.set("#brand",{{opacity:0}},E0);
tl.fromTo("#et",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),E0);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(23):.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(24):.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{b(25):.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{b(26):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(26) + 0.12:.3f});
tl.set({{}},{{}},{D}); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
for i, (k, h, sc, how) in enumerate(G): print(f"{T[i]:6.2f}-{ENDS[i]:6.2f} {sc} {how:4s} {h}")
print("phone", PH0, PH1, "end", E0, "D", D, "beats", B[:6])
