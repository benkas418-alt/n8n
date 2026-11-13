# Motion v2 « Lushi, ça bouge » — no voice-over: situations from Lubumbashi, few words, music + real SFX.
# Power cut -> stock asleep under the bed -> braider's talent -> wedding without a photographer -> the city lights up.
# usage: build_mc2.py out.html   (writes out.html.cues.json for the sound mix)
import json, random, sys
OUT = sys.argv[1]
T = {"cut": 0.8, "stock": 2.7, "lift": 4.5, "order": 6.7, "talent": 8.6, "flash": 10.3, "fans": 11.7,
     "pro": 14.4, "drop": 16.1, "pick": 18.2, "city": 20.2, "light": 22.0, "w1": 22.3, "w2": 22.8, "w3": 23.3,
     "logo": 25.6, "end": 30.4}
random.seed(7)
# a city of lights: clustered dots (quartiers) + a few long links
cl = [(300, 820), (720, 760), (520, 1040), (260, 1250), (820, 1180), (560, 1420)]
dots = []
for cx, cy in cl:
    for _ in range(11):
        dots.append((cx + random.gauss(0, 70), cy + random.gauss(0, 60), random.random()))
links = []
for i, (x, y, _) in enumerate(dots):
    j = min((k for k in range(len(dots)) if k != i), key=lambda k: (dots[k][0] - x) ** 2 + (dots[k][1] - y) ** 2)
    links.append((i, j))
for a, b in [(0, 11), (11, 22), (22, 33), (33, 44), (44, 55), (5, 40), (17, 60)]:
    links.append((a, b))
svg_lines = "".join(f'<line x1="{dots[a][0]:.0f}" y1="{dots[a][1]:.0f}" x2="{dots[b][0]:.0f}" y2="{dots[b][1]:.0f}"/>' for a, b in links)
svg_dots = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{6 + 6 * r:.1f}"/>' for x, y, r in dots)
box = '<div class="bx"><i></i></div>'

html = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;font-weight:500;src:url(assets/fonts/poppins-500.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:600;src:url(assets/fonts/poppins-600.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:700;src:url(assets/fonts/poppins-700.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:800;src:url(assets/fonts/poppins-800.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:P,sans-serif;color:#fff;background:#05070a}}
.sc{{position:absolute;inset:0;opacity:0;overflow:hidden}}
.big{{position:absolute;left:80px;right:80px;font-weight:800;letter-spacing:-3px;line-height:1.02}}
.big .ln{{display:block;overflow:hidden;padding-bottom:6px}} .big .ln span{{display:inline-block}}
/* 0 power cut */
#room{{position:absolute;inset:0;background:radial-gradient(70% 45% at 50% 28%,#fff3d6 0%,#f4c46b 30%,#9a6b2c 70%,#2b1d0d 100%)}}
#bulb{{position:absolute;left:50%;top:330px;width:150px;margin-left:-75px;transform-origin:50% -300px}}
#bulb .cord{{position:absolute;left:73px;top:-330px;width:4px;height:330px;background:#1c1408}}
#bulb .glass{{width:150px;height:190px;border-radius:50% 50% 45% 45%;background:radial-gradient(circle at 50% 40%,#fff 0%,#ffe9a8 45%,#f6c75b 100%);box-shadow:0 0 120px 60px rgba(255,214,120,.65)}}
#bulb .cap{{width:70px;height:46px;margin:-6px auto 0;background:linear-gradient(90deg,#6b6b6b,#c9c9c9,#6b6b6b);border-radius:6px}}
#dark{{position:absolute;inset:0;background:#05070a;opacity:0}}
#cutw{{position:absolute;left:0;right:0;top:880px;text-align:center;font-weight:700;font-size:96px;letter-spacing:-2px;opacity:0}}
/* 1 stock */
#glow{{position:absolute;left:560px;top:700px;width:700px;height:900px;border-radius:50%;background:radial-gradient(closest-side,rgba(80,170,240,.55),rgba(80,170,240,0));opacity:0}}
.bx{{position:absolute;width:250px;height:170px;background:linear-gradient(160deg,#c89a5c,#9c6f37);border-radius:8px;box-shadow:inset 0 -14px 0 rgba(0,0,0,.18),0 18px 30px rgba(0,0,0,.45)}}
.bx i{{position:absolute;left:105px;top:0;width:40px;height:100%;background:rgba(240,225,190,.55)}}
#zz{{position:absolute;left:150px;top:880px;font-weight:700;font-size:70px;color:#9fc8ea}}
#zz span{{position:absolute;opacity:0}}
.stage{{position:absolute;inset:0;perspective:2200px}}
.phone{{position:absolute;width:420px;height:905px;border-radius:66px;padding:13px;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,2px 1.2px 0 #3c3f45,4px 2.4px 0 #26282d,6px 3.6px 0 #1c1d21,8px 4.8px 0 #151619,10px 6px 0 #111215,40px 70px 90px rgba(0,0,0,.55)}}
.phone .scr{{position:absolute;inset:13px;border-radius:54px;overflow:hidden;background:#0b0c0f}}
.phone .scr img{{width:100%;height:100%;object-fit:cover;object-position:top}}
.phone .isl{{position:absolute;left:50%;top:30px;width:116px;height:34px;margin-left:-58px;border-radius:18px;background:#050506;z-index:3}}
.toast{{position:absolute;left:90px;right:90px;height:150px;border-radius:34px;background:rgba(255,255,255,.96);color:#101418;display:flex;align-items:center;gap:26px;padding:0 32px;box-shadow:0 30px 60px rgba(0,0,0,.35);opacity:0}}
.toast .ic{{flex:0 0 86px;height:86px;border-radius:22px;background:#1f88c9;display:flex;align-items:center;justify-content:center}}
.toast .ic img{{width:58px}} .toast b{{display:block;font-weight:700;font-size:38px}} .toast span{{font-weight:500;font-size:28px;color:#5b6570}}
/* 2 talent */
#salon{{position:absolute;inset:0;background:url(assets/ph/salon.jpg) 64% center/cover;filter:brightness(.32) saturate(.8)}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0}}
#prof{{position:absolute;left:150px;right:150px;top:560px;height:860px;border-radius:44px;background:#fff;color:#101418;overflow:hidden;opacity:0;box-shadow:0 40px 80px rgba(0,0,0,.5)}}
#prof .pic{{height:560px;background:url(assets/ph/salon.jpg) 64% 30%/cover}}
#prof b{{display:block;padding:34px 40px 6px;font-weight:700;font-size:48px}} #prof span{{display:block;padding:0 40px;font-size:32px;color:#5b6570}}
#prof .btn{{position:absolute;left:40px;right:40px;bottom:38px;height:84px;border-radius:22px;background:#1f88c9;color:#fff;font-weight:600;font-size:32px;display:flex;align-items:center;justify-content:center}}
.bub{{position:absolute;left:110px;right:110px;height:120px;border-radius:30px;background:rgba(255,255,255,.97);color:#101418;display:flex;align-items:center;gap:22px;padding:0 26px;opacity:0;box-shadow:0 20px 40px rgba(0,0,0,.35)}}
.av{{flex:0 0 76px;height:76px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:34px}}
.bub b{{font-weight:700;font-size:32px}} .bub span{{display:block;font-size:24px;color:#5b6570;font-weight:500}}
/* 3 pro */
#s3{{background:radial-gradient(90% 60% at 50% 30%,#14304a 0%,#0a1422 70%,#05070a 100%)}}
#cal{{position:absolute;left:50%;top:560px;width:420px;margin-left:-210px;border-radius:40px;background:#fff;color:#101418;overflow:hidden;box-shadow:0 40px 80px rgba(0,0,0,.5)}}
#cal .h{{height:110px;background:#e2463b;color:#fff;font-weight:700;font-size:48px;display:flex;align-items:center;justify-content:center;letter-spacing:4px}}
#cal .d{{font-weight:800;font-size:200px;text-align:center;line-height:1.1;letter-spacing:-8px}} #cal .t{{text-align:center;font-weight:600;font-size:40px;padding-bottom:30px}}
.cand{{position:absolute;left:110px;right:110px;height:150px;border-radius:32px;background:#fff;color:#101418;display:flex;align-items:center;gap:26px;padding:0 30px;opacity:0;box-shadow:0 24px 50px rgba(0,0,0,.45)}}
.cand b{{font-weight:700;font-size:38px}} .cand span{{display:block;font-size:28px;color:#5b6570}}
.cand .ok{{margin-left:auto;width:84px;height:84px;border-radius:50%;background:#1fae5b;display:flex;align-items:center;justify-content:center;opacity:0}}
.cand .ok svg{{width:50px;height:50px;stroke:#fff;stroke-width:3;fill:none;stroke-linecap:round;stroke-linejoin:round}}
/* 4 city */
#sky{{position:absolute;inset:0;background:radial-gradient(120% 90% at 30% 20%,#2a9be0 0%,#1f88c9 40%,#0d5a8f 100%);opacity:0}}
#net{{position:absolute;inset:0}} #net line{{stroke:#7cc4f2;stroke-width:2;opacity:.55}} #net circle{{fill:#ffe9a8}}
#lbl{{position:absolute;left:0;right:0;top:1580px;text-align:center;font-weight:600;font-size:34px;letter-spacing:10px;color:#9fc8ea;opacity:0}}
/* logo */
#E{{position:absolute;inset:0;opacity:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
#cv{{position:absolute;left:124px;top:640px;width:1500px;height:1900px;transform-origin:0 0;transform:scale(0.4)}}
#cv img,#cv .m{{position:absolute;left:0;top:0;width:1500px;height:1900px}}
#mo{{-webkit-mask-image:url(assets/mask_out.png);mask-image:url(assets/mask_out.png);-webkit-mask-size:100% 100%;mask-size:100% 100%}}
#ps{{-webkit-mask-image:url(assets/arrow_white.png),linear-gradient(#000,#000);-webkit-mask-size:1500px 1900px,100% 100%;-webkit-mask-repeat:no-repeat;-webkit-mask-position:0px 0px,0 0;-webkit-mask-composite:xor;mask-composite:exclude}}
#word{{position:absolute;left:50%;top:1010px;width:470px;margin-left:-235px;opacity:0}}
#tag2{{position:absolute;left:50%;top:1210px;width:520px;margin-left:-260px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1330px;text-align:center;font-weight:600;font-size:40px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1440px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{T['end']:.2f}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix2.wav" data-start="0" data-duration="{T['end']:.2f}" data-track-index="11"></audio>

<section class="sc" id="s0" style="opacity:1">
 <div id="room"></div>
 <div id="bulb"><div class="cord"></div><div class="glass"></div><div class="cap"></div></div>
 <div id="dark"></div>
 <div id="cutw">Coupure.</div>
</section>

<section class="sc" id="s1">
 <div id="glow"></div>
 <div class="bx" id="x0" style="left:90px;top:1450px"><i></i></div><div class="bx" id="x1" style="left:330px;top:1450px"><i></i></div>
 <div class="bx" id="x2" style="left:200px;top:1280px"><i></i></div><div class="bx" id="x3" style="left:120px;top:1110px;transform:rotate(-4deg)"><i></i></div>
 <div id="zz"><span style="left:0;top:0">z</span><span style="left:50px;top:-70px;font-size:90px">z</span><span style="left:110px;top:-160px;font-size:110px">z</span></div>
 <h1 class="big" id="h1" style="top:300px;font-size:120px"><span class="ln"><span>Ton stock</span></span><span class="ln"><span>dort ?</span></span></h1>
 <div class="stage"><div class="phone" id="ph1" style="left:560px;top:760px"><i class="isl"></i><div class="scr"><img id="shop" src="assets/scr/store_hd.png" alt="" style="opacity:0"></div></div></div>
 <div class="toast" id="o1" style="top:640px"><div class="ic"><img src="assets/icon_white.png" alt=""></div><div><b>Nouvelle commande</b><span>Un client veut tes baskets.</span></div></div>
</section>

<section class="sc" id="s2">
 <div id="salon"></div>
 <h1 class="big" id="h2" style="top:300px;font-size:120px"><span class="ln"><span>Ton talent</span></span><span class="ln"><span>attend ?</span></span></h1>
 <div id="prof"><div class="pic"></div><b>Coiffeuse</b><span>Tresses · Lubumbashi</span><div class="btn">Contacter</div></div>
 <div class="bub" id="f0" style="top:1180px"><div class="av" style="background:#1f88c9">G</div><div><b>Nouvelle cliente</b><span>Pour des tresses samedi</span></div></div>
 <div class="bub" id="f1" style="top:1320px"><div class="av" style="background:#e07a3c">E</div><div><b>Nouvelle cliente</b><span>Disponible demain ?</span></div></div>
 <div class="bub" id="f2" style="top:1460px"><div class="av" style="background:#7a5bd6">M</div><div><b>Nouvelle cliente</b><span>Pour une cérémonie</span></div></div>
 <div id="flash"></div>
</section>

<section class="sc" id="s3">
 <h1 class="big" id="h3" style="top:250px;font-size:110px"><span class="ln"><span>Il te manque</span></span><span class="ln"><span>un pro ?</span></span></h1>
 <div id="cal"><div class="h">SAMEDI</div><div class="d">14</div><div class="t">Mariage</div></div>
 {''.join(f'<div class="cand" id="c{k}" style="top:{1050 + k*180}px"><div class="av" style="background:{c}">{l}</div><div><b>{n}</b><span>Photographe · Lubumbashi</span></div><div class="ok"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div></div>' for k, (l, n, c) in enumerate([("P", "Patrick K.", "#e07a3c"), ("J", "Joël M.", "#1f88c9"), ("A", "Aline T.", "#7a5bd6")]))}
</section>

<section class="sc" id="s4">
 <div id="sky"></div>
 <svg id="net" viewBox="0 0 1080 1920"><g id="lines">{svg_lines}</g><g id="dots">{svg_dots}</g></svg>
 <div id="lbl">LUBUMBASHI</div>
 <h1 class="big" id="h4" style="top:330px;font-size:150px"><span class="ln"><span id="w1">Vends.</span></span><span class="ln"><span id="w2">Propose.</span></span><span class="ln"><span id="w3">Trouve.</span></span></h1>
</section>

<div id="E">
 <div id="cv"><img id="ps" src="assets/p_solid.png" alt=""><div class="m" id="mo"><img id="aw" src="assets/arrow_white.png" alt=""></div></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag2" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); const T = {json.dumps(T)};
const E = (o) => Object.assign({{ immediateRender: false }}, o);
const lines = (sel, t) => tl.fromTo(sel + " .ln > span", {{ yPercent: 110 }}, E({{ yPercent: 0, duration: 0.6, ease: "power3.out", stagger: 0.03 }}), t);
const scene = (id, a, b) => {{ tl.set(id, {{ opacity: 1 }}, a); tl.set(id, {{ opacity: 0 }}, b); }};
// 0 — power cut: bulb sways, switch clicks, everything goes black, then the word
tl.fromTo("#bulb", {{ rotation: -4 }}, {{ rotation: 3, duration: 0.8, ease: "sine.inOut" }}, 0);
tl.set("#dark", {{ opacity: 1 }}, T.cut); tl.set("#bulb .glass", {{ boxShadow: "0 0 0 0 rgba(0,0,0,0)", background: "#2a2a2a" }}, T.cut);
tl.fromTo("#cutw", {{ opacity: 0, filter: "blur(10px)" }}, E({{ opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power2.out" }}), T.cut + 0.45);
tl.to("#cutw", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, T.stock - 0.3);
scene("#s0", 0, T.stock);
// 1 — stock asleep: the phone screen lights the room, boxes fly into the app, an order arrives
scene("#s1", T.stock, T.talent);
tl.fromTo("#glow", {{ opacity: 0 }}, E({{ opacity: 1, duration: 0.8 }}), T.stock + 0.2);
tl.fromTo("#ph1", {{ x: 300, rotationY: -40, opacity: 0 }}, E({{ x: 0, rotationY: -12, opacity: 1, duration: 0.8, ease: "power3.out" }}), T.stock + 0.1);
lines("#h1", T.stock + 0.35);
tl.fromTo(".bx", {{ opacity: 0, y: 40 }}, E({{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.06 }}), T.stock + 0.2);
["#zz span:nth-child(1)", "#zz span:nth-child(2)", "#zz span:nth-child(3)"].forEach((s, k) => {{
  tl.fromTo(s, {{ opacity: 0, y: 20 }}, E({{ opacity: 1, y: -10, duration: 0.5, ease: "power2.out" }}), T.stock + 0.6 + k * 0.35);
  tl.to(s, {{ opacity: 0, duration: 0.3 }}, T.lift - 0.2);
}});
[3, 2, 1, 0].forEach((k, n) => {{
  const t = T.lift + n * 0.32;
  tl.to("#x" + k, {{ x: 760 - (k % 2) * 240, duration: 0.55, ease: "power2.in" }}, t);              // curved path: x eases in,
  tl.to("#x" + k, {{ y: -420 + k * 40, scale: 0.25, rotation: 18, duration: 0.55, ease: "power3.out" }}, t);   // y eases out
  tl.to("#x" + k, {{ opacity: 0, duration: 0.12 }}, t + 0.45);
}});
tl.to("#shop", {{ opacity: 1, duration: 0.4 }}, T.lift + 0.5);
tl.to("#ph1", {{ rotationY: -4, duration: 1.5, ease: "sine.inOut" }}, T.lift + 0.6);
tl.fromTo("#o1", {{ opacity: 0, y: -60, scale: 0.95 }}, E({{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}), T.order);
tl.to("#o1", {{ scale: 0.97, duration: 0.09, yoyo: true, repeat: 1 }}, T.order + 0.7);
// 2 — talent: dark salon, flash, the photo becomes a profile, clients arrive
scene("#s2", T.talent, T.pro);
lines("#h2", T.talent + 0.2);
tl.fromTo("#salon", {{ scale: 1.1 }}, E({{ scale: 1, duration: 1.7, ease: "power1.out" }}), T.talent);
tl.set("#flash", {{ opacity: 1 }}, T.flash); tl.to("#flash", {{ opacity: 0, duration: 0.35, ease: "power2.out" }}, T.flash + 0.06);
tl.set("#salon", {{ filter: "brightness(.22) saturate(.6) blur(6px)" }}, T.flash);
tl.fromTo("#prof", {{ opacity: 0, scale: 1.25, y: -40 }}, E({{ opacity: 1, scale: 1, y: 0, duration: 0.6, ease: "power3.out" }}), T.flash + 0.05);
tl.to("#h2", {{ opacity: 0, duration: 0.25 }}, T.flash);
["#f0", "#f1", "#f2"].forEach((s, k) => {{
  const t = T.fans + k * 0.55;
  tl.fromTo(s, {{ opacity: 0, x: 80, scale: 0.95 }}, E({{ opacity: 1, x: 0, scale: 1, duration: 0.4, ease: "power3.out" }}), t);
}});
tl.to("#prof", {{ y: -230, scale: 0.78, transformOrigin: "50% 0%", duration: 0.7, ease: "power2.inOut" }}, T.fans - 0.3);
// 3 — wedding Saturday, no photographer: three candidates drop, one is picked
scene("#s3", T.pro, T.city);
lines("#h3", T.pro + 0.2);
tl.fromTo("#cal", {{ opacity: 0, y: 60, rotation: -3 }}, E({{ opacity: 1, y: 0, rotation: 0, duration: 0.6, ease: "power3.out" }}), T.pro + 0.3);
tl.to("#cal", {{ y: -60, scale: 0.75, duration: 0.6, ease: "power2.inOut" }}, T.drop - 0.5);
[0, 1, 2].forEach(k => tl.fromTo("#c" + k, {{ opacity: 0, y: -140 }}, E({{ opacity: 1, y: 0, duration: 0.42, ease: "power2.in" }}), T.drop + k * 0.35));
tl.to("#c0, #c2", {{ opacity: 0.25, scale: 0.97, duration: 0.3, ease: "power2.out" }}, T.pick);
tl.to("#c1", {{ scale: 1.04, duration: 0.25, ease: "power2.out" }}, T.pick);
tl.fromTo("#c1 .ok", {{ opacity: 0, scale: 0.6, filter: "blur(6px)" }}, E({{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }}), T.pick + 0.1);
tl.to("#c1 .ok", {{ scale: 1.15, duration: 0.12, yoyo: true, repeat: 1 }}, T.pick + 0.5);
// 4 — the city lights up, the power comes back, three verbs
scene("#s4", T.city, T.logo + 0.4);
tl.set("#net line, #net circle", {{ opacity: 0 }}, T.city);
tl.to("#net circle", {{ opacity: 1, duration: 0.25, stagger: {{ each: 0.018, from: "random" }} }}, T.city + 0.15);
tl.to("#net line", {{ opacity: 0.55, duration: 0.3, stagger: 0.012 }}, T.city + 0.6);
tl.fromTo("#lbl", {{ opacity: 0 }}, E({{ opacity: 1, duration: 0.6 }}), T.city + 0.4);
tl.to("#sky", {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, T.light);
tl.to("#net", {{ opacity: 0.35, duration: 0.5 }}, T.light);
[["#w1", T.w1], ["#w2", T.w2], ["#w3", T.w3]].forEach(([s, t]) => tl.fromTo(s, {{ yPercent: 110 }}, E({{ yPercent: 0, duration: 0.5, ease: "power3.out" }}), t));
// logo sign-off (same build as the Mbote film)
const HIT = T.logo; tl.set("#E", {{ opacity: 1 }}, HIT);
const ARR0 = HIT + 0.45, dx = -0.496 * 1150, dy = 0.868 * 1150, ps = document.getElementById("ps"), aw = document.getElementById("aw"), o = {{ x: dx, y: dy }};
const put = () => {{ aw.style.transform = "translate(" + o.x + "px," + o.y + "px)"; ps.style.webkitMaskPosition = o.x + "px " + o.y + "px, 0px 0px"; }};
tl.fromTo("#ps", {{ scale: .8, opacity: 0, transformOrigin: "1040px 450px" }}, E({{ scale: 1, opacity: 1, duration: .5, ease: "expo.out" }}), HIT);
tl.set(o, {{ x: dx, y: dy, onUpdate: put }}, HIT); tl.set("#aw", {{ opacity: 0 }}, HIT); tl.set("#aw", {{ opacity: 1 }}, ARR0);
tl.fromTo(o, {{ x: dx, y: dy }}, E({{ x: 0, y: 0, duration: .85, ease: "back.out(1.35)", onUpdate: put }}), ARR0);
tl.to("#cv", {{ y: -90, duration: .6, ease: "power3.inOut" }}, ARR0 + .75);
tl.fromTo("#word", {{ opacity: 0, y: 40 }}, E({{ opacity: 1, y: 0, duration: .55, ease: "expo.out" }}), ARR0 + .9);
tl.fromTo("#tag2", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: .5, ease: "expo.out" }}), ARR0 + 1.1);
tl.fromTo("#url", {{ opacity: 0 }}, E({{ opacity: .9, duration: .5 }}), ARR0 + 1.3);
tl.fromTo("#stores", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: .5, ease: "expo.out" }}), ARR0 + 1.45);
tl.set({{}}, {{}}, T.end);
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
open(OUT, "w").write(html.replace(" ?", " ?"))
json.dump(T, open(OUT + ".cues.json", "w"))
print("ok", T["end"])
