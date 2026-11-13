# Voice over a music bed that stays clearly audible: under the voice the music sits ~9 dB below it and only its
# 300 Hz–3 kHz band is carved (so the words stay clear); after the last word it swells to full.
# usage: mix_bed.py voice.wav song off lead tail out.wav [bed_gain]
import sys, subprocess, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
vf, song, off, lead, tail, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
BED = float(sys.argv[7]) if len(sys.argv) > 7 else 0.34; HI = float(__import__("os").environ.get("HI", "0.80")); SR = 48000
MARGIN = float(sys.argv[8]) if len(sys.argv) > 8 else 9.0     # dB the voice sits above the bed
def load(f, ss=0, t=None, filt=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(t)] if t else []) + ["-i", f] + (["-af", filt] if filt else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
v = load(vf); e = np.abs(v).max(1); idx = np.where(e > 10 ** (-40 / 20))[0]; v = v[: idx[-1] + int(0.05 * SR)]
n = int((lead + len(v) / SR + tail) * SR)
m = load(song, off, n / SR + 1, "bass=g=2")[:n]; m = np.pad(m, ((0, n - len(m)), (0, 0)))
vox = np.zeros((n, 2), np.float32); i0 = int(lead * SR); vox[i0:i0 + len(v)] = v
s0, s1 = lead - 0.25, lead + len(v) / SR + 0.1
t = np.arange(n) / SR
inside = np.clip(np.minimum((t - (s0 - 0.6)) / 0.6, ((s1 + 1.2) - t) / 1.2), 0, 1)      # 0 = free, 1 = under the voice
mid = sosfiltfilt(butter(2, [300, 3000], "bandpass", fs=SR, output="sos"), m, axis=0)
carved = m - 0.45 * mid                                                            # about -5 dB in the speech band
music = (m * (1 - inside)[:, None] + carved * inside[:, None]) * (HI - (HI - BED) * inside)[:, None]
import os; fo = int(float(os.environ.get("FADE", "1.5")) * SR); music[-fo:] *= np.linspace(1, 0, fo)[:, None]
# level the voice so that it sits ~9 dB above the bed in the speech band
vr = np.sqrt((vox[i0:i0 + len(v)] ** 2).mean()); mr = np.sqrt((music[i0:i0 + len(v)] ** 2).mean())
g = (mr * 10 ** (MARGIN / 20)) / max(vr, 1e-6); vox *= g
mix = music + vox; sf.write(out + ".raw.wav", mix, SR, subtype="FLOAT")
mm = subprocess.run(["ffmpeg", "-v", "info", "-i", out + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(mm[mm.rindex("{"):mm.rindex("}") + 1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".raw.wav", "-af",
    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
    "-ar", str(SR), out], check=True)
print("voice gain", round(float(g), 2), "dur", round(n / SR, 2))
