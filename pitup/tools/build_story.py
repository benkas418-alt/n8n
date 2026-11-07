# Storytelling video builder (the "PitUp, c'est quoi ?" formula): one scene per voice line, each scene split into
# beats of real footage, real photos, product cutouts, a 3D phone with the real app/site, the 3D laptop, the shop mosaic.
import json, subprocess, sys, os, shutil
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
C = json.load(open(sys.argv[1])); P = f"{SP}/hf/videos/{C['project']}"; V = f"{SP}/audio/v8"
os.makedirs(P + "/assets", exist_ok=True)
for d in ["v", "img"]:
    if not os.path.exists(f"{P}/assets/{d}"): shutil.copytree(f"{SP}/story/{d}", f"{P}/assets/{d}")
for f in ["hyperframes.json", "hyperframes.lock.json", "meta.json", "package.json"]: shutil.copy(f"{SP}/hf/videos/pitup-voix1/{f}", P)
for f in ["fonts", "grain.png", "gsap.min.js", "icon.png", "icon_white.png", "logo_tag_white.png", "logo_word_white.png"]:
    s, d = f"{SP}/hf/videos/pitup-voix1/assets/{f}", f"{P}/assets/{f}"
    if not os.path.exists(d): (shutil.copytree if os.path.isdir(s) else shutil.copy)(s, d)

def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
def span(f):
    o = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(l.split("silence_start: ")[1]) for l in o.splitlines() if "silence_start" in l]
    en = [float(l.split("silence_end: ")[1].split(" ")[0]) for l in o.splitlines() if "silence_end" in l]
    d = dur(f); a = en[0] if en and st and st[0] < 0.05 else 0.0
    z = st[-1] if st and st[-1] > d - 1.5 and (not en or st[-1] > en[-1]) else d
    return a, z
vo, S, t = [], [], 0.3
for sc in C["scenes"]:
    a, z = span(f"{V}/{sc['vo']}.wav"); vo.append((sc["vo"], t + 0.15, a)); S.append(round(t, 3)); t += 0.15 + (z - a) + 0.45
S[0] = 0.0
last = C["scenes"][-1]; a, z = span(f"{V}/{last['vo']}.wav")
END = round(S[-1] + 0.15 + (z - a) * last.get("end_at", 0.45), 3)
DUR = round(S[-1] + 0.15 + (z - a) + 3.6, 3)
S.append(END)
json.dump({"vo": vo, "dur": DUR}, open(f"{P}/timing.json", "w"), indent=1)

tpl = open(f"{SP}/hf/videos/pitup-tendance5/index.html").read()
css = tpl[tpl.index("<style>") + 7: tpl.index("</style>")]
end_html = tpl[tpl.index('          <div id="end">'): tpl.index('        <div id="anchor">')]
end_html = end_html[: end_html.rindex("</div>")]

vids, scene_html, js, PW, n = [], [], [], [], [0]
STYLE = C.get("style", "base")
root_html = []

def nid(): n[0] += 1; return n[0]
for i, sc in enumerate(C["scenes"]):
    a, b = S[i], S[i + 1]; beats = sc["beats"]; w = (b - a) / len(beats)
    if sc.get("head"):
        h = sc["head"]
        if STYLE == "glass":   # liquid-glass card, words appear one by one across the spoken line
            words = [(w, 0) for w in h[0].split()] + [(w, 1) for w in (h[1].split() if len(h) > 1 else [])]
            scene_html.append(f'<div class="gl" id="h{i}">' + "".join(f'<span class="w{" em" if e else ""}" id="h{i}w{k}">{w}</span> ' for k, (w, e) in enumerate(words)) + '</div>')
            js.append(f'show("#h{i}", {a}, {b}, 0.35); tl.fromTo("#h{i}", {{ y: 40, scale: 0.96 }}, {{ y: 0, scale: 1, duration: 0.6, ease: "power3.out" }}, {a});')
            span_ = max(0.6, (b - a) * 0.7)
            for k in range(len(words)): js.append(f'tl.fromTo("#h{i}w{k}", {{ opacity: 0, y: 14, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "power2.out" }}, {a + 0.15 + k * span_ / len(words):.3f});')
        elif STYLE == "kin":   # huge black slab, Lubumbashi visible through the letters
            root_html.append(f'<div class="kin" id="h{i}"><div>{h[0]}</div><div>{h[1] if len(h) > 1 else ""}</div></div>')
            js.append(f'tl.set("#h{i}", {{ opacity: 1 }}, {a}); tl.set("#h{i}", {{ opacity: 0 }}, {b}); tl.fromTo("#h{i} div", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.55, stagger: 0.12, ease: "expo.out" }}, {a}); tl.fromTo("#h{i}", {{ scale: 1.0 }}, {{ scale: 1.05, duration: {b - a:.3f}, ease: "none" }}, {a});')
        elif STYLE == "city":  # small editorial caption, bottom-left, blue rule
            scene_html.append(f'<div class="ed" id="h{i}"><i></i><span>{h[0]}</span><b>{h[1] if len(h) > 1 else ""}</b></div>')
            js.append(f'tl.fromTo("#h{i}", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {a + 0.05}); tl.set("#h{i}", {{ opacity: 0 }}, {b}); tl.fromTo("#h{i} i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out", transformOrigin: "0 50%" }}, {a});')
        else:
            scene_html.append(f'<div class="hd" id="h{i}"><span>{h[0]}</span><b>{h[1] if len(h) > 1 else ""}</b></div>')
            js.append(f'hd("#h{i}", {a}, {b});')
    if sc.get("tag"):
        scene_html.append(f'<div class="tag" id="t{i}">{sc["tag"]}</div>'); js.append(f'show("#t{i}", {a}, {b});')
    for k, bt in enumerate(beats):
        ba, bb = round(a + k * w, 3), round(a + (k + 1) * w, 3); kind = bt["k"]; j = nid()
        if kind == "v":
            vids.append(f'<video id="v{j}" class="clip vid" src="assets/v/{bt["src"]}.mp4" muted playsinline data-start="{ba}" data-duration="{bb - ba:.3f}" data-track-index="{2 + j % 2}"></video>')
            js.append(f'tl.fromTo("#v{j}", {{ scale: 1.0 }}, {{ scale: 1.05, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "rapid":   # quick cuts on the music grid
            step = bt.get("step", 0.46); m, t0 = 0, ba
            while t0 < bb - 0.05:
                t1 = min(bb, t0 + step); jj = nid()
                vids.append(f'<video id="v{jj}" class="clip vid" src="assets/v/{bt["srcs"][m % len(bt["srcs"])]}.mp4" muted playsinline data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + jj % 2}"></video>')
                js.append(f'tl.fromTo("#v{jj}", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {t1 - t0:.3f}, ease: "power2.out" }}, {t0:.3f});')
                m += 1; t0 = t1
        elif kind == "split":   # 2 or 3 stacked strips, entering one after the other
            nn = len(bt["srcs"]); hh = 1920 / nn
            for m, src in enumerate(bt["srcs"]):
                jj = nid(); t0 = round(ba + m * 0.18, 3)
                vids.append(f'<video id="v{jj}" class="clip vid" src="assets/v/{src}.mp4" muted playsinline data-start="{t0}" data-duration="{bb - t0:.3f}" data-track-index="{2 + jj % 2}" style="top:{m * hh:.0f}px;height:{hh - (6 if m < nn - 1 else 0):.0f}px"></video>')
                js.append(f'tl.fromTo("#v{jj}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.45, ease: "expo.out" }}, {t0});')
        elif kind == "img":
            scene_html.append(f'<div class="full" id="b{j}"><img class="bg" src="assets/img/{bt["src"]}" alt=""></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.2); tl.fromTo("#b{j} img", {{ scale: 1.12 }}, {{ scale: 1.0, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "cut":
            scene_html.append(f'<div class="full" id="b{j}" style="background:{bt.get("bg", "#EFE6D8")}"><div class="giant" style="color:{bt.get("tone", "#E3D6C2")}">{bt.get("word", "")}</div><img class="cut" src="assets/img/{bt["src"]}" alt=""></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.15); tl.fromTo("#b{j} .cut", {{ scale: 0.86, y: 60 }}, {{ scale: 1, y: 0, duration: 0.5, ease: "back.out(1.6)" }}, {ba}); tl.fromTo("#b{j} .giant", {{ x: 50 }}, {{ x: -50, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "phone":
            PW.append((ba, bb, bt["src"], False))
        elif kind == "lap":
            PW.append((ba, bb, bt.get("src", "phs_full"), True))
            js.append(f'tl.set("#lapstage", {{ opacity: 1 }}, {ba}); tl.set("#lapstage", {{ opacity: 0 }}, {bb});'
                      f'tl.fromTo("#lap", {{ rotationY: 22, rotationX: 8, y: 120 }}, {{ rotationY: 8, rotationX: 4, y: 0, duration: 0.8, ease: "power3.out" }}, {ba});'
                      f'tl.to("#lap", {{ rotationY: -6, duration: {max(0.3, bb - ba - 0.8):.3f}, ease: "sine.inOut" }}, {ba + 0.8});'
                      f'tl.fromTo("#lid", {{ rotationX: -70 }}, {{ rotationX: 0, duration: 0.8, ease: "power3.out" }}, {ba});'
                      f'tl.fromTo("#lbody", {{ y: 0 }}, {{ y: -1150, duration: {max(0.3, bb - ba - 0.6):.3f}, ease: "sine.inOut" }}, {ba + 0.5});')
        elif kind == "mosaic":
            scene_html.append(f'<div class="full" id="b{j}"><img class="bg" src="assets/img/mosaic.jpg" alt="" style="height:auto"><div style="position:absolute;inset:0;background:rgba(10,14,20,.62)"></div><div class="big100">+<span id="num{j}">0</span></div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.2); tl.fromTo("#b{j} img", {{ y: 0 }}, {{ y: -60, duration: {bb - ba:.3f}, ease: "none" }}, {ba});'
                      f'const c{j} = {{ v: 0 }}; tl.fromTo(c{j}, {{ v: 0 }}, {{ v: 100, duration: 1.4, ease: "power2.out", onUpdate: () => (document.getElementById("num{j}").textContent = Math.round(c{j}.v)) }}, {ba + 0.1});')
        elif kind == "flag":
            scene_html.append(f'<div class="full" id="b{j}"><img class="bg" src="assets/img/aerial.jpg" alt=""><div style="position:absolute;inset:0;background:rgba(0,0,0,.25)"></div>'
                              f'<div class="flag"><svg viewBox="0 0 800 600" width="700" height="525"><rect width="800" height="600" fill="#007FFF"/><polygon points="0,510 680,0 800,0 800,90 120,600 0,600" fill="#F7D618"/><polygon points="0,555 740,0 800,0 800,45 60,600 0,600" fill="#CE1021"/><polygon points="150,40 172,108 244,108 186,150 208,218 150,176 92,218 114,150 56,108 128,108" fill="#F7D618"/></svg></div><div class="credit" style="opacity:1">Imagerie © Esri, Maxar</div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.3); tl.fromTo("#b{j} .flag", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.5)" }}, {ba + 0.2});')
        if bt.get("cap"):
            cls = {"glass": "cap gcap", "city": "cap ccap", "kin": "cap kcap"}.get(STYLE, "cap")
            scene_html.append(f'<div class="{cls}" id="c{j}" style="top:{bt.get("cap_top", 1560)}px"><span>{bt["cap"]}</span></div>'); js.append(f'cap("#c{j}", {ba}, {bb});')
        if bt.get("big"):
            scene_html.append(f'<div class="bigtxt" id="g{j}">{bt["big"]}</div>'); js.append(f'tl.fromTo("#g{j}", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.8)" }}, {ba + 0.05}); tl.set("#g{j}", {{ opacity: 0 }}, {bb});')

SW, SH = 520, 1126
slabs = "".join(f'<div class="slab{" back" if k == 20 else ""}" style="transform:translateZ(-{k}px)">' + ("" if k in (1, 20) else '<i class="btn" style="left:-5px;top:280px;height:64px"></i><i class="btn" style="left:-5px;top:370px;height:110px"></i><i class="btn" style="right:-5px;top:400px;height:160px"></i>') + '</div>' for k in range(20, 0, -1))
pv = "".join(f'<video id="pv{k}" class="clip pv" src="assets/v/{c}.mp4" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{5 + k % 2}"></video>' for k, (a, b, c, _) in enumerate(PW))
html = f'''<!doctype html>
<html lang="fr"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><script src="assets/gsap.min.js"></script>
<style>{css}
.vid {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
#scene {{ z-index: 8; background: transparent !important; }}
.full {{ position: absolute; inset: 0; opacity: 0; overflow: hidden; }}
.full img.bg {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
.full .cut {{ position: absolute; left: 140px; right: 140px; top: 640px; width: 800px; height: 860px; object-fit: contain; filter: drop-shadow(0 40px 34px rgba(0,0,0,.3)); }}
.full .giant {{ position: absolute; left: 0; right: 0; top: 1520px; text-align: center; font-weight: 800; font-size: 230px; letter-spacing: -8px; white-space: nowrap; }}
.shade {{ position: absolute; left: 0; right: 0; top: 0; height: 640px; background: linear-gradient(180deg, rgba(0,0,0,.72) 30%, rgba(0,0,0,0)); z-index: 8; }}
.hd {{ position: absolute; left: 76px; right: 76px; top: 250px; font-weight: 800; font-size: 92px; letter-spacing: -3px; line-height: 1.02; color: #fff; opacity: 0; z-index: 9; text-shadow: 0 6px 30px rgba(0,0,0,.35); }}
.hd span, .hd b {{ display: block; }} .hd b {{ color: #8fd0f7; }}
.tag {{ position: absolute; left: 76px; top: 330px; font-weight: 800; font-size: 40px; letter-spacing: 3px; color: #8fd0f7; opacity: 0; z-index: 9; }}
.cap {{ position: absolute; left: 60px; right: 60px; text-align: center; opacity: 0; z-index: 9; }}
.cap span {{ display: inline-block; background: #fff; color: #17120d; font-weight: 800; font-size: 64px; letter-spacing: -2px; padding: 22px 40px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,.3); }}
.bigtxt {{ position: absolute; left: 60px; right: 60px; top: 760px; text-align: center; font-weight: 800; font-size: 150px; letter-spacing: -6px; line-height: 1; color: #fff; z-index: 9; opacity: 0; text-shadow: 0 10px 50px rgba(0,0,0,.5); }}
.big100 {{ position: absolute; left: 0; right: 0; top: 700px; text-align: center; font-weight: 800; font-size: 400px; letter-spacing: -20px; color: #fff; text-shadow: 0 10px 50px rgba(0,0,0,.5); }}
.flag {{ position: absolute; left: 190px; top: 760px; width: 700px; height: 525px; border-radius: 34px; overflow: hidden; box-shadow: 0 40px 80px rgba(0,0,0,.45); }}
.credit {{ position: absolute; right: 30px; bottom: 26px; font-size: 22px; color: rgba(255,255,255,.75); font-weight: 600; }}
#anchor {{ z-index: 45; }}
.gl {{ position: absolute; left: 60px; right: 60px; top: 230px; padding: 34px 44px 40px; border-radius: 44px; z-index: 9; opacity: 0;
  background: linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,.10)); backdrop-filter: blur(22px) saturate(1.5); -webkit-backdrop-filter: blur(22px) saturate(1.5);
  box-shadow: inset 0 1.5px 0 rgba(255,255,255,.75), inset 0 0 0 1.5px rgba(255,255,255,.35), 0 30px 60px rgba(0,0,0,.25);
  font-weight: 800; font-size: 84px; letter-spacing: -2.5px; line-height: 1.05; color: #fff; text-shadow: 0 2px 18px rgba(0,0,0,.25); }}
.gl .w {{ display: inline-block; }} .gl .em {{ background: linear-gradient(90deg, #8fd0f7, #ffffff 60%, #ffd76a); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.gcap span {{ background: linear-gradient(180deg, rgba(255,255,255,.30), rgba(255,255,255,.12)) !important; color: #fff !important; backdrop-filter: blur(20px) saturate(1.5); -webkit-backdrop-filter: blur(20px) saturate(1.5); box-shadow: inset 0 1.5px 0 rgba(255,255,255,.8), inset 0 0 0 1.5px rgba(255,255,255,.35), 0 20px 50px rgba(0,0,0,.25) !important; text-shadow: 0 2px 14px rgba(0,0,0,.3); }}
.kin {{ position: absolute; inset: 0; z-index: 2; background: #000; mix-blend-mode: multiply; opacity: 0; display: flex; flex-direction: column; justify-content: center; padding: 0 50px; overflow: hidden; }}
.kin div {{ color: #fff; font-weight: 800; font-size: 210px; line-height: .9; letter-spacing: -10px; text-transform: uppercase; overflow: hidden; }}
.kcap span {{ background: #1f88c9 !important; color: #fff !important; border-radius: 0 !important; font-size: 58px !important; }}
.ed {{ position: absolute; left: 70px; right: 70px; bottom: 300px; z-index: 9; opacity: 0; color: #fff; text-shadow: 0 4px 24px rgba(0,0,0,.6); }}
.ed i {{ display: block; width: 120px; height: 10px; background: #1f88c9; margin-bottom: 26px; }}
.ed span {{ display: block; font-weight: 800; font-size: 70px; letter-spacing: -2px; line-height: 1.02; }} .ed b {{ display: block; font-weight: 600; font-size: 54px; color: #cfe9fb; }}
.ccap span {{ background: transparent !important; box-shadow: none !important; color: #fff !important; font-size: 52px !important; text-shadow: 0 4px 24px rgba(0,0,0,.7); border-bottom: 6px solid #1f88c9; border-radius: 0 !important; padding: 6px 4px !important; }}
#pbg {{ position: absolute; inset: 0; z-index: 3; opacity: 0; background: radial-gradient(120% 70% at 50% 40%, #39a4e6 0%, #1f88c9 45%, #0f5f93 100%); }}
#stage {{ position: absolute; inset: 0; perspective: 2600px; perspective-origin: 50% 55%; z-index: 6; pointer-events: none; }}
#phone {{ position: absolute; left: {(1080 - SW - 32) / 2}px; top: 560px; width: {SW + 32}px; height: {SH + 32}px; transform-style: preserve-3d; opacity: 0; }}
.slab {{ position: absolute; inset: 0; border-radius: 80px; background: linear-gradient(90deg, #5d6167, #c9cdd2 18%, #8b9096 50%, #d7dade 82%, #5a5e63); }}
.slab .btn {{ position: absolute; width: 8px; border-radius: 4px; background: linear-gradient(90deg, #8d9197, #c4c8cd); }}
.slab.back {{ background: #1b1c20; }}
#front {{ position: absolute; inset: 0; border-radius: 80px; background: #0b0c0f; padding: 16px; box-sizing: border-box; box-shadow: inset 0 0 0 3px #2b2d32, 0 0 0 2px #a9adb3; }}
#screen {{ position: relative; width: {SW}px; height: {SH}px; border-radius: 64px; overflow: hidden; background: #fff; }}
#screen .pv {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
#island {{ position: absolute; left: 50%; top: 18px; width: 140px; height: 40px; margin-left: -70px; border-radius: 20px; background: #050506; z-index: 6; }}
#glare {{ position: absolute; inset: 0; z-index: 5; background: linear-gradient(115deg, rgba(255,255,255,0) 35%, rgba(255,255,255,.17) 47%, rgba(255,255,255,0) 58%); background-size: 260% 100%; background-position: 100% 0; }}
#pshadow {{ position: absolute; left: 300px; top: 1730px; width: 480px; height: 60px; border-radius: 50%; background: rgba(0,0,0,.35); filter: blur(24px); z-index: 5; opacity: 0; }}
#lapstage {{ position: absolute; inset: 0; perspective: 2400px; perspective-origin: 50% 40%; z-index: 5; opacity: 0; pointer-events: none; }}
#lap {{ position: absolute; left: 60px; top: 640px; width: 960px; transform-style: preserve-3d; }}
#lid {{ position: relative; width: 960px; height: 620px; border-radius: 30px 30px 8px 8px; background: #0d0e11; padding: 22px 22px 30px; box-sizing: border-box; box-shadow: 0 0 0 2px #b9bdc2; transform-origin: 50% 100%; }}
#lscreen {{ position: relative; width: 916px; height: 568px; overflow: hidden; border-radius: 8px; background: #fff; }}
#lscreen .hd2 {{ position: absolute; left: 0; top: 0; width: 916px; z-index: 2; }}
#lscreen .body {{ position: absolute; left: 0; top: 41px; width: 916px; }}
#deck {{ position: relative; width: 1060px; height: 34px; margin-left: -50px; border-radius: 0 0 26px 26px; background: linear-gradient(180deg, #d9dce0, #9ea2a8); box-shadow: 0 30px 50px rgba(0,0,0,.35); }}
#deck i {{ position: absolute; left: 50%; top: 0; width: 170px; height: 10px; margin-left: -85px; border-radius: 0 0 10px 10px; background: #8d9196; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/bgm.wav" data-start="0" data-duration="{DUR:.3f}" data-track-index="11"></audio>
{"".join(vids)}
{"".join(root_html)}
<div id="pbg"></div>
<div id="lapstage"><div id="lap"><div id="lid"><div id="lscreen"><img class="hd2" src="assets/img/desk_head.png" alt=""><img class="body" id="lbody" src="assets/img/desk_body.jpg" alt=""></div></div><div id="deck"><i></i></div></div></div>
<div id="pshadow"></div>
<div id="stage"><div id="phone">{slabs}<div id="front"><div id="screen"><div id="island"></div><div id="glare"></div>{pv}</div></div></div></div>
<div id="scene" class="clip layer" data-start="0" data-duration="{DUR:.3f}" data-track-index="0"><div id="cam">
{"".join(scene_html)}
<div class="shade" id="shade"></div>
{end_html}
</div>
<div id="anchor"><img id="anchorIcon" src="assets/icon_white.png" alt="" /><span id="anchorTxt" style="color:#fff">PitUp · Lubumbashi</span></div>
<div id="flash"></div><div id="vignette"></div><div id="grain"></div></div>
</div>
<script>
const END = {END}, DUR = {DUR};
const tl = gsap.timeline({{ paused: true }});
const show = (sel, a, b, fade = 0.25) => {{ tl.fromTo(sel, {{ opacity: 0 }}, {{ opacity: 1, duration: fade, ease: "power1.out" }}, a); tl.set(sel, {{ opacity: 0 }}, b); }};
const hd = (sel, a, b) => {{ tl.fromTo(sel, {{ opacity: 0, yPercent: 25 }}, {{ opacity: 1, yPercent: 0, duration: 0.45, ease: "power3.out" }}, a + 0.05); tl.set(sel, {{ opacity: 0 }}, b); }};
const cap = (sel, a, b) => {{ tl.fromTo(sel, {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, a + 0.05); tl.set(sel, {{ opacity: 0 }}, b); }};
tl.set("#shade", {{ opacity: {0 if STYLE in ("kin", "city") else 1} }}, 0); tl.set("#shade", {{ opacity: 0 }}, END);
{chr(10).join(js)}
const PW = {json.dumps([(a, b, s7) for a, b, _, s7 in PW])};
PW.forEach(([a, b, s7], k) => {{
  const side = k % 2 ? -1 : 1;
  tl.set("#pbg", {{ opacity: 1 }}, a); tl.set("#pbg", {{ opacity: 0 }}, b);
  tl.set("#phone", {{ opacity: 1, x: s7 ? 250 : 0, y: s7 ? 330 : 0, scale: s7 ? 0.62 : 1 }}, a); tl.set("#phone", {{ opacity: 0 }}, b);
  tl.set("#pshadow", {{ opacity: s7 ? 0 : 1 }}, a); tl.set("#pshadow", {{ opacity: 0 }}, b);
  tl.fromTo("#phone", {{ rotationY: -60 * side, rotationX: 10 }}, {{ rotationY: -14 * side, rotationX: 6, duration: 0.7, ease: "power3.out" }}, a);
  tl.to("#phone", {{ rotationY: 12 * side, duration: Math.max(0.3, b - a - 0.7), ease: "sine.inOut" }}, a + 0.7);
  tl.fromTo("#glare", {{ backgroundPositionX: "100%" }}, {{ backgroundPositionX: "0%", duration: b - a, ease: "sine.inOut" }}, a);
}});
tl.set("#flash", {{ opacity: 1 }}, END); tl.set("#flash", {{ opacity: 0 }}, END + 1 / 30);
tl.set("#end", {{ opacity: 1, zIndex: 43 }}, END); tl.set("#anchor", {{ opacity: 0 }}, END);
tl.fromTo("#icon", {{ scale: 1.15, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.32, ease: "expo.out" }}, END);
tl.fromTo("#ring", {{ scale: 0.7, opacity: 0.9 }}, {{ scale: 1.5, opacity: 0, duration: 0.7, ease: "power2.out" }}, END + 0.05);
tl.fromTo("#word", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, END + 0.4);
tl.fromTo("#tag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, END + 0.7);
tl.fromTo("#count", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, END + 1.0);
tl.fromTo("#cta", {{ scale: 0.7, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.42, ease: "back.out(2)" }}, END + 0.2);
tl.fromTo("#stores .bdg", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.35, stagger: 0.12, ease: "back.out(1.6)" }}, END + 1.4);
for (let f = 0; f < DUR * 12; f++) {{ const ox = ((f * 137) % 512) - 256, oy = ((f * 251) % 512) - 256; tl.set("#grain", {{ x: ox / 8, y: oy / 8 }}, f / 12); }}
tl.set({{}}, {{}}, DUR);
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(html)
print(json.dumps({"S": S, "END": END, "DUR": DUR}))
