# PitUp "duo" motion (27 Nov. 2026): the founder's whole product palette, a dialogue between the sister's voice and
# the young man's voice, a light background with the flat PitUp logo melted into it.
# Founder feedback on the depth version: "C'est trop peu" — show many of his products, make the girl's voice heard
# (with the boy, mixed), no dark background and no 3D-looking logo ("rendu typique IA"), take hook, copy and text
# animation ideas from his references (r9: a question about a real problem written word by word; r5: one word at a
# time with a key word in colour; r1/r2: words that arrive with the voice).
# Input: audio/duo/place.json (picked takes: [{"who","file","words":[[w,s,e],...]}] in script order).
# Music: Dave & Tems "Raindance" (new), vocals removed by demucs. Real camera click on every other scene change.
import json, os, shutil, subprocess, numpy as np, soundfile as sf
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-duo"; A = f"{P}/assets"; CL = f"{SP}/hf/videos/pitup-clean/assets"; sr = 48000
os.makedirs(P, exist_ok=True)
if os.path.isdir(A): shutil.rmtree(A)
shutil.copytree(CL, A, ignore=shutil.ignore_patterns("mix.wav"))
for f in ["lb_minibus", "lb_tour", "lb_avenue2"]: shutil.copy(f"{SP}/inbox/rj/{f}.jpg", f"{A}/img/{f}.jpg")
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/build_clean.py").read()                  # the PitUp product window and its CSS
ns = {}; exec(src[src.index("ICO = {"):src.index("CARD0 = ")], ns)
ICO, fiche = ns["ICO"], ns["fiche"]
CARD_CSS = src[src.index(".card{{position:absolute;"):src.index(".ics{{")].replace("{{", "{").replace("}}", "}")

# ---- the founder's products (his 8 + his 11), with the category the voice names
REF = ["am95corteiz", "am95galets", "am95gris", "robe", "robes9", "rolex", "samba", "tees4"]
REF2 = ["cardigans", "mocassins_cuir", "mocassins_daim", "nb1906", "nb9060", "polos_col", "polos_zip", "pull_rl", "pulls_rl", "pulls_rl2", "timberland"]
for f in REF: shutil.copy(f"{SP}/appimg/ref/{f}.jpg", f"{A}/img/p_{f}.jpg")
for f in REF2: shutil.copy(f"{SP}/appimg/ref2/{f}.jpg", f"{A}/img/p_{f}.jpg")
CAT = {"baskets": ["am95corteiz", "am95galets", "am95gris", "samba", "nb1906", "nb9060"],
       "pulls": ["pull_rl", "pulls_rl", "pulls_rl2", "cardigans", "polos_col", "polos_zip"],
       "mocassins": ["mocassins_cuir", "mocassins_daim"], "montres": ["rolex"]}
catof = {p: c for c, ps in CAT.items() for p in ps}
ORDER = ["nb9060", "robe", "pull_rl", "rolex", "am95gris", "cardigans", "samba", "mocassins_daim", "tees4", "polos_zip",
         "timberland", "am95corteiz", "pulls_rl", "robes9", "mocassins_cuir", "nb1906", "polos_col", "am95galets", "pulls_rl2"]
WALL = ORDER + ORDER[7:] + ORDER[:7]                         # 38 tiles, the same piece never twice in a row
COLS = 4; TW, TH, G = 252, 330, 12

# ---- voice placement
PL = json.load(open(f"{SP}/audio/duo/place.json"))
GAP = [0.0, 0.32, 0.30, 0.34, 0.30, 0.12, 0.26, 0.40]       # silence before each line (a quick back-and-forth)
t = 0.25; LINES = []
for i, L in enumerate(PL):
    t += GAP[i]; w = [[x, round(s + t, 3), round(e + t, 3)] for x, s, e in L["words"]]
    LINES.append({"who": L["who"], "file": L["file"], "t0": t, "words": w}); t += L["words"][-1][2]
D = round(t + 2.6, 2); n = int(D * sr)
st = lambda i: LINES[i]["t0"]
def wt(i, k):                                                 # start of word k of line i
    return LINES[i]["words"][k][1]
def find(i, word):                                            # start of the first word of line i that contains `word`
    for x, s, e in LINES[i]["words"]:
        if word.lower() in x.lower(): return s
    raise KeyError(word)
SC = [st(i) - (0.06 if i else 0.25) for i in range(len(LINES))]   # scene i starts just before its line
SC[5] = st(5) - 0.05

# ---- audio: voices raw, music under them, real camera click on every other scene change
def load(f, ch=1):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
vo = np.zeros(n, np.float32)
for L in LINES:
    v = load(L["file"]); v = v / (np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)) + 1e-9) * 0.12   # same level for every line
    i = int(L["t0"] * sr); vo[i:i + len(v)] += v[:n - i]
BED = os.environ.get("BED", f"{SP}/audio/raindance_inst.wav"); OFF = float(os.environ.get("OFF", "0"))
mus = load(BED, 2).reshape(-1, 2)
mus = mus[int(OFF * sr):int(OFF * sr) + n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))
tt = np.arange(n) / sr; vend = LINES[-1]["words"][-1][2]
gain = np.where(tt < vend + 0.2, 10 ** (-17 / 20), 10 ** (-9 / 20))       # under the voices, then up for the end card
gain = np.convolve(gain, np.ones(int(0.25 * sr)) / int(0.25 * sr), "same")
mus = mus / (np.sqrt(np.mean(mus ** 2)) + 1e-9) * 0.12 * gain[:, None] * np.clip((D - tt) / 1.0, 0, 1)[:, None]
fx = np.zeros(n, np.float32); SH = load(f"{SP}/sfx/mk/1432.mp3")
for x in [SC[1], SC[5], SC[7]]: i = int((x - 0.30) * sr); s = SH[:n - i]; fx[i:i + len(s)] += 0.32 * s
mix = mus + (vo + fx)[:, None]
sf.write(f"{SP}/audio/duo_raw.wav", mix, sr, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/duo_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/duo_raw.wav", "-af", f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{A}/mix.wav"], check=True)

# ---- words: one span per voice word, appearing when it is said
KEY = {"ville": 1, "fini.": 1, "Lubumbashi,": 1, "téléphone.": 1, "commandes…": 1, "livre.": 1, "livraison.": 1}
def words_html(i, cls, skip=0, upto=None, key=(), id=None):
    ws = LINES[i]["words"][skip:upto]
    return f'<div class="tx {cls}" id="{id or f"t{i}"}">' + " ".join(
        f'<span class="wd{" k" if (x in key) else ""}" data-t="{s:.3f}">{x}</span>' for x, s, e in ws) + "</div>"
TILES = []
for k, p in enumerate(WALL):
    c, r = k % COLS, k // COLS
    TILES.append(f'<div class="tile" data-c="{catof.get(p, "")}" data-k="{k}" style="left:{G + c * (TW + G)}px;top:{r * (TH + G)}px">'
                 f'<img src="assets/img/p_{p}.jpg" alt=""></div>')
CITY = [("lb_avenue", -170, -40, -5), ("lb_minibus", 160, 30, 4), ("lb_tour", -120, 150, 3), ("lb_alilac", 150, 220, -3)]
CT = "".join(f'<img class="ph" id="ph{j}" src="assets/img/{f}.jpg" style="left:{540 - 280 + x}px;top:{1160 + y}px;transform:rotate({r}deg)" alt="">'
             for j, (f, x, y, r) in enumerate(CITY))
PILLS = "".join(f'<div class="pill" id="pl{i}">{c}</div>' for i, c in enumerate(CAT))
CYC = ["pull_rl", "mocassins_daim", "rolex", "timberland", "nb9060"]
CY = "".join(f'<img class="cy" src="assets/img/p_{p}.jpg" alt="">' for p in CYC)
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-500.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f5f8fb;font-family:P,sans-serif;color:#0d1b2a}}
.lay{{position:absolute;inset:0}}
#blue{{background:#1f88c9;opacity:0}}
.mark{{position:absolute;width:1500px;height:1690px;-webkit-mask:url(assets/icon_white.png) center/contain no-repeat;mask:url(assets/icon_white.png) center/contain no-repeat}}
#mk1{{left:180px;top:760px;background:#e4eef7}} #mk2{{left:-260px;top:420px;background:#3aa2df;opacity:0}}
#wl{{position:absolute;left:50%;top:96px;width:240px;margin-left:-120px;z-index:30}}
#ww{{position:absolute;left:50%;top:96px;width:240px;margin-left:-120px;z-index:30;opacity:0}}
.tx{{position:absolute;left:90px;right:90px;font-weight:700;letter-spacing:-.04em;line-height:1.08;z-index:20}}
.wd{{display:inline-block;opacity:0}} .k{{color:#1f88c9}}
.onb .k{{color:#bfe3ff}} .onb{{color:#fff}}
#t0{{top:300px;font-size:89px}}
#t1{{top:700px;font-size:144px;text-align:center;left:40px;right:40px}}
#t1b{{top:640px;font-size:89px;text-align:center;left:40px;right:40px}}
#hdr{{position:absolute;left:0;right:0;top:0;height:250px;background:#f5f8fb;z-index:29;opacity:0}}
#t3{{top:250px;font-size:89px;text-align:center;left:60px;right:60px}}
#t4{{top:250px;font-size:89px;text-align:center}}
#t5{{top:760px;font-size:144px;text-align:center;left:40px;right:40px}}
#t6{{top:640px;font-size:144px;text-align:center;left:40px;right:40px}}
.ph{{position:absolute;width:560px;height:400px;object-fit:cover;border-radius:28px;opacity:0;border:10px solid #fff;box-shadow:0 18px 40px rgba(13,40,70,.14)}}
#wall{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;opacity:0}}
.col{{position:absolute;top:0;left:0;width:1080px;height:100%}}
.tile{{position:absolute;width:{TW}px;height:{TH}px;border-radius:26px;overflow:hidden;background:#fff;opacity:0}}
.tile img{{width:100%;height:100%;object-fit:cover}}
#veil{{position:absolute;inset:0;background:#f5f8fb;opacity:0;z-index:10}}
.pill{{position:absolute;left:50%;top:860px;padding:18px 54px 26px;border-radius:999px;background:#1f88c9;color:#fff;font-weight:700;font-size:89px;letter-spacing:-.04em;opacity:0;z-index:25;white-space:nowrap}}
#fc{{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:15}}
#fc .card{{left:130px;top:560px;transform:scale(.86);transform-origin:50% 0}}
.cy{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0}}
{CARD_CSS}
.ico{{position:absolute;left:50%;top:1120px;width:190px;height:190px;margin-left:-95px;z-index:20;opacity:0}}
.ico svg{{width:100%;height:100%;fill:none;stroke:#fff;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}}
#ic6 svg{{stroke:#1f88c9}}
#end{{position:absolute;inset:0;background:#1f88c9;opacity:0;z-index:40;overflow:hidden}}
#mk3{{left:-300px;top:880px;background:#3aa2df}}
#et{{position:absolute;left:390px;top:560px;width:300px;height:300px;display:flex;align-items:center;justify-content:center}} #et img{{width:178px}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
<div class="mark" id="mk1"></div>
<div class="lay" id="blue"><div class="mark" id="mk2"></div></div>
<div id="hdr"></div><img id="wl" src="assets/logo_word_blue.png" alt=""><img id="ww" src="assets/logo_word_white.png" alt="">
{CT}
<div id="wall"><div class="col">{"".join(TILES)}</div></div><div id="veil"></div>
{PILLS}
<div id="fc">{fiche(9, "nb9060", "New Balance 9060")}</div>
{words_html(0, "", key=("ville",))}
{words_html(1, "onb", upto=3, key=("fini.",), id="t1")}{words_html(1, "onb", skip=3, upto=-1, id="t1b")}
{words_html(3, "", key=("Lubumbashi,", "téléphone."))}
{words_html(4, "", key=("commandes…",))}
{words_html(5, "onb", key=("livre.",))}
{words_html(6, "", key=("livraison.",))}
<div class="ico" id="ic5">{ICO["truck"]}</div><div class="ico" id="ic6">{ICO["cash"]}</div>
<div id="end"><div class="mark" id="mk3"></div><div id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const SC={json.dumps([round(x, 3) for x in SC])}, D={D};
// words arrive with the voice (r9 / r5): a short rise, no blur, no glow
document.querySelectorAll(".wd").forEach(w=>{{ const a=+w.dataset.t;
  tl.fromTo(w,{{opacity:0,y:34}},E({{opacity:1,y:0,duration:.22,ease:"power3.out"}}),a-.04); }});
const show=(sel,a,b)=>{{ tl.set(sel,{{opacity:1}},a); if(b!=null) tl.set(sel,{{opacity:0}},b); }};
show("#t0",0,SC[1]); show("#t1",SC[1],{find(1, "Tout"):.3f}-.05); show("#t1b",SC[1],SC[2]); show("#t3",SC[3],SC[4]); show("#t4",SC[4],SC[5]); show("#t5",SC[5],SC[6]); show("#t6",SC[6],SC[7]);
// the flat logo is part of the background: a pale mark that drifts, never lit, never in relief
tl.fromTo("#mk1",{{x:0,y:0}},E({{x:-120,y:-160,duration:D,ease:"none"}}),0);
tl.fromTo("#mk2",{{x:0,y:0}},E({{x:140,y:-120,duration:D,ease:"none"}}),0);
// scene 0: "Tu fais encore le tour de toute la ville…" city photos dealt one by one
{";".join(f'tl.fromTo("#ph{j}",{{opacity:0,y:60,scale:.92}},E({{opacity:1,y:0,scale:1,duration:.3,ease:"power3.out"}}),{t:.3f})'
          for j, t in enumerate([wt(0, 3), find(0, "toute"), find(0, "ville"), find(0, "trouver")]))};
tl.set(".ph",{{opacity:0}},SC[1]);
// scene 1: hard cut to PitUp blue, "Ça, c'est fini. Tout est sur PitUp."
const blueOn=(a,b)=>{{ tl.set("#blue",{{opacity:1}},a); tl.set("#mk2",{{opacity:.55}},a); tl.set("#ww",{{opacity:1}},a); tl.set("#wl",{{opacity:0}},a);
  tl.set("#blue",{{opacity:0}},b); tl.set("#mk2",{{opacity:0}},b); tl.set("#ww",{{opacity:0}},b); tl.set("#wl",{{opacity:1}},b); }};
blueOn(SC[1],SC[2]); blueOn(SC[5],SC[6]);
tl.fromTo("#ww",{{scale:1,y:0}},E({{scale:2.6,y:760,duration:.4,ease:"power3.out"}}),{find(1, "sur"):.3f}+.12);
tl.to("#ww",{{scale:1,y:0,duration:.01}},SC[2]);
// scene 2: the wall of products, all of his pieces; the columns drift in opposite directions
tl.set("#wall",{{opacity:1}},SC[2]); tl.set("#hdr",{{opacity:1}},SC[2]); tl.set("#hdr",{{opacity:0}},SC[5]);
const tiles=[...document.querySelectorAll(".tile")];
tiles.forEach((el,k)=>{{ const c=k%{COLS}, r=Math.floor(k/{COLS});
  tl.fromTo(el,{{opacity:0,scale:.8}},E({{opacity:1,scale:1,duration:.28,ease:"back.out(1.6)"}}),SC[2]+(r*0.045+c*0.03)); }});
// even columns rise, odd columns come down: the wall never stops moving
tiles.forEach((el,k)=>{{ const c=k%{COLS}, up=c%2===0;
  tl.fromTo(el,{{y:up?0:-1100}},E({{y:up?-1100:0,duration:SC[5]-SC[2],ease:"none"}}),SC[2]); }});
// the voice names a category: its pieces stand out, the word sits in a blue pill
const CAT={json.dumps([[c, find(2, c)] for c in CAT])};
CAT.forEach(([c,a],i)=>{{ const nx=i+1<CAT.length?CAT[i+1][1]:SC[3];
  tl.set("#pl"+i,{{opacity:1}},a); tl.set("#pl"+i,{{opacity:0}},nx);
  tl.fromTo("#pl"+i,{{scale:.85,xPercent:-50}},E({{scale:1,xPercent:-50,duration:.25,ease:"back.out(2)"}}),a);
  tiles.forEach(el=>{{ const on=el.dataset.c===c;
    tl.to(el,{{opacity:on?1:.35,scale:on?1.05:1,duration:.15}},a); }}); }});
tiles.forEach(el=>tl.to(el,{{opacity:1,scale:1,duration:.15}},SC[3]));
// scene 3: the wall fades behind the words, then the PitUp product window rises: "dans ton téléphone"
tl.fromTo("#veil",{{opacity:0}},E({{opacity:.86,duration:.3}}),SC[3]);
tl.set("#fc",{{opacity:0,y:1400}},0); tl.set("#fc",{{opacity:1}},SC[3]);
tl.fromTo("#fc",{{y:1400}},E({{y:0,duration:.55,ease:"power3.out"}}),{find(3, "téléphone"):.3f}-.15);
tl.set("#wall",{{opacity:0}},SC[5]); tl.set("#veil",{{opacity:0}},SC[5]); tl.set("#fc",{{opacity:0}},SC[5]);
tl.set("#c9",{{opacity:1}},0);
// scene 4: "Tu choisis" the photo changes fast, "tu commandes" the button is pressed
const cyc=[...document.querySelectorAll("#c9 .cy")];
document.querySelector("#c9 .imgc").append(...cyc);
const ch={find(4, "choisis"):.3f};
cyc.forEach((el,i)=>tl.set(el,{{opacity:1}},ch+i*.11));
tl.fromTo("#c9 .b2",{{scale:1}},E({{scale:.9,duration:.08,yoyo:true,repeat:1}}),{find(4, "commandes"):.3f});
tl.to("#c9 .b2",{{backgroundColor:"#1672ab",duration:.1}},{find(4, "commandes"):.3f});
// scene 5: blue, "On te livre." with a flat truck that crosses
tl.fromTo("#ic5",{{opacity:1,x:-700}},E({{x:0,duration:.45,ease:"power3.out"}}),SC[5]); tl.set("#ic5",{{opacity:0}},SC[6]);
// scene 6: "Tu paies à la livraison."
tl.fromTo("#ic6",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.3,ease:"power3.out"}}),{find(6, "livraison"):.3f}); tl.set("#ic6",{{opacity:0}},SC[7]);
// end: "Allez, télécharge l'appli !"
tl.set("#end",{{opacity:1}},SC[7]);
tl.fromTo("#et",{{scale:.3,rotation:-10}},E({{scale:1,rotation:0,duration:.45,ease:"back.out(2)"}}),SC[7]);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),SC[7]+.25);
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),SC[7]+.5);
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),SC[7]+.8);
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),SC[7]+1.05);
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),SC[7]+1.15);
tl.fromTo("#mk3",{{x:0}},E({{x:120,duration:D-SC[7],ease:"none"}}),SC[7]);
tl.set({{}},{{}},D); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
print("scenes", [round(x, 2) for x in SC], "D", D)
