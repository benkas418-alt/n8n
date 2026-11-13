# Voice-over mix: the instrumental sits well under the voice (MARGIN dB below it), then, when the voice ends, the music
# swells to full and crossfades to the ORIGINAL song (lyrics) at the same song position, so it continues without a jump.
# usage: mix_duck_end.py voice.wav instrumental.wav original.wav song_off lead total_dur out.wav [margin_db=16]
import sys, subprocess, json, numpy as np, soundfile as sf
vf, inst, orig, off, lead, dur, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
MARGIN = float(sys.argv[8]) if len(sys.argv) > 8 else 16.0; SR = 48000
def load(f, ss, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(t), "-i", f, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, 2).copy()
n = int(dur * SR)
v = load(vf, 0, dur); e = np.abs(v).max(1); last = np.where(e > 10 ** (-40 / 20))[0][-1]   # last voiced sample
vox = np.zeros((n, 2), np.float32); i0 = int(lead * SR); m_ = min(len(v), n - i0); vox[i0:i0 + m_] = v[:m_]
mi = load(inst, off, dur); mo = load(orig, off, dur)
mi = np.pad(mi, ((0, n - len(mi)), (0, 0))); mo = np.pad(mo, ((0, n - len(mo)), (0, 0)))
t = np.arange(n) / SR; vend = (i0 + last) / SR
# gain curve: low under the voice, swell to full over 0.8 s once the voice has finished
rv = np.sqrt((vox[i0:i0 + last] ** 2).mean()); rm = np.sqrt((mi[i0:i0 + last] ** 2).mean())
low = (rv * 10 ** (-MARGIN / 20)) / max(rm, 1e-9)
rmo = np.sqrt((mo[int(vend * SR):] ** 2).mean()); high = (rv * 10 ** (float(__import__("os").environ.get("HIGH_DB", "1.5")) / 20)) / max(rmo, 1e-9)   # song ~1.5 dB over the voice level
up = np.clip((t - (vend + 0.15)) / 0.8, 0, 1); up = 0.5 - 0.5 * np.cos(np.pi * up)
g = low + (high - low) * up
import os
if os.environ.get("ORIG_ALL") == "1":   # the original song (with Tems' vocals) all along; carve the speech band while the voice talks
    from scipy.signal import butter, sosfiltfilt
    base = mo; rm = np.sqrt((mo[i0:i0 + last] ** 2).mean()); low = (rv * 10 ** (-MARGIN / 20)) / max(rm, 1e-9); g = low + (high - low) * up
    mid = sosfiltfilt(butter(2, [300, 3000], "bandpass", fs=SR, output="sos"), base, axis=0)
    inside = 1 - up; base = base - (1 - 10 ** (-float(os.environ.get("CARVE_DB", "6")) / 20)) * mid * inside[:, None]
    music = base * g[:, None]
else:
    music = (mi * (1 - up)[:, None] + mo * up[:, None]) * g[:, None]   # crossfade instrumental -> original during the swell
fo = int(0.5 * SR); music[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = music + vox; sf.write(out + ".raw.wav", mix, SR, subtype="FLOAT")
mm = subprocess.run(["ffmpeg", "-v", "info", "-i", out + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(mm[mm.rindex("{"):mm.rindex("}") + 1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".raw.wav", "-af",
    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
    "-ar", str(SR), out], check=True)
print(f"voice ends at {vend:.2f}s, music under voice {20*np.log10(low):+.1f} dB, after voice {20*np.log10(high):+.1f} dB")
