# Adds the égérie's lines at fixed times over a motion video's music.
# Under each line the music glides down (raised-cosine curve in dB, starting 0.6 s early) to about -20 dB,
# its 300 Hz-4 kHz band is carved a further 8 dB, then it glides back over 1 s. Final gain is linear (no squashing).
import sys, json, subprocess, numpy as np, soundfile as sf
music, out, places = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
SR = 48000; PRE, POST, DEPTH = 0.6, 1.0, -20.0
def load(f, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", f] + (["-af", af] if af else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2)
m = load(music).copy(); mc = load(music, "equalizer=f=700:t=q:w=0.7:g=-8,equalizer=f=2200:t=q:w=0.7:g=-8")[:len(m)]
n = len(m); t = np.arange(n) / SR; vox = np.zeros_like(m); w = np.zeros(n)
spans = []
for f, at in places:
    v = load(f); e = np.abs(v).max(1); idx = np.where(e > 0.01)[0]
    v = v[max(0, idx[0] - 800): idx[-1] + 2400]
    v = v * (10 ** (-17 / 20) / max(1e-6, np.sqrt((v[np.abs(v).max(1) > 0.02] ** 2).mean())))   # every line at the same level
    i = int(at * SR); v = v[: n - i]; vox[i:i + len(v)] += v
    a, b = at, at + len(v) / SR; spans.append((a, b))
    up = np.clip((t - (a - PRE)) / PRE, 0, 1); down = np.clip(((b + POST) - t) / POST, 0, 1)
    w = np.maximum(w, np.minimum(0.5 - 0.5 * np.cos(np.pi * up), 0.5 - 0.5 * np.cos(np.pi * down)))
g = 10 ** (DEPTH * w / 20)
mus = (m * (1 - w[:, None]) + mc * w[:, None]) * g[:, None]
mix = mus + vox
sf.write(out + ".raw.wav", mix, SR, subtype="FLOAT"); sf.write(out + ".mus.wav", mus, SR, subtype="FLOAT"); sf.write(out + ".vox.wav", vox, SR, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-i", out + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(json.loads(meas[meas.rindex("{"):])["input_i"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".raw.wav", "-af", f"volume={-14 - I:.2f}dB,alimiter=limit=0.84:level=false", "-ar", str(SR), out], check=True)
def band(x):  # energy in 300 Hz - 4 kHz
    X = np.abs(np.fft.rfft(x.mean(1))) ** 2; fr = np.fft.rfftfreq(len(x), 1 / SR); return X[(fr > 300) & (fr < 4000)].sum() + 1e-12
for a, b in spans:
    s, e = int(a * SR), int(b * SR); print(f"line {a:5.2f}-{b:5.2f}s  voice over music (300-4k): {10*np.log10(band(vox[s:e])/band(mus[s:e])):5.1f} dB")
print("ok", out)
