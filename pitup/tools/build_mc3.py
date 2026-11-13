# Motion v2 « Lushi, ça bouge » — no voice-over: situations from Lubumbashi, few words, music + real SFX.
# Power cut -> stock asleep under the bed -> braider's talent -> wedding without a photographer -> the city lights up.
# usage: build_mc3.py out.html   (writes out.html.cues.json for the sound mix)
import json, random, sys
OUT = sys.argv[1]
T = {"cut": 0.8, "glow": 2.4, "stock": 5.0, "lift": 6.8, "order": 8.9, "talent": 10.6, "flash": 12.3, "fans": 13.6,
     "pro": 16.2, "type": 17.0, "drop": 18.6, "pick": 20.4, "city": 22.0, "light": 23.6, "w1": 23.9, "w2": 24.4, "w3": 24.9,
     "logo": 27.4, "end": 32.2}
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
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:P,sans-serif;color:#fff;background:#050a14}}
.bl{{color:#4fb0ec}}
#s1,#s3{{background:radial-gradient(90% 60% at 50% 30%,#12304c 0%,#0a1626 65%,#050a14 100%)}}
.vid{{position:absolute;left:0;width:1080px;object-fit:cover}}
.pc{{position:absolute;width:260px;height:300px;border-radius:26px;background:#fff center/cover;box-shadow:0 24px 50px rgba(0,0,0,.5);filter:brightness(.45) saturate(.6)}}
#vf{{position:absolute;left:170px;top:560px;width:740px;height:740px;opacity:0}} #vf i{{position:absolute;width:90px;height:90px;border:8px solid #fff}}
#vf i:nth-child(1){{left:0;top:0;border-right:0;border-bottom:0}}#vf i:nth-child(2){{right:0;top:0;border-left:0;border-bottom:0}}#vf i:nth-child(3){{left:0;bottom:0;border-right:0;border-top:0}}#vf i:nth-child(4){{right:0;bottom:0;border-left:0;border-top:0}}
#vf b{{position:absolute;left:50%;top:50%;width:60px;height:60px;margin:-30px;border:4px solid #4fb0ec;border-radius:50%}}
#sb{{position:absolute;left:110px;right:110px;top:840px;height:120px;border-radius:60px;background:#fff;color:#101418;display:flex;align-items:center;gap:22px;padding:0 40px;font-weight:600;font-size:44px;opacity:0;box-shadow:0 24px 50px rgba(0,0,0,.45)}}
#sb svg{{width:50px;height:50px;stroke:#1f88c9;stroke-width:2.6;fill:none;stroke-linecap:round}} #sb u{{text-decoration:none;display:inline-block;width:4px;height:52px;background:#1f88c9;margin-left:4px}}
.avp{{flex:0 0 96px;height:96px;border-radius:50%;background-size:cover;background-position:center 20%}}
#night{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,22,48,.9),rgba(4,12,30,.94))}}
#tint{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(31,136,201,.55) 0%,rgba(31,136,201,.12) 40%,rgba(13,90,143,.35) 100%);opacity:0}}
#w1,#w2,#w3{{transform:translateY(115%)}}
#scrim{{position:absolute;left:0;right:0;top:420px;height:900px;background:linear-gradient(180deg,rgba(8,40,80,0) 0%,rgba(8,40,80,.62) 22%,rgba(8,40,80,.62) 78%,rgba(8,40,80,0) 100%);opacity:0}}
.sep{{position:absolute;left:0;width:1080px;height:6px;background:#050a14}}
.sc{{position:absolute;inset:0;opacity:0;overflow:hidden;z-index:2}} #E{{z-index:3}}
.big{{position:absolute;left:80px;right:80px;font-weight:800;letter-spacing:-3px;line-height:1.02}}
.big .ln{{display:block;overflow:hidden;padding-bottom:6px}} .big .ln span{{display:inline-block}}
/* 0 power cut */
#room{{position:absolute;inset:-40px;background:url(assets/ph/bulb.jpg) 50% 30%/cover}}
#glowp{{position:absolute;inset:-40px;background:url(assets/ph/glow.jpg) 42% center/cover;opacity:0}}
#glowt{{position:absolute;left:80px;right:80px;top:1330px;font-weight:700;font-size:76px;line-height:1.08;letter-spacing:-2px}}
#glowt .ln{{display:block;overflow:hidden;padding-bottom:6px}} #glowt .ln span{{display:inline-block;transform:translateY(115%)}}
.vg{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,10,20,.55) 0%,rgba(5,10,20,0) 30%,rgba(5,10,20,0) 55%,rgba(5,10,20,.9) 100%)}}
#bulb{{position:absolute;left:50%;top:330px;width:150px;margin-left:-75px;transform-origin:50% -300px}}
#bulb .cord{{position:absolute;left:73px;top:-330px;width:4px;height:330px;background:#1c1408}}
#bulb .glass{{width:150px;height:190px;border-radius:50% 50% 45% 45%;background:radial-gradient(circle at 50% 40%,#fff 0%,#ffe9a8 45%,#f6c75b 100%);box-shadow:0 0 120px 60px rgba(255,214,120,.65)}}
#bulb .cap{{width:70px;height:46px;margin:-6px auto 0;background:linear-gradient(90deg,#6b6b6b,#c9c9c9,#6b6b6b);border-radius:6px}}
#dark{{position:absolute;inset:0;background:#050a14;opacity:0}}
#cutw{{position:absolute;left:0;right:0;top:880px;text-align:center;font-weight:700;font-size:96px;letter-spacing:-2px;opacity:0}}
/* 1 stock */
#glow{{position:absolute;left:560px;top:700px;width:700px;height:900px;border-radius:50%;background:radial-gradient(closest-side,rgba(80,170,240,.55),rgba(80,170,240,0));opacity:0}}
.bx{{position:absolute;width:250px;height:170px;background:linear-gradient(160deg,#c89a5c,#9c6f37);border-radius:8px;box-shadow:inset 0 -14px 0 rgba(0,0,0,.18),0 18px 30px rgba(0,0,0,.45)}}
.bx i{{position:absolute;left:105px;top:0;width:40px;height:100%;background:rgba(240,225,190,.55)}}
#zz{{position:absolute;left:440px;top:1010px;font-weight:700;font-size:70px;color:#9fc8ea}}
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
#salon{{position:absolute;inset:0;background:url(assets/ph/salon.jpg) 64% center/cover;filter:brightness(.5) saturate(.85)}}
#salont{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,26,48,.85) 0%,rgba(8,26,48,.25) 35%,rgba(8,26,48,.55) 100%)}}
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
#cal .h{{height:110px;background:#1f88c9;color:#fff;font-weight:700;font-size:48px;display:flex;align-items:center;justify-content:center;letter-spacing:4px}}
#cal .d{{font-weight:800;font-size:200px;text-align:center;line-height:1.1;letter-spacing:-8px}} #cal .t{{text-align:center;font-weight:600;font-size:40px;padding-bottom:30px}}
.cand{{position:absolute;left:110px;right:110px;height:150px;border-radius:32px;background:#fff;color:#101418;display:flex;align-items:center;gap:26px;padding:0 30px;opacity:0;box-shadow:0 24px 50px rgba(0,0,0,.45)}}
.cand b{{font-weight:700;font-size:38px}} .cand span{{display:block;font-size:28px;color:#5b6570}}
.cand .ok{{margin-left:auto;width:84px;height:84px;border-radius:50%;background:#1fae5b;display:flex;align-items:center;justify-content:center;opacity:0}}
.cand .ok svg{{width:50px;height:50px;stroke:#fff;stroke-width:3;fill:none;stroke-linecap:round;stroke-linejoin:round}}
/* 4 city */
#sky{{position:absolute;inset:0;background:radial-gradient(120% 90% at 30% 20%,#2a9be0 0%,#1f88c9 40%,#0d5a8f 100%);opacity:0}}
#net{{position:absolute;inset:0}} #net circle{{fill:#ffe9a8}}
#lbl{{position:absolute;left:0;right:0;top:250px;text-align:center;font-weight:600;font-size:34px;letter-spacing:10px;color:#9fc8ea;opacity:0}}
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
{"".join(f'<video id="cv{k}" class="clip vid" src="assets/v/{c}.mp4" muted playsinline data-start="{T["city"]:.2f}" data-duration="{T["logo"] + 0.4 - T["city"]:.2f}" data-track-index="{2 + k}" style="top:{k * 640}px;height:640px"></video>' for k, c in enumerate(["c_alilac", "c_traffic", "c_park"]))}
<audio id="bgm" src="assets/mix3.wav" data-start="0" data-duration="{T['end']:.2f}" data-track-index="11"></audio>

<section class="sc" id="s0" style="opacity:1">
 <div id="room"></div>
 <div id="dark"></div>
 <div id="glowp"></div><div class="vg" id="glowv" style="opacity:0"></div>
 <div id="cutw">Coupure.</div>
 <div id="glowt"><span class="ln"><span>Ton téléphone, lui,</span></span><span class="ln"><span class="bl">reste allumé.</span></span></div>
</section>

<section class="sc" id="s1">
 <div id="glow"></div>
 <div class="pc" id="x0" style="left:90px;top:1330px;background-image:url(assets/ph/c_d_am95.jpg);transform:rotate(-6deg)"></div>
 <div class="pc" id="x1" style="left:250px;top:1190px;background-image:url(assets/ph/c_d_crocs.jpg);transform:rotate(5deg)"></div>
 <div class="pc" id="x2" style="left:140px;top:1040px;background-image:url(assets/ph/c_d_yara.jpg);transform:rotate(-3deg)"></div>
 <div id="zz"><span style="left:0;top:0">z</span><span style="left:50px;top:-70px;font-size:90px">z</span><span style="left:110px;top:-160px;font-size:110px">z</span></div>
 <h1 class="big" id="h1" style="top:300px;font-size:120px"><span class="ln"><span>Ton stock</span></span><span class="ln"><span class="bl">dort ?</span></span></h1>
 <div class="stage"><div class="phone" id="ph1" style="left:560px;top:760px"><i class="isl"></i><div class="scr"><img id="shop" src="assets/scr/store_hd.png" alt="" style="opacity:0"></div></div></div>
 <div class="toast" id="o1" style="top:640px"><div class="ic"><img src="assets/icon_white.png" alt=""></div><div><b>Nouvelle commande</b><span>Un client veut tes baskets.</span></div></div>
</section>

<section class="sc" id="s2">
 <div id="salon"></div><div id="salont"></div>
 <div id="vf"><i></i><i></i><i></i><i></i><b></b></div>
 <h1 class="big" id="h2" style="top:300px;font-size:120px"><span class="ln"><span>Ton talent</span></span><span class="ln"><span class="bl">attend ?</span></span></h1>
 <div id="prof"><div class="pic"></div><b>Coiffeuse</b><span>Tresses · Lubumbashi</span><div class="btn">Contacter</div></div>
 <div class="bub" id="f0" style="top:1180px"><div class="av" style="background:#1f88c9">G</div><div><b>Nouvelle cliente</b><span>Pour des tresses samedi</span></div></div>
 <div class="bub" id="f1" style="top:1320px"><div class="av" style="background:#e07a3c">E</div><div><b>Nouvelle cliente</b><span>Disponible demain ?</span></div></div>
 <div class="bub" id="f2" style="top:1460px"><div class="av" style="background:#7a5bd6">M</div><div><b>Nouvelle cliente</b><span>Pour une cérémonie</span></div></div>
 <div id="flash"></div>
</section>

<section class="sc" id="s3">
 <h1 class="big" id="h3" style="top:250px;font-size:110px"><span class="ln"><span>Il te manque</span></span><span class="ln"><span class="bl">un pro ?</span></span></h1>
 <div id="sb"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/></svg><span id="sbt"></span><u id="cur"></u></div>
 <div id="cal"><div class="h">SAMEDI</div><div class="d">14</div><div class="t">Mariage</div></div>
 {''.join(f'<div class="cand" id="c{k}" style="top:{1020 + k*185}px">{av}<div><b>{n}</b><span>Photographe · Lubumbashi</span></div><div class="ok"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div></div>' for k, (n, av) in enumerate([("Patrick K.", '<div class="avp" style="background-image:url(assets/ph/8995315.jpg)"></div>'), ("Aline T.", '<div class="avp" style="background-image:url(assets/ph/12446331.jpg)"></div>'), ("Joël M.", '<div class="av" style="background:#1f88c9;flex:0 0 96px;height:96px">J</div>')]))}
</section>

<section class="sc" id="s4">
 <div class="sep" style="top:637px"></div><div class="sep" style="top:1277px"></div>
 <div id="tint"></div><div id="scrim"></div><div id="night"></div>
 <svg id="net" viewBox="0 0 1080 1920"><g id="dots">{svg_dots}</g></svg>
 <div id="lbl">LUBUMBASHI</div>
 <h1 class="big" id="h4" style="top:560px;font-size:170px;text-shadow:0 8px 40px rgba(0,0,0,.55)"><span class="ln"><span id="w1">Vends.</span></span><span class="ln"><span id="w2">Propose.</span></span><span class="ln"><span id="w3">Trouve.</span></span></h1>
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
tl.fromTo("#room", {{ scale: 1.06 }}, {{ scale: 1, duration: 0.8, ease: "none" }}, 0);
[[0.42, .35], [0.47, 1], [0.6, .2], [0.66, 1]].forEach(([t, o]) => tl.set("#room", {{ opacity: o }}, t));     // real flicker
tl.set("#dark", {{ opacity: 1 }}, T.cut);
tl.fromTo("#cutw", {{ opacity: 0, letterSpacing: "14px", filter: "blur(10px)" }}, E({{ opacity: 1, letterSpacing: "-2px", filter: "blur(0px)", duration: 0.6, ease: "power3.out" }}), T.cut + 0.4);
tl.to("#cutw", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, T.glow - 0.3);
tl.fromTo("#glowp", {{ opacity: 0, scale: 1.12 }}, E({{ opacity: 1, scale: 1, duration: 2.4, ease: "power2.out" }}), T.glow);
tl.to("#glowv", {{ opacity: 1, duration: 0.6 }}, T.glow);
tl.fromTo("#glowt .ln > span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.6, ease: "power3.out", stagger: 0.03 }}), T.glow + 0.7);
scene("#s0", 0, T.stock);
// 1 — stock asleep: the phone screen lights the room, boxes fly into the app, an order arrives
scene("#s1", T.stock, T.talent);
tl.fromTo("#glow", {{ opacity: 0 }}, E({{ opacity: 1, duration: 0.8 }}), T.stock + 0.2);
tl.fromTo("#ph1", {{ x: 300, rotationY: -40, opacity: 0 }}, E({{ x: 0, rotationY: -12, opacity: 1, duration: 0.8, ease: "power3.out" }}), T.stock + 0.1);
lines("#h1", T.stock + 0.35);
tl.fromTo(".pc", {{ opacity: 0, y: 40 }}, E({{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.06 }}), T.stock + 0.2);
["#zz span:nth-child(1)", "#zz span:nth-child(2)", "#zz span:nth-child(3)"].forEach((sel, k) => {{
  tl.fromTo(sel, {{ opacity: 0, y: 20 }}, E({{ opacity: 1, y: -10, duration: 0.5, ease: "power2.out" }}), T.stock + 0.6 + k * 0.3);
  tl.to(sel, {{ opacity: 0, duration: 0.3 }}, T.lift - 0.25);
}});
[2, 1, 0].forEach((k, n) => {{
  const t = T.lift + n * 0.4;
  tl.to("#x" + k, {{ filter: "brightness(1) saturate(1)", scale: 1.06, rotation: 0, duration: 0.25, ease: "power2.out" }}, t - 0.25);   // wakes up
  tl.to("#x" + k, {{ x: 560 - k * 60, duration: 0.6, ease: "power2.in" }}, t);
  tl.to("#x" + k, {{ y: -260 - k * 30, scale: 0.3, rotation: 14, duration: 0.6, ease: "power3.out" }}, t);
  tl.to("#x" + k, {{ opacity: 0, duration: 0.12 }}, t + 0.5);
}});
tl.to("#shop", {{ opacity: 1, duration: 0.4 }}, T.lift + 0.5);
tl.to("#ph1", {{ rotationY: -4, duration: 1.5, ease: "sine.inOut" }}, T.lift + 0.6);
tl.fromTo("#o1", {{ opacity: 0, y: -60, scale: 0.95 }}, E({{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}), T.order);
tl.to("#o1", {{ scale: 0.97, duration: 0.09, yoyo: true, repeat: 1 }}, T.order + 0.7);
// 2 — talent: dark salon, flash, the photo becomes a profile, clients arrive
scene("#s2", T.talent, T.pro);
lines("#h2", T.talent + 0.2);
tl.fromTo("#salon", {{ scale: 1.1 }}, E({{ scale: 1, duration: 1.7, ease: "power1.out" }}), T.talent);
tl.fromTo("#vf", {{ opacity: 0, scale: 1.25 }}, E({{ opacity: 1, scale: 1, duration: 0.5, ease: "power3.out" }}), T.flash - 0.9);
tl.to("#vf b", {{ scale: 0.6, duration: 0.25, yoyo: true, repeat: 1, ease: "sine.inOut" }}, T.flash - 0.5);
tl.set("#vf", {{ opacity: 0 }}, T.flash);
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
tl.to("#cal", {{ y: -130, scale: 0.62, duration: 0.5, ease: "power2.inOut" }}, T.type - 0.4);
tl.fromTo("#sb", {{ opacity: 0, y: 30, scale: 0.95 }}, E({{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" }}), T.type - 0.3);
"photographe".split("").forEach((c, k) => tl.set("#sbt", {{ textContent: "photographe".slice(0, k + 1) }}, T.type + k * 0.1));
for (let k = 0; k < 10; k++) tl.set("#cur", {{ opacity: k % 2 }}, T.type + 1.2 + k * 0.3);
[0, 1, 2].forEach(k => tl.fromTo("#c" + k, {{ opacity: 0, y: -140 }}, E({{ opacity: 1, y: 0, duration: 0.42, ease: "power2.in" }}), T.drop + k * 0.35));
tl.to("#c0, #c2", {{ opacity: 0.3, scale: 0.97, duration: 0.3, ease: "power2.out" }}, T.pick);
tl.to("#c1", {{ scale: 1.04, duration: 0.25, ease: "power2.out" }}, T.pick);
tl.fromTo("#c1 .ok", {{ opacity: 0, scale: 0.6, filter: "blur(6px)" }}, E({{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }}), T.pick + 0.1);
tl.to("#c1 .ok", {{ scale: 1.15, duration: 0.12, yoyo: true, repeat: 1 }}, T.pick + 0.5);
// 4 — the city lights up, the power comes back, three verbs
scene("#s4", T.city, T.logo + 0.4);
tl.set("#net circle", {{ opacity: 0 }}, T.city);
tl.to("#net circle", {{ opacity: 1, duration: 0.2, stagger: {{ each: 0.02, from: "random" }} }}, T.city + 0.15);   // windows light up
tl.fromTo("#lbl", {{ opacity: 0 }}, E({{ opacity: 1, duration: 0.6 }}), T.city + 0.3);
tl.to("#night", {{ opacity: 0, duration: 0.7, ease: "power2.out" }}, T.light);        // the power is back: night lifts
tl.to("#tint", {{ opacity: 1, duration: 0.7 }}, T.light);
tl.to("#net", {{ opacity: 0, duration: 0.5 }}, T.light);
[["#w1", T.w1], ["#w2", T.w2], ["#w3", T.w3]].forEach(([s, t]) => tl.fromTo(s, {{ y: "115%" }}, E({{ y: "0%", duration: 0.5, ease: "power3.out" }}), t));
tl.to("#scrim", {{ opacity: 1, duration: 0.5 }}, T.light + 0.1);
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
