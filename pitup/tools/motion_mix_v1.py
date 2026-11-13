# Adds the égérie's lines at fixed times over a motion video's music: music ducks low under each line, then comes back.
import sys, json, subprocess, numpy as np, soundfile as sf
music, out, places = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
SR = 48000
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).reshape(-1, 2)
m = load(music).copy(); n = len(m); vox = np.zeros_like(m); g = np.ones(n, np.float32)
t = np.arange(n) / SR
for f, at in places:
    v = load(f); e = np.abs(v).max(1); idx = np.where(e > 0.01)[0]
    v = v[max(0, idx[0] - 800): idx[-1] + 2400]; i = int(at * SR); v = v[: n - i]; vox[i:i + len(v)] += v * 1.7
    a, b = at - 0.1, at + len(v) / SR + 0.15
    duck = np.clip(np.minimum((t - (a - 0.15)) / 0.15, ((b + 0.5) - t) / 0.5), 0, 1)
    g = np.minimum(g, 1 - 0.8 * duck)                      # music at 20 % under the voice
mix = m * g[:, None] + vox
sf.write(out + ".raw.wav", mix, SR, subtype="FLOAT")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), out], check=True)
print("ok", out)
