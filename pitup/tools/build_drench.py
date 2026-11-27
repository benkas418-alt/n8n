# PitUp motion design in the manner of the founder's "drench" reference (27 Nov. 2026, after "C'est nul" on the flat
# motions): the 2D PitUp wordmark stays fixed in the centre while the world behind it changes every two beats with a
# hard cut: textured paper, a collage of his Lubumbashi shots, a night page of small editorial type and line icons,
# the app in a 3D phone, his collaborator's product shots graded like cinema, a technical grid. Film grain on top.
# Music: Sleepy Hallow "Anxiety" (ft. Doechii), chosen by the founder. Real camera click on every other cut.
# usage: build_drench.py   (env OFF=13.58 music start). Deliver with livrer.sh (charter check).
import json, os, shutil, subprocess, math, numpy as np, soundfile as sf, librosa
from PIL import Image, ImageFilter
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = f"{SP}/hf/videos/pitup-drench"; A = f"{P}/assets"; ST = f"{SP}/dr/st"; sr = 48000
os.makedirs(f"{A}/img", exist_ok=True)
for f in ["fonts", "gsap.min.js", "icon_white.png", "logo_word_white.png", "logo_tag_white.png", "appstore.svg", "Google_Play_Store_badge_EN.svg"]:
    src, dst = f"{SP}/hf/videos/pitup-md/assets/{f}", f"{A}/{f}"
    if not os.path.exists(dst): (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
os.makedirs(f"{A}/scr", exist_ok=True); shutil.copy(f"{SP}/hf/videos/pitup-md/assets/scr/app.mp4", f"{A}/scr/app.mp4")
shutil.copy(f"{REPO}/shared-assets/grain.png", f"{A}/grain.png")
BED = os.environ.get("BED", f"{SP}/audio/anxiety.wav"); OFF = float(os.environ.get("OFF", "13.58"))
y, _ = librosa.load(BED, sr=22050)                       # beat grid of the whole song (an excerpt misses the first beats)
_, bf = librosa.beat.beat_track(y=y, sr=22050)
B = [round(float(t) - OFF, 3) for t in librosa.frames_to_time(bf, sr=22050) if t >= OFF - 0.02]
if B[0] > 0.05: B = [0.0] + B
b = lambda k: B[k]

# ---- generated assets: paper texture, wordmark colours, graded stills (all from our own material)
rng = np.random.default_rng(11)
def paper():
    h, w = 1920, 1080; base = np.array([239, 233, 221], float)
    n = sum(np.array(Image.fromarray((rng.random((h // s + 1, w // s + 1)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255 * a
            for s, a in [(2, 10), (6, 8), (24, 6), (120, 10)])
    fib = np.zeros((h, w))
    for _ in range(900):
        x0, y0, L, ang = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(8, 40), rng.uniform(0, math.pi)
        for t in np.linspace(0, 1, 20):
            xi, yi = int(x0 + math.cos(ang) * L * t), int(y0 + math.sin(ang) * L * t)
            if 0 <= xi < w and 0 <= yi < h: fib[yi, xi] = rng.uniform(4, 10)
    img = np.clip(base[None, None, :] - (n - n.mean())[:, :, None] - fib[:, :, None], 0, 255).astype(np.uint8)
    Image.fromarray(img).filter(ImageFilter.GaussianBlur(0.6)).save(f"{A}/img/paper.jpg", quality=92)
if not os.path.exists(f"{A}/img/paper.jpg"): paper()
wm = Image.open(f"{A}/logo_word_white.png").convert("RGBA"); al = np.array(wm)[:, :, 3]
for name, col in [("navy", (13, 27, 42)), ("blue", (31, 136, 201)), ("cream", (239, 233, 221))]:
    arr = np.zeros((*al.shape, 4), np.uint8); arr[:, :, :3] = col; arr[:, :, 3] = al; Image.fromarray(arr).save(f"{A}/logo_word_{name}.png")
def grade(src, dst, crop=None):   # cinema look: 55 % desaturated, S-curve, navy shadows, cream highlights
    im = Image.open(src).convert("RGB")
    if crop: im = im.crop(crop)
    x = np.asarray(im, float) / 255; g = x @ np.array([.299, .587, .114]); x = g[..., None] + (x - g[..., None]) * 0.45
    x = 1 / (1 + np.exp(-(x - .5) * 6)); x = (x - x.min()) / (x.max() - x.min())
    sh, hi = np.array([13, 27, 42]) / 255, np.array([239, 233, 221]) / 255
    x = x * (1 - 0.18) + (sh * (1 - g[..., None]) + hi * g[..., None]) * 0.18
    Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).save(dst, quality=92)
for f, c in [("c1_5.8", (60, 120, 700, 990)), ("c1_3", (330, 940, 1080, 1720)), ("c2_1.5", None), ("maillot", None), ("blanches", None), ("noires", None), ("laptop", None)]:
    grade(f"{ST}/{f}.jpg", f"{A}/img/{f}.jpg", c)
grade(f"{ST}/c1_5.8.jpg", f"{A}/img/c1_taxi.jpg", (0, 1000, 660, 1720))   # the yellow taxi seen through the car window

CUT = f"{SP}/dr/cut"
def grade_cut(src, dst, box=None):   # same cinema look on a cut-out, alpha kept
    im = Image.open(src).convert("RGBA")
    if box: im = im.crop(box)
    im = im.crop(im.getbbox()); a = np.asarray(im, float); x = a[..., :3] / 255; g = x @ np.array([.299, .587, .114])
    x = g[..., None] + (x - g[..., None]) * 0.7; x = np.clip((x - .5) * 1.12 + .5, 0, 1)
    out = np.dstack([(x * 255), a[..., 3]]).astype(np.uint8); Image.fromarray(out).save(dst)
# 27 Nov. (founder): products come from the app listings (pi-tup.com), the most premium and trendy ones; colours kept
APP = f"{SP}/appimg"
def keep_cut(src, dst, cut_bottom=0.0):   # app product cut-out: colour kept, slight contrast, alpha kept
    im = Image.open(src).convert("RGBA"); im = im.crop(im.getbbox())
    if cut_bottom: im = im.crop((0, 0, im.width, int(im.height * (1 - cut_bottom))))
    a = np.asarray(im, float); x = np.clip((a[..., :3] / 255 - .5) * 1.08 + .5, 0, 1)
    Image.fromarray(np.dstack([x * 255, a[..., 3]]).astype(np.uint8)).save(dst)
PROD = {"jordan": ("p036_isnet.png", 0, "AIR JORDAN 4<br>NIGEL SYLVESTER"), "foam": ("p021_biref.png", 0.17, "NIKE AIR FORCE<br>FOAMPOSITE"),
        "shox": ("p161_biref.png", 0, "NIKE SHOX TL"), "congo": ("p209_isnet.png", 0, "MAILLOT<br>CONGO RDC"),
        "barca": ("p214_isnet.png", 0.06, "MAILLOT<br>FC BARCELONE")}
for k, (f, cb, _) in PROD.items(): keep_cut(f"{APP}/{f}", f"{A}/img/cut_{k}.png", cb)
for f in ["p007", "p031", "p143", "p003", "p122", "p214"]:   # product photos for the editorial grid and the collage
    shutil.copy(f"{APP}/{f}.jpg", f"{A}/img/{f}.jpg")

# ---- scenes: one every two beats, hard cuts. (kind, logo colour, line under the logo)
SC = [("paper", "navy", ""), ("collage1", "navy", ""), ("night", "cream", "Les boutiques de Lubumbashi"),
      ("phone", "cream", "dans ton téléphone."), ("studio:jordan", "cream", ""), ("gridp", "navy", ""),
      ("studio:congo", "cream", "Tu commandes,"), ("grid", "cream", "on te livre,"), ("studio:foam", "cream", ""),
      ("collage2", "navy", "tu paies à la livraison."), ("grid2", "cream", "Livré où tu veux."), ("studio:shox", "cream", "")]
T0 = [b(2 * i) for i in range(len(SC))]; E0 = b(2 * len(SC)); D = round(b(2 * len(SC) + 8) + 0.3, 2); n = int(D * sr)
T1 = T0[1:] + [E0]

# ---- audio: music + real camera click on every other cut
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFF}", "-t", f"{D}", "-i", BED, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2)
mus = mus[:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0))); tt = np.arange(n) / sr
mus = mus * (np.clip((D - tt) / 1.2, 0, 1) * np.clip(tt / 0.03, 0, 1))[:, None]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in (T0[1:] + [E0])[::2]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.5 * s
sf.write(f"{SP}/audio/dr_raw.wav", mus + fx[:, None], sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/dr_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/dr_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{A}/mix.wav"], check=True)

# ---- html pieces
ICON = {  # 2D line icons, 3 px stroke
 "cart": '<svg viewBox="0 0 48 48"><path d="M4 8h6l5 24h22l5-16H13" /><circle cx="18" cy="40" r="3"/><circle cx="34" cy="40" r="3"/></svg>',
 "pin": '<svg viewBox="0 0 48 48"><path d="M24 44s14-14 14-25a14 14 0 0 0-28 0c0 11 14 25 14 25z"/><circle cx="24" cy="19" r="5"/></svg>',
 "cash": '<svg viewBox="0 0 48 48"><rect x="4" y="12" width="40" height="24" rx="3"/><circle cx="24" cy="24" r="6"/></svg>',
 "box": '<svg viewBox="0 0 48 48"><path d="M6 14l18-8 18 8v20l-18 8-18-8z"/><path d="M6 14l18 8 18-8M24 22v20"/></svg>'}
def micro(txt, cls, style): return f'<div class="mc {cls}" style="{style}">{txt}</div>'
PW, PHH, PR, DZ, PX, PY, BZ, NL = 340, 712, 56, 30, 370, 1185, 13, 20
def tone(j): v = int(120 + 95 * math.sin(math.pi * j / (NL - 1))); return f"rgb({v},{v + 2},{v + 6})"
LAY = "".join(f'<i class="ly" style="transform:translateZ({-DZ / 2 + DZ * j / (NL - 1):.2f}px);background:{tone(j)}"></i>' for j in range(NL))
def scene(i, kind):
    if kind in ("paper", "paper2"):
        extra = micro("PITUP", "tl dk", "") + micro("LUBUMBASHI — RDC", "tr dk", "")
        if kind == "paper2": extra += '<div class="out">boutiques</div>' + micro("COMMERCE LOCAL<br>EN LIGNE", "bl dk", "")
        return f'<div class="bgimg" style="background-image:url(assets/img/paper.jpg)"></div>{extra}'
    if kind == "collage1":
        return ('<div class="bgimg" style="background-image:url(assets/img/paper.jpg)"></div>'
                '<img class="ph" src="assets/img/c1_5.8.jpg" style="left:0;top:180px;width:560px;height:760px;">'
                '<img class="ph" src="assets/img/c1_taxi.jpg" style="left:520px;top:980px;width:560px;height:760px;">' + micro("LUBUMBASHI", "tr dk", ""))
    if kind == "collage2":
        return ('<div class="bgimg" style="background-image:url(assets/img/paper.jpg)"></div>'
                '<img class="ph" src="assets/img/p214.jpg" style="left:0;top:140px;width:600px;height:640px">'
                '<img class="ph" src="assets/img/p122.jpg" style="left:480px;top:1250px;width:600px;height:600px">')
    if kind == "gridp":   # editorial grid of real app listings, labels in small capitals
        tiles = [("p007", "NIKE TN", 64, 200), ("p031", "NIKE DUNK", 556, 200), ("p143", "CASQUETTES", 64, 1150), ("p003", "POLOS", 556, 1150)]
        return ('<div class="bgimg" style="background-image:url(assets/img/paper.jpg)"></div>' +
                "".join(f'<img class="ph" src="assets/img/{f}.jpg" style="left:{x}px;top:{y}px;width:460px;height:560px">'
                        + micro(lab, "dk", f"left:{x}px;top:{y + 578}px") for f, lab, x, y in tiles))
    if kind in ("night", "grid", "grid2"):
        h = '<div class="bgc" style="background:#0d1b2a"></div>'
        if kind == "night":
            h += (micro("11°40′ S<br>27°28′ E", "c1", "left:0;right:0;top:640px;text-align:center") +
                  micro("LUBUMBASHI<br>HAUT-KATANGA · RDC", "c2", "left:0;right:0;top:1290px;text-align:center") +
                  f'<div class="ics" style="top:1430px">{ICON["cart"]}{ICON["box"]}{ICON["cash"]}</div>' + micro("PI-TUP.COM", "c3", "left:0;right:0;top:1560px;text-align:center"))
        else:
            h += ('<i class="ln h" style="top:860px"></i><i class="ln h" style="top:1060px"></i><i class="ln v" style="left:300px"></i><i class="ln v" style="left:780px"></i>'
                  '<i class="cr" style="left:540px;top:960px"></i><i class="cr s" style="left:780px;top:1060px"></i>' +
                  micro("COMMANDE&nbsp;&nbsp;✓<br>LIVRAISON&nbsp;&nbsp;✓", "c2", "left:96px;top:620px") +
                  micro("PAIEMENT<br>À LA LIVRAISON", "c2", "left:800px;top:1100px") +
                  f'<div class="ics" style="top:1500px">{ICON["pin"] if kind == "grid2" else ICON["box"]}</div>')
        return h
    if kind == "phone":
        return ('<div class="bgc" style="background:#0d1b2a"></div>'
                f'<div class="sh3" id="H"></div><div class="p3" id="Pp">{LAY}<div class="fr" style="transform:translateZ({DZ / 2 + .5}px)"></div></div>'
                f'<video id="Vp" class="clip scr3" src="assets/scr/app.mp4" muted playsinline data-start="{T0[i]:.3f}" data-duration="{T1[i] - T0[i]:.3f}" data-track-index="2"></video>'
                '<div class="g3" id="Gp"><b class="isl"></b></div>')
    if kind.startswith("studio:"):   # the product floats in a dark studio under one spotlight, like the rock in "drench"
        return ('<div class="bgc" style="background:radial-gradient(60% 45% at 50% 30%,#3b4a63 0%,#0d1b2a 70%)"></div>'
                '<div class="floor"></div><div class="shadow"></div>'
                f'<img class="prod" src="assets/img/cut_{kind[7:]}.png" alt="">' + micro(PROD[kind[7:]][2], "", "left:64px;bottom:150px") + micro("SUR PITUP", "", "right:64px;top:150px;text-align:right"))
    if kind.startswith("photo:"):
        return f'<img class="full" src="assets/img/{kind[6:]}.jpg"><div class="vig"></div>'
SCN = "".join(f'<div class="sc" id="s{i}">{scene(i, k)}</div>' for i, (k, c, l) in enumerate(SC))
LOGOS = "".join(f'<img class="wm" id="w{c}" src="assets/logo_word_{c}.png" alt="">' for c in ("navy", "blue", "cream"))
LINES = "".join(f'<div class="ul {"dk" if c in ("navy", "blue") else ""}" id="u{i}">{l}</div>' for i, (k, c, l) in enumerate(SC) if l)
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-500.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0d1b2a;font-family:P,sans-serif}}
.sc{{position:absolute;inset:0;opacity:0;overflow:hidden}}
.bgimg,.bgc{{position:absolute;inset:0;background-size:cover}}
.ph{{position:absolute;object-fit:cover}}
.full{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
.floor{{position:absolute;left:0;right:0;bottom:0;height:520px;background:linear-gradient(rgba(13,27,42,0),rgba(59,74,99,.5) 35%,#0d1b2a)}}
.shadow{{position:absolute;left:310px;top:1755px;width:460px;height:60px;border-radius:50%;background:rgba(0,0,0,.6);filter:blur(22px)}}
.prod{{position:absolute;left:50%;top:1240px;width:700px;margin-left:-350px;height:500px;object-fit:contain}}
.vig{{position:absolute;inset:0;background:radial-gradient(75% 60% at 50% 50%,rgba(13,27,42,0) 40%,rgba(13,27,42,.72) 100%)}}
.mc{{position:absolute;font-weight:500;font-size:21px;letter-spacing:.14em;line-height:1.5;color:#efe9dd}}
.mc.dk{{color:#0d1b2a}} .mc.tl{{left:64px;top:150px}} .mc.tr{{right:64px;top:150px;text-align:right}} .mc.bl{{left:64px;bottom:150px}}
.out{{position:absolute;left:0;right:0;top:1100px;text-align:center;font-weight:700;font-size:144px;letter-spacing:-.04em;color:transparent;-webkit-text-stroke:2px #0d1b2a}}
.ics{{position:absolute;left:0;right:0;display:flex;gap:44px;justify-content:center}} .ics svg{{width:55px;height:55px;fill:none;stroke:#efe9dd;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}}
.ln{{position:absolute;background:rgba(239,233,221,.55)}} .ln.h{{left:0;right:0;height:1px;transform-origin:0 50%}} .ln.v{{top:0;bottom:0;width:1px;transform-origin:50% 0}}
.cr{{position:absolute;width:34px;height:34px;margin:-17px 0 0 -17px;border:1px solid rgba(239,233,221,.8);border-radius:50%}} .cr.s{{width:21px;height:21px;margin:-10px 0 0 -10px}}
.wm{{position:absolute;left:50%;top:960px;width:520px;margin:-118px 0 0 -260px;opacity:0;z-index:30}}
.ul{{position:absolute;left:0;right:0;top:1130px;text-align:center;font-weight:600;font-size:55px;letter-spacing:-.02em;color:#efe9dd;opacity:0;z-index:30}} .ul.dk{{color:#0d1b2a}}
#grain{{position:absolute;inset:0;background:url(assets/grain.png);opacity:.16;mix-blend-mode:overlay;z-index:40;pointer-events:none}}
.p3{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PHH}px;transform-style:preserve-3d;opacity:0;z-index:7}}
.ly{{position:absolute;inset:0;border-radius:{PR}px}}
.fr{{position:absolute;inset:0;border-radius:{PR}px;background:#050506;box-shadow:inset 0 0 0 4px #c9ccd1,inset 0 0 0 6px #6d7076,inset 0 0 0 8px #0a0a0c}}
.scr3,.g3{{position:absolute;left:{PX + BZ}px;top:{PY + BZ}px;width:{PW - 2 * BZ}px;height:{PHH - 2 * BZ}px;border-radius:{PR - BZ}px;opacity:0;z-index:8;transform-origin:{PW / 2 - BZ}px {PHH / 2 - BZ}px}}
.scr3{{object-fit:cover;object-position:top;background:#fff}}
.g3{{z-index:9;background:linear-gradient(115deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.22) 42%,rgba(255,255,255,0) 55%);background-size:300% 100%}}
.g3 .isl{{position:absolute;left:50%;top:16px;width:126px;height:36px;margin-left:-63px;border-radius:18px;background:#050506}}
.sh3{{position:absolute;left:{PX + 30}px;top:{PY + PHH - 20}px;width:{PW - 60}px;height:60px;border-radius:50%;background:rgba(0,0,0,.5);filter:blur(24px);opacity:0;z-index:6}}
#end{{position:absolute;inset:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0;z-index:35}}
#et{{position:absolute;left:390px;top:560px;width:300px;height:300px;display:flex;align-items:center;justify-content:center}} #et img{{width:178px}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
{SCN}{LOGOS}{LINES}
<div id="end"><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
<div id="grain"></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const SC={json.dumps([[T0[i], T1[i], k, c, bool(l)] for i, (k, c, l) in enumerate(SC)])};
let li=0;
SC.forEach(([a,b,k,c,hasLine],i)=>{{ const s="#s"+i;
  tl.set(s,{{opacity:1}},a); tl.set(s,{{opacity:0}},b);
  ["navy","blue","cream"].forEach(n=>tl.set("#w"+n,{{opacity:n===c?1:0}},a));
  tl.fromTo(s,{{scale:1.035}},E({{scale:1,duration:b-a,ease:"power1.out"}}),a);              // slow settle inside each look
  tl.fromTo(s+" .ph",{{y:(j)=>j?40:-40}},E({{y:0,duration:.5,ease:"expo.out"}}),a);
  tl.fromTo(s+" .mc",{{opacity:0,y:10}},E({{opacity:1,y:0,duration:.25,stagger:.05,ease:"power2.out"}}),a+.05);
  tl.fromTo(s+" .ln.h",{{scaleX:0}},E({{scaleX:1,duration:.4,ease:"expo.out",stagger:.04}}),a);
  tl.fromTo(s+" .ln.v",{{scaleY:0}},E({{scaleY:1,duration:.4,ease:"expo.out",stagger:.04}}),a);
  tl.fromTo(s+" .cr",{{scale:0}},E({{scale:1,duration:.3,ease:"back.out(2)"}}),a+.1);
  tl.fromTo(s+" .ics svg",{{opacity:0,y:12}},E({{opacity:1,y:0,duration:.25,stagger:.06}}),a+.1);
  tl.fromTo(s+" .prod",{{y:30,rotation:-5}},E({{y:-14,rotation:3,duration:b-a,ease:"sine.inOut"}}),a);
  tl.fromTo(s+" .shadow",{{scaleX:.85,opacity:.7}},E({{scaleX:1,opacity:1,duration:b-a,ease:"sine.inOut"}}),a);
  tl.fromTo(s+" .out",{{opacity:0,letterSpacing:"0.08em"}},E({{opacity:1,letterSpacing:"-0.04em",duration:.5,ease:"expo.out"}}),a);
}});
// the line under the logo: a few words, on the cut
{"".join(f'tl.fromTo("#u{i}",{{opacity:0,y:18}},E({{opacity:1,y:0,duration:.22,ease:"power2.out"}}),{T0[i]:.3f}); tl.set("#u{i}",{{opacity:0}},{T1[i]:.3f});' for i, (k, c, l) in enumerate(SC) if l)}
// the phone scene
const pi={[k for k, *_ in SC].index("phone")}, P0=SC[pi][0], P1=SC[pi][1];
const Pp=document.getElementById("Pp"), Vp=document.getElementById("Vp"), Gp=document.getElementById("Gp"), H=document.getElementById("H");
const st={{y:260,ry:-30,rx:10}};
const TT=()=>"perspective(2600px) translate3d(0,"+st.y+"px,0) rotateX("+st.rx+"deg) rotateY("+st.ry+"deg)";
const put=()=>{{ const t=TT(); Pp.style.transform=t; Vp.style.transform=t+" translateZ({DZ / 2 + 1}px)"; Gp.style.transform=t+" translateZ({DZ / 2 + 1.5}px)";
  Gp.style.backgroundPosition=(110-(st.ry+40)*2.2)+"% 0"; H.style.transform="translateY("+st.y*0.9+"px)"; }};
[Pp,Vp,Gp,H].forEach((el)=>{{ tl.set(el,{{opacity:1}},P0); tl.set(el,{{opacity:0}},P1); }});
tl.fromTo(st,{{y:260,ry:-30,rx:10}},E({{y:0,ry:12,rx:4,duration:P1-P0,ease:"expo.out",onUpdate:put,modifiers:{{y:(v)=>{{st.y=parseFloat(v);put();return v;}}}}}}),P0); put();
// end
const E0={E0:.3f};
["navy","blue","cream"].forEach(n=>tl.set("#w"+n,{{opacity:0}},E0));
tl.set("#end",{{opacity:1}},E0);
tl.fromTo("#et",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),E0);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(2 * len(SC) + 1):.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(2 * len(SC) + 2):.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{b(2 * len(SC) + 3):.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{b(2 * len(SC) + 4):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(2 * len(SC) + 4) + 0.12:.3f});
tl.set({{}},{{}},{D}); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
for i, (k, c, l) in enumerate(SC): print(f"{T0[i]:6.2f}-{T1[i]:6.2f} {k:15s} {c:5s} {l}")
print("end", E0, "D", D)
