# Subtle room acoustic on the dry voice-over: word endings decay naturally into the pauses instead of stopping dead.
# Synthetic small-room impulse (exponential noise, RT60 ~0.35 s, 12 ms pre-delay, low-passed), mixed WET dB under dry.
# usage: room_tail.py in.wav out.wav [wet_db=-17] [rt60=0.35]
import sys, numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
src, dst = sys.argv[1], sys.argv[2]; WET = float(sys.argv[3]) if len(sys.argv) > 3 else -17; RT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.35
a, sr = sf.read(src, dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
n = int(RT * 1.2 * sr); t = np.arange(n) / sr; rng = np.random.default_rng(11)
ir = rng.standard_normal(n) * np.exp(-6.9 * t / RT); ir = sosfilt(butter(2, [200, 6000], "bandpass", fs=sr, output="sos"), ir)
ir = np.concatenate([np.zeros(int(.012 * sr)), ir]); ir /= np.sqrt((ir ** 2).sum())
wet = fftconvolve(a, ir)[:len(a)].astype(np.float32)
y = a + wet * 10 ** (WET / 20); pk = np.abs(y).max(); y = y * (0.95 / pk) if pk > 0.95 else y
sf.write(dst, y, sr); print(f"room tail: wet {WET} dB, RT60 {RT}s, peak {np.abs(y).max():.3f}")
