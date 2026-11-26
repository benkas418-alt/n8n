# PitUp presenter video (25-26 Nov. 2026): a collaborator shows a jersey and two pairs of sneakers, his cloned voice (v3).
# Hook: he walks to the lens and covers it, the 2D PitUp logo grows out of the black (logo sound), all in about 3 s.
# Full-screen graded rushes, hard cuts, 1-3 white words at a time on a dark top gradient.
# Only three sounds (founder, 19 Nov.): whoosh on cuts 1 and 4, real camera shutter + flash on 2 cuts, logo chime.
# End: he covers the lens again, logo + wordmark + tagline, "Disponible sur" above the store badges.
# usage: build_gh.py   (env BED=<music wav> MUS_DB=-17 LOGO_DB=-8 for the music; without BED: voice and sounds only)
import json, os, subprocess, numpy as np, soundfile as sf, librosa
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
P = f"{SP}/hf/videos/pitup-gh"; A = f"{SP}/audio/gh/v3"; sr = 48000
W = {int(k): v for k, v in json.load(open(f"{A}/words.json")).items()}
V = {i: librosa.load(f"{A}/{i}.wav", sr=sr)[0] for i in range(3)}

def cut_at(i, t, win=0.12):   # quietest 10 ms frame near t, so a cut never falls inside a syllable
    y = V[i]; a, b = int(max(0, t - win) * sr), int(min(len(y) / sr, t + win) * sr); h = int(0.01 * sr)
    e = [np.sqrt(np.mean(y[j:j + h] ** 2)) for j in range(a, b - h, h // 2)]
    return (a + int(np.argmin(e)) * (h // 2) + h // 2) / sr

def wd(i, word, k=0, after=0.0):   # whisper word start in voice file i, searched after a file time
    return [w for w in W[i] if w[1] >= after - 0.05 and w[0].lower().strip(",.?!'-").startswith(word.lower())][k][1]

# voice pieces: (name, file, start, end, silence before)
c = lambda i, t: round(cut_at(i, t), 3)
PIECES = [("A1", 0, 0.0, c(0, 1.68), 0.05), ("A2", 0, c(0, 1.68), c(0, 2.68), 0.08), ("A3", 0, c(0, 2.68), c(0, 3.76), 0.05),
          ("B", 0, c(0, 3.76), c(0, 5.55), 0.80), ("C", 0, c(0, 5.55), len(V[0]) / sr, 0.12),
          ("D", 1, 0.0, c(1, 2.17), 0.16), ("E", 1, c(1, 2.17), len(V[1]) / sr, 0.14),
          ("F1", 2, 0.0, c(2, 0.78), 0.10), ("F2", 2, c(2, 0.78), c(2, 3.40), 0.16), ("G", 2, c(2, 3.40), len(V[2]) / sr, 0.16)]
voice, place, t = [], {}, 0.0
for name, i, a, b, gap in PIECES:
    y = V[i][int(a * sr):int(b * sr)].copy()
    e = np.abs(y); th = 0.03 * e.max(); idx = np.where(e > th)[0]
    s0, s1 = max(0, idx[0] - int(0.04 * sr)), min(len(y), idx[-1] + int(0.09 * sr))
    y = y[s0:s1]; f = int(0.008 * sr); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    t += gap; place[name] = (round(t, 3), round(t + len(y) / sr, 3), i, a + s0 / sr)   # (start, end, file, file time at start)
    voice.append((t, y)); t += len(y) / sr
def at(name, word=None, k=0):   # timeline time of a piece start or of a word inside it
    s, e, i, f0 = place[name]
    return s if word is None else round(s + wd(i, word, k, f0) - f0, 3)

LOGO0 = place["A3"][1] + 0.02            # the lens is covered: logo grows out of the black
CUT1 = at("B") - 0.08                    # logo -> jersey (whoosh)
END0 = place["G"][1] + 0.12              # second lens cover -> end card
D = round(END0 + 2.9, 2); n = int(D * sr)
# shots: (clip, timeline start, timeline end, clip time at start, entry)
CUTS = [CUT1, at("C") - 0.06, at("D") - 0.06, at("E") - 0.06, at("F2") - 0.06]
HOOK_BLACK = 3.07; CLOSE2_BLACK = 2.93   # frame where the hand fully covers the lens in each clip
SHOTS = [("hook", 0.0, LOGO0, HOOK_BLACK - LOGO0, "cut"), ("maillot2", CUTS[0], CUTS[1], 0.85, "cut"),
         ("blanches", CUTS[1], CUTS[2], 0.7, "flash"), ("noires", CUTS[2], CUTS[3], 0.1, "flash"),
         ("laptop", CUTS[3], CUTS[4], 0.4, "cut"), ("close", CUTS[4], at("G") - 0.06, 0.05, "cut"),
         ("close2", at("G") - 0.06, END0, CLOSE2_BLACK - (END0 - (at("G") - 0.06)), "cut")]
WHOOSH_AT = [CUTS[0], CUTS[3]]           # cuts 1 and 4
FLASH_AT = [CUTS[1], CUTS[2]]            # the two sneaker reveals
# words on screen: (start, html); each stays until the next one, <a> = light blue accent
WORDS = [(at("A1"), "Yo les gars !"), (at("A2"), "Attendez…"), (at("A3"), "Regardez ça !"),
         (at("B"), "Un maillot"), (at("B", "tout"), "tout <a>propre.</a>"),
         (at("C"), "Des baskets<br>blanches"), (at("C", "bien"), "bien <a>clean.</a>"),
         (at("D"), "Et celles-là ?"), (at("D", "lourdes") - 0.12, "<a>Lourdes !</a>"),
         (at("E"), "C'est sur<br><a>PitUp</a>"), (at("F1"), "Tu commandes,"), (at("F2"), "on te livre,"),
         (at("F2", "tu"), "<a>Paiement</a><br>à la livraison"),   # the one buyer benefit, as the founder's validated card
         (at("G"), "Allez,"), (at("G", "télécharge"), "télécharge<br><a>l'appli</a>"), (at("G", "on"), "On se capte !")]
WORD_END = [w[0] for w in WORDS[1:]] + [END0]
for k, (a, h) in enumerate(WORDS):   # nothing on screen during the hook logo
    if a < LOGO0 <= WORD_END[k]: WORD_END[k] = LOGO0

# ---------------------------------------------------------------- audio
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                                        capture_output=True).stdout, np.float32)
vox = np.zeros(n, np.float32)
for s, y in voice:
    y = y * (10 ** (-18 / 20) / max(1e-6, np.sqrt(np.mean(y[np.abs(y) > 0.02] ** 2)))); i = int(s * sr); vox[i:i + len(y)] += y[:n - i]
fx = np.zeros(n, np.float32)
def add(t0, s, g):
    i = int(t0 * sr); s = s[:max(0, n - i)]; fx[i:i + len(s)] += g * s
MK = f"{SP}/sfx/mk"; WH, SH, LG = load(f"{MK}/1491.mp3"), load(f"{MK}/1432.mp3"), load(f"{MK}/2573.mp3")
for x in WHOOSH_AT: add(x - 0.30, WH, 0.45)          # whoosh peak sits 0.30 s into the file
for x in FLASH_AT: add(x - 0.30, SH, 0.80)           # shutter peak at 0.31 s
add(LOGO0 - 0.10, LG, 0.55); add(END0 - 0.10, LG, 0.55)
mix = vox + fx
BED = os.environ.get("BED")
if BED:   # music low under the voice, rises on the end logo, full once the voice is over
    mus = load(BED)[:n]; mus = np.pad(mus, (0, n - len(mus))); tt = np.arange(n) / sr
    up = np.clip((tt - END0) / 0.4, 0, 1)
    g = float(os.environ.get("MUS_DB", "-17")) * (1 - up) + float(os.environ.get("LOGO_DB", "-6")) * up
    mix = mix + mus * 10 ** (g / 20)
sf.write(f"{SP}/audio/gh_raw.wav", np.stack([mix, mix], 1), sr, subtype="FLOAT")   # measure loudness on the stereo file
meas = subprocess.run(["ffmpeg", "-i", f"{SP}/audio/gh_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
Iin = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SP}/audio/gh_raw.wav", "-af",
                f"volume={-14 - Iin:.2f}dB,aresample=192000,alimiter=limit=0.8:level=0,aresample=48000",
                "-c:a", "pcm_s16le", f"{P}/assets/mix.wav"], check=True)

# ---------------------------------------------------------------- shots, cut to their exact length
os.makedirs(f"{P}/assets/cut", exist_ok=True)
for j, (k, a, b, off, how) in enumerate(SHOTS):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, off):.3f}", "-i", f"{P}/assets/rushf/{k}.mp4", "-t", f"{b - a + 0.1:.3f}",
                    "-an", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", f"{P}/assets/cut/{j}.mp4"], check=True)

# ---------------------------------------------------------------- html
def fs(h):
    L = max(len(x) for x in h.replace("<a>", "").replace("</a>", "").split("<br>"))
    return max(x for x in (55, 89, 144) if x <= max(55, min(144, 900 / (0.56 * max(L, 4)))))
VIDS = "".join(f'<video id="r{j}" class="clip rc" src="assets/cut/{j}.mp4" muted playsinline data-start="{a:.3f}" '
               f'data-duration="{b - a:.3f}" data-track-index="{2 + j % 2}"></video>' for j, (k, a, b, off, how) in enumerate(SHOTS))
TXT = "".join(f'<div class="w" id="w{k}" style="font-size:{fs(h)}px"><span class="in">{h}</span></div>' for k, (a, h) in enumerate(WORDS))
doc = f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:P;src:url(assets/fonts/poppins-600.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/fonts/poppins-700.woff2);font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:P,sans-serif}}
.rc{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;opacity:0;z-index:1}}
#shade{{position:absolute;left:0;right:0;top:0;height:820px;background:linear-gradient(rgba(5,20,35,.6),rgba(5,20,35,0));z-index:3;opacity:0}}
.w{{position:absolute;left:0;right:0;top:250px;text-align:center;color:#fff;font-weight:700;letter-spacing:-.045em;line-height:1.04;
   white-space:nowrap;text-shadow:0 4px 30px rgba(0,0,0,.45);opacity:0;z-index:4}}
.w .in{{display:inline-block}} .w a{{color:#8fd0ff;text-decoration:none}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;z-index:20}}
#lg{{position:absolute;inset:0;background:#000;opacity:0;z-index:10}}
.tile{{position:absolute;left:390px;top:810px;width:300px;height:300px;border-radius:82px;background:#1f88c9;display:flex;align-items:center;justify-content:center}}
.tile img{{width:178px}}
#end{{position:absolute;inset:0;background:radial-gradient(110% 75% at 85% 0%,#3aa2df 0%,#1f88c9 45%,#1672ab 100%);opacity:0;z-index:11}}
#end .tile{{top:560px;background:transparent}}
#word{{position:absolute;left:50%;top:930px;width:520px;margin-left:-260px;opacity:0}}
#tag{{position:absolute;left:50%;top:1110px;width:560px;margin-left:-280px;opacity:0}}
#url{{position:absolute;left:0;right:0;top:1240px;text-align:center;color:#fff;font-weight:600;font-size:40px;opacity:0}}
#avail{{position:absolute;left:0;right:0;top:1340px;text-align:center;color:#fff;font-weight:600;font-size:36px;opacity:0}}
#stores{{position:absolute;left:0;right:0;top:1410px;display:flex;gap:28px;justify-content:center;opacity:0}} #stores img{{height:100px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<audio id="bgm" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="11"></audio>
{VIDS}<div id="shade"></div>{TXT}
<div id="lg"><div class="tile" id="lt"><img src="assets/icon_white.png" alt=""></div></div>
<div id="end"><div class="tile" id="et"><img src="assets/icon_white.png" alt=""></div>
 <img id="word" src="assets/logo_word_white.png" alt=""><img id="tag" src="assets/logo_tag_white.png" alt="">
 <div id="url">pi-tup.com</div><div id="avail">Disponible sur</div>
 <div id="stores"><img src="assets/appstore.svg" alt=""><img src="assets/Google_Play_Store_badge_EN.svg" alt=""></div></div>
<div id="flash"></div></div>
<script>
const tl=gsap.timeline({{paused:true}}); const E=(o)=>Object.assign({{immediateRender:false}},o);
const SHOTS={json.dumps(SHOTS)}, WORDS={json.dumps([[a, e] for (a, h), e in zip(WORDS, WORD_END)])}, FL={json.dumps(FLASH_AT)};
SHOTS.forEach(([k,a,b,off,how],j)=>{{ const r="#r"+j; tl.set(r,{{opacity:1}},a); tl.set(r,{{opacity:0}},b);
  tl.fromTo(r,{{scale:1.0}},E({{scale:1.045,duration:b-a,ease:"none"}}),a);
  if(how==="flash") tl.fromTo(r,{{scale:1.09}},E({{scale:1.0,duration:.35,ease:"expo.out"}}),a); }});
FL.forEach((a)=>tl.fromTo("#flash",{{opacity:.85}},E({{opacity:0,duration:.2,ease:"power2.out"}}),a));
WORDS.forEach(([a,b],k)=>{{ const w="#w"+k;
  tl.set(w,{{opacity:1}},a); tl.set(w,{{opacity:0}},b); tl.set("#shade",{{opacity:1}},a);
  tl.fromTo(w+" .in",{{y:60,scale:.86,opacity:0}},E({{y:0,scale:1,opacity:1,duration:.28,ease:"back.out(1.7)"}}),a); }});
// hook: the 2D logo grows out of the black, then its blue fills the screen and the jersey cuts in
const L0={LOGO0:.3f}, C1={CUT1:.3f}, E0={END0:.3f};
tl.set("#lg",{{opacity:1}},L0); tl.set("#lg",{{opacity:0}},C1); tl.set("#shade",{{opacity:0}},L0); tl.set("#shade",{{opacity:1}},C1);
tl.fromTo("#lt",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.38,ease:"back.out(2)"}}),L0);
tl.to("#lt",{{scale:9,borderRadius:"20px",duration:Math.max(.2,C1-L0-.42),ease:"power3.in"}},L0+.42);
tl.to("#lt img",{{opacity:0,duration:.12}},C1-.14);
// end card
tl.set("#end",{{opacity:1}},E0); tl.set("#shade",{{opacity:0}},E0);
tl.fromTo("#et",{{scale:.2,rotation:-12}},E({{scale:1,rotation:0,duration:.42,ease:"back.out(2)"}}),E0);
tl.fromTo("#word",{{opacity:0,y:40}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),E0+.3);
tl.fromTo("#tag",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),E0+.55);
tl.fromTo("#url",{{opacity:0}},E({{opacity:.9,duration:.4}}),E0+.8);
tl.fromTo("#avail",{{opacity:0,y:20}},E({{opacity:1,y:0,duration:.4,ease:"expo.out"}}),E0+.95);
tl.fromTo("#stores",{{opacity:0,y:30}},E({{opacity:1,y:0,duration:.45,ease:"expo.out"}}),E0+1.05);
tl.set({{}},{{}},{D}); window.__timelines=window.__timelines||{{}}; window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>'''
open(f"{P}/index.html", "w").write(doc)
for nm, (s, e, i, f0) in place.items(): print(f"voice {nm:3s} {s:6.2f}-{e:6.2f}")
for s in SHOTS: print("shot", s)
print("logo", round(LOGO0, 2), "cut1", round(CUT1, 2), "end", round(END0, 2), "D", D)
