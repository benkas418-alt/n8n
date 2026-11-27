# PitUp motion design drawn with p5.js (27 Nov. 2026). Generative layer in the art direction: shops appear as blue
# dots on a city map, link into a network, fly into the 2D PitUp logo, then ripple on the beat behind the words.
# Every frame is a pure function of the timeline time (p5 in noLoop mode, redrawn from GSAP's onUpdate), so the
# HyperFrames render, which seeks frame by frame, is the same each time. Seeded random, logo points sampled here.
# Sounds: real camera click on every other change of scene. Charter check: livrer.sh / charte_lint.py.
# usage: build_p5.py   (env BED=<music wav> OFF=106.07)
import json, os, shutil, subprocess, numpy as np, soundfile as sf, librosa
from PIL import Image
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-p5"; sr = 48000; REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f"{P}/assets", exist_ok=True)
for f in ["fonts", "gsap.min.js", "icon_white.png", "logo_word_white.png", "logo_tag_white.png", "appstore.svg", "Google_Play_Store_badge_EN.svg"]:
    src = f"{SP}/hf/videos/pitup-md/assets/{f}"; dst = f"{P}/assets/{f}"
    if not os.path.exists(dst): (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
shutil.copy("/home/user/ext/npm/node_modules/p5/lib/p5.min.js", f"{P}/assets/p5.min.js")   # p5.js 2.4.0
BED = os.environ.get("BED", f"{SP}/audio/tems.wav"); OFF = float(os.environ.get("OFF", "106.07"))
y, _ = librosa.load(BED, sr=22050, offset=OFF, duration=24)
_, bf = librosa.beat.beat_track(y=y, sr=22050); B = [round(float(t), 3) for t in librosa.frames_to_time(bf, sr=22050)]
if B[0] > 0.2: B = [0.0] + B
b = lambda k: B[k]
# words: (beat, html, background l|b, entry). Each lands on a beat; the dots do the rest.
G = [(0, "Les boutiques", "l", "pop"), (2, "de<br><a>Lubumbashi,</a>", "l", "pop"), (4, "réunies", "l", "swap"),
     (6, "dans ton<br><a>téléphone.</a>", "l", "pop"), (12, "Tu<br>commandes.", "b", "pop"), (14, "On te livre.", "b", "pop"),
     (16, "Tu paies", "b", "swap"), (17, "à la livraison.", "b", "mark")]
LOGO0, LOGO1 = b(8), b(10)       # dots fly into the logo, hold, the wordmark comes in
E0 = b(20); D = round(b(27) + 0.2, 2); n = int(D * sr)
T = [b(k) for k, *_ in G]; ENDS = T[1:] + [E0]
for i, (k, *_ ) in enumerate(G):
    if k == 6: ENDS[i] = LOGO0     # nothing on screen while the logo forms
BLUE_AT = LOGO0                  # background turns PitUp blue when the logo forms
SCENES = [b(4), LOGO0, b(12), E0]

# ---- particles, seeded: city positions and logo positions (sampled from the 2D icon)
rng = np.random.default_rng(7); N = 240
home = []
while len(home) < N:
    x, yy = rng.uniform(70, 1010), rng.uniform(640, 1820)
    if all((x - a) ** 2 + (yy - c) ** 2 > 56 ** 2 for a, c in home): home.append((round(x, 1), round(yy, 1)))
al = np.array(Image.open(f"{REPO}/shared-assets/icon_white.png").convert("RGBA"))[:, :, 3]
ys, xs = np.nonzero(al[::6, ::6] > 128); pts = np.stack([xs * 6, ys * 6], 1).astype(float)
pick = pts[rng.choice(len(pts), N, replace=False)]
sc = 620 / al.shape[1]; icon = [(round(540 + (px - al.shape[1] / 2) * sc, 1), round(1120 + (py - al.shape[0] / 2) * sc, 1)) for px, py in pick]
order = np.argsort([h[1] + 0.3 * h[0] for h in home])            # appear from top-left to bottom-right
appear = [0.0] * N
for r, i in enumerate(order): appear[int(i)] = round(0.15 + 2.2 * r / N, 3)
edges = []
for i in range(N):
    d = sorted(((home[i][0] - home[j][0]) ** 2 + (home[i][1] - home[j][1]) ** 2, j) for j in range(N) if j != i)
    for dd, j in d[:2]:
        if i < j and dd < 150 ** 2: edges.append((i, j))
ring = [(round(float(rng.uniform(0, 6.283)), 3), round(float(rng.uniform(180, 520)), 1)) for _ in range(N)]
DATA = dict(home=home, icon=icon, appear=appear, edges=edges, ring=ring,
            t=dict(net0=b(4), net1=b(6), fly0=LOGO0, fly1=LOGO0 + 0.9, burst=b(12), regroup=E0 - 0.9, end=E0), beats=B[:40])

# ---- audio: music + real camera click on every other change of scene
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFF}", "-t", f"{D}", "-i", BED, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2)
mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))[:n]; tt = np.arange(n) / sr
mus = mus * (np.clip((D - tt) / 1.0, 0, 1) * np.clip(tt / 0.05, 0, 1))[:, None]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in SCENES[::2]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.55 * s
sf.write(f"{SP}/audio/p5_raw.wav", mus + fx[:, None], sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/p5_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/p5_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{P}/assets/mix.wav"], check=True)

# ---- html
def fs(h):
    L = max(len(x) for x in h.replace("<a>", "").replace("</a>", "").split("<br>"))
    return max(x for x in (55, 89, 144) if x <= max(55, min(144, 1000 / (0.53 * max(L, 4)))))
WD = "".join(f'<div class="w s-{bg}{" mk" if how == "mark" else ""}" id="g{i}" style="font-size:{fs(h)}px">{"<span class=hl></span>" if how == "mark" else ""}<span class="in">{h}</span></div>'
             for i, (k, h, bg, how) in enumerate(G))
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><script src="assets/p5.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f5f8fb;font-family:P,sans-serif}}
.bg{{position:absolute;inset:0}}
#bgl{{background:radial-gradient(110% 70% at 80% 0%,#ffffff 0%,#f3f7fb 50%,#e4eef7 100%)}}
#bgb{{background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0}}
#cv{{position:absolute;inset:0;z-index:5}} #cv canvas{{display:block;width:1080px!important;height:1920px!important}}
.w{{position:absolute;left:0;right:0;top:300px;text-align:center;font-weight:700;letter-spacing:-.045em;line-height:1.05;white-space:nowrap;opacity:0;z-index:12;color:#0d1b2a}}
.w .in{{display:inline-block;position:relative}} .w a{{color:#1f88c9;text-decoration:none}}
.w.s-b{{color:#fff}} .w.s-b a{{color:#bfe3ff}}
.mk .hl{{position:absolute;left:50%;top:50%;width:var(--hw);height:1.15em;margin-left:calc(var(--hw) / -2);margin-top:-.6em;background:#fff;border-radius:.14em;transform-origin:0 50%;transform:scaleX(0)}}
#brand{{position:absolute;left:480px;top:90px;width:120px;height:120px;border-radius:34px;background:#1f88c9;display:flex;align-items:center;justify-content:center;z-index:13}} #brand img{{width:70px}}
#wm{{position:absolute;left:50%;top:1560px;width:440px;margin-left:-220px;opacity:0;z-index:12}}
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
<div class="bg" id="bgl"></div><div class="bg" id="bgb"></div><div id="cv"></div>
<div id="brand"><img src="assets/icon_white.png" alt=""></div>{WD}
<img id="wm" src="assets/logo_word_white.png" alt="">
<div id="end"><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const DATA={json.dumps(DATA)};
// ---- p5.js layer: draw(T) depends on T only
let P=null, ready=false, lastT=0;
const clamp=(x)=>Math.max(0,Math.min(1,x)), easeIO=(x)=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2, easeOut=(x)=>1-Math.pow(1-x,3);
function pulse(T){{ let k=0; for(const b of DATA.beats){{ if(b<=T) k=b; }} return Math.exp(-(T-k)*6); }}   // 1 on each beat, fades
function drawAt(T){{
  if(!ready) return; const p=P, d=DATA, t=d.t; p.clear();
  const blue = T>=t.fly0 && T<t.end;
  const fly = easeIO(clamp((T-t.fly0)/(t.fly1-t.fly0)));            // city -> logo
  const burst = easeOut(clamp((T-t.burst)/0.8));                     // logo -> rings
  const back = easeIO(clamp((T-t.regroup)/0.8));                     // rings -> logo
  const pu = pulse(T);
  // network lines, drawn progressively, fade when the dots fly
  if(T>=t.net0 && fly<1){{
    const gr = clamp((T-t.net0)/(t.net1-t.net0)); p.strokeWeight(3);
    d.edges.forEach(([i,j],k)=>{{ const f=clamp((gr-(k/d.edges.length)*0.7)/0.3);
      if(f<=0) return; const a=d.home[i], b=d.home[j];
      p.stroke(31,136,201, 255*0.45*(1-fly)); p.line(a[0],a[1], a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f); }});
  }}
  p.noStroke();
  d.home.forEach((h,i)=>{{
    const ap = easeOut(clamp((T-d.appear[i])/0.25)); if(ap<=0) return;
    const ic=d.icon[i], r=d.ring[i];
    let x=h[0]+(ic[0]-h[0])*fly, y=h[1]+(ic[1]-h[1])*fly;
    if(burst>0){{ const rad=r[1]*(1+0.08*pu), ang=r[0]+T*0.25; const rx=540+Math.cos(ang)*rad, ry=1150+Math.sin(ang)*rad;
      x=ic[0]+(rx-ic[0])*burst; y=ic[1]+(ry-ic[1])*burst; }}
    if(back>0){{ const ex=540+(ic[0]-540)*0.484, ey=710+(ic[1]-1120)*0.484;   // the end card icon: same place, same size
      x=x+(ex-x)*back; y=y+(ey-y)*back; }}
    const sz = (blue? 19 : 22)*ap*(1+0.25*pu*(burst>0&&back<1?1:0))*(1-0.45*back);
    if(blue) p.fill(255,255,255, 255*(burst>0&&back<1? 0.85:1)); else p.fill(31,136,201);
    p.circle(x,y,sz);
  }});
}}
p5.disableFriendlyErrors=true;   // no help-message fetches (they hang the render)
new p5((s)=>{{ P=s; s.setup=()=>{{ s.pixelDensity(1); const c=s.createCanvas(1080,1920); c.parent("cv"); s.noLoop(); ready=true; drawAt(lastT); }}; s.draw=()=>{{}}; }});
// ---- timeline
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const G={json.dumps([[T[i], ENDS[i], bg, how] for i, (k, h, bg, how) in enumerate(G)])};
G.forEach(([a,b,bg,how],i)=>{{ const w="#g"+i, n=w+" .in";
  tl.set(w,{{opacity:1}},a); tl.set(w,{{opacity:0}},b);
  if(how==="pop") tl.fromTo(n,{{y:80,scale:.86,opacity:0}},E({{y:0,scale:1,opacity:1,duration:.3,ease:"back.out(1.7)"}}),a);
  if(how==="swap"){{ tl.fromTo(n,{{yPercent:80,opacity:0,clipPath:"inset(0 0 100% 0)"}},E({{yPercent:0,opacity:1,clipPath:"inset(0 0 0% 0)",duration:.32,ease:"expo.out"}}),a);
                     tl.to(n,{{yPercent:-50,opacity:0,duration:.14,ease:"power2.in"}},b-.14); }}
  if(how==="mark"){{ const W=document.querySelector(n).offsetWidth; document.querySelector(w).style.setProperty("--hw",(W*1.12)+"px");
                     tl.fromTo(w+" .hl",{{scaleX:0}},E({{scaleX:1,duration:.3,ease:"expo.out"}}),a+.08);
                     tl.fromTo(n,{{scale:1.15,opacity:0}},E({{scale:1,opacity:1,duration:.22,ease:"expo.out"}}),a);
                     tl.to(n,{{color:"#1f88c9",duration:.12}},a+.18); }}
}});
tl.fromTo("#brand",{{scale:0,rotation:-15}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),0.05);
const L0={LOGO0:.3f}, E0={E0:.3f};
tl.set("#bgb",{{opacity:1}},L0); tl.set("#brand",{{background:"rgba(255,255,255,.18)"}},L0);
tl.fromTo("#wm",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{DATA["t"]["fly1"]:.3f}); tl.set("#wm",{{opacity:0}},{b(12):.3f});
tl.set("#end",{{opacity:1}},E0); tl.set("#brand",{{opacity:0}},E0);
tl.fromTo("#et",{{scale:.9,opacity:0}},E({{scale:1,opacity:1,duration:.3,ease:"expo.out"}}),E0);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(21):.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(22):.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{b(23):.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{b(24):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(24) + 0.12:.3f});
const clock={{t:0}};   // drawn from a modifier: it runs on every render, even when the seek suppresses callbacks
tl.fromTo(clock,{{t:0}},{{t:{D},duration:{D},ease:"none",immediateRender:false,modifiers:{{t:(v)=>{{ lastT=parseFloat(v); drawAt(lastT); return v; }}}}}},0);
window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
for i, (k, h, bg, how) in enumerate(G): print(f"{T[i]:6.2f}-{ENDS[i]:6.2f} {bg} {how:4s} {h}")
print("logo", LOGO0, LOGO1, "end", E0, "D", D, "edges", len(edges))
