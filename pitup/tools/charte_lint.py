# PitUp charter check: blocks a video that breaks the charter before it is delivered (idea from the
# langchain-ai/lca-managed-agents course: brand as data + a check that refuses off-brand work).
# usage: charte_lint.py <hyperframes project dir> [--video render.mp4] [--script build.py] [--musique name:start_s]
# Exit code 1 when an ERREUR is found. ATTENTION lines are for a human decision.
import argparse, json, os, re, subprocess, sys, html as H
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "charte", "charte.json"), encoding="utf-8"))
ap = argparse.ArgumentParser(); ap.add_argument("projet"); ap.add_argument("--video"); ap.add_argument("--script"); ap.add_argument("--musique")
a = ap.parse_args()
err, warn = [], []
E = lambda m: err.append(m); W = lambda m: warn.append(m)
doc = open(os.path.join(a.projet, "index.html"), encoding="utf-8").read()
css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", doc, re.S)) + " " + " ".join(re.findall(r'style="([^"]*)"', doc))

# ---- colours: palette, or neutral grey / black / white
def hexes(v):
    out = []
    for c in C["couleurs"].values(): out += c if isinstance(c, list) else [c]
    return {x.lower() for x in out}
PAL = hexes(C["couleurs"]) | {x.lower() for x in C.get("couleurs_telephone", [])}
def rgb_of(tok):
    if tok.startswith("#"):
        h = tok[1:]; h = "".join(ch * 2 for ch in h) if len(h) == 3 else h[:6]
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)), "#" + h.lower()
    n = [int(float(x)) for x in re.findall(r"[\d.]+", tok)[:3]]
    return tuple(n), "#%02x%02x%02x" % tuple(n)
seen = set()
for tok in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)", css):
    (r, g, b), hx = rgb_of(tok)
    if hx in PAL or max(r, g, b) - min(r, g, b) <= 14 or hx in seen: continue
    seen.add(hx); E(f"couleur hors charte : {tok} (palette : {', '.join(sorted(PAL))})")

# ---- fonts and type sizes
for fam in set(re.findall(r"font-family:\s*([^;}\"]+)", css)):
    names = [x.strip().strip("'\"") for x in fam.split(",")]
    faces = re.findall(r"@font-face\{\{?font-family:\s*(\w+);src:url\(([^)]*)\)", doc)
    alias = {n: u for n, u in faces}
    real = [("Poppins" if "poppins" in alias.get(n, "").lower() else n) for n in names]
    if not any(r in C["polices"] + C["polices_videos_produit"] for r in real): E(f"police hors charte : {fam}")
ok_sizes = set(C["tailles_texte_px"]) | set(C["tailles_texte_service_px"]) | set(C.get("tailles_micro_px", []))
for s in sorted({int(float(x)) for x in re.findall(r"font-size:\s*([\d.]+)px", css)}):
    if s not in ok_sizes: E(f"taille de texte hors échelle : {s} px (échelle : {sorted(C['tailles_texte_px'])})")

# ---- visible text
body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", doc, flags=re.S)
body = re.sub(r"<br\s*/?>", " ", body)
blocks = [H.unescape(re.sub(r"<[^>]+>", "", m)).strip() for m in re.findall(r'<div class="w[^"]*"[^>]*>(.*?)</div>', body, re.S)]
blocks = [re.sub(r"\s+", " ", b) for b in blocks if b]
alltext = H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
for rule in C["texte"]["interdits"]:
    for b in blocks + [alltext]:
        if re.search(rule["motif"], b, re.I if "PitUp" not in rule["motif"] else 0):
            E(f"texte : {rule['raison']} -> « {b[:80]} »"); break
script_text = " ".join(blocks)
if re.search(C["texte"]["vendeurs"], script_text, re.I):
    if C["texte"]["chiffre_doit_dire"] not in script_text: E("« +100 » sans « nous ont déjà rejoints »")
    for b in blocks:
        if re.search(C["texte"]["vendeurs"], b, re.I) and re.search(C["texte"]["acheteurs"], b, re.I):
            E(f"acheteurs et vendeurs mélangés dans un même bloc : « {b} »")
if "pitup" not in script_text.lower() and "icon_white" not in doc: W("PitUp n'est ni écrit ni montré")

# ---- end: badges need "Disponible sur" above them
if any(bdg in doc for bdg in C["fin"]["badges"]):
    i_av = doc.find(C["fin"]["au_dessus_des_badges"]); i_bd = min(doc.find(x) for x in C["fin"]["badges"] if x in doc)
    if i_av < 0: E("badges des stores sans « Disponible sur »")
    else:
        tops = dict(re.findall(r"#(avail|stores)\{\{?position:absolute;[^}]*?top:(\d+)px", doc))
        if tops and int(tops.get("avail", 0)) >= int(tops.get("stores", 99999)): E("« Disponible sur » n'est pas au-dessus des badges")
else:
    W("pas de badges App Store / Google Play à la fin")

# ---- logo visible from the first frame (brand in the first 3 s)
if not re.search(r'icon_white\.png', doc): W("logo PitUp absent du projet")

# ---- build script: banned sounds
if a.script:
    st = open(a.script, encoding="utf-8").read()
    code = "\n".join(l for l in st.splitlines() if not l.lstrip().startswith("#"))
    for k in C["son"]["bannis_code"]:
        if k in code: E(f"son fabriqué par code banni dans le script : {k}")
    for k in C["son"]["bannis_fichiers"]:
        if re.search(rf"\b{re.escape(k)}\b", code): E(f"son de banque banni dans le script : {k}")
    if "elevenlabs" in code.lower(): E("ElevenLabs dans le script")

# ---- music already used in another video
if a.musique:
    name = a.musique.split(":")[0].lower()
    for m in C["musiques_deja_utilisees"]:
        if m["fichier"] in name: W(f"musique déjà utilisée : {m['titre']} ({'; '.join(m['videos'])}) -> le signaler au fondateur")
    for m in C["musiques_bannies"]:
        if m.lower() in name: E(f"musique bannie : {m}")

# ---- rendered video
if a.video:
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,color_primaries",
                                    "-show_entries", "format=duration", "-of", "json", a.video], capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    if [v["width"], v["height"]] not in [list(x) for x in C["formats"].values()]: E(f"format {v['width']}x{v['height']} hors charte")
    num, den = map(int, v["r_frame_rate"].split("/"))
    if abs(num / den - C["video"]["images_par_seconde"]) > 0.01: E(f"{num / den:.2f} images/s au lieu de {C['video']['images_par_seconde']}")
    if not any(s["codec_type"] == "audio" for s in pr["streams"]): W("vidéo sans son")
    else:
        o = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.video, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-1])
        if abs(I - C["video"]["lufs"]) > C["video"]["tolerance_lufs"]: E(f"volume {I} LUFS (attendu {C['video']['lufs']} ± {C['video']['tolerance_lufs']})")
        if pk > C["video"]["crete_max_db"]: E(f"crête {pk} dB (max {C['video']['crete_max_db']})")
        print(f"rendu : {v['width']}x{v['height']}, {num / den:.0f} i/s, {float(pr['format']['duration']):.1f} s, {I} LUFS, crête {pk} dB")

for m in err: print("ERREUR    ", m)
for m in warn: print("ATTENTION ", m)
print(f"{len(err)} erreur(s), {len(warn)} attention(s)" + (" : livraison bloquée" if err else " : conforme à la charte"))
sys.exit(1 if err else 0)
