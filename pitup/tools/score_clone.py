# usage: score_gh.py dir ref.wav -> json lines: file, text, f0 median, similarity, duration
import sys, glob, json, os, numpy as np, librosa
from resemblyzer import VoiceEncoder, preprocess_wav
d, ref = sys.argv[1], sys.argv[2]
enc = VoiceEncoder("cpu")
r = enc.embed_utterance(preprocess_wav(ref))
out = {}
for f in sorted(glob.glob(d + "/*.wav")):
    y, sr = librosa.load(f, sr=16000)
    f0, v, _ = librosa.pyin(y, fmin=70, fmax=300, sr=sr)
    f0 = f0[~np.isnan(f0)]
    e = enc.embed_utterance(preprocess_wav(f))
    out[os.path.basename(f)] = dict(f0=float(np.median(f0)) if len(f0) else 0, sim=float(np.dot(r, e)), dur=len(y)/sr)
json.dump(out, open(d + "/score.json", "w"), indent=1)
