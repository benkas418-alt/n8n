# PitUp launch film (17 Nov. 2026), adapted from the founder's reference "Meet heyclicky" (app launch film):
# sky + floating products + typed name, chat bubble, real app screens in a 3D phone, manifesto text with a highlighted
# line, dots circle with a typed sentence, "open your shop" with real shop logos, glass cards over the sky, word swap,
# typed name again + "Disponible sur" + badges. Voice: the sister (recipe "Motion point"), music: the reference's
# instrumental (demucs), cut before the Instagram outro.
# usage: build_launch.py lines.json words.json out.html     (lines.json = [[start, end], ...] per spoken line)
import json, sys
LN = json.load(open(sys.argv[1])); W = json.load(open(sys.argv[2])); OUT = sys.argv[3]
L0 = [a for a, b in LN]; L1 = [b for a, b in LN]
END = 35.4   # the reference music ends here (the Instagram outro comes after)

def wt(line, word, k=0, default=None):
    """start time of the k-th occurrence of `word` in spoken line `line`"""
    hits = [w for w in W if w[3] == line and word.lower() in w[0].lower()]
    return hits[k][1] if len(hits) > k else (default if default is not None else L0[line])

def typed_html(txt, sid):
    return "".join(f'<span class="k" id="{sid}{j}">{"&nbsp;" if c == " " else c}</span>' for j, c in enumerate(txt)) + f'<i class="cur" id="{sid}cur"></i>'

# --- scene boundaries
T = {}
T["s0"] = 0.0
T["s1"] = L0[1] - 0.15
T["s2"] = L0[2] - 0.15
T["s3"] = L0[3] - 0.15
T["s4"] = L0[4] - 0.15
T["s5"] = L0[5] - 0.15
T["s6"] = L0[6] - 0.15
T["s7"] = L0[7] - 0.15
T["s8"] = L0[8] - 0.15
T["end"] = END
ORDER = ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "end"]
SPAN = {k: (T[k], T[ORDER[i + 1]]) for i, k in enumerate(ORDER[:-1])}

# floating product cards for the intro (real photos of products sold on the app)
CARDS = [("p00", 90, 260, -8, 0.0), ("pcongo", 700, 180, 7, 0.2), ("p02", 760, 640, -5, 0.35), ("p04", 60, 1180, 6, 0.5),
         ("pfern", 720, 1260, -7, 0.15), ("p20", 120, 1560, 4, 0.6), ("ptimb", 640, 1620, 8, 0.4), ("p23", 40, 700, -4, 0.7)]
cards = "".join(f'<img class="card" id="c{i}" src="assets/img/{n}.png" style="left:{x}px;top:{y}px;--r:{r}deg" alt="">' for i, (n, x, y, r, d) in enumerate(CARDS))
LOGOS = ["s03", "s10", "s15", "s16", "s24", "s28", "s29", "s30", "s11"]
logos = "".join(f'<img class="lg" id="lg{i}" src="assets/img/{n}.png" alt="">' for i, n in enumerate(LOGOS))
DOTS = "".join(f'<i class="dot" style="--a:{i * 360 / 28}deg;background:{["#1f88c9", "#f7c948", "#e5484d", "#2bb673"][i % 4]}"></i>' for i in range(28))
MANI = [("Les boutiques de Lubumbashi, réunies dans ton téléphone.", 0), ("Tu cherches, tu compares, tu choisis.", 2),
        ("Mais nous ne faisons pas que te montrer des articles.", 3), ("Tu commandes, la boutique confirme,", 4), ("et nous te livrons.", 4)]
mani = "".join(f'<p class="ml" id="m{i}">' + (txt.replace("Mais", '<b class="hl">Mais</b>', 1)) + '</p>' for i, (txt, ln) in enumerate(MANI))
GLASS = [("+100 boutiques locales", "Habillement, chaussures, téléphones, électronique.", "g0"),
         ("Paiement à la livraison", "Tu paies quand tu reçois ta commande.", "g1"),
         ("Livraison jusque chez toi", "Nous livrons partout dans la ville.", "g2")]
glass = "".join(f'<div class="gl" id="{i}"><img src="assets/icon_white.png" alt=""><div><b>{t}</b><span>{s}</span></div></div>' for t, s, i in GLASS)

html = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;font-weight:500;src:url(assets/fonts/poppins-500.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:600;src:url(assets/fonts/poppins-600.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:700;src:url(assets/fonts/poppins-700.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:P,sans-serif;background:#f5f8fb}}
.full{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
.sc{{position:absolute;inset:0;opacity:0}}
#warm{{position:absolute;inset:0;background:linear-gradient(180deg,#f9b9c9 0%,#fcd3a8 45%,#f9e2b5 70%,#bfe0f7 100%);mix-blend-mode:soft-light;opacity:0;z-index:2}}
#warm2{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(250,180,200,.55),rgba(252,210,160,.45) 55%,rgba(255,255,255,0));opacity:0;z-index:2}}
.card{{position:absolute;width:250px;height:250px;border-radius:30px;box-shadow:0 24px 50px rgba(20,60,110,.28);transform:rotate(var(--r));opacity:0;z-index:3}}
.ty{{position:absolute;left:0;right:0;text-align:center;font-weight:600;letter-spacing:-.045em;white-space:nowrap}}
.k{{display:inline-block;opacity:0}}
.cur{{display:inline-block;width:.06em;height:.86em;margin-left:.03em;vertical-align:-.06em;background:currentColor;border-radius:3px;opacity:0}}
#t0{{top:860px;font-size:150px;color:#fff;z-index:4;text-shadow:0 8px 40px rgba(20,70,130,.35)}}
#i0{{position:absolute;left:470px;top:650px;width:140px;z-index:4;opacity:0}}
#sub0{{position:absolute;left:0;right:0;top:1080px;text-align:center;color:#fff;font-weight:500;font-size:46px;z-index:4;text-shadow:0 4px 24px rgba(20,70,130,.4)}}
.wd{{display:inline-block;opacity:0;margin:0 .14em}}
#bub{{position:absolute;left:140px;top:820px;width:800px;z-index:4;display:flex;flex-direction:column;align-items:center;gap:26px;opacity:0}}
#bub .ic{{width:190px;height:190px;border-radius:50px;background:linear-gradient(145deg,#3aa2df,#1672ab);display:flex;align-items:center;justify-content:center;box-shadow:0 30px 60px rgba(22,114,171,.35)}}
#bub .ic img{{width:110px}}
#bub .msg{{background:#e9f3fb;border:3px solid #1f88c9;color:#0d2a40;font-weight:600;font-size:52px;padding:22px 46px;border-radius:60px;box-shadow:0 18px 40px rgba(22,114,171,.18)}}
.chips{{position:absolute;left:0;right:0;top:1230px;display:flex;justify-content:center;gap:22px;z-index:4}}
.chip{{background:#fff;color:#1f88c9;font-weight:600;font-size:44px;padding:16px 34px;border-radius:50px;box-shadow:0 14px 34px rgba(22,114,171,.2);opacity:0}}
.ph{{position:absolute;width:482px;height:1040px;border-radius:74px;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,2px 1.2px 0 #3c3f45,4px 2.4px 0 #26282d,6px 3.6px 0 #1c1d21,8px 4.8px 0 #151619,10px 6px 0 #111215,40px 70px 90px rgba(4,30,60,.45);opacity:0}}
.scr{{position:absolute;border-radius:62px;object-fit:cover;object-position:top;background:#fff;opacity:0}}
.isl{{position:absolute;width:136px;height:38px;border-radius:19px;background:#050506;opacity:0}}
.win{{position:absolute;border-radius:28px;overflow:hidden;box-shadow:0 30px 70px rgba(10,40,80,.35);background:#fff;opacity:0}}
.win video{{width:100%;height:100%;object-fit:cover;object-position:top}}
#manif{{position:absolute;left:70px;right:60px;top:250px;font-weight:500;font-size:74px;line-height:1.14;letter-spacing:-.035em;color:#c3ccd6}}
.ml{{margin-bottom:12px}} .ml.on{{color:#0d1b2a}}
.hl{{font-weight:500;background:linear-gradient(transparent 8%,#fde68a 8%,#fde68a 92%,transparent 92%);padding:0 .08em;color:#0d1b2a}}
#dots{{position:absolute;left:540px;top:960px;width:0;height:0}}
.dot{{position:absolute;width:20px;height:20px;border-radius:50%;left:-10px;top:-10px;transform:rotate(var(--a)) translateY(-480px);opacity:0}}
#t4{{top:850px;font-size:66px;font-weight:500;color:#0d2a40;letter-spacing:-.03em}}
#t4m{{top:935px;font-size:66px;font-weight:500;color:#0d2a40;letter-spacing:-.03em}}
#t4b{{top:1020px;font-size:66px;font-weight:600;color:#1f88c9;letter-spacing:-.03em}}
#s5 .dark{{position:absolute;left:0;right:0;top:1000px;bottom:0;background:#0b1520}}
#t5{{position:absolute;left:70px;top:1060px;color:#fff;font-weight:600;font-size:120px;line-height:1.02;letter-spacing:-.05em}}
#t5 .a{{color:#3aa2df}}
.lgs{{position:absolute;left:70px;right:70px;top:1420px;display:grid;grid-template-columns:repeat(5,1fr);gap:22px}}
.lg{{width:160px;height:160px;border-radius:50%;object-fit:cover;border:5px solid #fff;box-shadow:0 12px 30px rgba(0,0,0,.4);opacity:0}}
.gl{{position:absolute;left:90px;right:90px;display:flex;align-items:center;gap:30px;padding:30px 36px;border-radius:36px;
 background:rgba(255,255,255,.22);border:2px solid rgba(255,255,255,.55);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
 box-shadow:0 20px 60px rgba(10,50,100,.25);color:#fff;opacity:0}}
.gl img{{width:96px;height:96px;padding:18px;border-radius:26px;background:#1f88c9}}
.gl b{{display:block;font-weight:600;font-size:50px;letter-spacing:-.02em}} .gl span{{display:block;font-weight:500;font-size:34px;opacity:.92;margin-top:4px}}
#g0{{top:640px}} #g1{{top:900px}} #g2{{top:1160px}}
#ui{{position:absolute;inset:0;background-image:linear-gradient(#e6edf4 2px,transparent 2px),linear-gradient(90deg,#e6edf4 2px,transparent 2px);background-size:270px 270px;background-position:-2px -2px}}
.uib{{position:absolute;background:#fff;border-radius:22px;box-shadow:0 10px 30px rgba(20,60,110,.10)}}
#sw{{position:absolute;left:0;right:0;top:900px;text-align:center;font-weight:600;font-size:128px;letter-spacing:-.05em;color:#0d1b2a;white-space:nowrap}}
#sw .wa{{display:inline-block;position:relative;width:640px;height:185px;vertical-align:top;text-align:left;overflow:hidden}}
#sw .wa span{{position:absolute;left:0;top:0;color:#1f88c9;opacity:0}}
#sw .wb{{display:inline-block;width:250px;text-align:right}}
#i8{{position:absolute;left:470px;top:680px;width:140px;height:140px;border-radius:38px;background:linear-gradient(145deg,#3aa2df,#1672ab);display:flex;align-items:center;justify-content:center;box-shadow:0 24px 50px rgba(22,114,171,.3);opacity:0}} #i8 img{{width:82px}}
#t8{{top:860px;font-size:130px;color:#0d1b2a}}
#tag8{{position:absolute;left:0;right:0;top:1040px;text-align:center;font-weight:500;font-size:48px;color:#1f88c9;opacity:0}}
#url8{{position:absolute;left:0;right:0;top:1250px;text-align:center;font-weight:600;font-size:40px;color:#0d2a40;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1330px;text-align:center;font-weight:500;font-size:36px;color:#51667a;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1395px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:104px}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;z-index:20;pointer-events:none}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END:.2f}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{END:.2f}" data-track-index="11"></audio>
<video id="skyA" class="clip full" src="assets/v/skyA.mp4" muted playsinline data-start="0" data-duration="{SPAN['s2'][0]:.2f}" data-track-index="1"></video>
<video id="skyB" class="clip full" src="assets/v/skyB.mp4" muted playsinline data-start="{SPAN['s2'][0]:.2f}" data-duration="{SPAN['s2'][1] - SPAN['s2'][0]:.2f}" data-track-index="2"></video>
<video id="skyC" class="clip full" src="assets/v/skyA.mp4" muted playsinline data-start="{SPAN['s6'][0]:.2f}" data-duration="{SPAN['s6'][1] - SPAN['s6'][0]:.2f}" data-track-index="3"></video>
<video id="w0v" class="clip win" src="assets/scr/ph_fernando.mp4" muted playsinline data-start="{SPAN['s2'][0]:.2f}" data-duration="{SPAN['s2'][1] - SPAN['s2'][0]:.2f}" data-track-index="4" style="left:40px;top:300px;width:330px;height:560px;z-index:4"></video>
<video id="w1v" class="clip win" src="assets/scr/ph_congo.mp4" muted playsinline data-start="{SPAN['s2'][0]:.2f}" data-duration="{SPAN['s2'][1] - SPAN['s2'][0]:.2f}" data-track-index="5" style="left:710px;top:1240px;width:330px;height:560px;z-index:4"></video>
<div id="warm"></div><div id="warm2"></div>
{cards}
<img id="i0" src="assets/icon_white.png" alt="">
<div class="ty" id="t0">{typed_html("Découvre PitUp", "t0k")}</div>
<div id="sub0">{"".join(f'<span class="wd" id="u{i}">{w}</span>' for i, w in enumerate("les boutiques de Lubumbashi, dans ton téléphone".split()))}</div>
<div id="bub"><div class="ic"><img src="assets/icon_white.png" alt=""></div><div class="msg">Tu cherches quoi aujourd'hui ?</div></div>
<div class="chips" id="chips"><span class="chip" id="ch0">Baskets</span><span class="chip" id="ch1">Robe</span><span class="chip" id="ch2">Téléphone</span></div>
<div class="ph" id="ph2" style="left:299px;top:440px;z-index:5"></div>
<video id="scr2" class="clip scr" src="assets/scr/phs_full.mp4" muted playsinline data-start="{SPAN['s2'][0]:.2f}" data-duration="{SPAN['s2'][1] - SPAN['s2'][0]:.2f}" data-track-index="6" style="left:314px;top:455px;width:452px;height:1010px;z-index:6"></video>
<div class="isl" id="isl2" style="left:472px;top:474px;z-index:7"></div>
<section class="sc" id="s3" style="background:#f7f9fb;z-index:8"><div id="manif">{mani}</div></section>
<section class="sc" id="s4" style="background:#f7f9fb;z-index:8"><div id="dots">{DOTS}</div>
 <div class="ty" id="t4">{typed_html("Tu commandes,", "t4k")}</div><div class="ty" id="t4m">{typed_html("la boutique confirme,", "t4mk")}</div><div class="ty" id="t4b">{typed_html("et nous te livrons.", "t4bk")}</div></section>
<section class="sc" id="s5" style="background:#dfeaf4;z-index:8"><div class="dark"></div>
 <div class="ph" id="ph5" style="left:330px;top:-120px;width:420px;height:906px"></div>
 <div id="t5"><span class="a">Ouvre ta</span><br>boutique.</div><div class="lgs">{logos}</div></section>
<video id="scr5" class="clip scr" src="assets/scr/phapp.mp4" muted playsinline data-start="{SPAN['s5'][0]:.2f}" data-duration="{SPAN['s5'][1] - SPAN['s5'][0]:.2f}" data-track-index="7" style="left:343px;top:-107px;width:394px;height:880px;z-index:9;border-radius:54px"></video>
{glass}
<section class="sc" id="s7" style="background:#f7f9fb;z-index:8"><div id="ui">
 <div class="uib" style="left:90px;top:330px;width:110px;height:320px"></div><div class="uib" style="left:330px;top:390px;width:420px;height:90px"></div>
 <div class="uib" style="left:820px;top:360px;width:200px;height:200px"></div><div class="uib" style="left:90px;top:1330px;width:300px;height:260px"></div>
 <div class="uib" style="left:470px;top:1400px;width:540px;height:110px"></div><div class="uib" style="left:470px;top:1560px;width:380px;height:110px"></div></div>
 <div id="sw"><span class="wb" id="swa">Tes</span>&nbsp;<span class="wa"><span id="sw0">achats.</span><span id="sw1">boutique.</span><span id="sw2">ville.</span></span></div></section>
<section class="sc" id="s8" style="background:#f7f9fb;z-index:10">
 <div id="i8"><img src="assets/icon_white.png" alt=""></div>
 <div class="ty" id="t8">{typed_html("Découvre PitUp", "t8k")}</div><div id="tag8">Le commerce, simplement.</div>
 <div id="url8">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></section>
<div id="flash"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); const E = (o) => Object.assign({{ immediateRender: false }}, o);
const SP = {json.dumps(SPAN)}, TY = {{}};
function type(prefix, n, a, b, cur) {{   // letters at even steps between a and b, cursor after the last one
  for (let j = 0; j < n; j++) {{ const t = a + (b - a) * j / Math.max(1, n - 1);
    tl.fromTo("#" + prefix + j, {{ opacity: 0, y: 10 }}, E({{ opacity: 1, y: 0, duration: .08, ease: "power2.out" }}), t); }}
  tl.set(cur, {{ opacity: 1 }}, a); for (let k = 0; k < 6; k++) {{ tl.set(cur, {{ opacity: 0 }}, b + .25 + k * .5); tl.set(cur, {{ opacity: 1 }}, b + .5 + k * .5); }}
}}
// ---- s0: sunrise sky, products float in, the name is typed with the voice
tl.fromTo("#warm", {{ opacity: 1 }}, E({{ opacity: 0, duration: 2.2, ease: "sine.inOut" }}), 0.6);
tl.fromTo("#warm2", {{ opacity: 1 }}, E({{ opacity: 0, duration: 2.4, ease: "sine.inOut" }}), 0.6);
tl.fromTo("#skyA", {{ scale: 1.15 }}, E({{ scale: 1.0, duration: SP.s2[0], ease: "sine.out" }}), 0);
{"".join(f'tl.fromTo("#c{i}", {{ opacity: 0, y: 160, scale: .8 }}, E({{ opacity: 1, y: 0, scale: 1, duration: .9, ease: "power3.out" }}), {0.15 + d:.2f}); tl.to("#c{i}", {{ y: -120, duration: SP.s1[1] - 1.1, ease: "none" }}, {1.05 + d:.2f}); tl.to("#c{i}", {{ opacity: 0, duration: .3 }}, SP.s1[1] - .3);' for i, (n, x, y, r, d) in enumerate(CARDS))}
tl.fromTo("#i0", {{ opacity: 0, y: 30, scale: .8 }}, E({{ opacity: 1, y: 0, scale: 1, duration: .5, ease: "back.out(1.6)" }}), {max(0.1, wt(0, "Découvre") - 0.3):.2f});
type("t0k", 14, {wt(0, "Découvre"):.2f}, {wt(0, "PitUp", default=L0[0] + 0.9) + 0.32:.2f}, "#t0kcur");
{"".join(f'tl.fromTo("#u{i}", {{ opacity: 0, y: 16 }}, E({{ opacity: 1, y: 0, duration: .3, ease: "power2.out" }}), {wt(0, w.strip(","), default=L0[0] + 1.2 + 0.2 * i):.2f});' for i, w in enumerate("les boutiques de Lubumbashi, dans ton téléphone".split()))}
tl.to("#i0, #t0, #sub0", {{ opacity: 0, y: -40, duration: .3, ease: "power2.in" }}, SP.s1[0] - .05);
// ---- s1: chat bubble, then the three things people look for
tl.fromTo("#bub", {{ opacity: 0, y: 60, scale: .9 }}, E({{ opacity: 1, y: 0, scale: 1, duration: .5, ease: "back.out(1.5)" }}), SP.s1[0]);
{"".join(f'tl.fromTo("#ch{i}", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: .3, ease: "back.out(2)" }}), {wt(1, w, default=L0[1] + 0.8 + 0.5 * i):.2f});' for i, w in enumerate(["baskets", "robe", "téléphone"]))}
tl.to("#bub, #chips", {{ opacity: 0, scale: .9, duration: .25, ease: "power2.in" }}, SP.s1[1] - .05);
// ---- s2: the phone rises on a curve with the real search screen; two product windows pop
["#ph2", "#scr2", "#isl2"].forEach((s) => {{ tl.set(s, {{ opacity: 1 }}, SP.s2[0]); tl.set(s, {{ opacity: 0 }}, SP.s2[1]);
  tl.fromTo(s, {{ transformPerspective: 2200, transformOrigin: "540px 960px", y: 700, rotationX: 18, rotationZ: -6 }}, E({{ y: 0, rotationX: 0, rotationZ: 0, duration: 1.0, ease: "power3.out" }}), SP.s2[0]); }});
tl.fromTo("#w0v", {{ opacity: 0, scale: .6, x: -80 }}, E({{ opacity: 1, scale: 1, x: 0, duration: .45, ease: "back.out(1.6)" }}), {wt(2, "compares", default=L0[2] + 0.6):.2f});
tl.fromTo("#w1v", {{ opacity: 0, scale: .6, x: 80 }}, E({{ opacity: 1, scale: 1, x: 0, duration: .45, ease: "back.out(1.6)" }}), {wt(2, "choisis", default=L0[2] + 1.2):.2f});
// ---- s3: manifesto, the spoken line darkens, "Mais" is highlighted
tl.set("#s3", {{ opacity: 1 }}, SP.s3[0]); tl.set("#s3", {{ opacity: 0 }}, SP.s3[1]);
tl.fromTo("#manif", {{ y: 220 }}, E({{ y: -60, duration: SP.s3[1] - SP.s3[0], ease: "power1.inOut" }}), SP.s3[0]);
tl.set("#m2", {{ className: "ml on" }}, SP.s3[0] + .05);
tl.fromTo("#s3 .hl", {{ backgroundSize: "0% 100%" }}, E({{ backgroundSize: "100% 100%", duration: .3 }}), SP.s3[0] + .1);
// ---- s4: dots circle; the sentence is typed with the voice
tl.set("#s4", {{ opacity: 1 }}, SP.s4[0]); tl.set("#s4", {{ opacity: 0 }}, SP.s4[1]);
tl.fromTo("#s4 .dot", {{ opacity: 0, scale: 0 }}, E({{ opacity: 1, scale: 1, duration: .35, ease: "back.out(2)", stagger: {{ each: .025 }} }}), SP.s4[0]);
tl.to("#dots", {{ rotation: 40, duration: SP.s4[1] - SP.s4[0], ease: "none" }}, SP.s4[0]);
type("t4k", 13, {wt(4, "commandes", default=L0[4]) - 0.2:.2f}, {wt(4, "la", default=L0[4] + 0.7) - 0.1:.2f}, "#t4kcur");
tl.set("#t4kcur", {{ opacity: 0 }}, {wt(4, "la", default=L0[4] + 0.7) - 0.05:.2f});
type("t4mk", 21, {wt(4, "la", default=L0[4] + 0.7) - 0.05:.2f}, {wt(4, "confirme", default=L0[4] + 1.4) + 0.3:.2f}, "#t4mkcur");
tl.set("#t4mkcur", {{ opacity: 0 }}, {wt(4, "nous", default=L0[4] + 1.9) - 0.1:.2f});
type("t4bk", 19, {wt(4, "nous", default=L0[4] + 1.9) - 0.1:.2f}, {L1[4] - 0.1:.2f}, "#t4bkcur");
// ---- s5: open your shop (real "create my shop" screen) + real shop logos
tl.set("#s5", {{ opacity: 1 }}, SP.s5[0]); tl.set("#s5", {{ opacity: 0 }}, SP.s5[1]);
["#ph5", "#scr5"].forEach((s) => {{ tl.set(s, {{ opacity: 1 }}, SP.s5[0]); tl.set(s, {{ opacity: 0 }}, SP.s5[1]);
  tl.fromTo(s, {{ y: -500 }}, E({{ y: 0, duration: .8, ease: "power3.out" }}), SP.s5[0]); }});
tl.fromTo("#t5", {{ opacity: 0, x: -60 }}, E({{ opacity: 1, x: 0, duration: .45, ease: "power3.out" }}), {wt(5, "Ouvre", default=L0[5] + 0.6) - 0.05:.2f});
tl.fromTo(".lg", {{ opacity: 0, scale: .4 }}, E({{ opacity: 1, scale: 1, duration: .35, ease: "back.out(2)", stagger: .07 }}), {wt(5, "boutique", default=L0[5] + 1.2):.2f});
// ---- s6: glass cards over the sky, one per fact, on the words
{"".join(f'tl.fromTo("#g{i}", {{ opacity: 0, y: 50, scale: .94 }}, E({{ opacity: 1, y: 0, scale: 1, duration: .5, ease: "power3.out" }}), {t:.2f}); tl.set("#g{i}", {{ opacity: 0 }}, SP.s6[1]);' for i, t in enumerate([wt(6, "cent", default=L0[6] + 0.2), wt(6, "paiement", default=L0[6] + 1.5), wt(6, "livraison", default=L0[6] + 2.2) + 0.25]))}
// ---- s7: word swap
tl.set("#s7", {{ opacity: 1 }}, SP.s7[0]); tl.set("#s7", {{ opacity: 0 }}, SP.s7[1]);
{"".join(f'tl.fromTo("#sw{i}", {{ opacity: 0, y: 70 }}, E({{ opacity: 1, y: 0, duration: .35, ease: "power3.out" }}), {t:.2f});' + (f'tl.to("#sw{i}", {{ opacity: 0, y: -70, duration: .25, ease: "power2.in" }}, {n - 0.25:.2f});' if n else "") for i, (t, n) in enumerate(zip([wt(7, "achats", default=L0[7] + 0.2), wt(7, "boutique", default=L0[7] + 1.0), wt(7, "ville", default=L0[7] + 1.8)], [wt(7, "boutique", default=L0[7] + 1.0), wt(7, "ville", default=L0[7] + 1.8), None])))}
tl.set("#swa", {{ textContent: "Ta" }}, {wt(7, "boutique", default=L0[7] + 1.0) - 0.05:.2f});
// ---- s8: the name typed again, slogan, site, "Disponible sur", badges
tl.set("#s8", {{ opacity: 1 }}, SP.s8[0]);
tl.fromTo("#i8", {{ opacity: 0, y: 30, scale: .8 }}, E({{ opacity: 1, y: 0, scale: 1, duration: .5, ease: "back.out(1.6)" }}), SP.s8[0]);
type("t8k", 14, {wt(8, "Découvre", default=L0[8]):.2f}, {wt(8, "PitUp", default=L0[8] + 0.8) + 0.3:.2f}, "#t8kcur");
tl.fromTo("#tag8", {{ opacity: 0, y: 20 }}, E({{ opacity: 1, y: 0, duration: .45, ease: "power3.out" }}), {wt(8, "commerce", default=L0[8] + 1.3) - 0.1:.2f});
tl.fromTo("#url8", {{ opacity: 0 }}, E({{ opacity: 1, duration: .4 }}), {wt(8, "simplement", default=L0[8] + 2) + 0.1:.2f});
tl.fromTo("#avail", {{ opacity: 0, y: 16 }}, E({{ opacity: 1, y: 0, duration: .4, ease: "power3.out" }}), {wt(8, "simplement", default=L0[8] + 2) + 0.35:.2f});
tl.fromTo("#stores", {{ opacity: 0, y: 24 }}, E({{ opacity: 1, y: 0, duration: .45, ease: "power3.out" }}), {wt(8, "simplement", default=L0[8] + 2) + 0.5:.2f});
// flashes on the two scene changes that land on a hit of the music
[SP.s2[0], SP.s5[0]].forEach((t) => tl.fromTo("#flash", {{ opacity: .6 }}, E({{ opacity: 0, duration: .18 }}), t));
tl.set({{}}, {{}}, {END:.2f});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
open(OUT, "w").write(html.replace(" ?", " ?"))
json.dump({"end": END, "span": SPAN, "type": [[wt(0, "Découvre"), wt(0, "PitUp", default=L0[0] + 0.9) + 0.32, 14],
           [wt(4, "commandes", default=L0[4]) - 0.2, wt(4, "confirme", default=L0[4] + 1.4) + 0.3, 35],
           [wt(4, "nous", default=L0[4] + 1.9) - 0.1, L1[4] - 0.1, 19], [wt(8, "Découvre", default=L0[8]), wt(8, "PitUp", default=L0[8] + 0.8) + 0.3, 14]]},
          open(OUT + ".t.json", "w"))
print("ok END", END)
