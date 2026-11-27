# PitUp motion design "the PitUp magazine" (27 Nov. 2026, after "un autre motion design encore plus beau").
# Idea from the founder's reference "I make things move": a real sheet of paper in 3D under window light. Here a magazine
# lies on a dark table, light bars from a window drift across it, the camera floats, and the pages turn in 3D on the beat:
# cover (PitUp masthead, Lubumbashi in colour) -> one editorial page per product (his taste: Air Max 95, Samba, the little
# black dress, watches, basics) -> back page with the promise -> end card. Music: Jorja Smith "Blue Lights" (92 BPM).
# Sounds: real camera click on every other page turn. Deliver with livrer.sh (charter check).
# usage: build_mag.py   (env OFF=39.87 music start)
import json, os, shutil, subprocess, numpy as np, soundfile as sf, librosa
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-mag"; A = f"{P}/assets"; DR = f"{SP}/hf/videos/pitup-drench/assets"; sr = 48000
os.makedirs(f"{A}/img", exist_ok=True)
for f in ["fonts", "gsap.min.js", "icon_white.png", "logo_word_white.png", "logo_tag_white.png", "logo_word_navy.png", "logo_word_blue.png",
          "appstore.svg", "Google_Play_Store_badge_EN.svg", "grain.png"]:
    src, dst = f"{DR}/{f}", f"{A}/{f}"
    if not os.path.exists(dst): (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
for f in ["paper.jpg", "cut_am95.png", "cut_robe.png", "cut_tees.png", "t_samba.jpg", "t_rolex.jpg", "lb_alilac.jpg", "lb_avenue.jpg"]:
    shutil.copy(f"{DR}/img/{f}", f"{A}/img/{f}")
BED = os.environ.get("BED", f"{SP}/audio/bluelights.wav"); OFF = float(os.environ.get("OFF", "39.87"))
y, _ = librosa.load(BED, sr=22050)
_, bf = librosa.beat.beat_track(y=y, sr=22050)
B = [round(float(t) - OFF, 3) for t in librosa.frames_to_time(bf, sr=22050) if t >= OFF - 0.02]
if B[0] > 0.05: B = [0.0] + B
b = lambda k: B[k]

# pages, top of the stack first: (id, html). Inner page 820 x 1120, paper texture.
def micro(t, st): return f'<div class="mc" style="{st}">{t}</div>'
PAGES = [
 ("cover", '<img class="mast" src="assets/logo_word_navy.png" alt="">' + micro("ÉDITION LUBUMBASHI", "left:48px;top:44px") + micro("RDC · 2026", "right:48px;top:44px;text-align:right")
  + '<img class="pic" src="assets/img/lb_alilac.jpg" style="left:48px;top:300px;width:470px;height:360px">'
  + '<img class="pic" src="assets/img/lb_avenue.jpg" style="left:302px;top:560px;width:470px;height:360px">'
  + '<div class="cl" id="cl1">Les boutiques<br>de Lubumbashi,</div><div class="cl b" id="cl2">dans ton téléphone.</div>'),
 ("am95", '<div class="tt">AIR MAX<br>95</div><div class="sh"></div><img class="cut" src="assets/img/cut_am95.png" style="top:470px;height:520px" alt="">'
  + micro("NIKE", "left:48px;bottom:48px") + micro("SUR PITUP", "right:48px;bottom:48px;text-align:right")),
 ("samba", '<div class="tt">SAMBA</div><img class="pic" src="assets/img/t_samba.jpg" style="left:120px;top:300px;width:580px;height:700px">'
  + micro("ADIDAS", "left:48px;bottom:48px") + micro("SUR PITUP", "right:48px;bottom:48px;text-align:right")),
 ("robe", '<div class="tt s">LA PETITE<br>ROBE NOIRE</div><div class="sh"></div><img class="cut" src="assets/img/cut_robe.png" style="top:330px;height:690px" alt="">'
  + micro("COLLECTION", "left:48px;bottom:48px") + micro("SUR PITUP", "right:48px;bottom:48px;text-align:right")),
 ("montres", '<div class="tt">MONTRES</div><img class="pic" src="assets/img/t_rolex.jpg" style="left:120px;top:300px;width:580px;height:700px">'
  + micro("ACCESSOIRES", "left:48px;bottom:48px") + micro("SUR PITUP", "right:48px;bottom:48px;text-align:right")),
 ("basiques", '<div class="tt">BASIQUES</div><div class="sh"></div><img class="cut" src="assets/img/cut_tees.png" style="top:380px;height:620px" alt="">'
  + micro("T-SHIRTS UNIS", "left:48px;bottom:48px") + micro("SUR PITUP", "right:48px;bottom:48px;text-align:right")),
 ("back", '<div class="bl" id="bl1">Tu commandes.</div><div class="bl" id="bl2">On te livre.</div><div class="bl b" id="bl3">Tu paies<br>à la livraison.</div>'
  + '<img class="bmast" src="assets/logo_word_blue.png" alt="">' + micro("PI-TUP.COM", "left:48px;bottom:48px") + micro("LUBUMBASHI — RDC", "right:48px;bottom:48px;text-align:right")),
]
FLIPS = [b(4 + 2 * i) for i in range(len(PAGES) - 1)]          # page i turns at FLIPS[i]
BACK0 = FLIPS[-1]; E0 = b(4 + 2 * (len(PAGES) - 1) + 6); D = round(b(4 + 2 * (len(PAGES) - 1) + 12) + 0.3, 2); n = int(D * sr)

# ---- audio
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFF}", "-t", f"{D}", "-i", BED, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2)
mus = mus[:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0))); tt = np.arange(n) / sr
mus = mus * (np.clip((D - tt) / 1.4, 0, 1) * np.clip(tt / 0.4, 0, 1))[:, None]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in (FLIPS + [E0])[::2]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.45 * s
sf.write(f"{SP}/audio/mag_raw.wav", mus + fx[:, None], sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/mag_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/mag_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{A}/mix.wav"], check=True)

PG = "".join(f'<div class="page" id="p{i}" style="z-index:{50 - i}"><div class="front">{h}<div class="shade"></div></div><div class="backside"></div></div>'
             for i, (k, h) in enumerate(PAGES))
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-500.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(80% 60% at 50% 40%,#3b4a63 0%,#0d1b2a 75%);font-family:P,sans-serif}}
#cam{{position:absolute;inset:0;perspective:2400px;perspective-origin:50% 40%}}
#book{{position:absolute;left:130px;top:360px;width:820px;height:1120px;transform-style:preserve-3d;transform-origin:50% 50%}}
#bshadow{{position:absolute;left:110px;top:1520px;width:860px;height:90px;border-radius:50%;background:rgba(0,0,0,.6);filter:blur(30px)}}
.page{{position:absolute;inset:0;transform-style:preserve-3d;transform-origin:0 50%}}
.front,.backside{{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:url(assets/img/paper.jpg) center/1080px 1920px;overflow:hidden;
  box-shadow:0 0 0 1px rgba(13,27,42,.06)}}
.backside{{transform:rotateY(180deg)}}
.shade{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(13,27,42,.0),rgba(13,27,42,.35));opacity:0;pointer-events:none}}
.mc{{position:absolute;font-weight:500;font-size:21px;letter-spacing:.14em;line-height:1.5;color:#0d1b2a}}
.mast{{position:absolute;left:48px;top:110px;width:520px}}
.pic{{position:absolute;object-fit:cover;box-shadow:0 18px 40px rgba(13,27,42,.25)}}
.cl{{position:absolute;left:48px;top:960px;font-weight:700;font-size:55px;letter-spacing:-.03em;line-height:1.05;color:#0d1b2a;opacity:0}}
.cl.b{{top:1075px;font-size:34px;color:#1f88c9;letter-spacing:-.01em}}
.tt{{position:absolute;left:48px;top:96px;font-weight:700;font-size:144px;letter-spacing:-.05em;line-height:.92;color:#0d1b2a}}
.tt.s{{font-size:89px;line-height:.98}}
.cut{{position:absolute;left:50%;width:740px;margin-left:-370px;object-fit:contain}}
.sh{{position:absolute;left:190px;top:1000px;width:440px;height:46px;border-radius:50%;background:rgba(13,27,42,.3);filter:blur(16px)}}
.bl{{position:absolute;left:48px;font-weight:700;font-size:89px;letter-spacing:-.04em;line-height:1;color:#0d1b2a;opacity:0}}
#bl1{{top:140px}} #bl2{{top:300px}} #bl3{{top:460px;color:#1f88c9}}
.bmast{{position:absolute;left:48px;top:860px;width:360px}}
#light{{position:absolute;inset:-200px;pointer-events:none;z-index:60;mix-blend-mode:soft-light;
  background:repeating-linear-gradient(115deg,rgba(239,233,221,0) 0px,rgba(239,233,221,0) 120px,rgba(239,233,221,.55) 160px,rgba(239,233,221,.55) 230px,rgba(239,233,221,0) 270px,rgba(239,233,221,0) 420px);filter:blur(18px)}}
#dark{{position:absolute;inset:-200px;pointer-events:none;z-index:59;
  background:repeating-linear-gradient(115deg,rgba(13,27,42,0) 0px,rgba(13,27,42,0) 300px,rgba(13,27,42,.28) 340px,rgba(13,27,42,.28) 380px,rgba(13,27,42,0) 420px);filter:blur(10px)}}
#grain{{position:absolute;inset:0;background:url(assets/grain.png);opacity:.14;mix-blend-mode:overlay;z-index:70;pointer-events:none}}
#end{{position:absolute;inset:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0;z-index:65}}
#et{{position:absolute;left:390px;top:560px;width:300px;height:300px;display:flex;align-items:center;justify-content:center}} #et img{{width:178px}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div id="cam"><div id="bshadow"></div><div id="book">{PG}</div></div>
<div id="dark"></div><div id="light"></div>
<div id="end"><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
<div id="grain"></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const D={D}, F={json.dumps(FLIPS)}, B0={BACK0:.3f}, E0={E0:.3f};
// the camera floats over the magazine the whole time
tl.fromTo("#book",{{rotateX:26,rotateZ:-8,y:120,scale:1.06}},E({{rotateX:14,rotateZ:-3,y:0,scale:1.18,duration:E0,ease:"sine.inOut"}}),0);
tl.fromTo("#bshadow",{{opacity:.5,scaleX:.9}},E({{opacity:.8,scaleX:1,duration:E0,ease:"sine.inOut"}}),0);
// window light drifts slowly across the scene
tl.fromTo("#light",{{x:-160}},E({{x:200,duration:D,ease:"none"}}),0);
tl.fromTo("#dark",{{x:120}},E({{x:-140,duration:D,ease:"none"}}),0);
// cover lines
tl.fromTo("#cl1",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.5,ease:"expo.out"}}),{b(1):.3f});
tl.fromTo("#cl2",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.5,ease:"expo.out"}}),{b(2):.3f});
// page turns: each page lifts and turns over its spine, the next page is already there under it
F.forEach((t,i)=>{{ const p="#p"+i;
  tl.to(p,{{rotateY:-178,duration:.62,ease:"power2.inOut"}},t);
  tl.fromTo(p+" .shade",{{opacity:0}},E({{opacity:1,duration:.31,ease:"power1.in",yoyo:true,repeat:1}}),t);
  tl.set(p,{{opacity:0}},t+.62);
  tl.fromTo("#p"+(i+1)+" .cut, #p"+(i+1)+" .pic",{{y:24,scale:.97}},E({{y:0,scale:1,duration:.7,ease:"expo.out"}}),t+.2);
  tl.fromTo("#p"+(i+1)+" .tt",{{letterSpacing:"0.02em",opacity:.0}},E({{letterSpacing:"-0.05em",opacity:1,duration:.6,ease:"expo.out"}}),t+.25);
}});
// back page: the promise, one line per beat
tl.fromTo("#bl1",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 1):.3f});
tl.fromTo("#bl2",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 2):.3f});
tl.fromTo("#bl3",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 3):.3f});
// end card
tl.fromTo("#end",{{opacity:0}},E({{opacity:1,duration:.35,ease:"power2.out"}}),E0);
tl.fromTo("#et",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),E0+.1);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 7):.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 8):.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{b(4 + 2 * (len(PAGES) - 1) + 9):.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 10):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(4 + 2 * (len(PAGES) - 1) + 10) + 0.12:.3f});
tl.set({{}},{{}},D); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
print("flips", FLIPS, "back", BACK0, "end", E0, "D", D)
