# PitUp "solo" motion (27 Nov. 2026): the sister's voice alone, kinetic typography at the level of the founder's
# references. Feedback on the duo version: "très nul visuellement… on dirait qu'un gosse l'a fait… regarde ce que les
# autres font" and "une seule voix, celle de la fille… fluidité et articulation".
# What the references do (r2 Luca Radez, r5 marq.now, r1 heyclicky, r9 DataSave):
#   one focal element per frame; one to three words, very large, replaced in place on the voice (mask slide);
#   the first words typed with a cursor; cream background alternating with one strong colour; small editorial labels
#   in the corners; a vertical list of words where the active one is large (r2); clean objects on a plain background.
# Input: audio/solo/place.json ([{"file", "words": [[w, s, e], ...]}] one entry per voice block, in order).
# Music: "Raindance" instrumental (vocals removed). Real camera click on every other background change.
import json, os, re, shutil, subprocess, unicodedata, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-solo"; A = f"{P}/assets"; CL = f"{SP}/hf/videos/pitup-clean/assets"; sr = 48000
os.makedirs(P, exist_ok=True)
if os.path.isdir(A): shutil.rmtree(A)
shutil.copytree(CL, A, ignore=shutil.ignore_patterns("mix.wav"))
os.makedirs(f"{A}/cut", exist_ok=True)
for f in os.listdir(f"{SP}/appimg/cut2"): shutil.copy(f"{SP}/appimg/cut2/{f}", f"{A}/cut/{f}")
shutil.copy(f"{SP}/appimg/ref2/pull_rl.jpg", f"{A}/img/chip_pull.jpg")

# ---- what is said (display spelling), per voice block
BLOCKS = ["Tu fais encore le tour de toute la ville pour trouver tes habits\u00a0? Ça, c'est fini.",
          "Sur PitUp, les boutiques de Lubumbashi sont dans ton téléphone\u00a0: des baskets, des pulls, des mocassins, des montres…",
          "Tu choisis, tu commandes, et on te livre. Et tu paies à la livraison.",
          "Allez, télécharge l'appli\u00a0!"]
DISP = [b.split() for b in BLOCKS]
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)

PL = json.load(open(f"{SP}/audio/solo/place.json"))
GAP = [0.0, 0.45, 0.40, 0.45]
t = 0.30; W = []                                   # W[block] = [[display word, start, end], ...] in film time
for i, L in enumerate(PL):
    t += GAP[i]
    tr = [w for w in L["words"] if norm(w[0])]
    d = DISP[i]
    if len(tr) != len(d):                          # spoken words differ from the script: spread the script over them
        print("! block", i, "word count", len(d), "vs", len(tr))
        s0, e0 = tr[0][1], tr[-1][2]; step = (e0 - s0) / len(d)
        tr = [[x, s0 + k * step, s0 + (k + 1) * step] for k, x in enumerate(d)]
    W.append([[x, round(s + t, 3), round(e + t, 3)] for x, (_, s, e) in zip(d, tr)])
    L["t0"] = t; t += L["words"][-1][2]
D = round(t + 2.4, 2); n = int(D * sr)
w = lambda b, k: W[b][k][1]                        # start of word k of block b
we = lambda b, k: W[b][k][2]

# ---- audio: the voice untouched, music under it, real camera click on every other background change
def load(f, ch=1):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
vo = np.zeros(n, np.float32)
for L in PL:
    f = L["file"] if os.path.isabs(L["file"]) else f"{SP}/{L['file']}"
    v = load(f); assert len(v) > sr * 0.3 and np.abs(v).max() > 0.05, f"voice missing or silent: {f}"
    v = v / (np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)) + 1e-9) * 0.12
    i = int(L["t0"] * sr); vo[i:i + len(v)] += v[:n - i]
BED = os.environ.get("BED", f"{SP}/audio/raindance_inst.wav"); OFF = float(os.environ.get("OFF", "36.873"))
mus = load(BED, 2).reshape(-1, 2)[int(OFF * sr):][:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))
tt = np.arange(n) / sr; vend = W[-1][-1][2]
gain = np.where(tt < vend + 0.2, 10 ** (-17 / 20), 10 ** (-9 / 20))
gain = np.convolve(gain, np.ones(int(0.25 * sr)) / int(0.25 * sr), "same")
mus = mus / (np.sqrt(np.mean(mus ** 2)) + 1e-9) * 0.12 * gain[:, None] * np.clip((D - tt) / 1.0, 0, 1)[:, None]

# ---- scenes (background: c = cream, b = PitUp blue)
BLUE1 = w(0, 13) - 0.08                            # "Ça, c'est fini."
CREAM2 = w(1, 0) - 0.12                            # "Sur PitUp…"
BLUE3 = w(2, 0) - 0.10                             # "Tu choisis…"
CREAM4 = w(2, 7) - 0.10                            # "Et tu paies à la livraison."
END = w(3, 0) - 0.10
CUTS = [BLUE1, CREAM2, BLUE3, CREAM4, END]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in CUTS[::2]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.30 * s
sf.write(f"{SP}/audio/solo_raw.wav", mus + (vo + fx)[:, None], sr, subtype="FLOAT")
def lufs(f):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
TGT = -13.6; g = TGT - lufs(f"{SP}/audio/solo_raw.wav")
for _ in range(4):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/solo_raw.wav", "-af", f"volume={g:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                    "-c:a", "pcm_s16le", f"{A}/mix.wav"], check=True)
    out = lufs(f"{A}/mix.wav")
    if abs(out - TGT) < 0.3: break
    g += TGT - out
print("mix", out, "LUFS")

# ---- kinetic typography: chunks of 1 to 3 words, each word slides up out of a mask when it is said
# (block, first word, last word, size, extra class)
CH = [(0, 0, 2, 144, "typed"), (0, 3, 5, 144, ""), (0, 6, 8, 144, "chipv"), (0, 9, 10, 144, ""), (0, 11, 12, 144, "chiph"),
      (0, 13, 14, 144, "onb"), (0, 15, 15, 233, "onb"),
      (1, 2, 3, 144, ""), (1, 4, 5, 144, ""), (1, 6, 8, 144, ""), (1, 9, 9, 144, ""),
      (2, 0, 1, 144, "onb"), (2, 2, 3, 144, "onb"), (2, 4, 7, 144, "onb"),
      (2, 8, 10, 144, ""), (2, 11, 13, 144, "")]
KEYW = {"ville", "habits", "fini", "lubumbashi", "telephone", "commandes", "livre", "livraison"}
def chunk_end(j):
    b, a, z, *_ = CH[j]
    if j + 1 < len(CH):
        nb, na, *_ = CH[j + 1]
        return min(w(nb, na) - 0.12, we(b, z) + 1.4)
    return END
SPECIAL_END = {6: CREAM2, 10: w(1, 11) - 0.35, 13: CREAM4, 15: END}
html_chunks = []; js = []
for j, (b, a, z, size, cls) in enumerate(CH):
    ws = W[b][a:z + 1]
    end = SPECIAL_END.get(j, chunk_end(j))
    spans = []
    for k, (x, s, e) in enumerate(ws):
        key = " k" if norm(x).rstrip(".,?!:") in KEYW else ""
        chip = ""
        if cls == "chipv" and norm(x) == "ville": chip = '<span class="chip" style="background-image:url(assets/img/lb_avenue.jpg)"></span>'
        if cls == "chiph" and norm(x) == "habits": chip = '<span class="chip" style="background-image:url(assets/img/chip_pull.jpg)"></span>'
        u = '<i class="u"></i>' if (j == 15 and k == len(ws) - 1) else ""
        spans.append(f'{chip}<span class="m"><span class="in{key}" data-t="{s:.3f}">{x}{u}</span></span>')
    html_chunks.append(f'<div class="ch {cls} ch{j}" id="ch{j}" data-a="{ws[0][1]:.3f}" data-e="{end:.3f}" style="font-size:{size}px">{" ".join(spans)}</div>')

# ---- products: the category the voice names, then all of his pieces in a fast flicker
CAT = [("baskets", ["am95gris", "samba", "nb9060", "am95corteiz", "nb1906"]),
       ("pulls", ["pull_rl", "cardigans", "pulls_rl", "polos_zip"]),
       ("mocassins", ["mocassins_daim", "mocassins_cuir"]),
       ("montres", ["rolex"])]
CATW = [w(1, 11), w(1, 13), w(1, 15), w(1, 17)]
ALL = ["timberland", "robe", "pulls_rl2", "am95galets", "tees4", "polos_col", "robes9", "nb9060", "pull_rl", "samba", "rolex", "mocassins_daim"]
CUTI = []; seq = []
for ci, (c, ps) in enumerate(CAT):
    a = CATW[ci]; nx = CATW[ci + 1] if ci + 1 < len(CAT) else we(1, 17)
    step = min(0.16, (nx - a) / len(ps))
    for k, p in enumerate(ps): seq.append((p, a + k * step))
fl0 = we(1, 17) - 0.05
for k, p in enumerate(ALL): seq.append((p, fl0 + k * 0.085))
FLEND = fl0 + len(ALL) * 0.085
seq.append((None, FLEND))
for k, (p, a) in enumerate(seq[:-1]):
    CUTI.append(f'<img class="cut" id="cu{k}" src="assets/cut/{p}.png" data-a="{a:.3f}" data-e="{seq[k + 1][1]:.3f}" alt="">')
LIST = "".join(f'<div class="li" id="li{i}">{c}</div>' for i, (c, _) in enumerate(CAT))

doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-500.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:P,sans-serif;color:#0d1b2a;
  background:radial-gradient(110% 70% at 28% 12%,#ffffff 0%,#efe9dd 72%)}}
#blue{{position:absolute;inset:0;background:#1f88c9;opacity:0}}
#rings{{position:absolute;left:50%;top:50%;width:1800px;height:1800px;margin:-900px 0 0 -900px;border-radius:50%;
  background:repeating-radial-gradient(circle,rgba(58,162,223,0) 0 219px,rgba(58,162,223,.9) 220px 222px);
  -webkit-mask:radial-gradient(circle,#000 30%,transparent 70%);mask:radial-gradient(circle,#000 30%,transparent 70%)}}
.lab{{position:absolute;font-weight:500;font-size:21px;letter-spacing:.22em;text-transform:uppercase;z-index:30}}
.lab.c{{color:rgba(13,27,42,.55)}} .lab.w{{color:rgba(255,255,255,.75);opacity:0}}
#tl{{left:64px;top:84px;display:flex;align-items:center;gap:16px}} #tl i{{width:44px;height:44px;border-radius:12px;background:#1f88c9;display:flex;align-items:center;justify-content:center}}
#tl i img{{width:26px}}
#tr{{right:64px;top:96px}} #bl{{left:64px;bottom:84px}} #br{{right:64px;bottom:84px}}
#tlw{{left:64px;top:84px;display:flex;align-items:center;gap:16px}} #tlw i{{width:44px;height:44px;border-radius:12px;background:#fff;display:flex;align-items:center;justify-content:center}}
#tlw i b{{width:26px;height:29px;background:#1f88c9;-webkit-mask:url(assets/icon_white.png) center/contain no-repeat;mask:url(assets/icon_white.png) center/contain no-repeat}}
#trw{{right:64px;top:96px}} #blw{{left:64px;bottom:84px}} #brw{{right:64px;bottom:84px}}
.ch{{position:absolute;left:40px;right:40px;top:50%;transform:translateY(-50%);text-align:center;font-weight:700;letter-spacing:-.055em;line-height:1.02;z-index:20;opacity:0}}
.ch.top{{top:330px;transform:none}}
.m{{display:inline-block;overflow:hidden;vertical-align:bottom;padding:0 .04em .08em}}
.in{{display:inline-block}} .k{{color:#1f88c9}}
.onb{{color:#fff}} .onb .k{{color:#bfe3ff}}
.chip{{display:inline-block;width:0;height:.62em;border-radius:.31em;background-size:cover;background-position:center;vertical-align:.06em;margin:0 .06em}}
#cur{{position:absolute;width:10px;height:120px;background:#1f88c9;z-index:21;opacity:0}}
#logo{{position:absolute;left:50%;top:50%;width:640px;margin:-145px 0 0 -320px;opacity:0;z-index:20}}
#sur{{position:absolute;left:0;right:0;top:600px;text-align:center;font-weight:700;font-size:144px;letter-spacing:-.055em;opacity:0;z-index:20}}
#prod{{position:absolute;left:90px;right:90px;top:300px;height:880px;z-index:15}}
.cut{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:contain;opacity:0}}
#list{{position:absolute;left:0;right:0;top:1290px;height:420px;overflow:hidden;z-index:20;opacity:0;
  -webkit-mask:linear-gradient(transparent,#000 30%,#000 70%,transparent);mask:linear-gradient(transparent,#000 30%,#000 70%,transparent)}}
#lw{{position:absolute;left:0;right:0;top:0}}
.li{{height:140px;line-height:140px;text-align:center;font-weight:700;font-size:144px;letter-spacing:-.055em;transform:scale(.38);opacity:.25;transform-origin:50% 50%}}
#dot{{position:absolute;left:150px;top:1490px;width:22px;height:22px;border-radius:50%;background:#1f88c9;opacity:0;z-index:21}}
.in{{position:relative}} .u{{position:absolute;left:.02em;right:.12em;bottom:.02em;height:.07em;border-radius:.04em;background:#1f88c9;transform:scaleX(0);transform-origin:0 50%}}
.ch15 .m{{padding-bottom:.14em}}
#end{{position:absolute;inset:0;background:#1f88c9;opacity:0;z-index:40;overflow:hidden}}
#end #rings2{{position:absolute;left:50%;top:44%;width:1800px;height:1800px;margin:-900px 0 0 -900px;border-radius:50%;
  background:repeating-radial-gradient(circle,rgba(58,162,223,0) 0 219px,rgba(58,162,223,.9) 220px 222px);
  -webkit-mask:radial-gradient(circle,#000 30%,transparent 70%);mask:radial-gradient(circle,#000 30%,transparent 70%)}}
#et{{position:absolute;left:390px;top:560px;width:300px;height:300px;display:flex;align-items:center;justify-content:center}} #et img{{width:178px}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div id="blue"><div id="rings"></div></div>
<div class="lab c" id="tl"><i><img src="assets/icon_white.png" alt=""></i>PitUp</div><div class="lab c" id="tr">Lubumbashi — RDC</div>
<div class="lab c" id="bl">Boutiques locales</div><div class="lab c" id="br">pi-tup.com</div>
<div class="lab w" id="tlw"><i><b></b></i>PitUp</div><div class="lab w" id="trw">Lubumbashi — RDC</div>
<div class="lab w" id="blw">Livraison</div><div class="lab w" id="brw">pi-tup.com</div>
{"".join(html_chunks)}<div id="cur"></div>
<div id="sur">Sur</div><img id="logo" src="assets/logo_word_blue.png" alt="">
<div id="prod">{"".join(CUTI)}</div>
<div id="list"><div id="lw">{LIST}</div></div>
<div id="end"><div id="rings2"></div><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const CUTS={json.dumps([round(x, 3) for x in CUTS])}, D={D};
// backgrounds: cream, PitUp blue with thin rings (r2), and the matching corner labels
const bg=(on,a,b)=>{{ tl.set("#blue",{{opacity:on}},a); tl.set(".lab.c",{{opacity:1-on}},a); tl.set(".lab.w",{{opacity:on}},a); }};
bg(1,CUTS[0]); bg(0,CUTS[1]); bg(1,CUTS[2]); bg(0,CUTS[3]);
tl.fromTo("#rings",{{scale:.9,rotation:0}},E({{scale:1.12,rotation:8,duration:D,ease:"none"}}),0);
tl.fromTo(".lab.c",{{opacity:0}},E({{opacity:1,duration:.5}}),0);
// chunks: each word slides up out of its mask when it is said; the chunk leaves upwards
document.querySelectorAll(".ch").forEach(ch=>{{ const a=+ch.dataset.a, e=+ch.dataset.e;
  tl.set(ch,{{opacity:1}},a-.05); tl.set(ch,{{opacity:0}},e);
  const ins=[...ch.querySelectorAll(".in")];
  if(!ch.classList.contains("typed")) ins.forEach(el=>tl.fromTo(el,{{yPercent:110}},E({{yPercent:0,duration:.42,ease:"expo.out"}}),+el.dataset.t-.06));
  tl.to(ins,{{yPercent:-110,duration:.22,ease:"power3.in",stagger:.02}},e-.24);
  ch.querySelectorAll(".chip").forEach(c=>{{ const t0=+c.nextElementSibling.firstElementChild.dataset.t;
    tl.fromTo(c,{{width:0}},E({{width:"1.25em",duration:.45,ease:"expo.out"}}),t0-.1); }});
}});
// the first words are typed with a blue cursor (r1, r2)
(()=>{{ const ch=document.querySelector(".ch.typed"), ins=[...ch.querySelectorAll(".in")];
  const words=ins.map(el=>[el,el.textContent,+el.dataset.t]); const nx={W[0][3][1]:.3f};
  words.forEach(([el,txt,t0],i)=>{{ const t1=i+1<words.length?words[i+1][2]:Math.min(nx-.1,t0+.4);
    const o={{n:0}}; el.textContent="";
    tl.fromTo(o,{{n:0}},E({{n:txt.length,duration:Math.max(.12,(t1-t0)*.85),ease:"none",
      onUpdate:()=>{{ el.textContent=txt.slice(0,Math.round(o.n)); }}, modifiers:{{n:(v)=>{{ el.textContent=txt.slice(0,Math.round(+v)); return v; }}}}}}),t0);
  }});
  tl.set("#cur",{{opacity:1}},0); tl.set("#cur",{{opacity:0}},+ch.dataset.e);
  const place=()=>{{ const r=ch.getBoundingClientRect(), last=ins.filter(x=>x.textContent).pop()||ins[0], q=last.getBoundingClientRect();
    const root=document.getElementById("root").getBoundingClientRect(), s=root.width/1080;
    gsap.set("#cur",{{left:(q.right-root.left)/s+8,top:(r.top-root.top)/s+(r.height/s-120)/2}}); }};
  const ck={{t:0}}; tl.fromTo(ck,{{t:0}},{{t:1,duration:+ch.dataset.e,ease:"none",immediateRender:false,modifiers:{{t:(v)=>{{ place(); return v; }}}}}},0);
  for(let b=0;b<+ch.dataset.e;b+=.5) tl.set("#cur",{{autoAlpha:(Math.floor(b/.5)%2&&b>{W[0][2][2]:.3f})?0:1}},b);
}})();
// "Sur PitUp": the word, then the flat logo arrives in place of the name
tl.set("#sur",{{opacity:1}},{w(1, 0) - 0.05:.3f}); tl.fromTo("#sur",{{yPercent:60,opacity:0}},E({{yPercent:0,opacity:1,duration:.35,ease:"expo.out"}}),{w(1, 0) - 0.05:.3f});
tl.fromTo("#logo",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{w(1, 1) - 0.05:.3f});
tl.to(["#sur","#logo"],{{opacity:0,y:-60,duration:.22,ease:"power3.in"}},{w(1, 2) - 0.25:.3f});
// products: the cut-outs follow the voice, then all of his pieces flicker (r1, r6)
document.querySelectorAll(".cut").forEach(el=>{{ tl.set(el,{{opacity:1}},+el.dataset.a); tl.set(el,{{opacity:0}},+el.dataset.e); }});
tl.fromTo("#prod",{{scale:.92}},E({{scale:1,duration:{FLEND - CATW[0]:.3f},ease:"none"}}),{CATW[0]:.3f});
// the list of categories turns like r2's word wheel: the one said is large and dark
tl.set("#list",{{opacity:1}},{CATW[0] - 0.3:.3f}); tl.set("#list",{{opacity:0}},{FLEND:.3f});
tl.set("#dot",{{opacity:1}},{CATW[0] - 0.3:.3f}); tl.set("#dot",{{opacity:0}},{FLEND:.3f});
const CW={json.dumps([round(x, 3) for x in CATW])};
tl.set("#lw",{{y:140}},0);
CW.forEach((a,i)=>{{ tl.to("#lw",{{y:140-i*140,duration:.32,ease:"power3.inOut"}},a-.18);
  document.querySelectorAll(".li").forEach((el,j)=>tl.to(el,{{scale:j===i?1:.38,opacity:j===i?1:.25,duration:.32,ease:"power3.inOut"}},a-.18)); }});
// "à la livraison.": a blue line draws under it
tl.to("#ch15 .u",{{scaleX:1,duration:.5,ease:"expo.out"}},{we(2, 13) - 0.2:.3f});
// end: "Allez, télécharge l'appli !"
tl.set("#end",{{opacity:1}},{END:.3f});
tl.fromTo("#et",{{scale:.3,rotation:-10}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),{END:.3f});
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{END + 0.25:.3f});
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{END + 0.5:.3f});
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),{END + 0.8:.3f});
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),{END + 1.0:.3f});
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),{END + 1.1:.3f});
tl.fromTo("#rings2",{{scale:.9}},E({{scale:1.1,duration:{D - END:.3f},ease:"none"}}),{END:.3f});
tl.set({{}},{{}},D); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
print("cuts", [round(x, 2) for x in CUTS], "flicker end", round(FLEND, 2), "D", D)
