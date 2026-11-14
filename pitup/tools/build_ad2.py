# Brand film with voice-over (sister): who PitUp is for, what you do there, how, and what you need.
# Each profile = a real person (footage) asking the question, then the real app on a 3D phone with the 3 steps,
# each step appearing on the word the voice says. usage: build_ad2.py cues.json out.html
import json, sys
C = json.load(open(sys.argv[1])); OUT = sys.argv[2]
LOGO = C["parti"] - 0.15; END = LOGO + 4.9
FOOT = [("market", C["q1"], C["ouvre"] - 0.1, "Des articles|à vendre ?"), ("sew", C["q2"], C["talent"] - 0.1, "Un métier,|un talent ?"),   # one caption over two short shots
        ("braid", C["talent"] - 0.1, C["cree1"] - 0.1, ""), ("phone", C["q3"], C["cherches2"] - 0.1, "Tu cherches|un article, un pro ?")]
APPS = [("S", C["ouvre"] - 0.1, C["q2"], "VENDEURS", ["store_hd.png"], None,
         [("Ouvre ta boutique", C["ouvre"]), ("Publie tes photos", C["publie"]), ("Nous livrons tes clients", C["livrons"])]),
        ("P", C["cree1"] - 0.1, C["q3"], "PRESTATAIRES", ["real_feed.png", "real_beauty.png"], C["montre"],
         [("Crée ton profil", C["cree1"]), ("Montre ton travail", C["montre"]), ("Les clients te contactent", C["contactent"])]),
        ("K", C["cherches2"] - 0.1, C["faut"] - 0.15, "CLIENTS", ["market2.png", "jordan.png"], C["choisis"],
         [("Cherche", C["cherches2"]), ("Choisis", C["choisis"]), ("Commande", C["commandes"]), ("Paie à la livraison", C["paies"])])]
HERO = C["faut"] - 0.15
vids = "".join(f'<video id="c{k}" class="clip strip" src="assets/v/{c}.mp4" muted playsinline data-start="0" data-duration="{C["q1"]:.2f}" data-track-index="{2 + k}" style="top:{k * 640}px"></video>' for k, c in enumerate(["c_alilac", "c_traffic_s", "c_park"]))
vids += "".join(f'<video id="v{k}" class="clip full" src="assets/v/{n}.mp4" muted playsinline data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="{5 + k % 2}"></video>' for k, (n, a, b, _) in enumerate(FOOT))
caps = "".join(f'<div class="cap" id="t{k}"><i></i>' + "".join(f'<span class="ln"><span>{l}</span></span>' for l in txt.split("|")) + '</div>' for k, (n, a, b, txt) in enumerate(FOOT))
apps = ""
for key, a, b, label, scr, swap, steps in APPS:
    imgs = "".join(f'<img id="{key}i{k}" src="assets/scr/{s}" alt="" style="opacity:{1 if k == 0 else 0}">' for k, s in enumerate(scr))
    chips = "".join(f'<div class="chip" id="{key}s{k}"><em>{k + 1}</em><span>{t}</span></div>' for k, (t, _) in enumerate(steps))
    apps += f'<section class="app{" four" if len(steps) > 3 else ""}" id="{key}"><div class="lbl">{label}</div><div class="chips">{chips}</div><div class="stage"><div class="phone" id="{key}p"><i class="isl"></i><div class="scr">{imgs}</div></div></div></section>'
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
#scrim{{position:absolute;left:0;right:0;bottom:0;height:900px;background:linear-gradient(180deg,rgba(4,14,28,0),rgba(4,14,28,.8));z-index:2;opacity:0}}
#cdim{{position:absolute;inset:0;z-index:2;background:rgba(4,14,28,.45)}}
#city{{position:absolute;left:0;right:0;top:700px;text-align:center;z-index:3;font-weight:800;font-size:104px;line-height:1.08;letter-spacing:-3px;text-shadow:0 8px 40px rgba(0,0,0,.6)}}
#city small{{display:block;font-weight:600;font-size:34px;letter-spacing:10px;margin-bottom:14px}}
.cap{{position:absolute;left:80px;right:80px;bottom:330px;z-index:3;font-weight:800;font-size:112px;letter-spacing:-4px;line-height:1.05;opacity:0}}
.cap i{{display:block;width:110px;height:12px;border-radius:6px;background:#1f88c9;margin-bottom:26px;transform-origin:0 50%}}
.ln{{display:block;overflow:hidden;padding-bottom:10px}} .ln span{{display:inline-block;transform:translateY(115%)}}
.app,#H{{position:absolute;inset:0;z-index:4;opacity:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%)}}
.lbl{{position:absolute;left:80px;top:200px;font-weight:600;font-size:36px;letter-spacing:8px;color:#d9eefb}}
.chips{{position:absolute;left:80px;top:290px;right:80px;display:flex;flex-direction:column;gap:22px}}
.chip{{display:flex;align-items:center;gap:24px;width:fit-content;padding:16px 36px 16px 16px;border-radius:60px;background:#fff;color:#0d2a40;font-weight:700;font-size:46px;letter-spacing:-1px;box-shadow:0 18px 40px rgba(4,30,60,.3);opacity:0}}
.chip em{{flex:0 0 72px;height:72px;border-radius:50%;background:#1f88c9;color:#fff;font-style:normal;font-size:36px;display:flex;align-items:center;justify-content:center}}
.four .chips{{gap:16px}} .four .chip{{font-size:40px;padding:10px 30px 10px 10px}} .four .chip em{{flex-basis:60px;height:60px;font-size:30px}}
.stage{{position:absolute;inset:0;perspective:2200px}}
.phone{{position:absolute;left:299px;top:730px;width:482px;height:1040px;border-radius:74px;padding:15px;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,2px 1.2px 0 #3c3f45,4px 2.4px 0 #26282d,6px 3.6px 0 #1c1d21,8px 4.8px 0 #151619,10px 6px 0 #111215,40px 70px 90px rgba(4,30,60,.5)}}
.phone .scr{{position:absolute;inset:15px;border-radius:64px;overflow:hidden;background:#fff}}
.phone .scr img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top}}
.phone .isl{{position:absolute;left:50%;top:34px;width:136px;height:38px;margin-left:-68px;border-radius:18px;background:#050506;z-index:3}}
#H h2{{position:absolute;left:80px;right:80px;top:230px;font-weight:800;font-size:100px;letter-spacing:-3px;line-height:1.05}}
#Hp{{left:325px;top:760px;width:430px;height:900px;border-radius:68px}}
#Hs{{position:absolute;left:0;right:0;top:1690px;display:flex;gap:28px;justify-content:center;opacity:0}} #Hs img{{height:96px}}
#Hc{{position:absolute;left:80px;top:500px;display:flex;flex-direction:column;gap:18px}} #Hc .chip{{font-size:42px;padding:12px 32px 12px 12px}} #Hc .chip em{{flex-basis:62px;height:62px}}
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
{apps}
<section id="H"><h2><span class="ln"><span>Il te faut juste</span></span><span class="ln"><span>ton téléphone.</span></span></h2>
 <div id="Hc"><div class="chip" id="Hc0"><em>1</em><span>Télécharge l'appli</span></div><div class="chip" id="Hc1"><em>2</em><span>Crée ton compte</span></div></div>
 <div class="stage"><div class="phone" id="Hp"><i class="isl"></i><div class="scr"><img src="assets/scr/market2.png" alt=""></div></div></div>
 <div id="Hs"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></section>
<div id="E">
 <div id="cv"><img id="ps" src="assets/p_solid.png" alt=""><div class="m" id="mo"><img id="aw" src="assets/arrow_white.png" alt=""></div></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag2" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); const E = (o) => Object.assign({{ immediateRender: false }}, o);
const FOOT = {json.dumps([[a, b, (FOOT[k + 1][2] if k + 1 < len(FOOT) and not FOOT[k + 1][3] else b), bool(t)] for k, (n, a, b, t) in enumerate(FOOT)])};
const APPS = {json.dumps([[k, a, b, sw, [t for _, t in st]] for k, a, b, lb, sc, sw, st in APPS])};
tl.fromTo("#city .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.6, ease: "power3.out", stagger: 0.08 }}), 0.3);
tl.set("#city, #cdim", {{ opacity: 0 }}, {C["q1"]:.3f});
FOOT.forEach(([a, b, ce, cap], k) => {{
  tl.set("#scrim", {{ opacity: 1 }}, a); tl.set("#scrim", {{ opacity: 0 }}, b);
  tl.fromTo("#v" + k, {{ scale: 1 }}, E({{ scale: 1.06, duration: b - a, ease: "none" }}), a);
  if (!cap) return;
  tl.set("#t" + k, {{ opacity: 1 }}, a);
  tl.fromTo("#t" + k + " i", {{ scaleX: 0 }}, E({{ scaleX: 1, duration: 0.4, ease: "power3.out" }}), a + 0.1);
  tl.fromTo("#t" + k + " .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.5, ease: "power3.out", stagger: 0.1 }}), a + 0.15);
  tl.set("#t" + k, {{ opacity: 0 }}, ce);
}});
APPS.forEach(([key, a, b, sw, steps]) => {{
  tl.set("#" + key, {{ opacity: 1 }}, a); tl.set("#" + key, {{ opacity: 0 }}, b);
  tl.fromTo("#" + key + "p", {{ y: 420, rotationY: -20, rotationX: 8 }}, E({{ y: 0, rotationY: -8, rotationX: 3, duration: 0.8, ease: "power3.out" }}), a);
  tl.to("#" + key + "p", {{ rotationY: 0, rotationX: 0, duration: Math.max(0.6, b - a - 0.9), ease: "sine.inOut" }}, a + 0.8);
  steps.forEach((t, k) => tl.fromTo("#" + key + "s" + k, {{ opacity: 0, x: -50 }}, E({{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}), t - 0.05));
  if (sw) {{ tl.to("#" + key + "i1", {{ opacity: 1, duration: 0.3 }}, sw); }}
}});
// what you need
tl.set("#H", {{ opacity: 1 }}, {HERO:.3f});
tl.fromTo("#H .ln span", {{ y: "115%" }}, E({{ y: "0%", duration: 0.55, ease: "power3.out", stagger: 0.08 }}), {HERO:.3f} + 0.15);
tl.fromTo("#Hp", {{ y: 520, rotationY: -22, rotationX: 8 }}, E({{ y: 0, rotationY: -6, rotationX: 2, duration: 0.9, ease: "power3.out" }}), {HERO:.3f} + 0.1);
tl.to("#Hp", {{ rotationY: 0, rotationX: 0, duration: 1.6, ease: "sine.inOut" }}, {HERO:.3f} + 1.0);
tl.fromTo("#Hc0", {{ opacity: 0, x: -50 }}, E({{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}), {C["telecharge"]:.3f});
tl.fromTo("#Hs", {{ opacity: 0, y: 30 }}, E({{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}), {C["telecharge"]:.3f});
tl.fromTo("#Hc1", {{ opacity: 0, x: -50 }}, E({{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}), {C["cree2"]:.3f});
// logo sign-off
const HIT = {LOGO:.3f}; tl.set("#E", {{ opacity: 1 }}, HIT);
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
json.dump({"end": END, "logo": LOGO, "hero": HERO, "foot": [[a, b] for n, a, b, t in FOOT], "apps": [[a, b] for k, a, b, *_ in APPS]}, open(OUT + ".t.json", "w"))
print("ok END", round(END, 2), "foot durations", [round(b - a, 2) for n, a, b, t in FOOT], "app durations", [round(b - a, 2) for k, a, b, *_ in APPS])
