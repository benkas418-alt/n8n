# Scores the one-pass voice takes: words heard vs script (pronunciation), sentence starts for vo_full timing,
# per-sentence pitch and rate (natural rhythm varies), voice similarity. Run with system python3 -I.
import json, re, subprocess, sys, glob, os, difflib, unicodedata
import numpy as np, parselmouth
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
cfg = json.load(open(f"{SP}/cfg/scripts_v13.json")); only = sys.argv[1:] or list(cfg)
files = sorted(f for v in only for f in glob.glob(f"{SP}/audio/v13/{v}*.wav"))

def norm(t):
    t = unicodedata.normalize("NFKD", t.lower().replace("’", "'")); t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9]+", " ", t.replace("pit up", "pitup").replace("louboumbachi", "lubumbashi").replace("lubumbachi", "lubumbashi")); return t.split()

W = json.loads(subprocess.run(["/home/user/fw/bin/python", "-I", "-c", """
import sys, json, subprocess, soundfile as sf
from faster_whisper import WhisperModel
m = WhisperModel('medium', compute_type='int8'); out = {}
for f in sys.argv[1:]:
    # this venv's PyAV cannot open files: decode with ffmpeg and pass samples
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ar', '16000', '-ac', '1', '/tmp/sc13.wav'])
    b, _ = sf.read('/tmp/sc13.wav', dtype='float32')
    s, _ = m.transcribe(b, language='fr', word_timestamps=True, initial_prompt='PitUp.')
    out[f] = [(w.word, w.start, w.end) for x in s for w in x.words]
print(json.dumps(out))""", *files], capture_output=True, text=True).stdout.strip().splitlines()[-1])

E = json.loads(subprocess.run(["/home/user/voxcpm/.venv/bin/python", "-I", "-c", """
import sys, json
from resemblyzer import VoiceEncoder, preprocess_wav
enc = VoiceEncoder('cpu'); print(json.dumps({f: enc.embed_utterance(preprocess_wav(f)).tolist() for f in sys.argv[1:]}))""",
    *files, *{f"{SP}/{cfg[v]['ref']}" for v in only}], capture_output=True, text=True).stdout.strip().splitlines()[-1])

res = {}
for f in files:
    v = next(k for k in cfg if os.path.basename(f).startswith(k)); sents = cfg[v]["scenes"]
    sw, sid = [], []
    for i, s in enumerate(sents):
        for w in norm(s): sw.append(w); sid.append(i)
    hw, ht = [], []
    for word, a, b in W[f]:
        for w in norm(word): hw.append(w); ht.append((a, b))
    sm = difflib.SequenceMatcher(None, sw, hw, autojunk=False); m = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): m[blk.a + k] = blk.b + k
    errs = [f"« {' '.join(sw[i1:i2])} » -> « {' '.join(hw[j1:j2])} »" for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    snd = parselmouth.Sound(f); pit = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
    f0 = pit.selected_array["frequency"]; tt = pit.xs()
    rows, starts, tail, head_end = [], [], None, None
    for i, s in enumerate(sents):
        idx = [k for k in range(len(sw)) if sid[k] == i and k in m]
        if not idx: rows.append(None); starts.append(None); continue
        a, b = ht[m[idx[0]]][0], ht[m[idx[-1]]][1]; starts.append(round(a, 3))
        if i == 0: head_end = ht[m[idx[0]] - 1][1] if m[idx[0]] > 0 else None
        if i == len(sents) - 1: tail = ht[m[idx[-1]] + 1][0] if m[idx[-1]] + 1 < len(ht) else None
        seg = f0[(tt >= a) & (tt <= b) & (f0 > 0)]; head = f0[(tt >= a) & (tt <= a + 0.5) & (f0 > 0)]
        syl = len(re.findall(r"[aeiouyéèêàâîôûù]+", s.lower()))
        rows.append(dict(rate=round(syl / max(0.3, b - a), 1), f0=round(float(np.median(seg)), 0) if len(seg) else 0,
                         head=round(float(np.median(head)), 0) if len(head) else 0, dur=round(b - a, 2)))
    e = np.array(E[f]); r = np.array(E[f"{SP}/{cfg[v]['ref']}"]); ok = [x for x in rows if x]
    res[f] = dict(voice=v, tail=tail, head_end=head_end, wt=[[sw[k], sid[k], ht[m[k]][0], ht[m[k]][1]] for k in sorted(m)], sim=round(float(e @ r), 3), ratio=round(sm.ratio(), 3), errors=errs, starts=starts, sentences=rows,
                  f0_med=round(float(np.median(f0[f0 > 0])), 0), rate_sd=round(float(np.std([x["rate"] for x in ok])), 2),
                  head_sd=round(float(np.std([x["head"] for x in ok])), 1), end=round(W[f][-1][2], 2) if W[f] else 0)
    x = res[f]; print(f"{os.path.basename(f)} sim {x['sim']} txt {x['ratio']} f0 {x['f0_med']} rate_sd {x['rate_sd']} head_sd {x['head_sd']} end {x['end']}")
    for k, rw in enumerate(rows): print("   ", k, rw)
    for er in errs: print("    !", er)
old = json.load(open(f"{SP}/audio/v13/score.json")) if os.path.exists(f"{SP}/audio/v13/score.json") else {}
old.update(res); json.dump(old, open(f"{SP}/audio/v13/score.json", "w"), indent=1, ensure_ascii=False)
