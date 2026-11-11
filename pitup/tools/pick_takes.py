# Picks the best take of each line: text must match (whisper), voice must match its target (resemblyzer), duration sane.
import glob, json, re, subprocess, difflib, sys, os, shutil, unicodedata
import soundfile as sf, numpy as np
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
lines = json.load(open(sys.argv[1]))           # {name: [text, target]} target in jum|mixA|mixC|soe
src, dst = f"{SP}/audio/v11", f"{SP}/audio/v8"
def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("pitup", "pitup").replace("pit up", "pitup"); return re.sub(r"[^a-z0-9 ]", " ", t).split()
# voice embeddings via the voxcpm venv (resemblyzer lives there)
emb = json.loads(subprocess.run(["/home/user/voxcpm/.venv/bin/python", "-c", """
import glob, json
from resemblyzer import VoiceEncoder, preprocess_wav
S='%s/audio'; enc=VoiceEncoder('cpu'); r={}
r['ref_soe']=enc.embed_utterance(preprocess_wav(S+'/soeur/ref.wav')).tolist(); r['ref_jum']=enc.embed_utterance(preprocess_wav(S+'/jumelle/ref.wav')).tolist()
for f in glob.glob(S+'/v11/*.wav'): r[f.split('/')[-1][:-4]]=enc.embed_utterance(preprocess_wav(f)).tolist()
print(json.dumps(r))""" % SP], capture_output=True, text=True).stdout.strip().splitlines()[-1])
es, ej = np.array(emb["ref_soe"]), np.array(emb["ref_jum"])
from faster_whisper import WhisperModel
m = WhisperModel("medium", compute_type="int8"); report = []
for name, (text, target) in lines.items():
    best = None
    for f in sorted(glob.glob(f"{src}/{name}_*.wav")):
        k = os.path.basename(f)[:-4]; a, sr = sf.read(f, dtype="float32"); d = len(a) / sr
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "16000", "-ac", "1", f"{SP}/dup/pk.wav"])
        b, _ = sf.read(f"{SP}/dup/pk.wav", dtype="float32"); s, _ = m.transcribe(b, language="fr", initial_prompt="PitUp, Lubumbashi")
        heard = " ".join(x.text.strip() for x in s); tr = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
        e = np.array(emb[k]); ss, sj = float(e @ es), float(e @ ej)
        vs = {"jum": sj, "soe": ss, "mixA": 1 - abs((ss - sj) - (-0.07)), "mixC": 1 - abs((ss - sj) - 0.10)}[target]
        maxd = 0.13 * len(text) + 1.5; ok = d <= maxd
        score = 3 * tr + vs - (5 if not ok else 0)
        report.append(f"{k:7s} {d:5.2f}s txt {tr:.2f} soe {ss:.2f} jum {sj:.2f} {'' if ok else 'TROP LONG'} | {heard}")
        if best is None or score > best[0]: best = (score, f, tr)
    shutil.copy(best[1], f"{dst}/{sys.argv[2]}{name}.wav"); report.append(f"  -> {name}: {os.path.basename(best[1])} (texte {best[2]:.2f})")
print("\n".join(report))
