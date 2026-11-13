# Motion design "carrousel RDC" (9:16): each beat is keyed to the word the voice says (whisper word times).
# Animation rules from the founder's reference: ease-out entries, 30 ms line stagger, exits 20 % shorter,
# no spring on scene transitions, icons fade in with blur, success pulse, curved paths, 0.97 press.
# usage: build_mc.py words.json lead total out.html
import json, re, sys
W = json.load(open(sys.argv[1])); LEAD = float(sys.argv[2]); DUR = float(sys.argv[3]); OUT = sys.argv[4]
norm = lambda t: re.sub(r"[^a-zà-ÿ0-9]", "", t.lower())
words = [(norm(w), s + LEAD, e + LEAD) for w, s, e, p in W]
def at(key, after=0.0, end=False):
    for w, s, e in words:
        if w == key and s >= after - 1e-3: return e if end else s
    raise SystemExit(f"word not found: {key} after {after}")
# scene starts (cut a hair before the word so the picture leads the voice slightly)
t_prep = LEAD
t_tuas = at("tu", 1.0) - 0.15
t_bout = at("boutique", t_tuas); t_stock = at("stock", t_tuas); t_whats = at("whatsapp", t_tuas)
t_pub = at("publies", t_whats) - 0.2
t_cmd = at("client", t_pub); t_livr = at("livrons", t_pub); t_paie = at("paie", t_pub)
t_talent = at("et", t_paie + 0.3) - 0.15
t_graph = at("graphiste", t_talent) - 0.12
jobs = [at(k, t_graph - 0.2) for k in ("graphiste", "vidéaste", "photographe", "maquilleuse", "coiffeuse")]
t_profil = at("crée", jobs[-1]) - 0.15; t_post = at("postule", t_profil)
t_cherch = at("tu", t_post + 0.4) - 0.15
t_besoin = at("publie", t_cherch); t_comp = at("compare", t_cherch); t_disc = at("discute", t_cherch)
t_cent = at("plus", t_disc + 0.3) - 0.12
t_vend = at("vendeur", t_cent) - 0.15
t_appli = at("appli", t_vend)
S = [t_prep, t_tuas, t_pub, t_talent, t_graph, t_cherch, t_cent, t_vend, DUR]
print(json.dumps({"scenes": [round(x, 2) for x in S], "jobs": [round(j, 2) for j in jobs]}))

ICON = {
 "shop": '<svg viewBox="0 0 24 24"><path d="M3 9l1.5-5h15L21 9"/><path d="M3 9h18v2a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/><path d="M5 13v7h14v-7"/><path d="M10 20v-5h4v5"/></svg>',
 "home": '<svg viewBox="0 0 24 24"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><rect x="9" y="13" width="6" height="7"/></svg>',
 "phone": '<svg viewBox="0 0 24 24"><rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18.5h2"/></svg>',
 "check": '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'}
job_img = [("Graphiste", "5254659", "center 30%"), ("Vidéaste", "8995315", "center 30%"), ("Photographe", "12446331", "center 12%"),
           ("Maquilleuse", "6954163", "center 30%"), ("Coiffeuse", "15576672", "center 0%")]

html = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;font-weight:500;src:url(assets/fonts/poppins-500.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:600;src:url(assets/fonts/poppins-600.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:700;src:url(assets/fonts/poppins-700.woff2) format("woff2")}}
@font-face{{font-family:P;font-weight:800;src:url(assets/fonts/poppins-800.woff2) format("woff2")}}
:root{{--blue:#1f88c9;--deep:#0d5a8f;--sky:#e4f1fa;--ink:#101418;--mute:#5b6570;--line:#e3e8ee}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#fff}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:P,sans-serif;color:var(--ink)}}
.sc{{position:absolute;inset:0;opacity:0;overflow:hidden}}
.dark{{background:radial-gradient(120% 90% at 20% 15%,#2a9be0 0%,#1f88c9 40%,#0d5a8f 100%);color:#fff}}
.white{{background:#fff}}
.tag{{position:absolute;z-index:5;left:80px;top:250px;display:flex;align-items:center;gap:14px;font-weight:600;font-size:32px}}
.tag img{{width:46px}}
.h{{position:absolute;left:80px;right:80px;font-weight:800;letter-spacing:-3px;line-height:1.04}}
.h .ln{{display:block;overflow:hidden}} .h .ln span{{display:inline-block}}
.bl{{color:var(--blue)}}
.sub{{position:absolute;left:80px;right:80px;font-weight:500;font-size:40px;line-height:1.35}}
.photo{{position:absolute;background-size:cover;background-position:center;border-radius:36px}}
.card{{position:absolute;left:80px;right:80px;height:150px;display:flex;align-items:center;gap:30px;padding:0 36px;border-radius:30px;background:#f4f7fa;border:2px solid var(--line)}}
.card .ic{{flex:0 0 92px;height:92px;border-radius:24px;background:var(--sky);display:flex;align-items:center;justify-content:center}}
.card svg,.st em svg{{width:52px;height:52px;stroke:var(--blue);fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}}
.card b{{display:block;font-weight:700;font-size:44px}} .card span{{font-weight:500;font-size:30px;color:var(--mute)}}
.st{{position:absolute;left:80px;width:480px;display:flex;gap:24px;align-items:center}}
.st em{{flex:0 0 76px;height:76px;border-radius:50%;background:var(--blue);color:#fff;font-style:normal;font-weight:700;font-size:36px;display:flex;align-items:center;justify-content:center}}
.st em svg{{stroke:#fff;width:42px;height:42px}}
.st p{{font-weight:600;font-size:40px;line-height:1.2}}
.stage{{position:absolute;inset:0;perspective:2200px}}
.phone{{position:absolute;width:440px;height:948px;border-radius:70px;padding:14px;
 background:linear-gradient(145deg,#4b4f57 0%,#16171b 18%,#0b0c0f 55%,#2a2c32 100%);
 box-shadow:inset 0 0 0 2px #6c7079,inset 0 0 0 5px #0b0c0f,1px .6px 0 #55585f,2px 1.2px 0 #3c3f45,3px 1.8px 0 #2f3137,4px 2.4px 0 #26282d,5px 3px 0 #212226,6px 3.6px 0 #1c1d21,7px 4.2px 0 #18191c,8px 4.8px 0 #151619,9px 5.4px 0 #131417,10px 6px 0 #111215,40px 70px 90px rgba(8,40,70,.38)}}
.phone img{{display:block;width:100%;height:100%;object-fit:cover;object-position:top;border-radius:57px}}
.phone .isl{{position:absolute;left:50%;top:32px;width:122px;height:36px;margin-left:-61px;border-radius:18px;background:#050506;z-index:3}}
.phone:after{{content:"";position:absolute;inset:14px;border-radius:57px;background:linear-gradient(118deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.16) 42%,rgba(255,255,255,0) 54%);background-size:260% 100%}}
.badge{{position:absolute;border-radius:50%;border:10px solid #fff;box-shadow:0 24px 50px rgba(13,90,143,.3);background-size:cover;background-position:center 25%}}
.tile{{position:absolute;width:440px;height:330px;border-radius:30px;overflow:hidden;background:#f4f7fa;border:2px solid var(--line)}}
.tile i{{display:block;height:230px;background-size:cover}} .tile b{{display:block;padding:18px 26px;font-weight:700;font-size:40px}}
.big{{position:absolute;left:0;right:0;text-align:center;font-weight:800;color:#fff}}
.faces{{position:absolute;left:80px;display:flex}} .faces i{{width:120px;height:120px;border-radius:50%;border:6px solid #1f88c9;margin-right:-24px;background-size:cover;background-position:center 25%}}
.stores{{position:absolute;left:80px;display:flex;gap:26px;align-items:center}} .stores img{{height:112px}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{DUR:.3f}" data-track-index="11"></audio>

<section class="sc dark" id="c0">
 <div class="tag"><img src="assets/icon_white.png" alt="">PitUp · RDC</div>
 <div class="photo" id="c0p" style="left:440px;right:0;top:1000px;bottom:0;border-radius:0;background-image:url(assets/ph/7802856.jpg);background-position:center 15%"></div>
 <div style="position:absolute;inset:0;background:linear-gradient(90deg,#1f88c9 0%,rgba(31,136,201,.85) 38%,rgba(31,136,201,0) 60%)"></div>
 <h1 class="h" id="c0h" style="top:420px;font-size:122px"><span class="ln"><span>Prépare-toi</span></span><span class="ln"><span>à un changement</span></span><span class="ln"><span>digital</span></span><span class="ln"><span>en RDC.</span></span></h1>
</section>

<section class="sc white" id="c1">
 <div class="tag" style="color:var(--ink)"><img src="assets/icon.png" alt="">Vendeurs</div>
 <h2 class="h" id="c1h" style="top:340px;font-size:88px"><span class="ln"><span>Pas besoin d'une</span></span><span class="ln"><span>grande boutique</span></span><span class="ln"><span class="bl">pour vendre.</span></span></h2>
 <div class="photo" id="c1p" style="left:80px;right:80px;top:700px;height:430px;background-image:url(assets/ph/7191992.jpg);background-position:center 30%"></div>
 <div class="card" id="k0" style="top:1180px"><div class="ic">{ICON['shop']}</div><div><b>Une boutique en ville</b><span>Avec une adresse.</span></div></div>
 <div class="card" id="k1" style="top:1350px"><div class="ic">{ICON['home']}</div><div><b>Un stock à la maison</b><span>Tu vends depuis chez toi.</span></div></div>
 <div class="card" id="k2" style="top:1520px"><div class="ic">{ICON['phone']}</div><div><b>Une boutique perso</b><span>Sur WhatsApp ou les réseaux.</span></div></div>
</section>

<section class="sc white" id="c2">
 <div class="tag" style="color:var(--ink)"><img src="assets/icon.png" alt="">Vendeurs</div>
 <h2 class="h" style="top:340px;font-size:96px"><span class="ln"><span>Tu vends,</span></span><span class="ln"><span class="bl">nous livrons.</span></span></h2>
 {''.join(f'<div class="st" id="t{k}" style="top:{700 + k*170}px"><em>{ICON["check"]}</em><p>{x}</p></div>' for k, x in enumerate(["Tu publies", "Le client commande", "Nous livrons", "Paiement à la livraison"]))}
 <div class="stage"><div class="phone" id="ph2" style="right:60px;top:640px"><i class="isl"></i><img src="assets/scr/store_hd.png" alt=""></div></div>
 <div class="badge" id="b2" style="left:560px;top:1430px;width:250px;height:250px;background-image:url(assets/ph/6868266.jpg)"></div>
</section>

<section class="sc dark" id="c3">
 <div class="photo" id="c3p" style="inset:0;border-radius:0;background-image:url(assets/ph/3769021.jpg);background-position:58% center"></div>
 <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,90,143,0) 30%,rgba(13,90,143,.6) 52%,rgba(13,90,143,.97) 72%)"></div>
 <div class="tag" style="color:var(--ink)"><img src="assets/icon.png" alt="">Prestataires</div>
 <h2 class="h" id="c3h" style="top:1180px;font-size:112px;color:#fff"><span class="ln"><span>Et si ton talent,</span></span><span class="ln"><span>c'est un service ?</span></span></h2>
</section>

<section class="sc white" id="c4">
 <div class="tag" style="color:var(--ink)"><img src="assets/icon.png" alt="">Prestataires</div>
 {''.join(f'<div class="tile" id="j{k}" style="left:{80 + (k%2)*480}px;top:{360 + (k//2)*370}px"><i style="background-image:url(assets/ph/{img}.jpg);background-position:{pos}"></i><b>{n}</b></div>' for k, (n, img, pos) in enumerate(job_img))}
 <div class="tile" id="j5" style="left:560px;top:1100px;background:var(--blue);border-color:var(--blue);color:#fff;display:flex;align-items:center;padding:30px"><b style="padding:0;font-size:38px">Et bien d'autres métiers</b></div>
 <div class="stage"><div class="phone" id="ph4" style="right:60px;top:600px"><i class="isl"></i><img src="assets/scr/real_feed.png" alt=""></div></div>
 <h2 class="h" id="c4h" style="top:640px;width:500px;font-size:72px;opacity:0"><span class="ln"><span>Crée ton</span></span><span class="ln"><span>profil,</span></span><span class="ln"><span class="bl">postule.</span></span></h2>
</section>

<section class="sc white" id="c5">
 <div class="tag" style="color:var(--ink)"><img src="assets/icon.png" alt="">Clients</div>
 <h2 class="h" style="top:340px;font-size:96px"><span class="ln"><span>Tu cherches</span></span><span class="ln"><span class="bl">un pro ?</span></span></h2>
 {''.join(f'<div class="st" id="u{k}" style="top:{760 + k*190}px"><em>{k+1}</em><p>{x}</p></div>' for k, x in enumerate(["Publie ton besoin", "Compare les profils", "Discute directement"]))}
 <div class="stage"><div class="phone" id="ph5" style="right:60px;top:640px"><i class="isl"></i><img src="assets/scr/real_beauty.png" alt=""></div></div>
 <div class="badge" id="b5" style="left:540px;top:1400px;width:240px;height:240px;background-image:url(assets/ph/5332457.jpg)"></div>
</section>

<section class="sc dark" id="c6">
 <div class="big" id="n100" style="top:640px;font-size:300px;letter-spacing:-12px">+100</div>
 <div class="big" id="n100t" style="top:1000px;font-size:64px;font-weight:700">boutiques locales</div>
 <div class="big" id="n100s" style="top:1090px;font-size:44px;font-weight:500;color:#d9eefb">sont déjà sur l'appli.</div>
</section>

<section class="sc dark" id="c7">
 <div class="tag"><img src="assets/icon_white.png" alt="">PitUp · RDC</div>
 <div class="faces" id="faces" style="top:420px">{''.join(f'<i style="background-image:url(assets/ph/{x}.jpg)"></i>' for x in ["12446331", "6868266", "6954163", "8995315", "7191992"])}</div>
 <h2 class="h" id="c7h" style="top:620px;font-size:104px;color:#fff"><span class="ln"><span>Vendeurs,</span></span><span class="ln"><span>prestataires,</span></span><span class="ln"><span>clients :</span></span><span class="ln"><span>une seule appli.</span></span></h2>
 <div class="sub" id="url" style="top:1210px;font-weight:700;font-size:60px">pi-tup.com</div>
 <div class="stores" id="stores" style="top:1340px"><img src="assets/Google_Play_Store_badge_EN.svg" alt=""><img src="assets/appstore.svg" alt=""></div>
</section>
<div id="flash"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
const S = {json.dumps([round(x, 3) for x in S])};
const JOBS = {json.dumps([round(j, 3) for j in jobs])};
const OUT = 0.28, IN = 0.35;                      // exits ~20 % shorter than entries
// scenes: cross-fade with a slight lift, no spring
for (let i = 0; i < 8; i++) {{
  const id = "#c" + i, a = S[i], b = S[i + 1];
  if (i === 0) tl.set(id, {{ opacity: 1 }}, 0); else tl.fromTo(id, {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: IN, ease: "power3.out" }}, a);
  if (i < 7) tl.to(id, {{ opacity: 0, y: -30, duration: OUT, ease: "power2.in" }}, b - OUT * 0.5);
}}
// headline lines: ease-out rise, 30 ms stagger per line
function lines(sel, t) {{ tl.fromTo(sel + " .ln > span", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.55, ease: "power3.out", stagger: 0.03 }}, t); }}
lines("#c0h", 0.15); lines("#c1h", S[1] + 0.1); lines("#c2 .h", S[2] + 0.1); lines("#c3h", S[3] + 0.25); lines("#c5 .h", S[5] + 0.1); lines("#c7h", S[7] + 0.35);
// photos: slow push (weight on reveals)
tl.fromTo("#c0p", {{ y: 260, scale: 1.08 }}, {{ y: 0, scale: 1, duration: 1.1, ease: "power3.out" }}, 0.35);
tl.fromTo("#c1p", {{ clipPath: "inset(0 0 100% 0 round 36px)" }}, {{ clipPath: "inset(0 0 0% 0 round 36px)", duration: 0.7, ease: "power3.out" }}, S[1] + 0.2);
tl.fromTo("#c3p", {{ scale: 1.12 }}, {{ scale: 1, duration: S[4] - S[3], ease: "power1.out" }}, S[3]);
// seller cards on their words, icons fade in with blur
[{t_bout:.3f}, {t_stock:.3f}, {t_whats:.3f}].forEach((t, k) => {{
  tl.fromTo("#k" + k, {{ opacity: 0, x: -60, scale: 0.95 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, t - 0.05);
  tl.fromTo("#k" + k + " svg", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.4 }}, t + 0.05);
}});
// selling steps + success pulse
[{S[2] + 0.35:.3f}, {t_cmd:.3f}, {t_livr:.3f}, {t_paie:.3f}].forEach((t, k) => {{
  tl.fromTo("#t" + k, {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, t - 0.05);
  tl.fromTo("#t" + k + " em", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.35, ease: "power3.out" }}, t);
  tl.to("#t" + k + " em", {{ scale: 1.12, duration: 0.12, yoyo: true, repeat: 1, ease: "sine.inOut" }}, t + 0.38);
}});
// 3D phones: curved entry from the trigger side (x and y on different eases), settle face-on
function phone(sel, t) {{
  tl.fromTo(sel, {{ x: 420, rotationY: -55, rotationX: 8, opacity: 0 }}, {{ x: 0, rotationY: -12, rotationX: 4, opacity: 1, duration: 0.8, ease: "power3.out" }}, t);
  tl.fromTo(sel, {{ y: 160 }}, {{ y: 0, duration: 0.8, ease: "power2.out" }}, t);
  tl.to(sel, {{ rotationY: -4, rotationX: 2, duration: 2.5, ease: "sine.inOut" }}, t + 0.8);
  tl.fromTo(sel + ":after", {{ backgroundPositionX: "100%" }}, {{ backgroundPositionX: "0%", duration: 1.6 }}, t + 0.3);
}}
phone("#ph2", S[2] + 0.15); phone("#ph5", S[5] + 0.15);
tl.fromTo("#b2", {{ scale: 0.95, opacity: 0, filter: "blur(6px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out" }}, {t_livr:.3f});
tl.fromTo("#b5", {{ scale: 0.95, opacity: 0, filter: "blur(6px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out" }}, {t_disc:.3f});
// job tiles on each name, then they make room for the phone (old and new state blended)
JOBS.forEach((t, k) => tl.fromTo("#j" + k, {{ opacity: 0, y: 50, scale: 0.95 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "power3.out" }}, t - 0.06));
tl.fromTo("#j5", {{ opacity: 0, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "power3.out" }}, JOBS[4] + 0.35);
tl.to("#c4 .tile", {{ opacity: 0, y: -40, duration: 0.3, ease: "power2.in", stagger: 0.03 }}, {t_profil:.3f} - 0.2);
phone("#ph4", {t_profil:.3f} - 0.05);
tl.to("#c4h", {{ opacity: 1, duration: 0.01 }}, {t_profil:.3f}); lines("#c4h", {t_profil:.3f});
// client steps
[{t_besoin:.3f}, {t_comp:.3f}, {t_disc:.3f}].forEach((t, k) => {{
  tl.fromTo("#u" + k, {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, t - 0.05);
  tl.to("#u" + k + " em", {{ scale: 0.97, duration: 0.08, yoyo: true, repeat: 1 }}, t + 0.3);
}});
// +100: counter with weight
const cnt = {{ v: 0 }};
tl.fromTo("#n100", {{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }}, S[6] + 0.1);
tl.to(cnt, {{ v: 100, duration: 0.9, ease: "power2.out", onUpdate: () => {{ document.getElementById("n100").textContent = "+" + Math.round(cnt.v); }} }}, S[6] + 0.1);
tl.fromTo("#n100t, #n100s", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out", stagger: 0.03 }}, S[6] + 0.45);
// end card
tl.fromTo("#faces i", {{ opacity: 0, scale: 0.95, filter: "blur(6px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power3.out", stagger: 0.05 }}, S[7] + 0.1);
tl.fromTo("#url", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t_appli:.3f} + 0.3);
tl.fromTo("#stores img", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out", stagger: 0.06 }}, {t_appli:.3f} + 0.45);
tl.set({{}}, {{}}, {DUR:.3f});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
import re as _re
head, body = html.split("<body>", 1)
body = _re.sub(r" ([?!:])(?=[^<]*<)", lambda m: "\u00a0" + m.group(1), body)
html = head + "<body>" + body
open(OUT, "w").write(html)
json.dump({"scenes": S, "jobs": jobs, "cards": [t_bout, t_stock, t_whats], "steps": [S[2] + 0.35, t_cmd, t_livr, t_paie],
           "client": [t_besoin, t_comp, t_disc], "profil": t_profil, "appli": t_appli}, open(OUT + ".cues.json", "w"))
