# PitUp motion design with depth (27 Nov. 2026). The clean motion was "très plat"; the founder's references (light
# beams, UI cards floating in 3D, focus pulls, glossy reflections, camera travelling through a scene) all have depth.
# Same content: Lubumbashi, the six PitUp product windows, the promise. Built in 3D space: a light beam reveals the
# logo, city photos float at several depths while the camera moves in, the product windows turn on a circular 3D
# carousel (front card sharp, the others blurred and angled, reflections on a glossy floor), focus pulls on the words.
# Every frame depends on the timeline time only (blur and depth are set from a GSAP modifier).
# Music: Jorja Smith "Blue Lights". Real camera click on every other turn. Deliver with livrer.sh.
import json, os, shutil, subprocess, importlib.util, numpy as np, soundfile as sf, librosa
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-depth"; A = f"{P}/assets"; CL = f"{SP}/hf/videos/pitup-clean/assets"; sr = 48000
if os.path.isdir(A): shutil.rmtree(A)
shutil.copytree(CL, A)
shutil.copy(f"{SP}/inbox/rj/lb_tour.jpg", f"{A}/img/lb_tour.jpg")
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/build_clean.py").read()                  # reuse the product window markup and its CSS
ns = {}; exec(src[src.index("ICO = {"):src.index("CARD0 = ")], ns)
ICO, fiche, PROD = ns["ICO"], ns["fiche"], ns["PROD"]
CARD_CSS = src[src.index(".card{{position:absolute;"):src.index(".ics{{")].replace("{{", "{").replace("}}", "}")
BED = os.environ.get("BED", f"{SP}/audio/bluelights.wav"); OFF = float(os.environ.get("OFF", "39.87"))
y, _ = librosa.load(BED, sr=22050)
_, bf = librosa.beat.beat_track(y=y, sr=22050)
B = [round(float(t) - OFF, 3) for t in librosa.frames_to_time(bf, sr=22050) if t >= OFF - 0.02]
if B[0] > 0.05: B = [0.0] + B
b = lambda k: B[k]
N = len(PROD); RING0 = 6; TURNS = [b(RING0 + 2 * i) for i in range(N)]; RING1 = b(RING0 + 2 * N)
W = [(2, "Les boutiques"), (3, "de<br><a>Lubumbashi,</a>"), (4, "dans ton<br><a>téléphone.</a>"),
     (RING0 + 2 * N, "Tu<br>commandes."), (RING0 + 2 * N + 1, "On te <a>livre.</a>"), (RING0 + 2 * N + 2, "Tu paies"), (RING0 + 2 * N + 3, "à la<br><a>livraison.</a>")]
E0 = b(RING0 + 2 * N + 5); D = round(b(RING0 + 2 * N + 11) + 0.3, 2); n = int(D * sr)
WT = [b(k) for k, _ in W]; WE = WT[1:] + [E0]; WE[2] = round(TURNS[0] - 0.15, 3)

# ---- audio
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFF}", "-t", f"{D}", "-i", BED, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2)
mus = mus[:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0))); tt = np.arange(n) / sr
mus = mus * (np.clip((D - tt) / 1.4, 0, 1) * np.clip(tt / 0.3, 0, 1))[:, None]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in (TURNS + [E0])[::2]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.45 * s
sf.write(f"{SP}/audio/depth_raw.wav", mus + fx[:, None], sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/depth_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/depth_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{A}/mix.wav"], check=True)

def fs(h):
    L = max(len(x) for x in h.replace("<a>", "").replace("</a>", "").split("<br>"))
    return max(x for x in (55, 89, 144) if x <= max(55, min(144, 1000 / (0.53 * max(L, 4)))))
WD = "".join(f'<div class="w" id="w{i}" style="font-size:{fs(h)}px"><span class="in">{h}</span></div>' for i, (k, h) in enumerate(W))
R = 760                                                     # carousel radius
RING = "".join(f'<div class="slot" id="sl{i}" style="transform:rotateY({i * 360 / N:.1f}deg) translateZ({R}px)">{fiche(i, f, nm, pos)}</div>'
               for i, (f, nm, pos) in enumerate(PROD))
CITY = [("lb_alilac", -250, -90, -300, -7), ("lb_avenue", 250, 260, -100, 6), ("lb_tour", -200, 610, -500, -4)]   # (img, x, y, z, rotation)
CT = "".join(f'<img class="city" src="assets/img/{f}.jpg" style="transform:translate3d({x}px,{y}px,{z}px) rotate({r}deg)" alt="">' for f, x, y, z, r in CITY)
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-500.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0d1b2a;font-family:P,sans-serif}}
#glow{{position:absolute;inset:0;background:radial-gradient(60% 40% at 50% 62%,rgba(31,136,201,.45) 0%,rgba(13,27,42,0) 70%)}}
#floor{{position:absolute;left:-200px;right:-200px;top:1340px;height:900px;background:linear-gradient(rgba(31,136,201,.18),rgba(13,27,42,0) 70%);transform:perspective(900px) rotateX(70deg);transform-origin:50% 0}}
#beam{{position:absolute;left:-400px;top:-300px;width:1900px;height:1900px;pointer-events:none;mix-blend-mode:screen;z-index:30;
  background:conic-gradient(from 100deg at 0% 50%,rgba(239,233,221,0) 0deg,rgba(239,233,221,.28) 8deg,rgba(239,233,221,.06) 20deg,rgba(239,233,221,0) 28deg);filter:blur(24px)}}
#logo{{position:absolute;left:50%;top:960px;width:560px;margin:-127px 0 0 -280px;z-index:25}}
#tile{{position:absolute;left:50%;top:150px;width:110px;height:110px;margin-left:-55px;border-radius:32px;background:#1f88c9;display:flex;align-items:center;justify-content:center;z-index:25;opacity:0;
  box-shadow:0 0 60px rgba(31,136,201,.6)}} #tile img{{width:64px}}
#scene{{position:absolute;inset:0;perspective:1800px;perspective-origin:50% 45%}}
#city{{position:absolute;left:50%;top:960px;width:0;height:0;transform-style:preserve-3d}}
.city{{position:absolute;left:-280px;top:-210px;width:560px;height:420px;border-radius:32px;object-fit:cover;box-shadow:0 40px 80px rgba(0,0,0,.45)}}
#ring{{position:absolute;left:50%;top:1000px;width:0;height:0;transform-style:preserve-3d}}
.slot{{position:absolute;left:-410px;top:-590px;width:820px;height:1180px;transform-style:preserve-3d}}
.slot .card{{left:0;top:0;opacity:1;-webkit-box-reflect:below 18px linear-gradient(transparent 72%,rgba(255,255,255,.22))}}
{CARD_CSS}
.w{{position:absolute;left:0;right:0;top:250px;text-align:center;font-weight:700;letter-spacing:-.045em;line-height:1.05;white-space:nowrap;color:#efe9dd;opacity:0;z-index:28;
  text-shadow:0 0 50px rgba(31,136,201,.55)}}
.w .in{{display:inline-block}} .w a{{color:#3aa2df;text-decoration:none}}
.w.late{{top:760px}}
#end{{position:absolute;inset:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0;z-index:40}}
#et{{position:absolute;left:390px;top:560px;width:300px;height:300px;display:flex;align-items:center;justify-content:center}} #et img{{width:178px}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div id="glow"></div><div id="floor"></div>
<div id="scene"><div id="city">{CT}</div><div id="ring">{RING}</div></div>
<div id="tile"><img src="assets/icon_white.png" alt=""></div><img id="logo" src="assets/logo_word_white.png" alt="">
{WD}<div id="beam"></div>
<div id="end"><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const b={json.dumps(B[:60])}, TURNS={json.dumps(TURNS)}, R1={RING1:.3f}, E0={E0:.3f}, D={D}, N={N};
const W={json.dumps([[WT[i], WE[i]] for i in range(len(W))])};
// opening: a light beam sweeps the dark and reveals the logo with a focus pull
tl.fromTo("#beam",{{rotation:-35,opacity:0}},E({{rotation:20,opacity:1,duration:1.6,ease:"power2.out"}}),0);
tl.fromTo("#logo",{{opacity:0,scale:1.25,filter:"blur(28px)"}},E({{opacity:1,scale:1,filter:"blur(0px)",duration:1.0,ease:"expo.out"}}),.25);
tl.to("#logo",{{opacity:0,scale:.9,filter:"blur(16px)",duration:.35,ease:"power2.in"}},b[2]-.35);
tl.fromTo("#tile",{{opacity:0,scale:.6}},E({{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}}),b[2]);
tl.to("#beam",{{rotation:60,opacity:.35,duration:D-1.6,ease:"none"}},1.6);
// Lubumbashi: photos float at several depths, the camera moves in between them
// opacity goes on the photos: below 1 on a preserve-3d parent it flattens the scene
tl.set(".city",{{opacity:0}},0);
tl.fromTo(".city",{{opacity:0}},E({{opacity:1,duration:.6,stagger:.12}}),b[2]);
tl.fromTo("#city",{{z:-700}},E({{z:120,duration:b[6]-b[2],ease:"power1.inOut"}}),b[2]);
tl.fromTo("#city",{{rotationY:-10}},E({{rotationY:8,duration:b[6]-b[2],ease:"sine.inOut"}}),b[2]);
tl.to(".city",{{opacity:0,duration:.3}},TURNS[0]-.3);
// words: focus pulls
W.forEach(([a,e],i)=>{{ const w="#w"+i;
  if(i>=3) document.querySelector(w).classList.add("late");
  tl.set(w,{{opacity:1}},a); tl.set(w,{{opacity:0}},e);
  tl.fromTo(w+" .in",{{opacity:0,scale:1.18,filter:"blur(22px)"}},E({{opacity:1,scale:1,filter:"blur(0px)",duration:.42,ease:"expo.out"}}),a);
  tl.to(w+" .in",{{opacity:0,scale:.94,filter:"blur(14px)",duration:.2,ease:"power2.in"}},e-.2);
}});
// the circular carousel: it comes in from the depth, then turns one product per two beats
// the circular carousel, computed from the time only (a tween on a plain object can update after the draw)
const ring=document.getElementById("ring"), slots=[...document.querySelectorAll(".slot")];
const io=gsap.parseEase("power3.inOut"), eo=gsap.parseEase("expo.out"), pi=gsap.parseEase("power2.in"), cl=(x)=>Math.max(0,Math.min(1,x));
function place(t){{ let a=0; TURNS.forEach((x,i)=>{{ if(i) a-=io(cl((t-(x-.3))/.62))*360/N; }});
  const pin=eo(cl((t-(TURNS[0]-.2))/.8)), pout=pi(cl((t-(R1-.5))/.45));
  const z=-1600*(1-pin)-1400*pout, o=pin*(1-pout);
  ring.style.transform="translateZ("+(z-760)+"px) rotateY("+a+"deg)"; 
  slots.forEach((s,i)=>{{ let d=((i*360/N+a)%360+540)%360-180; const f=Math.min(1,Math.abs(d)/60);
    s.firstElementChild.style.opacity=o; s.firstElementChild.style.filter="blur("+(f*7).toFixed(2)+"px) brightness("+(1-f*.45).toFixed(3)+")"; }}); }}
const clock={{t:0}};
tl.fromTo(clock,{{t:0}},{{t:D,duration:D,ease:"none",immediateRender:false,modifiers:{{t:(v)=>{{ place(+v); return v; }}}}}},0);
TURNS.forEach((t,i)=>tl.fromTo("#c"+i+" .imgc img",{{scale:1.12}},E({{scale:1,duration:1.1,ease:"power2.out"}}),t));
// small PitUp tile stays on top during the film
tl.to("#tile",{{opacity:0,duration:.2}},E0-.2);
// end
tl.fromTo("#end",{{opacity:0}},E({{opacity:1,duration:.3}}),E0);
tl.fromTo("#et",{{scale:.2,rotation:-12,filter:"blur(12px)"}},E({{scale:1,rotation:0,filter:"blur(0px)",duration:.5,ease:"back.out(2)"}}),E0+.05);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(RING0 + 2 * N + 6):.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(RING0 + 2 * N + 7):.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{b(RING0 + 2 * N + 8):.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{b(RING0 + 2 * N + 9):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(RING0 + 2 * N + 9) + 0.12:.3f});
tl.set({{}},{{}},D); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0); place(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
print("turns", TURNS, "promise", RING1, "end", E0, "D", D)
