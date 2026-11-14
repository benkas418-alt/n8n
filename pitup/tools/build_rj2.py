# « Rejoignez-nous » v2 (14 Nov). Same voice and text as v1. Changes asked by the founder:
#  - no Lubumbashi archive shots (soft): only sharp free footage;
#  - app scenes: real screen RECORDINGS and other real captures on the 3D phone, and NO numbered list:
#    the words themselves are animated (word by word, blur to sharp, key words highlighted), one phrase replaces the other;
#  - « fièrement congolaise »: people in full frame (telecom-ad codes: faces, pagne, flag colours as an accent), no map.
# Motion rules (founder's sheet): ease-out entrances, no spring, exits ~20 % shorter, phone enters on a curve.
# usage: build_rj2.py out.html
import json, sys
OUT = sys.argv[1]
PRIDE0, LOGO = 33.25, 36.9; END = LOGO + 4.8
SHOTS = [("cityA", 0, 1.75, "", 0), ("cityB", 1.75, 3.4, "", 0), ("cityC", 3.4, 5.0, "", 0),
         ("market", 5.0, 6.95, "", 0), ("stall", 6.95, 8.75, "", 0),
         ("phone", 8.75, 11.7, "Tout passe|par le téléphone.", 9.29),
         ("home", 11.7, 13.6, "À la maison ?", 12.3), ("stock", 13.6, 14.5, "Un petit stock ?", 13.66),
         ("shop", 14.5, 15.6, "Une grande|boutique ?", 14.56),
         ("graph", 19.1, 20.8, "Graphiste", 19.6), ("photo", 20.8, 21.7, "Photographe", 20.85),
         ("makeup", 21.7, 22.6, "Maquilleuse", 21.77), ("couture", 22.6, 23.3, "Couturier", 22.63),
         ("p_vend", 29.4, 30.5, "Vendeurs.", 29.46), ("p_prest", 30.5, 31.5, "Prestataires.", 30.54), ("p_ach", 31.5, PRIDE0, "Acheteurs.", 31.54),
         ("pride", PRIDE0, LOGO, "", 0)]
STACKS = [("w0", [("Vendre.", 6.70), ("Créer.", 7.20), ("Se débrouiller.", 7.80)], 6.6, 8.75)]
# app scenes: (id, start, end, label, [(screen file, from time)], [(phrase with [key words], time)])
APPS = [("A", 15.6, 19.1, "VENDEURS", [("phapp.mp4", 15.6), ("ph_vb.mp4", 17.35)], [("Publie|[tes articles.]", 15.66), ("Les clients|[viennent à toi.]", 17.44)]),
        ("B", 23.3, 26.4, "PRESTATAIRES", [("works.png", 23.3), ("offers.png", 24.4)], [("Montre|[tes travaux.]", 23.35), ("Postule|[aux offres.]", 24.43)]),
        ("C", 26.4, 29.4, "ACHETEURS", [("phs_full.mp4", 26.4)], [("Ceux qui|cherchent|[te trouvent.]", 27.0)])]
JOIN = 32.30
PX, PY, PW, PH = 299, 770, 482, 1040   # phone frame

def phrase(txt):
    out = ""
    for line in txt.split("|"):
        key = line.startswith("["); line = line.strip("[]")
        ws = "".join(f'<span class="w"><span>{w}</span></span>' for w in line.split(" "))
        out += f'<span class="l{" k" if key else ""}">' + ('<i class="hl"></i>' if key else "") + ws + '</span>'
    return out

vids = "".join(f'<video id="v{k}" class="clip full" src="assets/v/{n}.mp4" muted playsinline data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="{2 + k % 2}"></video>' for k, (n, a, b, c, ct) in enumerate(SHOTS))
caps = "".join(f'<div class="cap" id="t{k}"><i></i>' + "".join(f'<span class="ln"><span>{l}</span></span>' for l in c.split("|")) + '</div>' for k, (n, a, b, c, ct) in enumerate(SHOTS) if c)
stacks = "".join(f'<div class="stack" id="{sid}">' + "".join(f'<span class="ln"><span>{t}</span></span>' for t, _ in L) + '</div>' for sid, L, a, b in STACKS)
apps = ""; scr = ""; ti = 6
for key, a, b, label, screens, phrases in APPS:
    apps += f'<section class="app" id="{key}"><div class="lbl">{label}</div>' + "".join(f'<div class="kh" id="{key}h{k}">{phrase(t)}</div>' for k, (t, _) in enumerate(phrases)) + '</section>'
    apps += f'<div class="ph" id="{key}p"></div>'
    for k, (f, t0) in enumerate(screens):
        t1 = screens[k + 1][1] if k + 1 < len(screens) else b
        if f.endswith(".mp4"):
            scr += f'<video id="{key}c{k}" class="clip sc" src="assets/scr/{f}" muted playsinline data-start="{t0:.2f}" data-duration="{t1 - t0:.2f}" data-track-index="{ti}"></video>'; ti += 1
        else:
            scr += f'<img id="{key}c{k}" class="sc" src="assets/scr/{f}" alt="">'
    apps += f'<div class="isl" id="{key}n"></div>'

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
#join{{position:absolute;left:80px;bottom:150px;z-index:3;padding:14px 34px;border-radius:16px;background:#1f88c9;font-weight:800;font-size:84px;letter-spacing:-3px;opacity:0}}
.app,#E{{position:absolute;inset:0;z-index:4;opacity:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
.lbl{{position:absolute;left:84px;top:210px;font-weight:600;font-size:34px;letter-spacing:9px;color:#d9eefb}}
.kh{{position:absolute;left:80px;right:60px;top:280px;font-weight:800;font-size:112px;letter-spacing:-4.5px;line-height:1.16;opacity:0}}
.kh .l{{display:block;position:relative;width:fit-content;white-space:nowrap}}
.kh .w{{display:inline-block;overflow:hidden;padding:0 0 14px;margin-right:.24em;vertical-align:top}} .kh .w:last-child{{margin-right:0}}
.kh .w span{{display:inline-block;transform:translateY(110%)}}
.kh .k{{padding:0 26px 0 22px;margin-left:-22px;color:#1672ab}}
.kh .hl{{position:absolute;left:0;right:0;top:6px;bottom:18px;border-radius:22px;background:#fff;transform-origin:0 50%;transform:scaleX(0);z-index:-1;box-shadow:0 18px 40px rgba(4,30,60,.25)}}
.ph{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PH}px;border-radius:74px;z-index:6;opacity:0;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,2px 1.2px 0 #3c3f45,4px 2.4px 0 #26282d,6px 3.6px 0 #1c1d21,8px 4.8px 0 #151619,10px 6px 0 #111215,40px 70px 90px rgba(4,30,60,.5)}}
.sc{{position:absolute;left:{PX + 15}px;top:{PY + 15}px;width:{PW - 30}px;height:{PH - 30}px;border-radius:62px;object-fit:cover;object-position:top;background:#fff;z-index:7;opacity:0}}
.isl{{position:absolute;left:{PX + PW // 2 - 68}px;top:{PY + 34}px;width:136px;height:38px;border-radius:19px;background:#050506;z-index:8;opacity:0}}
#pt{{position:absolute;left:80px;right:60px;bottom:420px;z-index:3;font-weight:800;font-size:128px;letter-spacing:-5px;line-height:1.04;opacity:0;text-shadow:0 8px 40px rgba(0,0,0,.45)}}
#pbar{{position:absolute;left:84px;bottom:372px;z-index:3;display:flex;gap:10px}} #pbar b{{display:block;width:96px;height:14px;border-radius:7px;transform-origin:0 50%;transform:scaleX(0)}}
#psub{{position:absolute;left:84px;bottom:270px;z-index:3;font-weight:700;font-size:60px;letter-spacing:-2px;opacity:0;text-shadow:0 6px 30px rgba(0,0,0,.5)}}
.band{{position:absolute;top:-200px;left:-700px;width:560px;height:2400px;z-index:9;transform:translateX(-900px) skewX(-18deg)}}
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
{vids}{scr}
<div id="scrim"></div>
{caps}{stacks}<div id="join">Rejoignez-nous.</div>
<div id="pt"><span class="ln"><span>Fièrement</span></span><span class="ln"><span>congolaise.</span></span></div>
<div id="pbar"><b style="background:#0a84ff"></b><b style="background:#f7d618"></b><b style="background:#ce1021"></b></div>
<div id="psub">Pour les Congolais.</div>
{apps}
<div class="band" id="bd0" style="background:#0a84ff"></div><div class="band" id="bd1" style="background:#f7d618"></div><div class="band" id="bd2" style="background:#ce1021"></div>
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
tl.set("#join", {{ opacity: 0 }}, {PRIDE0});
// app scenes: phone on a curve, words animated
const APPS = {json.dumps([[k, a, b, [t for _, t in sc], [t for _, t in ph]] for k, a, b, lb, sc, ph in APPS])};
const ORG = ["{PW // 2}px {PH // 2}px", "{PW // 2 - 15}px {PH // 2 - 15}px", "68px {PH // 2 - 34}px"];
APPS.forEach(([key, a, b, st, pt]) => {{
  tl.set("#" + key, {{ opacity: 1 }}, a); tl.set("#" + key, {{ opacity: 0 }}, b);
  const parts = [["#" + key + "p", ORG[0]], ["#" + key + "n", ORG[2]]].concat(st.map((t, k) => ["#" + key + "c" + k, ORG[1]]));
  parts.forEach(([sel, org]) => {{
    const isScr = sel.indexOf(key + "c") === 1; const k = isScr ? +sel.slice(-1) : -1;
    tl.set(sel, {{ opacity: 1 }}, isScr ? st[k] : a); tl.set(sel, {{ opacity: 0 }}, isScr && k + 1 < st.length ? st[k + 1] : b);
    tl.fromTo(sel, {{ transformPerspective: 2200, transformOrigin: org, x: 150, y: 560, rotationZ: 7, rotationY: -26, rotationX: 10 }},
      E({{ x: 0, y: 0, rotationZ: 0, rotationY: -7, rotationX: 3, duration: 0.95, ease: "power3.out" }}), a);
    tl.to(sel, {{ rotationY: 5, rotationX: 0, duration: Math.max(0.6, b - a - 0.95), ease: "sine.inOut" }}, a + 0.95);
  }});
  pt.forEach((t, k) => {{
    const h = "#" + key + "h" + k, t0 = Math.max(a + 0.12, t - 0.05);
    tl.set(h, {{ opacity: 1, y: 0, filter: "blur(0px)" }}, t0);
    tl.fromTo(h + " .w span", {{ y: "110%", opacity: 0, filter: "blur(14px)" }}, E({{ y: "0%", opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out", stagger: 0.05 }}), t0);
    tl.fromTo(h + " .hl", {{ scaleX: 0 }}, E({{ scaleX: 1, duration: 0.42, ease: "power3.out" }}), t0 + 0.14);
    if (k + 1 < pt.length) tl.to(h, {{ y: -46, opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power2.in" }}, pt[k + 1] - 0.4);
  }});
}});
// fièrement congolaise: people in full frame, flag colours as an accent
tl.set("#scrim", {{ opacity: 1 }}, {PRIDE0}); tl.set("#scrim", {{ opacity: 0 }}, {LOGO});
tl.set("#pt", {{ opacity: 1 }}, 34.3);
tl.fromTo("#pt .ln:nth-child(1) span", {{ y: "115%", filter: "blur(12px)" }}, E({{ y: "0%", filter: "blur(0px)", duration: 0.55, ease: "power3.out" }}), 34.37);
tl.fromTo("#pt .ln:nth-child(2) span", {{ y: "115%", filter: "blur(12px)" }}, E({{ y: "0%", filter: "blur(0px)", duration: 0.55, ease: "power3.out" }}), 35.05);
tl.fromTo("#pbar b", {{ scaleX: 0 }}, E({{ scaleX: 1, duration: 0.4, ease: "power3.out", stagger: 0.09 }}), 35.2);
tl.fromTo("#psub", {{ opacity: 0, y: 26 }}, E({{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}), 35.75);
tl.set("#pt, #pbar, #psub", {{ opacity: 0 }}, {LOGO});
// flag-colour bands sweep, then the logo card
[0, 1, 2].forEach((k) => tl.fromTo("#bd" + k, {{ x: -900, skewX: -18 }}, E({{ x: 2700, skewX: -18, duration: 0.75, ease: "power2.inOut" }}), {LOGO} - 0.42 + k * 0.07));
const HIT = {LOGO}; tl.set("#E", {{ opacity: 1 }}, HIT);
const ARR0 = HIT + 0.5, dx = -0.496 * 1150, dy = 0.868 * 1150, ps = document.getElementById("ps"), aw = document.getElementById("aw"), o = {{ x: dx, y: dy }};
const put = () => {{ aw.style.transform = "translate(" + o.x + "px," + o.y + "px)"; ps.style.webkitMaskPosition = o.x + "px " + o.y + "px, 0px 0px"; }};
tl.fromTo("#ps", {{ scale: .8, opacity: 0, transformOrigin: "1040px 450px" }}, E({{ scale: 1, opacity: 1, duration: .5, ease: "expo.out" }}), HIT + 0.1);
tl.set(o, {{ x: dx, y: dy, onUpdate: put }}, HIT); tl.set("#aw", {{ opacity: 0 }}, HIT); tl.set("#aw", {{ opacity: 1 }}, ARR0);
tl.fromTo(o, {{ x: dx, y: dy }}, E({{ x: 0, y: 0, duration: .85, ease: "power3.out", onUpdate: put }}), ARR0);
tl.to("#cv", {{ y: -90, duration: .6, ease: "power3.inOut" }}, ARR0 + .75);
tl.fromTo("#word", {{ opacity: 0, y: 40 }}, E({{ opacity: 1, y: 0, duration: .55, ease: "expo.out" }}), ARR0 + .9);
tl.fromTo("#tag2", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: .5, ease: "expo.out" }}), ARR0 + 1.1);
tl.fromTo("#url", {{ opacity: 0 }}, E({{ opacity: .9, duration: .5 }}), ARR0 + 1.3);
tl.fromTo("#stores", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: .5, ease: "expo.out" }}), ARR0 + 1.45);
tl.set({{}}, {{}}, {END:.2f});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
open(OUT, "w").write(html.replace(" ?", " ?"))
json.dump({"end": END, "logo": LOGO, "pride": PRIDE0, "apps": [[a, b] for k, a, b, *_ in APPS], "steps": [t for *_, ph in APPS for _, t in ph]}, open(OUT + ".t.json", "w"))
print("ok END", round(END, 2))
