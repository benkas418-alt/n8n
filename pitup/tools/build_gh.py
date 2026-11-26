# PitUp presenter video (25-26 Nov. 2026): a collaborator shows a jersey and two pairs of sneakers, his cloned voice (v3).
# Hook: he walks to the lens and covers it, the 2D PitUp logo grows out of the black, all in about 3 s.
# v2 (26 Nov., founder): no sound effects from a sound bank ("ça donne IA", chime refused) -> voice (and music) only
# until the real sounds of his reference videos are back; no shot that repeats an earlier gesture (the second lens
# cover is gone); to fill, show the app in a realistic 3D phone (pi-tup.com recording, prices hidden) or the PitUp logo.
# usage: build_gh.py   (env BED=<music wav> MUS_DB=-17 LOGO_DB=-6 for the music; without BED: voice only)
import json, os, subprocess, numpy as np, soundfile as sf, librosa
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-gh"; A = f"{SP}/audio/gh/v3"; sr = 48000
W = {int(k): v for k, v in json.load(open(f"{A}/words.json")).items()}
V = {i: librosa.load(f"{A}/{i}.wav", sr=sr)[0] for i in range(3)}

def cut_at(i, t, win=0.12):   # quietest 10 ms frame near t, so a cut never falls inside a syllable
    y = V[i]; a, b = int(max(0, t - win) * sr), int(min(len(y) / sr, t + win) * sr); h = int(0.01 * sr)
    e = [np.sqrt(np.mean(y[j:j + h] ** 2)) for j in range(a, b - h, h // 2)]
    return (a + int(np.argmin(e)) * (h // 2) + h // 2) / sr

def wd(i, word, k=0, after=0.0):   # whisper word start in voice file i, searched after a file time
    return [w for w in W[i] if w[1] >= after - 0.05 and w[0].lower().strip(",.?!'-").startswith(word.lower())][k][1]

# voice pieces: (name, file, start, end, silence before)
c = lambda i, t: round(cut_at(i, t), 3)
PIECES = [("A1", 0, 0.0, c(0, 1.68), 0.05), ("A2", 0, c(0, 1.68), c(0, 2.68), 0.08), ("A3", 0, c(0, 2.68), c(0, 3.76), 0.05),
          ("B", 0, c(0, 3.76), c(0, 5.55), 0.80), ("C", 0, c(0, 5.55), len(V[0]) / sr, 0.12),
          ("D", 1, 0.0, c(1, 2.17), 0.16), ("E", 1, c(1, 2.17), len(V[1]) / sr, 0.14),
          ("F1", 2, 0.0, c(2, 0.78), 0.30), ("F2", 2, c(2, 0.78), c(2, 3.40), 0.12), ("G", 2, c(2, 3.40), len(V[2]) / sr, 0.40)]
voice, place, t = [], {}, 0.0
for name, i, a, b, gap in PIECES:
    y = V[i][int(a * sr):int(b * sr)].copy()
    e = np.abs(y); th = 0.03 * e.max(); idx = np.where(e > th)[0]
    s0, s1 = max(0, idx[0] - int(0.04 * sr)), min(len(y), idx[-1] + int(0.09 * sr))
    y = y[s0:s1]; f = int(0.008 * sr); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    t += gap; place[name] = (round(t, 3), round(t + len(y) / sr, 3), i, a + s0 / sr)   # (start, end, file, file time at start)
    voice.append((t, y)); t += len(y) / sr
def at(name, word=None, k=0):   # timeline time of a piece start or of a word inside it
    s, e, i, f0 = place[name]
    return s if word is None else round(s + wd(i, word, k, f0) - f0, 3)

LOGO0 = place["A3"][1] + 0.02            # the lens is covered: logo grows out of the black
CUT1 = at("B") - 0.08                    # logo -> jersey
PH0 = at("F1") - 0.22                    # the app in a 3D phone: "Tu commandes, on te livre, paiement à la livraison"
END0 = at("G") - 0.12                    # "Allez, télécharge l'appli": logo, stores
D = round(place["G"][1] + 2.4, 2); n = int(D * sr)
CUTS = [CUT1, at("C") - 0.06, at("D") - 0.06, at("E") - 0.06]
HOOK_BLACK = 3.07                        # frame where his hand fully covers the lens
# shots: (clip, timeline start, timeline end, clip time at start)
SHOTS = [("hook", 0.0, LOGO0, HOOK_BLACK - LOGO0), ("maillot2", CUTS[0], CUTS[1], 0.85),
         ("blanches", CUTS[1], CUTS[2], 0.7), ("noires", CUTS[2], CUTS[3], 0.1), ("laptop", CUTS[3], PH0, 0.4)]
# words on screen: (start, html, dark text on the light background); each stays until the next one
WORDS = [(at("A1"), "Yo les gars !", 0), (at("A2"), "Attendez…", 0), (at("A3"), "Regardez ça !", 0),
         (at("B"), "Un maillot", 0), (at("B", "tout"), "tout <a>propre.</a>", 0),
         (at("C"), "Des baskets<br>blanches", 0), (at("C", "bien"), "bien <a>clean.</a>", 0),
         (at("D"), "Et celles-là ?", 0), (at("D", "lourdes") - 0.12, "<a>Lourdes !</a>", 0),
         (at("E"), "C'est sur<br><a>PitUp</a>", 0), (at("F1"), "Tu commandes,", 1), (at("F2"), "on te livre,", 1),
         (at("F2", "tu"), "<a>Paiement</a><br>à la livraison", 1)]
WORD_END = [w[0] for w in WORDS[1:]] + [END0]
for k, (a, h, dk) in enumerate(WORDS):
    if a < LOGO0 <= WORD_END[k]: WORD_END[k] = LOGO0   # nothing on screen during the hook logo
    if a < PH0 <= WORD_END[k]: WORD_END[k] = PH0

# ---------------------------------------------------------------- audio: voice only (+ music when given)
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                                        capture_output=True).stdout, np.float32)
vox = np.zeros(n, np.float32)
for s, y in voice:
    y = y * (10 ** (-18 / 20) / max(1e-6, np.sqrt(np.mean(y[np.abs(y) > 0.02] ** 2)))); i = int(s * sr); vox[i:i + len(y)] += y[:n - i]
mix = vox
BED = os.environ.get("BED")
if BED:   # music low under the voice, rises once the last line is over
    mus = load(BED)[:n]; mus = np.pad(mus, (0, n - len(mus))); tt = np.arange(n) / sr
    up = np.clip((tt - (place["G"][1] + 0.05)) / 0.4, 0, 1)
    g = float(os.environ.get("MUS_DB", "-17")) * (1 - up) + float(os.environ.get("LOGO_DB", "-6")) * up
    mix = mix + mus * 10 ** (g / 20)
sf.write(f"{SP}/audio/gh_raw.wav", np.stack([mix, mix], 1), sr, subtype="FLOAT")   # measure loudness on the stereo file
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/gh_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/gh_raw.wav", "-af",
                f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{P}/assets/mix.wav"], check=True)

# ---------------------------------------------------------------- shots, cut to their exact length
os.makedirs(f"{P}/assets/cut", exist_ok=True)
for j, (k, a, b, off) in enumerate(SHOTS):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, off):.3f}", "-i", f"{P}/assets/rushf/{k}.mp4", "-t", f"{b - a + 0.1:.3f}",
                    "-an", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", "-r", "30",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", f"{P}/assets/cut/{j}.mp4"], check=True)

# ---------------------------------------------------------------- html
def fs(h):
    L = max(len(x) for x in h.replace("<a>", "").replace("</a>", "").split("<br>"))
    return max(x for x in (55, 89, 144) if x <= max(55, min(144, 900 / (0.56 * max(L, 4)))))
VIDS = "".join(f'<video id="r{j}" class="clip rc" src="assets/cut/{j}.mp4" muted playsinline data-start="{a:.3f}" '
               f'data-duration="{b - a:.3f}" data-track-index="{2 + j % 2}"></video>' for j, (k, a, b, off) in enumerate(SHOTS))
TXT = "".join(f'<div class="w{" dk" if dk else ""}" id="w{k}" style="font-size:{fs(h)}px"><span class="in">{h}</span></div>'
              for k, (a, h, dk) in enumerate(WORDS))
# realistic 3D phone (same build as the launch film): layered titanium edge, back with cameras, buttons, glass, screen
PW, PHH, PR, DZ, PX, PY, BZ, NL = 470, 984, 76, 40, 305, 640, 17, 20
import math
def tone(j):
    v = int(120 + 95 * math.sin(math.pi * j / (NL - 1))); return f"rgb({v},{v + 2},{v + 6})"
LAY = "".join(f'<i class="ly" style="transform:translateZ({-DZ / 2 + DZ * j / (NL - 1):.2f}px);background:{tone(j)}"></i>' for j in range(NL))
PHONE = (f'<div class="sh3" id="H"></div><div class="p3" id="Pp">{LAY}'
         f'<div class="bk" style="transform:translateZ({-DZ / 2 - .5}px) rotateY(180deg)"><b class="cam"><i></i><i></i><i></i></b></div>'
         f'<b class="btn" style="top:210px;transform:translateX(-3px) rotateY(-90deg)"></b><b class="btn" style="top:320px;height:84px;transform:translateX(-3px) rotateY(-90deg)"></b>'
         f'<b class="btn" style="top:290px;height:140px;transform:translateX({PW - DZ * .6 + 3}px) rotateY(90deg)"></b>'
         f'<div class="fr" style="transform:translateZ({DZ / 2 + .5}px)"></div></div>'
         f'<video id="Vp" class="clip scr3" src="assets/scr/app.mp4" muted playsinline data-start="{PH0:.3f}" data-duration="{END0 - PH0:.3f}" data-track-index="6"></video>'
         f'<div class="g3" id="Gp"><b class="isl"></b></div>')
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:P,sans-serif}}
.rc{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;opacity:0;z-index:1}}
#shade{{position:absolute;left:0;right:0;top:0;height:820px;background:linear-gradient(rgba(5,20,35,.6),rgba(5,20,35,0));z-index:3;opacity:0}}
.w{{position:absolute;left:0;right:0;top:250px;text-align:center;color:#fff;font-weight:700;letter-spacing:-.045em;line-height:1.04;
   white-space:nowrap;text-shadow:0 4px 30px rgba(0,0,0,.45);opacity:0;z-index:12}}
.w .in{{display:inline-block}} .w a{{color:#8fd0ff;text-decoration:none}}
.w.dk{{color:#0d1b2a;text-shadow:none;top:200px}} .w.dk a{{color:#1f88c9}}
#lg{{position:absolute;inset:0;background:#000;opacity:0;z-index:10}}
.tile{{position:absolute;left:390px;top:810px;width:300px;height:300px;border-radius:82px;background:#1f88c9;display:flex;align-items:center;justify-content:center}}
.tile img{{width:178px}}
#app{{position:absolute;inset:0;background:radial-gradient(110% 70% at 80% 0%,#ffffff 0%,#f3f7fb 50%,#e4eef7 100%);opacity:0;z-index:5}}
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
#end{{position:absolute;inset:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0;z-index:11}}
#end .tile{{top:560px;background:transparent}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
{VIDS}<div id="shade"></div><div id="app"></div>{PHONE}{TXT}
<div id="lg"><div class="tile" id="lt"><img src="assets/icon_white.png" alt=""></div></div>
<div id="end"><div class="tile" id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const SHOTS={json.dumps(SHOTS)}, WORDS={json.dumps([[a, e] for (a, h, dk), e in zip(WORDS, WORD_END)])};
SHOTS.forEach(([k,a,b,off],j)=>{{ const r="#r"+j; tl.set(r,{{opacity:1}},a); tl.set(r,{{opacity:0}},b);
  tl.fromTo(r,{{scale:1.0}},E({{scale:1.045,duration:b-a,ease:"none"}}),a); }});
WORDS.forEach(([a,b],k)=>{{ const w="#w"+k;
  tl.set(w,{{opacity:1}},a); tl.set(w,{{opacity:0}},b); tl.set("#shade",{{opacity:1}},a);
  tl.fromTo(w+" .in",{{y:60,scale:.86,opacity:0}},E({{y:0,scale:1,opacity:1,duration:.28,ease:"back.out(1.7)"}}),a); }});
// hook: the 2D logo grows out of the black, then its blue fills the screen and the jersey cuts in
const L0={LOGO0:.3f}, C1={CUT1:.3f}, P0={PH0:.3f}, E0={END0:.3f};
tl.set("#lg",{{opacity:1}},L0); tl.set("#lg",{{opacity:0}},C1); tl.set("#shade",{{opacity:0}},L0); tl.set("#shade",{{opacity:1}},C1);
tl.fromTo("#lt",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.38,ease:"back.out(2)"}}),L0);
tl.to("#lt",{{scale:9,borderRadius:"20px",duration:Math.max(.2,C1-L0-.42),ease:"power3.in"}},L0+.42);
tl.to("#lt img",{{opacity:0,duration:.12}},C1-.14);
// the app in a realistic 3D phone: one state drives body, screen and glass so they stay locked together
tl.set("#app",{{opacity:1}},P0); tl.set("#app",{{opacity:0}},E0); tl.set("#shade",{{opacity:0}},P0);
const Pp=document.getElementById("Pp"), Vp=document.getElementById("Vp"), Gp=document.getElementById("Gp"), H=document.getElementById("H");
const st={{y:1100,rx:16,ry:-40,rz:-7,sc:.94}};
const TT=()=>"perspective(2600px) translate3d(0,"+st.y+"px,0) rotateX("+st.rx+"deg) rotateY("+st.ry+"deg) rotateZ("+st.rz+"deg) scale("+st.sc+")";
const put=()=>{{ const t=TT(); Pp.style.transform=t; Vp.style.transform=t+" translateZ({DZ / 2 + 1}px)"; Gp.style.transform=t+" translateZ({DZ / 2 + 1.5}px)";
  Gp.style.backgroundPosition=(110-(st.ry+40)*2.2)+"% 0"; H.style.transform="translateY("+st.y*0.9+"px) scaleX("+(1-Math.abs(st.ry)/160)+")"; }};
[Pp,Vp,Gp,H].forEach((el)=>{{ tl.set(el,{{opacity:1}},P0); tl.set(el,{{opacity:0}},E0); }});
tl.fromTo(st,{{y:1100,rx:16,ry:-40,rz:-7,sc:.94}},E({{y:0,rx:6,ry:-18,rz:0,sc:1,duration:.6,ease:"expo.out",onUpdate:put}}),P0);
tl.fromTo(st,{{rx:6,ry:-18}},E({{rx:3,ry:14,duration:Math.max(.3,E0-P0-.6),ease:"sine.inOut",onUpdate:put}}),P0+.6); put();
// end: "Allez, télécharge l'appli. On se capte sur PitUp !"
tl.set("#end",{{opacity:1}},E0); tl.set("#shade",{{opacity:0}},E0);
tl.fromTo("#et",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.42,ease:"back.out(2)"}}),E0);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),E0+.35);
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),E0+.7);
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),E0+1.1);
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{at("G", "télécharge"):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{at("G", "télécharge") + 0.1:.3f});
tl.set({{}},{{}},{D}); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
for nm, (s, e, i, f0) in place.items(): print(f"voice {nm:3s} {s:6.2f}-{e:6.2f}")
for s in SHOTS: print("shot", s)
print("logo", round(LOGO0, 2), "cut1", round(CUT1, 2), "phone", round(PH0, 2), "end", round(END0, 2), "D", D)
