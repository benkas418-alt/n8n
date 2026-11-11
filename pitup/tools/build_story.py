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
for sc in ([] if C.get("vo_full") else C["scenes"]):
    a, z = span(f"{V}/{sc['vo']}.wav"); vo.append((sc["vo"], t + 0.15, a)); S.append(round(t, 3)); t += 0.15 + (z - a) + 0.45
if S: S[0] = 0.0
last = C["scenes"][-1]; a, z = span(f"{V}/{last['vo']}.wav") if not C.get("vo_full") else (0, 0)
END = round(S[-1] + 0.15 + (z - a) * last.get("end_at", 0.45), 3) if S else 0
DUR = round(S[-1] + 0.15 + (z - a) + 3.6, 3) if S else 0
if C.get("vo_full"):   # whole script spoken in one take: keep its natural rhythm, scenes follow the sentence starts
    lead = 0.3; st = C["starts"]; S = [0.0] + [round(lead + t, 3) for t in st[1:]]
    vo = [(C["vo_full"], lead, 0.0)]; END = round(lead + C["end_card_at"], 3); DUR = round(lead + C["vo_end"] + 3.0, 3)
S.append(END)
json.dump({"vo": vo, "dur": DUR}, open(f"{P}/timing.json", "w"), indent=1)

tpl = open(f"{SP}/hf/videos/pitup-tendance5/index.html").read()
css = tpl[tpl.index("<style>") + 7: tpl.index("</style>")]
end_html = tpl[tpl.index('          <div id="end">'): tpl.index('        <div id="anchor">')]
end_html = end_html[: end_html.rindex("</div>")]

vids, scene_html, js, PW, n = [], [], [], [], [0]
STYLE = C.get("style", "base")
# "plate": false keeps the word-by-word glass typography but drops the frosted card behind headlines and captions
NOPLATE = "" if C.get("plate", True) else ("#root .gl { background: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important; box-shadow: none !important; padding: 0 !important; left: 70px !important; right: 70px !important; text-shadow: 0 4px 30px rgba(0,0,0,.6), 0 1px 4px rgba(0,0,0,.35) !important; }"
  " #root .gl .em { background: none !important; -webkit-text-fill-color: #fff !important; color: #fff !important; } #root .gcap span { background: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important; box-shadow: none !important; text-shadow: 0 4px 26px rgba(0,0,0,.75), 0 1px 4px rgba(0,0,0,.4) !important; font-size: 56px !important; }")
root_html = []

LAPPH = {}; LIGHT = []   # light-background beats: no dark shade or vignette, dark top tag
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
            # over the 3D phone or laptop the caption moves above the device, never across the screen
            edpos = ' style="top:300px;bottom:auto"' if any(b_["k"] in ("phone", "lap") for b_ in beats) else ""
            scene_html.append(f'<div class="ed" id="h{i}"{edpos}><i></i><span>{h[0]}</span><b>{h[1] if len(h) > 1 else ""}</b></div>')
            js.append(f'tl.fromTo("#h{i}", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {a + 0.05}); tl.set("#h{i}", {{ opacity: 0 }}, {b}); tl.fromTo("#h{i} i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out", transformOrigin: "0 50%" }}, {a});')
        else:
            scene_html.append(f'<div class="hd" id="h{i}"><span>{h[0]}</span><b>{h[1] if len(h) > 1 else ""}</b></div>')
            js.append(f'hd("#h{i}", {a}, {b});')
    if sc.get("tag"):
        scene_html.append(f'<div class="tag" id="t{i}">{sc["tag"]}</div>'); js.append(f'show("#t{i}", {a}, {b});')
    for k, bt in enumerate(beats):
        ba, bb = round(a + k * w, 3), round(a + (k + 1) * w, 3); kind = bt["k"]; j = nid()
        bgc = bt.get("bg", "#ffffff" if kind == "kt" else "#f4f5f7")
        if kind in ("kt", "cards") and int(bgc[1:3], 16) + int(bgc[3:5], 16) + int(bgc[5:7], 16) > 450: LIGHT.append((ba, bb))
        if kind == "v":
            vids.append(f'<video id="v{j}" class="clip vid" src="assets/v/{bt["src"]}.mp4" muted playsinline data-start="{ba}" data-duration="{bb - ba:.3f}" data-track-index="{2 + j % 2}"></video>')
            js.append(f'tl.fromTo("#v{j}", {{ scale: 1.0 }}, {{ scale: 1.05, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
            if bt.get("credit"):   # source credit shown over the shot (map or imagery licences)
                scene_html.append(f'<div class="credit" id="cr{j}" style="opacity:0;z-index:9;color:rgba(40,40,40,.8)">{bt["credit"]}</div>'); js.append(f'tl.set("#cr{j}", {{ opacity: 1 }}, {ba}); tl.set("#cr{j}", {{ opacity: 0 }}, {bb});')
        elif kind == "rapid":   # quick cuts on the music grid
            # each shot plays once: stretch the cut length (whole beats) rather than loop the list
            nn_ = len(bt["srcs"]); g = bt.get("step", 0.46); step = g * max(1, -(-(bb - ba) // (nn_ * g))); m, t0 = 0, ba
            while t0 < bb - 0.05 and m < nn_:
                t1 = bb if m == nn_ - 1 else min(bb, t0 + step); jj = nid()
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
        elif kind == "kt":    # kinetic typography on a clean background, words land one by one, accent words in brand blue
            ws = bt["words"]; acc = set(bt.get("accent", []))
            spans_ = "".join(f'<span class="ktw{" kta" if k in acc else ""}" id="b{j}k{k}">{w}</span> ' for k, w in enumerate(ws))
            scene_html.append(f'<div class="full" id="b{j}" style="background:{bt.get("bg", "#ffffff")};z-index:9"><div class="kt" style="font-size:{bt.get("size", 120)}px;color:{bt.get("ink", "#111214")}">{spans_}</div>{f'<div class="ktsub">{bt["sub"]}</div>' if bt.get("sub") else ""}</div>')
            gap = min(0.32, max(0.12, (bb - ba) * 0.6 / max(1, len(ws))))
            js.append(f'show("#b{j}", {ba}, {bb}, 0.12);' + "".join(f'tl.fromTo("#b{j}k{k}", {{ opacity: 0, y: 50, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.7)" }}, {ba + 0.05 + k * gap:.3f});' for k in range(1 if ba < 0.01 else 0, len(ws)))
                      + (f'tl.fromTo("#b{j} .ktsub", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {ba + 0.1 + len(ws) * gap:.3f});' if bt.get("sub") else "")
                      + f'tl.fromTo("#b{j} .kt", {{ scale: 1 }}, {{ scale: 1.04, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "cards":  # lookbook: real product photos as rounded cards with their name
            its = bt["items"]; n_ = len(its)
            geo = {1: [(190, 520, 700, 880)], 2: [(70, 600, 455, 600), (555, 600, 455, 600)], 3: [(50, 300, 470, 560), (560, 300, 470, 560), (305, 1020, 470, 470)]}[n_]
            html_ = "".join(f'<div class="pcard" id="b{j}c{k}" style="left:{x}px;top:{y}px;width:{w}px"><img src="assets/img/{it["src"]}" alt="" style="height:{h}px"><b>{it["label"]}</b></div>' for k, (it, (x, y, w, h)) in enumerate(zip(its, geo)))
            scene_html.append(f'<div class="full" id="b{j}" style="background:{bt.get("bg", "#f4f5f7")};z-index:9">{html_}</div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.12);' + "".join(f'tl.fromTo("#b{j}c{k}", {{ opacity: 0, y: 80, rotation: {(-3, 3, 0)[k % 3]} }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.55, ease: "power3.out" }}, {ba + 0.08 + k * min(0.45, (bb - ba) / (n_ + 1)):.3f});' for k in range(n_))
                      + f'tl.fromTo("#b{j} .pcard img", {{ scale: 1.0 }}, {{ scale: 1.06, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "vs":    # duel: two products side by side, "OU" badge, made to get a choice in the comments
            scene_html.append(f'<div class="full" id="b{j}"><div class="vsl" style="background:{bt.get("bga", "#E9EEF3")}"><img src="assets/img/{bt["a"]}" alt=""><b>{bt["la"]}</b></div>'
                              f'<div class="vsr" style="background:{bt.get("bgb", "#F3ECE4")}"><img src="assets/img/{bt["b"]}" alt=""><b>{bt["lb"]}</b></div><div class="vsou">OU</div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.1); tl.fromTo("#b{j} .vsl", {{ xPercent: -100 }}, {{ xPercent: 0, duration: 0.45, ease: "power3.out" }}, {ba}); tl.fromTo("#b{j} .vsr", {{ xPercent: 100 }}, {{ xPercent: 0, duration: 0.45, ease: "power3.out" }}, {ba + 0.1:.3f});'
                      f'tl.fromTo("#b{j} .vsou", {{ scale: 0, rotation: -25 }}, {{ scale: 1, rotation: 0, duration: 0.5, ease: "back.out(2.2)" }}, {ba + 0.35:.3f}); tl.fromTo("#b{j} img", {{ scale: 1 }}, {{ scale: 1.06, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "shop":  # shop spotlight: blurred banner, round logo, name, three real products
            ph = "".join(f'<img class="sp sp{k}" src="assets/img/{q}" alt="">' for k, q in enumerate(bt["p"]))
            scene_html.append(f'<div class="full" id="b{j}" style="background:#0d1520"><img class="bg shopbg" src="assets/img/{bt["banner"]}" alt=""><div class="shopdim"></div>'
                              f'<img class="slogo" src="assets/img/{bt["logo"]}" alt=""><div class="sname">{bt["name"]}</div><div class="ssub">{bt.get("sub", "")}</div>{ph}</div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.15); tl.fromTo("#b{j} .slogo", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.8)" }}, {ba});'
                      f'tl.fromTo("#b{j} .sname, #b{j} .ssub", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, stagger: 0.1, ease: "power3.out" }}, {ba + 0.2:.3f});'
                      f'tl.fromTo("#b{j} .sp", {{ y: 120, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, stagger: 0.12, ease: "power3.out" }}, {ba + 0.45:.3f}); tl.fromTo("#b{j} .shopbg", {{ scale: 1.15 }}, {{ scale: 1.25, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "zoom":  # guessing game: extreme close-up that slowly backs off, then the reveal
            rv = ba + bt.get("rev", 0.68) * (bb - ba)
            scene_html.append(f'<div class="full" id="b{j}" style="background:{bt.get("bg", "#EDE7DE")}"><img class="zimg" src="assets/img/{bt["src"]}" alt="" style="transform-origin:{bt.get("fx", 0.5) * 100:.0f}% {bt.get("fy", 0.5) * 100:.0f}%">'
                              f'<div class="zq">?</div><div class="giant zw" style="color:{bt.get("tone", "#1f88c9")}">{bt.get("word", "")}</div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.1); tl.fromTo("#b{j} .zimg", {{ scale: 5.5 }}, {{ scale: 3.2, duration: {rv - ba:.3f}, ease: "none" }}, {ba}); tl.to("#b{j} .zimg", {{ scale: 1, duration: 0.5, ease: "power3.inOut" }}, {rv:.3f});'
                      f'tl.fromTo("#b{j} .zq", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {ba + 0.2:.3f}); tl.to("#b{j} .zq", {{ opacity: 0, scale: 1.4, duration: 0.25 }}, {rv:.3f});'
                      f'tl.fromTo("#b{j} .zw", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {rv + 0.3:.3f});')
        elif kind == "cut":
            scene_html.append(f'<div class="full" id="b{j}" style="background:{bt.get("bg", "#EFE6D8")}"><div class="giant" style="color:{bt.get("tone", "#E3D6C2")}">{bt.get("word", "")}</div><img class="cut" src="assets/img/{bt["src"]}" alt=""></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.15); tl.fromTo("#b{j} .cut", {{ scale: 0.86, y: 60 }}, {{ scale: 1, y: 0, duration: 0.5, ease: "back.out(1.6)" }}, {ba}); tl.fromTo("#b{j} .giant", {{ x: 50 }}, {{ x: -50, duration: {bb - ba:.3f}, ease: "none" }}, {ba});')
        elif kind == "phone":
            PW.append((ba, bb, bt["src"], False))
        elif kind == "lap":
            PW.append((ba, bb, bt.get("src", "lapscroll"), True)); LAPPH[ba] = bt.get("phone", "ph_swipe")
            js.append(f'tl.set("#lapstage", {{ opacity: 1 }}, {ba}); tl.set("#lapstage", {{ opacity: 0 }}, {bb});'
                      f'tl.fromTo("#lap", {{ rotationY: 22, rotationX: 8, y: 120 }}, {{ rotationY: 8, rotationX: 4, y: 0, duration: 0.8, ease: "power3.out" }}, {ba});'
                      f'tl.to("#lap", {{ rotationY: -6, duration: {max(0.3, bb - ba - 0.8):.3f}, ease: "sine.inOut" }}, {ba + 0.8});'
                      f'tl.fromTo("#lid", {{ rotationX: -70 }}, {{ rotationX: 0, duration: 0.8, ease: "power3.out" }}, {ba});'
                      '')
        elif kind == "mosaic":
            scene_html.append(f'<div class="full" id="b{j}"><img class="bg" src="assets/img/mosaic.jpg" alt="" style="height:auto"><div style="position:absolute;inset:0;background:rgba(10,14,20,.62)"></div><div class="big100">+<span id="num{j}">0</span></div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.2); tl.fromTo("#b{j} img", {{ y: 0 }}, {{ y: -60, duration: {bb - ba:.3f}, ease: "none" }}, {ba});'
                      f'const c{j} = {{ v: 0 }}; tl.fromTo(c{j}, {{ v: 0 }}, {{ v: 100, duration: 1.4, ease: "power2.out", onUpdate: () => (document.getElementById("num{j}").textContent = Math.round(c{j}.v)) }}, {ba + 0.1});')
        elif kind == "drc":   # real DRC outline (Natural Earth 50m) filled with PitUp: brand blue, logo pattern, Lubumbashi pin
            import math
            ring = json.load(open(f"{SP}/real/drc/drc.json"))[0]; k0 = math.cos(math.radians(4))
            xs = [x * k0 for x, y in ring]; ys = [-y for x, y in ring]; sc = 880 / (max(xs) - min(xs)); hgt = (max(ys) - min(ys)) * sc
            ox, oy = 540 - (max(xs) + min(xs)) / 2 * sc, 930 - (max(ys) + min(ys)) / 2 * sc
            prj = lambda lon, lat: (lon * k0 * sc + ox, -lat * sc + oy)
            dd = "M" + " L".join(f"{prj(x, y)[0]:.1f},{prj(x, y)[1]:.1f}" for x, y in ring) + "Z"
            lx, ly = prj(27.4793, -11.6647)
            pat = "".join(f'<image href="assets/icon_white.png" x="{x}" y="{y}" width="34" height="34" opacity="0.16"/>' for y in range(int(930 - hgt / 2) - 40, int(930 + hgt / 2) + 40, 70) for x in range(60 + (35 if (y // 70) % 2 else 0), 1030, 70))
            scene_html.append(f'<div class="full" id="b{j}" style="background:radial-gradient(90% 60% at 50% 48%,#123a5c 0%,#07131f 100%)">'
                              f'<svg class="drc" viewBox="0 0 1080 1920" width="1080" height="1920" style="position:absolute;left:0;top:0"><defs><clipPath id="drcclip{j}"><path d="{dd}"/></clipPath>'
                              f'<linearGradient id="drcg{j}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3aa3e3"/><stop offset="1" stop-color="#1668a8"/></linearGradient></defs>'
                              f'<path class="dfill" d="{dd}" fill="url(#drcg{j})"/><g class="dpat" clip-path="url(#drcclip{j})">{pat}</g>'
                              f'<path class="dline" d="{dd}" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" stroke-dasharray="6000" stroke-dashoffset="6000"/>'
                              f'<circle class="dring" cx="{lx:.0f}" cy="{ly:.0f}" r="18" fill="none" stroke="#fff" stroke-width="5"/><circle class="dpin" cx="{lx:.0f}" cy="{ly:.0f}" r="15" fill="#fff"/></svg>'
                              f'<div class="dlogo" style="position:absolute;left:0;right:0;top:{870 - 40:.0f}px;display:flex;align-items:center;justify-content:center;gap:22px;color:#fff;font-weight:800;font-size:112px;letter-spacing:-4px"><img src="assets/icon_white.png" style="width:120px" alt="">PitUp</div>'
                              f'<div class="dlab" style="position:absolute;right:{1080 - lx + 30:.0f}px;top:{ly - 26:.0f}px;color:#fff;font-weight:700;font-size:36px;text-shadow:0 2px 12px rgba(0,0,0,.4)">Lubumbashi</div></div>')
            fq = min(1.0, (bb - ba) / 1.9)   # compress the reveal so it fits the beat
            T = lambda x: f"{ba + x * fq:.2f}"
            js.append(f'show("#b{j}", {ba}, {bb}, 0.2); tl.fromTo("#b{j} .dline", {{ strokeDashoffset: 6000 }}, {{ strokeDashoffset: 0, duration: {0.9 * fq:.2f}, ease: "power2.inOut" }}, {T(0.05)});'
                      f'tl.fromTo("#b{j} .dfill", {{ opacity: 0 }}, {{ opacity: 1, duration: {0.5 * fq:.2f} }}, {T(0.45)}); tl.fromTo("#b{j} .dpat", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: {0.6 * fq:.2f} }}, {T(0.6)});'
                      f'tl.fromTo("#b{j} .dlogo", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: {0.5 * fq:.2f}, ease: "back.out(1.7)" }}, {T(0.7)});'
                      f'tl.fromTo("#b{j} .dpin", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {T(0.95)}); tl.fromTo("#b{j} .dlab", {{ opacity: 0, x: 20 }}, {{ opacity: 1, x: 0, duration: 0.3 }}, {T(1.05)});'
                      f'tl.fromTo("#b{j} .dring", {{ attr: {{ r: 18 }}, opacity: 1 }}, {{ attr: {{ r: 70 }}, opacity: 0, duration: 0.8, repeat: 2, ease: "power2.out" }}, {T(1.05)});')
        elif kind == "africa":  # hook: Africa on the cover frame, DRC in brand blue, the camera falls onto Lubumbashi, then satellite
            polys = json.load(open(f"{SP}/real/drc/africa.json")); sc = 13.2; lon0, lat0 = 17.0, 1.5
            prj = lambda lon, lat: (540 + (lon - lon0) * sc, 930 - (lat - lat0) * sc)
            paths = []
            for pg in polys:
                xs_ = [x for x, y in pg["ring"]]; ys_ = [y for x, y in pg["ring"]]
                if max(xs_) < -30 or min(xs_) > 70 or max(ys_) < -45 or min(ys_) > 45: continue
                d_ = "M" + " L".join(f"{prj(x, y)[0]:.1f},{prj(x, y)[1]:.1f}" for x, y in pg["ring"]) + "Z"
                drc_ = pg["name"].startswith("Dem. Rep. Congo")
                paths.append(f'<path d="{d_}" fill="{"url(#afg%d)" % j if drc_ else "#1a3550"}" stroke="{"#ffffff" if drc_ else "#0b1724"}" stroke-width="{1.6 if drc_ else 1.1}" stroke-linejoin="round"/>')
            lx, ly = prj(27.4793, -11.6647); mid = ba + (bb - ba) * bt.get("swap", 0.62); z0 = ba + bt.get("hold", 0.55)
            scene_html.append(f'<div class="full" id="b{j}" style="background:radial-gradient(90% 60% at 50% 45%,#10283f 0%,#06111b 100%);overflow:hidden">'
                              f'<div class="afm" style="position:absolute;inset:0;transform-origin:{lx:.1f}px {ly:.1f}px">'
                              f'<svg viewBox="0 0 1080 1920" width="1080" height="1920" style="position:absolute;left:0;top:0"><defs><linearGradient id="afg{j}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3aa3e3"/><stop offset="1" stop-color="#1668a8"/></linearGradient></defs>'
                              + "".join(paths) + f'<circle class="afr" cx="{lx:.1f}" cy="{ly:.1f}" r="10" fill="none" stroke="#fff" stroke-width="3"/><circle class="afp" cx="{lx:.1f}" cy="{ly:.1f}" r="6" fill="#fff"/></svg>'
                              f'<div class="afl" style="position:absolute;left:{lx + 18:.0f}px;top:{ly - 18:.0f}px;color:#fff;font-weight:700;font-size:26px;text-shadow:0 2px 10px rgba(0,0,0,.5)">Lubumbashi</div></div>'
                              f'<img class="afs bg" src="assets/img/aerial.jpg" alt="" style="opacity:0"><div class="credit" style="opacity:1">Imagerie © Esri, Maxar</div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.05); tl.fromTo("#b{j} .afm", {{ scale: 1.0 }}, {{ scale: 1.08, duration: {z0 - ba:.3f}, ease: "none" }}, {ba});'
                      f'tl.fromTo("#b{j} .afr", {{ attr: {{ r: 10 }}, opacity: 1 }}, {{ attr: {{ r: 46 }}, opacity: 0, duration: 0.7, repeat: 1, ease: "power2.out" }}, {ba});'
                      f'tl.to("#b{j} .afm", {{ scale: 70, duration: {mid - z0 + 0.35:.3f}, ease: "power3.in" }}, {z0:.3f}); tl.to("#b{j} .afl", {{ opacity: 0, duration: 0.15 }}, {z0 + 0.1:.3f});'
                      f'tl.to("#b{j} .afp, #b{j} .afr", {{ opacity: 0, duration: 0.12 }}, {z0 + 0.25:.3f}); tl.to("#b{j} .afm", {{ opacity: 0, duration: 0.3 }}, {mid - 0.3:.3f});'
                      f'tl.fromTo("#b{j} .afs", {{ opacity: 0, scale: 2.4, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1.25, filter: "blur(0px)", duration: {bb - mid + 0.35:.3f}, ease: "power2.out" }}, {mid - 0.35:.3f});')
        elif kind == "dive":  # hook: camera already moving, falls from the DRC map onto Lubumbashi, then into satellite imagery
            import math
            ring = json.load(open(f"{SP}/real/drc/drc.json"))[0]; k0 = math.cos(math.radians(4))
            xs = [x * k0 for x, y in ring]; ys = [-y for x, y in ring]; sc = 880 / (max(xs) - min(xs))
            ox, oy = 540 - (max(xs) + min(xs)) / 2 * sc, 930 - (max(ys) + min(ys)) / 2 * sc
            prj = lambda lon, lat: (lon * k0 * sc + ox, -lat * sc + oy)
            dd = "M" + " L".join(f"{prj(x, y)[0]:.1f},{prj(x, y)[1]:.1f}" for x, y in ring) + "Z"
            lx, ly = prj(27.4793, -11.6647); mid = ba + (bb - ba) * bt.get("swap", 0.5)
            scene_html.append(f'<div class="full" id="b{j}" style="background:#06111b;overflow:hidden">'
                              f'<div class="dvm" style="position:absolute;inset:0;transform-origin:{lx:.0f}px {ly:.0f}px">'
                              f'<svg viewBox="0 0 1080 1920" width="1080" height="1920" style="position:absolute;left:0;top:0"><defs><linearGradient id="dvg{j}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3aa3e3"/><stop offset="1" stop-color="#1668a8"/></linearGradient></defs>'
                              f'<path d="{dd}" fill="url(#dvg{j})"/><circle class="dvl" cx="{lx:.0f}" cy="{ly:.0f}" r="9" fill="#fff"/></svg>'
                              f'<div class="dvl" style="position:absolute;right:{1080 - lx + 22:.0f}px;top:{ly - 20:.0f}px;color:#fff;font-weight:700;font-size:28px">Lubumbashi</div></div>'
                              f'<img class="dvs bg" src="assets/img/aerial.jpg" alt="" style="opacity:0"><div class="credit" style="opacity:1">Imagerie © Esri, Maxar</div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.05); tl.fromTo("#b{j} .dvm", {{ scale: 1.25 }}, {{ scale: 14, duration: {mid - ba + 0.25:.3f}, ease: "power3.in" }}, {ba});'
                      f'tl.to("#b{j} .dvl", {{ opacity: 0, duration: 0.2 }}, {ba + 0.25:.3f}); tl.to("#b{j} .dvm", {{ opacity: 0, duration: 0.3 }}, {mid - 0.1:.3f});'
                      f'tl.fromTo("#b{j} .dvs", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1.25, duration: {bb - mid:.3f}, ease: "power2.out" }}, {mid - 0.12:.3f});'
                      f'tl.fromTo("#b{j} .dvs", {{ filter: "blur(10px)" }}, {{ filter: "blur(0px)", duration: 0.45 }}, {mid - 0.12:.3f});')
        elif kind == "flag":
            scene_html.append(f'<div class="full" id="b{j}"><img class="bg" src="assets/img/aerial.jpg" alt=""><div style="position:absolute;inset:0;background:rgba(0,0,0,.25)"></div>'
                              f'<div class="flag"><svg viewBox="0 0 800 600" width="700" height="525"><rect width="800" height="600" fill="#007FFF"/><polygon points="0,510 680,0 800,0 800,90 120,600 0,600" fill="#F7D618"/><polygon points="0,555 740,0 800,0 800,45 60,600 0,600" fill="#CE1021"/><polygon points="150,40 172,108 244,108 186,150 208,218 150,176 92,218 114,150 56,108 128,108" fill="#F7D618"/></svg></div><div class="credit" style="opacity:1">Imagerie © Esri, Maxar</div></div>')
            js.append(f'show("#b{j}", {ba}, {bb}, 0.3); tl.fromTo("#b{j} .flag", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.5)" }}, {ba + 0.2});')
        if bt.get("cap"):
            cls = {"glass": "cap gcap", "city": "cap ccap", "kin": "cap kcap"}.get(STYLE, "cap")
            scene_html.append(f'<div class="{cls}" id="c{j}" style="top:{bt.get("cap_top", 1560)}px"><span>{bt["cap"]}</span></div>'); js.append(f'cap("#c{j}", {ba}, {bb});')
        if bt.get("big"):
            if ba < 0.01:   # opening beat: the word is on the cover frame already
                scene_html.append(f'<div class="bigtxt" id="g{j}" style="opacity:1">{bt["big"]}</div>'); js.append(f'tl.set("#g{j}", {{ opacity: 0 }}, {bb});')
            else:
                scene_html.append(f'<div class="bigtxt" id="g{j}">{bt["big"]}</div>'); js.append(f'tl.fromTo("#g{j}", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.8)" }}, {ba + 0.05}); tl.set("#g{j}", {{ opacity: 0 }}, {bb});')

SW, SH = 520, 1126
slabs = "".join(f'<div class="slab{" back" if k == 20 else ""}" style="transform:translateZ(-{k}px)">' + ("" if k in (1, 20) else '<i class="btn" style="left:-5px;top:280px;height:64px"></i><i class="btn" style="left:-5px;top:370px;height:110px"></i><i class="btn" style="right:-5px;top:400px;height:160px"></i>') + '</div>' for k in range(20, 0, -1))
lv = "".join(f'<video id="lv{k}" class="clip lv" src="assets/v/{c}.mp4" muted playsinline data-start="{a:.3f}" data-duration="{min(5.0, b - a):.3f}" data-track-index="{8 + k % 2}"></video>' for k, (a, b, c, s7) in enumerate(PW) if s7)
pv = "".join(f'<video id="pv{k}" class="clip pv" src="assets/v/{LAPPH.get(a, "ph_swipe") if s7 else c}.mp4" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{5 + k % 2}"></video>' for k, (a, b, c, s7) in enumerate(PW))
html = f'''<!doctype html>
<html lang="fr"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><script src="assets/gsap.min.js"></script>
<style>{css}
.vid {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
#scene {{ z-index: 8; background: transparent !important; }}
.full {{ position: absolute; inset: 0; opacity: 0; overflow: hidden; }}
.full img.bg {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
.full .cut {{ position: absolute; left: 140px; right: 140px; top: 640px; width: 800px; height: 860px; object-fit: contain; filter: drop-shadow(0 40px 34px rgba(0,0,0,.3)); }}
 .vsl, .vsr {{ position: absolute; top: 0; bottom: 0; width: 540px; overflow: hidden; }} .vsl {{ left: 0; }} .vsr {{ right: 0; }}
.vsl img, .vsr img {{ position: absolute; left: 35px; top: 600px; width: 470px; height: 700px; object-fit: contain; filter: drop-shadow(0 30px 26px rgba(0,0,0,.28)); }}
.vsl b, .vsr b {{ position: absolute; left: 20px; right: 20px; top: 1350px; text-align: center; font-weight: 800; font-size: 56px; letter-spacing: -1.5px; color: #111214; line-height: 1.05; }}
.vsou {{ position: absolute; left: 430px; top: 830px; width: 220px; height: 220px; border-radius: 50%; background: #1f88c9; color: #fff; font-weight: 800; font-size: 86px; display: flex; align-items: center; justify-content: center; box-shadow: 0 20px 50px rgba(31,136,201,.45); border: 8px solid #fff; }}
.shopbg {{ filter: blur(26px) brightness(.5) saturate(1.2); }} .shopdim {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,14,22,.25), rgba(8,14,22,.75)); }}
.slogo {{ position: absolute; left: 400px; top: 430px; width: 280px; height: 280px; border-radius: 50%; object-fit: cover; border: 8px solid #fff; box-shadow: 0 30px 60px rgba(0,0,0,.4); }}
.sname {{ position: absolute; left: 40px; right: 40px; top: 760px; text-align: center; color: #fff; font-weight: 800; font-size: 96px; letter-spacing: -3px; line-height: 1; }}
.ssub {{ position: absolute; left: 40px; right: 40px; top: 880px; text-align: center; color: #cfe9fb; font-weight: 600; font-size: 46px; }}
.sp {{ position: absolute; top: 1040px; width: 300px; height: 380px; object-fit: cover; border-radius: 28px; border: 6px solid #fff; box-shadow: 0 24px 50px rgba(0,0,0,.4); }}
.sp0 {{ left: 60px; transform: rotate(-4deg); }} .sp1 {{ left: 390px; top: 1010px; }} .sp2 {{ left: 720px; transform: rotate(4deg); }}
.zimg {{ position: absolute; left: 90px; top: 460px; width: 900px; height: 1000px; object-fit: contain; }}
.zq {{ position: absolute; left: 0; right: 0; top: 760px; text-align: center; font-weight: 800; font-size: 360px; color: #fff; text-shadow: 0 10px 60px rgba(0,0,0,.35); }}
 .kt {{ position: absolute; left: 80px; right: 80px; top: 50%; transform: translateY(-50%); text-align: center; font-weight: 800; letter-spacing: -4px; line-height: 1.05; }}
.ktw {{ display: inline-block; }} .kta {{ color: #1f88c9; }}
.ktsub {{ position: absolute; left: 80px; right: 80px; top: 62%; text-align: center; font-weight: 600; font-size: 46px; color: #5b6570; }}
.pcard {{ position: absolute; background: #fff; border-radius: 40px; padding: 18px 18px 26px; box-shadow: 0 30px 60px rgba(17,18,20,.14); overflow: hidden; }}
.pcard img {{ display: block; width: 100%; object-fit: cover; border-radius: 26px; }}
.pcard b {{ display: block; margin-top: 18px; text-align: center; font-weight: 700; font-size: 40px; color: #111214; letter-spacing: -1px; }}
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
.gl {{ position: absolute; left: 60px; right: 60px; top: 330px; padding: 34px 44px 40px; border-radius: 44px; z-index: 9; opacity: 0;
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
#lscreen .lv {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
#lscreen .hd2 {{ position: absolute; left: 0; top: 0; width: 916px; z-index: 2; }}
#lscreen .body {{ position: absolute; left: 0; top: 41px; width: 916px; }}
#deck {{ position: relative; width: 1060px; height: 34px; margin-left: -50px; border-radius: 0 0 26px 26px; background: linear-gradient(180deg, #d9dce0, #9ea2a8); box-shadow: 0 30px 50px rgba(0,0,0,.35); }}
#deck i {{ position: absolute; left: 50%; top: 0; width: 170px; height: 10px; margin-left: -85px; border-radius: 0 0 10px 10px; background: #8d9196; }}
{NOPLATE}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/bgm.wav" data-start="0" data-duration="{DUR:.3f}" data-track-index="11"></audio>
{"".join(vids)}
{"".join(root_html)}
<div id="pbg"></div>
<div id="lapstage"><div id="lap"><div id="lid"><div id="lscreen">{lv}</div></div><div id="deck"><i></i></div></div></div>
<div id="pshadow"></div>
<div id="stage"><div id="phone">{slabs}<div id="front"><div id="screen"><div id="island"></div><div id="glare"></div>{pv}</div></div></div></div>
<div id="scene" class="clip layer" data-start="0" data-duration="{DUR:.3f}" data-track-index="0"><div id="cam">
{"".join(scene_html)}
<div class="shade" id="shade"></div>
{end_html}
</div>
<div id="anchor"><img id="anchorIcon" src="assets/icon_white.png" alt="" /><span id="anchorTxt" style="color:#fff">PitUp · Lubumbashi</span></div>
<div id="flash"></div><div id="vignette" style="opacity:1"></div><div id="grain"></div></div>
</div>
<script>
const END = {END}, DUR = {DUR};
const tl = gsap.timeline({{ paused: true }});
const show = (sel, a, b, fade = 0.25) => {{ if (a < 0.01) gsap.set(sel, {{ opacity: 1 }}); else tl.fromTo(sel, {{ opacity: 0 }}, {{ opacity: 1, duration: fade, ease: "power1.out" }}, a); tl.set(sel, {{ opacity: 0 }}, b); }};
const hd = (sel, a, b) => {{ tl.fromTo(sel, {{ opacity: 0, yPercent: 25 }}, {{ opacity: 1, yPercent: 0, duration: 0.45, ease: "power3.out" }}, a + 0.05); tl.set(sel, {{ opacity: 0 }}, b); }};
const cap = (sel, a, b) => {{ tl.fromTo(sel, {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, a + 0.05); tl.set(sel, {{ opacity: 0 }}, b); }};
tl.set("#shade", {{ opacity: {0 if STYLE in ("kin", "city") else 1} }}, 0); tl.set("#shade", {{ opacity: 0 }}, END);
{"".join(f'tl.set("#shade, #vignette", {{ opacity: 0 }}, {la}); tl.set("#shade", {{ opacity: {0 if STYLE in ("kin", "city") else 1} }}, {lb}); tl.set("#vignette", {{ opacity: 1 }}, {lb}); tl.set("#anchor", {{ filter: "invert(1)" }}, {la}); tl.set("#anchor", {{ filter: "none" }}, {lb});' for la, lb in LIGHT)}
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
