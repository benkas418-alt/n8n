# PitUp clean motion design (27 Nov. 2026): the magazine content told as a pure motion piece in the art direction
# ("au lieu de faire sortir ça en journal… en motion, animation de texte… un truc très propre").
# Light PitUp background, kinetic type on the beat, the six PitUp product windows (same layout as the app, no price,
# no invented shop) passing as a carousel with a small 3D turn, then the promise in type, then the end card.
# Music: Jorja Smith "Blue Lights" (same content as the magazine). Real camera click on every other card.
# usage: build_clean.py   (env OFF=39.87). Deliver with livrer.sh (charter check).
import json, os, shutil, subprocess, numpy as np, soundfile as sf, librosa
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-clean"; A = f"{P}/assets"; MG = f"{SP}/hf/videos/pitup-mag/assets"; sr = 48000
os.makedirs(A, exist_ok=True)
for f in ["fonts", "img", "gsap.min.js", "icon_white.png", "logo_word_white.png", "logo_tag_white.png", "logo_word_navy.png", "logo_word_blue.png",
          "appstore.svg", "Google_Play_Store_badge_EN.svg"]:
    src, dst = f"{MG}/{f}", f"{A}/{f}"
    if os.path.isdir(dst): shutil.rmtree(dst)
    (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
BED = os.environ.get("BED", f"{SP}/audio/bluelights.wav"); OFF = float(os.environ.get("OFF", "39.87"))
y, _ = librosa.load(BED, sr=22050)
_, bf = librosa.beat.beat_track(y=y, sr=22050)
B = [round(float(t) - OFF, 3) for t in librosa.frames_to_time(bf, sr=22050) if t >= OFF - 0.02]
if B[0] > 0.05: B = [0.0] + B
b = lambda k: B[k]

ICO = {"back": '<svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>', "user": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c1-4 4-6 8-6s7 2 8 6"/></svg>',
       "truck": '<svg viewBox="0 0 24 24"><path d="M3 6h11v9H3zM14 9h4l3 3v3h-7"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>',
       "shield": '<svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z"/></svg>',
       "cash": '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="11" rx="2"/><circle cx="12" cy="12.5" r="2.5"/></svg>',
       "cart": '<svg viewBox="0 0 24 24"><path d="M3 4h2l2.5 11h10l2.5-8H7"/><circle cx="9.5" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/></svg>'}
def fiche(i, img, name, pos="50% 50%"):   # the PitUp product window (layout of the real app page)
    return (f'<div class="card" id="c{i}"><div class="bar"><img src="assets/icon_white.png" class="ic" alt=""><i>{ICO["user"]}</i></div>'
            f'<div class="hd"><i>{ICO["back"]}</i><b>Produit</b></div>'
            f'<div class="imgc"><img src="assets/img/{img}.jpg" style="object-position:{pos}" alt=""></div>'
            f'<div class="info"><span class="chip">Vêtements &amp; Mode</span><div class="nm"><span>{name}</span></div>'
            f'<div class="ln">{ICO["truck"]}Les livraisons sont assurées par PitUp</div><div class="ln">{ICO["cash"]}Paiement à la livraison</div>'
            f'<div class="ln">{ICO["shield"]}Achat sécurisé</div></div>'
            '<div class="btns"><span class="b1">Ajouter au panier</span><span class="b2">Acheter maintenant</span></div></div>')
PROD = [("nb9060", "New Balance 9060", "50% 50%"), ("pull_rl", "Pull torsadé Ralph Lauren", "50% 40%"), ("mocassins_daim", "Mocassins en daim", "50% 60%"),
        ("polos_zip", "Polos en maille zippés", "50% 50%"), ("cardigans", "Cardigans en maille", "50% 55%"), ("timberland", "Timberland 6 pouces", "50% 50%")]
CARD0 = 6                                                  # first card on beat 6, one card every two beats
CT = [b(CARD0 + 2 * i) for i in range(len(PROD))]; CEND = b(CARD0 + 2 * len(PROD))
# kinetic words: (beat, html, style). Each stays until the next one.
W = [(2, "Les boutiques", "pop"), (3, "de<br><a>Lubumbashi,</a>", "pop"), (4, "dans ton<br><a>téléphone.</a>", "mask"),
     (CARD0 + 2 * len(PROD), "Tu<br>commandes.", "mask"), (CARD0 + 2 * len(PROD) + 1, "On te <a>livre.</a>", "mask"),
     (CARD0 + 2 * len(PROD) + 2, "Tu paies", "mask"), (CARD0 + 2 * len(PROD) + 3, "à la livraison.", "mark")]
E0 = b(CARD0 + 2 * len(PROD) + 5); D = round(b(CARD0 + 2 * len(PROD) + 11) + 0.3, 2); n = int(D * sr)
WT = [b(k) for k, *_ in W]; WE = WT[1:] + [E0]
WE[2] = CT[0]                                             # "dans ton téléphone." leaves when the first card comes in

# ---- audio
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFF}", "-t", f"{D}", "-i", BED, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2)
mus = mus[:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0))); tt = np.arange(n) / sr
mus = mus * (np.clip((D - tt) / 1.4, 0, 1) * np.clip(tt / 0.3, 0, 1))[:, None]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in (CT + [E0])[::2]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.45 * s
sf.write(f"{SP}/audio/clean_raw.wav", mus + fx[:, None], sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/clean_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/clean_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{A}/mix.wav"], check=True)

def fs(h):
    L = max(len(x) for x in h.replace("<a>", "").replace("</a>", "").split("<br>"))
    return max(x for x in (55, 89, 144) if x <= max(55, min(144, 1000 / (0.53 * max(L, 4)))))
WD = "".join(f'<div class="w{" mk" if st == "mark" else ""}" id="w{i}" style="font-size:{fs(h)}px">{"<span class=hl></span>" if st == "mark" else ""}<span class="in">{h}</span></div>'
             for i, (k, h, st) in enumerate(W))
CARDS = "".join(fiche(i, f, nm, pos) for i, (f, nm, pos) in enumerate(PROD))
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-500.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(110% 70% at 80% 0%,#ffffff 0%,#f3f7fb 50%,#e4eef7 100%);font-family:P,sans-serif}}
#logo{{position:absolute;left:50%;top:960px;width:520px;margin:-118px 0 0 -260px;z-index:20}}
#tile{{position:absolute;left:50%;top:700px;width:150px;height:150px;margin-left:-75px;border-radius:42px;background:#1f88c9;display:flex;align-items:center;justify-content:center;z-index:20}} #tile img{{width:88px}}
.w{{position:absolute;left:0;right:0;top:330px;text-align:center;font-weight:700;letter-spacing:-.045em;line-height:1.05;white-space:nowrap;color:#0d1b2a;opacity:0;z-index:15}}
.w .in{{display:inline-block;position:relative}} .w a{{color:#1f88c9;text-decoration:none}}
.w.late{{top:820px}}
.mk .hl{{position:absolute;left:50%;top:50%;width:var(--hw);height:1.15em;margin-left:calc(var(--hw) / -2);margin-top:-.6em;background:#1f88c9;border-radius:.14em;transform-origin:0 50%;transform:scaleX(0)}}
.city{{position:absolute;width:560px;height:420px;border-radius:36px;object-fit:cover;box-shadow:0 30px 60px rgba(13,40,70,.18);opacity:0;z-index:10}}
#stage{{position:absolute;inset:0;perspective:2200px}}
.card{{position:absolute;left:130px;top:420px;width:820px;height:1180px;border-radius:44px;background:#f5f8fb;overflow:hidden;opacity:0;
  box-shadow:0 40px 90px rgba(13,40,70,.22),0 0 0 1px rgba(13,40,70,.05);transform-origin:50% 50%}}
.bar{{position:absolute;left:0;right:0;top:0;height:100px;background:#fff;box-shadow:0 2px 10px rgba(13,27,42,.06);display:flex;align-items:center;justify-content:space-between;padding:0 40px}}
.bar .ic{{width:54px;height:54px;padding:9px;border-radius:14px;background:#1f88c9}}
.card svg{{width:34px;height:34px;fill:none;stroke:#0d1b2a;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.hd{{position:absolute;left:40px;right:40px;top:124px;height:60px;display:flex;align-items:center;justify-content:center}} .hd i{{position:absolute;left:0;top:13px}}
.hd b{{font-weight:600;font-size:34px;color:#0d1b2a}}
.imgc{{position:absolute;left:40px;right:40px;top:204px;height:470px;border-radius:30px;background:#fff;overflow:hidden}} .imgc img{{width:100%;height:100%;object-fit:cover}}
.info{{position:absolute;left:40px;right:40px;top:696px;border-radius:30px;background:#fff;padding:30px 34px}}
.chip{{display:inline-block;padding:8px 22px;border-radius:30px;background:#e4eef7;color:#1672ab;font-weight:500;font-size:21px}}
.nm{{margin-top:16px;font-weight:700;font-size:55px;letter-spacing:-.03em;line-height:1.05;color:#0d1b2a;overflow:hidden}} .nm span{{display:inline-block}}
.ln{{margin-top:12px;display:flex;align-items:center;gap:14px;font-weight:500;font-size:21px;color:#1672ab}} .ln svg{{width:28px;height:28px;stroke:#1f88c9}}
.btns{{position:absolute;left:40px;right:40px;bottom:34px;display:flex;gap:20px}}
.btns span{{flex:1;text-align:center;padding:24px 0;border-radius:22px;font-weight:600;font-size:21px}}
.b1{{background:#e4eef7;color:#1672ab;border:2px solid #bfe3ff}} .b2{{background:#1f88c9;color:#fff}}
.ics{{position:absolute;left:0;right:0;top:1180px;display:flex;gap:60px;justify-content:center;z-index:15}}
.ics svg{{width:89px;height:89px;fill:none;stroke:#1f88c9;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;opacity:0}}
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
<div id="tile"><img src="assets/icon_white.png" alt=""></div><img id="logo" src="assets/logo_word_navy.png" alt="">
<img class="city" id="ct1" src="assets/img/lb_alilac.jpg" style="left:50px;top:760px" alt=""><img class="city" id="ct2" src="assets/img/lb_avenue.jpg" style="left:470px;top:1160px" alt="">
{WD}
<div class="ics" id="ics">{ICO["cart"]}{ICO["truck"]}{ICO["cash"]}</div>
<div id="stage">{CARDS}</div>
<div id="end"><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const b={json.dumps(B[:60])}, CT={json.dumps(CT)}, CEND={CEND:.3f}, E0={E0:.3f};
const W={json.dumps([[WT[i], WE[i], st] for i, (k, h, st) in enumerate(W)])};
// opening: the 2D logo, then it goes up and gets small
tl.fromTo("#tile",{{scale:0,rotation:-20}},E({{scale:1,rotation:0,duration:.5,ease:"back.out(2)"}}),0.05);
tl.fromTo("#logo",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.5,ease:"expo.out"}}),0.3);
tl.to("#tile",{{opacity:0,scale:.4,y:-120,duration:.45,ease:"power3.in"}},b[2]-.3);
tl.to("#logo",{{y:-800,scale:.46,duration:.6,ease:"expo.inOut"}},b[2]-.3);   // the wordmark stays small at the top
// Lubumbashi in two rounded cards
tl.fromTo("#ct1",{{x:-500,opacity:0,rotation:-6}},E({{x:0,opacity:1,rotation:-4,duration:.6,ease:"expo.out"}}),b[2]);
tl.fromTo("#ct2",{{x:500,opacity:0,rotation:6}},E({{x:0,opacity:1,rotation:4,duration:.6,ease:"expo.out"}}),b[3]);
tl.to("#ct1",{{x:-700,opacity:0,duration:.4,ease:"power3.in"}},b[4]+.1); tl.to("#ct2",{{x:700,opacity:0,duration:.4,ease:"power3.in"}},b[4]+.1);
// kinetic words
W.forEach(([a,e,st],i)=>{{ const w="#w"+i, n=w+" .in";
  if(i>=3) document.querySelector(w).classList.add("late");
  tl.set(w,{{opacity:1}},a); tl.set(w,{{opacity:0}},e);
  if(st==="pop") tl.fromTo(n,{{y:80,scale:.86,opacity:0}},E({{y:0,scale:1,opacity:1,duration:.34,ease:"back.out(1.7)"}}),a);
  if(st==="mask"){{ tl.fromTo(n,{{yPercent:90,opacity:0,clipPath:"inset(0 0 100% 0)"}},E({{yPercent:0,opacity:1,clipPath:"inset(0 0 0% 0)",duration:.4,ease:"expo.out"}}),a);
                    tl.to(n,{{yPercent:-40,opacity:0,duration:.16,ease:"power2.in"}},e-.16); }}
  if(st==="mark"){{ const Wd=document.querySelector(n).offsetWidth; document.querySelector(w).style.setProperty("--hw",(Wd*1.12)+"px");
                    tl.fromTo(w+" .hl",{{scaleX:0}},E({{scaleX:1,duration:.32,ease:"expo.out"}}),a+.08);
                    tl.fromTo(n,{{scale:1.15,opacity:0}},E({{scale:1,opacity:1,duration:.24,ease:"expo.out"}}),a);
                    tl.to(n,{{color:"#ffffff",duration:.12}},a+.18); }}
}});
// the product windows, as a carousel: in from the right with a small 3D turn, out to the left
CT.forEach((a,i)=>{{ const c="#c"+i, nx=(i+1<CT.length)?CT[i+1]:CEND;
  tl.set(c,{{opacity:1}},a-.02);
  tl.fromTo(c,{{x:1000,rotateY:-28,scale:.9}},E({{x:0,rotateY:0,scale:1,duration:.55,ease:"expo.out"}}),a-.02);
  tl.fromTo(c+" .imgc img",{{scale:1.12}},E({{scale:1,duration:1.2,ease:"power2.out"}}),a);
  tl.fromTo(c+" .nm span",{{yPercent:110}},E({{yPercent:0,duration:.45,ease:"expo.out"}}),a+.18);
  tl.fromTo(c+" .ln",{{opacity:0,x:-20}},E({{opacity:1,x:0,duration:.3,stagger:.07,ease:"power2.out"}}),a+.3);
  tl.fromTo(c+" .btns span",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.3,stagger:.06,ease:"back.out(1.6)"}}),a+.42);
  tl.to(c,{{x:-1000,rotateY:28,scale:.9,duration:.45,ease:"power3.in"}},nx-.42);
  tl.set(c,{{opacity:0}},nx);
}});
// small line icons under the promise
tl.fromTo("#ics svg",{{opacity:0,y:30,scale:.7}},E({{opacity:1,y:0,scale:1,duration:.4,stagger:{{each:.65}},ease:"back.out(2)"}}),CEND);
tl.to("#ics",{{opacity:0,duration:.2}},E0-.2);
// end
tl.set(["#tile","#logo"],{{opacity:0}},E0);
tl.fromTo("#end",{{opacity:0}},E({{opacity:1,duration:.3}}),E0);
tl.fromTo("#et",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),E0+.05);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(CARD0 + 2 * len(PROD) + 6):.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(CARD0 + 2 * len(PROD) + 7):.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{b(CARD0 + 2 * len(PROD) + 8):.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{b(CARD0 + 2 * len(PROD) + 9):.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{b(CARD0 + 2 * len(PROD) + 9) + 0.12:.3f});
tl.set({{}},{{}},{D}); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
print("cards", CT, "promise", CEND, "end", E0, "D", D)
