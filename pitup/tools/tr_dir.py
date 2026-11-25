# usage: tr_dir.py dir -> dir/tr.json (whisper medium, fr)
import sys, glob, os, json, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.wav")):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language="fr")
    out[os.path.basename(f)] = " ".join(s.text.strip() for s in segs)
json.dump(out, open(sys.argv[1] + "/tr.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print(k, v)
