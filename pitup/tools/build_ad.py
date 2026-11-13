# Brand film « Lushi, ça bouge » — live-action style (telecom ads): real footage, clean cuts, one short line per shot,
# real app on a 3D phone, logo sign-off. No effects that draw attention to themselves. usage: build_ad.py out.html
import json, sys
OUT = sys.argv[1]
SH = [("city", 0.0, ""), ("market", 2.6, "Des articles|à vendre."), ("sew", 5.2, "Un métier."), ("braid", 7.4, "Un talent."),
      ("phone", 9.6, "Et quelqu'un|qui en a besoin."), ("deliv", 15.4, "Tu commandes.|Nous livrons.|Tu paies à la livraison.")]
APP, LOGO, END = 12.4, 18.6, 23.4
ENDS = [5.2, 7.4, 9.6, 12.4, 18.6]          # end of each full-frame shot (the app scene sits between phone and delivery)
T = {"shots": [s[1] for s in SH], "app": APP, "logo": LOGO, "end": END}
vids = "".join(f'<video id="c{k}" class="clip strip" src="assets/v/{c}.mp4" muted playsinline data-start="0" data-duration="2.6" data-track-index="{2 + k}" style="top:{k * 640}px"></video>' for k, c in enumerate(["c_alilac", "c_traffic", "c_park"]))
for k, (n, t, _) in enumerate(SH[1:]):
    nxt = ENDS[k]
    vids += f'<video id="v{k}" class="clip full" src="assets/v/{n}.mp4" muted playsinline data-start="{t}" data-duration="{nxt - t:.2f}" data-track-index="{5 + k % 2}"></video>'
caps = "".join(f'<div class="cap{" sm" if txt.count("|") > 1 else ""}" id="t{k}"><i></i>' + "".join(f'<span class="ln"><span>{l}</span></span>' for l in txt.split("|")) + '</div>' for k, (n, t, txt) in enumerate(SH[1:]))
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
.strip{{position:absolute;left:0;width:1080px;height:634px;object-fit:cover}}
#scrim{{position:absolute;left:0;right:0;bottom:0;height:900px;background:linear-gradient(180deg,rgba(4,14,28,0),rgba(4,14,28,.78));z-index:2;opacity:0}}
#city{{position:absolute;left:0;right:0;top:700px;text-align:center;z-index:3;font-weight:800;font-size:104px;line-height:1.08;letter-spacing:-3px;text-shadow:0 8px 40px rgba(0,0,0,.6)}}
#city small{{display:block;font-weight:600;font-size:34px;letter-spacing:10px;margin-bottom:14px}}
#cdim{{position:absolute;inset:0;z-index:2;background:rgba(4,14,28,.45)}}
.cap{{position:absolute;left:80px;right:80px;bottom:330px;z-index:3;font-weight:800;font-size:116px;letter-spacing:-4px;line-height:1.05;opacity:0}}
.cap.sm{{font-size:80px;letter-spacing:-2.5px}}
.cap i{{display:block;width:110px;height:12px;border-radius:6px;background:#1f88c9;margin-bottom:26px;transform-origin:0 50%}}
.ln{{display:block;overflow:hidden;padding-bottom:10px}} .ln span{{display:inline-block;transform:translateY(115%)}}
#A{{position:absolute;inset:0;z-index:4;opacity:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
#A h2{{position:absolute;left:80px;right:80px;top:260px;font-weight:800;font-size:104px;letter-spacing:-3px;line-height:1.05}}
.stage{{position:absolute;inset:0;perspective:2200px}}
.phone{{position:absolute;left:310px;top:640px;width:460px;height:992px;border-radius:72px;padding:14px;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,2px 1.2px 0 #3c3f45,4px 2.4px 0 #26282d,6px 3.6px 0 #1c1d21,8px 4.8px 0 #151619,10px 6px 0 #111215,40px 70px 90px rgba(4,30,60,.5)}}
.phone img{{display:block;width:100%;height:100%;object-fit:cover;object-position:top;border-radius:58px}}
.phone .isl{{position:absolute;left:50%;top:32px;width:124px;height:36px;margin-left:-62px;border-radius:18px;background:#050506;z-index:3}}
#E{{position:absolute;inset:0;z-index:5;opacity:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
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
<div id="scrim"></div><div id="cdim"></div>
<div id="city"><small>LUBUMBASHI</small><span class="ln"><span>Ici, chacun a</span></span><span class="ln"><span>quelque chose</span></span><span class="ln"><span>à offrir.</span></span></div>
{caps}
<div id="A"><h2><span class="ln"><span>Une seule appli</span></span><span class="ln"><span>les réunit.</span></span></h2>
 <div class="stage"><div class="phone" id="ph"><i class="isl"></i><img src="assets/scr/store_hd.png" alt=""></div></div></div>
<div id="E">
 <div id="cv"><img id="ps" src="assets/p_solid.png" alt=""><div class="m" id="mo"><img id="aw" src="assets/arrow_white.png" alt=""></div></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag2" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); const E = (o) => Object.assign({{ immediateRender: false }}, o);
const S = {json.dumps([s[1] for s in SH[1:]])}, EN = {json.dumps(ENDS)};
// opening: the city, one word
tl.fromTo("#city .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.6, ease: "power3.out", stagger: 0.08 }}), 0.25);
tl.fromTo("#city small", {{ opacity: 0 }}, E({{ opacity: 1, duration: 0.5 }}), 0.15);
tl.set("#city, #cdim", {{ opacity: 0 }}, S[0]);
tl.set("#scrim", {{ opacity: 1 }}, S[0]); tl.set("#scrim", {{ opacity: 0 }}, {LOGO});
// shots: straight cuts, a slow push-in, one line each
for (let k = 0; k < 5; k++) {{
  const a = S[k], b = EN[k];
  tl.fromTo("#v" + k, {{ scale: 1 }}, E({{ scale: 1.06, duration: b - a, ease: "none" }}), a);
  tl.set("#t" + k, {{ opacity: 1 }}, a);
  tl.fromTo("#t" + k + " i", {{ scaleX: 0 }}, E({{ scaleX: 1, duration: 0.4, ease: "power3.out" }}), a + 0.1);
  tl.fromTo("#t" + k + " .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.5, ease: "power3.out", stagger: k === 4 ? 0.75 : 0.1 }}), a + 0.15);
  tl.to("#t" + k, {{ opacity: 0, duration: 0.18, ease: "power2.in" }}, b - 0.2);
}}
// the app
tl.set("#A", {{ opacity: 1 }}, {APP}); tl.set("#A", {{ opacity: 0 }}, S[4]);
tl.fromTo("#A .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.55, ease: "power3.out", stagger: 0.08 }}), {APP} + 0.15);
tl.fromTo("#ph", {{ y: 500, rotationY: -22, rotationX: 8 }}, E({{ y: 0, rotationY: -8, rotationX: 3, duration: 0.9, ease: "power3.out" }}), {APP} + 0.1);
tl.to("#ph", {{ rotationY: 0, rotationX: 0, duration: 1.8, ease: "sine.inOut" }}, {APP} + 1.0);
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
tl.set({{}}, {{}}, {END});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
open(OUT, "w").write(html); json.dump(T, open(OUT + ".cues.json", "w")); print("ok", END)
