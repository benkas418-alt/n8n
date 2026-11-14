# « Rejoins-nous » brand film (14 Nov): 5 s of Lubumbashi with music only, then the sister's voice:
# sellers (home, small stock, big shop) -> app; freelancers (graphiste, photographe, maquilleuse, couturier) -> app;
# buyers -> app; « Vendeurs, prestataires, acheteurs : rejoignez-nous » -> DRC map « fièrement congolaise » -> logo.
# Shot list and word times are in SHOTS / APPS below (seconds, voice placed by audio/rj/places.json).
# usage: build_rj.py out.html
import json, math, sys
OUT = sys.argv[1]; SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
MAP0, LOGO = 33.25, 36.9; END = LOGO + 4.8
# full-frame clips: (file, start, end, caption lines, caption time) ; caption "" = no text
SHOTS = [("ae_stadium", 0, 1.75, "", 0), ("s_train", 1.75, 3.4, "", 0), ("street_golden", 3.4, 5.0, "", 0),
         ("market", 5.0, 6.95, "", 0), ("stall", 6.95, 8.75, "", 0),
         ("phone", 8.75, 11.7, "Tout passe|par le téléphone.", 9.29),
         ("home", 11.7, 13.6, "À la maison ?", 12.3), ("jd_racks1", 13.6, 14.5, "Un petit stock ?", 13.66),
         ("s_mode1", 14.5, 15.6, "Une grande|boutique ?", 14.56),
         ("graph", 19.1, 20.8, "Graphiste", 19.6), ("photo", 20.8, 21.7, "Photographe", 20.85),
         ("makeup", 21.7, 22.6, "Maquilleuse", 21.77), ("couture", 22.6, 23.3, "Couturier", 22.63),
         ("pride", 29.4, MAP0, "", 0)]
# words that build up on screen over one or two shots: (id, lines with their times, start, end)
STACKS = [("w0", [("Vendre.", 6.70), ("Créer.", 7.20), ("Se débrouiller.", 7.80)], 6.6, 8.75),
          ("w1", [("Vendeurs.", 29.46), ("Prestataires.", 30.54), ("Acheteurs.", 31.54)], 29.4, MAP0)]
APPS = [("A", 15.6, 19.1, "VENDEURS", ["store_hd.png"], None, [("Publie tes articles", 15.66), ("Les clients viennent à toi", 17.44)]),
        ("B", 23.3, 26.4, "PRESTATAIRES", ["real_feed.png", "real_beauty.png"], 24.43, [("Montre tes travaux", 23.35), ("Postule aux offres", 24.43)]),
        ("C", 26.4, 29.4, "ACHETEURS", ["market2.png"], None, [("Ceux qui cherchent te trouvent", 27.31)])]
JOIN = 32.30
# DRC outline (Natural Earth 50 m), PitUp blue, pin on Lubumbashi
ring = json.load(open(f"{SP}/real/drc/drc.json"))[0]; k0 = math.cos(math.radians(4))
xs = [x * k0 for x, y in ring]; ys = [-y for x, y in ring]; sc = 760 / (max(xs) - min(xs))
ox, oy = 540 - (max(xs) + min(xs)) / 2 * sc, 1000 - (max(ys) + min(ys)) / 2 * sc
prj = lambda lon, lat: (lon * k0 * sc + ox, -lat * sc + oy)
dd = "M" + " L".join(f"{prj(x, y)[0]:.1f},{prj(x, y)[1]:.1f}" for x, y in ring) + "Z"
lx, ly = prj(27.4793, -11.6647)

vids = "".join(f'<video id="v{k}" class="clip full" src="assets/v/{n}.mp4" muted playsinline data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="{2 + k % 2}"></video>' for k, (n, a, b, c, ct) in enumerate(SHOTS))
caps = "".join(f'<div class="cap" id="t{k}"><i></i>' + "".join(f'<span class="ln"><span>{l}</span></span>' for l in c.split("|")) + '</div>' for k, (n, a, b, c, ct) in enumerate(SHOTS) if c)
stacks = "".join(f'<div class="stack" id="{sid}">' + "".join(f'<span class="ln"><span>{t}</span></span>' for t, _ in L) + '</div>' for sid, L, a, b in STACKS)
apps = ""
for key, a, b, label, scr, swap, steps in APPS:
    imgs = "".join(f'<img id="{key}i{k}" src="assets/scr/{s}" alt="" style="opacity:{1 if k == 0 else 0}">' for k, s in enumerate(scr))
    chips = "".join(f'<div class="chip" id="{key}s{k}"><em>{k + 1}</em><span>{t}</span></div>' for k, (t, _) in enumerate(steps))
    apps += f'<section class="app" id="{key}"><div class="lbl">{label}</div><div class="chips">{chips}</div><div class="stage"><div class="phone" id="{key}p"><i class="isl"></i><div class="scr">{imgs}</div></div></div></section>'

html = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;font-weight:500;src:url(assets/fonts/poppins-500.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:600;src:url(assets/fonts/poppins-600.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:700;src:url(assets/fonts/poppins-700.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:800;src:url(assets/fonts/poppins-800.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:P,sans-serif;color:#fff;background:#06101c}}
.full{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
#scrim{{position:absolute;left:0;right:0;bottom:0;height:1000px;background:linear-gradient(180deg,rgba(4,14,28,0),rgba(4,14,28,.82));z-index:2;opacity:0}}
.cap,.stack{{position:absolute;left:80px;right:80px;bottom:330px;z-index:3;font-weight:800;font-size:108px;letter-spacing:-4px;line-height:1.05;opacity:0}}
.cap i{{display:block;width:110px;height:12px;border-radius:6px;background:#1f88c9;margin-bottom:26px;transform-origin:0 50%}}
.stack{{font-size:100px;bottom:430px}}
.ln{{display:block;overflow:hidden;padding-bottom:10px}} .ln span{{display:inline-block;transform:translateY(115%)}}
#join{{position:absolute;left:80px;bottom:200px;z-index:3;padding:14px 34px;border-radius:16px;background:#1f88c9;font-weight:800;font-size:84px;letter-spacing:-3px;opacity:0}}
.app,#M,#E{{position:absolute;inset:0;z-index:4;opacity:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
.lbl{{position:absolute;left:80px;top:200px;font-weight:600;font-size:36px;letter-spacing:8px;color:#d9eefb}}
.chips{{position:absolute;left:80px;top:290px;right:60px;display:flex;flex-direction:column;gap:22px}}
.chip{{display:flex;align-items:center;gap:24px;width:fit-content;padding:16px 36px 16px 16px;border-radius:60px;background:#fff;color:#0d2a40;font-weight:700;font-size:46px;letter-spacing:-1px;box-shadow:0 18px 40px rgba(4,30,60,.3);opacity:0}}
.chip em{{flex:0 0 72px;height:72px;border-radius:50%;background:#1f88c9;color:#fff;font-style:normal;font-size:36px;display:flex;align-items:center;justify-content:center}}
.stage{{position:absolute;inset:0;perspective:2200px}}
.phone{{position:absolute;left:299px;top:730px;width:482px;height:1040px;border-radius:74px;padding:15px;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,2px 1.2px 0 #3c3f45,4px 2.4px 0 #26282d,6px 3.6px 0 #1c1d21,8px 4.8px 0 #151619,10px 6px 0 #111215,40px 70px 90px rgba(4,30,60,.5)}}
.phone .scr{{position:absolute;inset:15px;border-radius:64px;overflow:hidden;background:#fff}}
.phone .scr img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top}}
.phone .isl{{position:absolute;left:50%;top:34px;width:136px;height:38px;margin-left:-68px;border-radius:18px;background:#050506;z-index:3}}
#M{{background:radial-gradient(90% 60% at 50% 50%,#2b9ae0 0%,#1672ab 60%,#0f5688 100%)}}
#M h2{{position:absolute;left:80px;right:80px;top:200px;font-weight:800;font-size:104px;letter-spacing:-4px;line-height:1.04}}
#M .sub{{position:absolute;left:80px;right:80px;top:1640px;font-weight:700;font-size:64px;letter-spacing:-2px;opacity:0}}
#E{{z-index:5}}
#cv{{position:absolute;left:124px;top:640px;width:1500px;height:1900px;transform-origin:0 0;transform:scale(0.4)}}
#cv img,#cv .m{{position:absolute;left:0;top:0;width:1500px;height:1900px}}
#mo{{-webkit-mask-image:url(assets/mask_out.png);mask-image:url(assets/mask_out.png);-webkit-mask-size:100% 100%;mask-size:100% 100%}}
#ps{{-webkit-mask-image:url(assets/arrow_white.png),linear-gradient(#000,#000);-webkit-mask-size:1500px 1900px,100% 100%;-webkit-mask-repeat:no-repeat;-webkit-mask-position:0px 0px,0 0;-webkit-mask-composite:xor;mask-composite:exclude}}
#word{{position:absolute;left:50%;top:1010px;width:470px;margin-left:-235px;opacity:0}}
#tag2{{position:absolute;left:50%;top:1210px;width:520px;margin-left:-260px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1330px;text-align:center;font-weight:600;font-size:40px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1440px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END:.2f}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{END:.2f}" data-track-index="11"></audio>
{vids}
<div id="scrim"></div>
{caps}{stacks}<div id="join">Rejoignez-nous.</div>
{apps}
<section id="M"><h2><span class="ln"><span>Fièrement</span></span><span class="ln"><span>congolaise.</span></span></h2>
 <svg viewBox="0 0 1080 1920" width="1080" height="1920" style="position:absolute;left:0;top:0">
  <path class="dfill" d="{dd}" fill="#ffffff" fill-opacity="0.16"/>
  <path class="dline" d="{dd}" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" stroke-dasharray="6000" stroke-dashoffset="6000"/>
  <circle class="dring" cx="{lx:.0f}" cy="{ly:.0f}" r="20" fill="none" stroke="#fff" stroke-width="5"/><circle class="dpin" cx="{lx:.0f}" cy="{ly:.0f}" r="15" fill="#fff"/></svg>
 <div class="dlab" style="position:absolute;left:{lx - 110:.0f}px;top:{ly + 36:.0f}px;font-weight:700;font-size:40px;opacity:0">Lubumbashi</div>
 <div class="sub">Pour les Congolais.</div></section>
<div id="E">
 <div id="cv"><img id="ps" src="assets/p_solid.png" alt=""><div class="m" id="mo"><img id="aw" src="assets/arrow_white.png" alt=""></div></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag2" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); const E = (o) => Object.assign({{ immediateRender: false }}, o);
const SH = {json.dumps([[a, b, bool(c), ct] for n, a, b, c, ct in SHOTS])};
let ci = 0;
SH.forEach(([a, b, cap, ct], k) => {{
  tl.fromTo("#v" + k, {{ scale: 1.0 }}, E({{ scale: 1.06, duration: b - a, ease: "none" }}), a);
  if (!cap) return;
  const id = "#t" + k;
  tl.set("#scrim", {{ opacity: 1 }}, a); tl.set("#scrim", {{ opacity: 0 }}, b);
  tl.set(id, {{ opacity: 1 }}, ct - 0.05);
  tl.fromTo(id + " i", {{ scaleX: 0 }}, E({{ scaleX: 1, duration: 0.35, ease: "power3.out" }}), ct - 0.05);
  tl.fromTo(id + " .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.45, ease: "power3.out", stagger: 0.08 }}), ct);
  tl.set(id, {{ opacity: 0 }}, b);
}});
const ST = {json.dumps([[sid, [t for _, t in L], a, b] for sid, L, a, b in STACKS])};
ST.forEach(([sid, ts, a, b]) => {{
  tl.set("#scrim", {{ opacity: 1 }}, a); tl.set("#scrim", {{ opacity: 0 }}, b);
  tl.set("#" + sid, {{ opacity: 1 }}, a); tl.set("#" + sid, {{ opacity: 0 }}, b);
  ts.forEach((t, k) => tl.fromTo(`#${{sid}} .ln:nth-child(${{k + 1}}) span`, {{ y: "115%" }}, E({{ y: "0%", duration: 0.45, ease: "power3.out" }}), t - 0.05));
}});
tl.fromTo("#join", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}), {JOIN});
tl.set("#join", {{ opacity: 0 }}, {MAP0});
const APPS = {json.dumps([[k, a, b, sw, [t for _, t in st]] for k, a, b, lb, sc, sw, st in APPS])};
APPS.forEach(([key, a, b, sw, steps]) => {{
  tl.set("#" + key, {{ opacity: 1 }}, a); tl.set("#" + key, {{ opacity: 0 }}, b);
  tl.fromTo("#" + key + "p", {{ y: 420, rotationY: -20, rotationX: 8 }}, E({{ y: 0, rotationY: -8, rotationX: 3, duration: 0.8, ease: "power3.out" }}), a);
  tl.to("#" + key + "p", {{ rotationY: 0, rotationX: 0, duration: Math.max(0.6, b - a - 0.9), ease: "sine.inOut" }}, a + 0.8);
  steps.forEach((t, k) => tl.fromTo("#" + key + "s" + k, {{ opacity: 0, x: -50 }}, E({{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}), Math.max(a + 0.1, t - 0.05)));
  if (sw) tl.to("#" + key + "i1", {{ opacity: 1, duration: 0.3 }}, sw);
}});
// map: fièrement congolaise
const M0 = {MAP0};
tl.set("#M", {{ opacity: 1 }}, M0); tl.set("#M", {{ opacity: 0 }}, {LOGO});
tl.fromTo("#M .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.5, ease: "power3.out", stagger: 0.1 }}), 34.35);
tl.fromTo("#M .dline", {{ strokeDashoffset: 6000 }}, E({{ strokeDashoffset: 0, duration: 1.2, ease: "power2.inOut" }}), M0 + 0.05);
tl.fromTo("#M .dfill", {{ opacity: 0 }}, E({{ opacity: 1, duration: 0.5 }}), M0 + 0.9);
tl.fromTo("#M .dpin", {{ opacity: 0, scale: 0, transformOrigin: "50% 50%" }}, E({{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}), M0 + 1.0);
tl.fromTo("#M .dring", {{ opacity: 1, scale: 1, transformOrigin: "50% 50%" }}, E({{ opacity: 0, scale: 3, duration: 1.0, ease: "power2.out" }}), M0 + 1.15);
tl.fromTo("#M .dlab", {{ opacity: 0, x: 20 }}, E({{ opacity: 1, x: 0, duration: 0.35 }}), M0 + 1.15);
tl.fromTo("#M .sub", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}), 35.75);
tl.to("#M svg, #M .dlab", {{ scale: 1.04, transformOrigin: "50% 52%", duration: {LOGO} - M0, ease: "none" }}, M0);
// logo sign-off
const HIT = {LOGO}; tl.set("#E", {{ opacity: 1 }}, HIT);
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
tl.set({{}}, {{}}, {END:.2f});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
open(OUT, "w").write(html.replace(" ?", " ?"))
json.dump({"end": END, "logo": LOGO, "map": MAP0, "apps": [[a, b] for k, a, b, *_ in APPS], "steps": [t for *_, st in APPS for _, t in st]}, open(OUT + ".t.json", "w"))
print("ok END", round(END, 2))
