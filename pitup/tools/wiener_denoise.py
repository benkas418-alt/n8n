# Speech denoise for the cloned voice: learn the recording hiss from the quietest frames, remove it everywhere,
# speech included (decision-directed Wiener gain, smoothed, with a floor so no "musical" artefacts).
# usage: wiener_denoise.py in.wav out.wav [reduction_db=18] [over=1.5]
import sys, numpy as np, soundfile as sf
from scipy.signal import stft, istft
from scipy.ndimage import uniform_filter1d
a, sr = sf.read(sys.argv[1], dtype="float64"); a = a if a.ndim == 1 else a.mean(1)
red = float(sys.argv[3]) if len(sys.argv) > 3 else 18.0; over = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
N = 2048; H = 512
f, t, Z = stft(a, sr, nperseg=N, noverlap=N - H); P = np.abs(Z) ** 2
e = P.sum(0); q = e <= np.percentile(e, 12)                      # quietest 12 % of frames = hiss only
noise = P[:, q].mean(1, keepdims=True)
gmin = 10 ** (-red / 20); G = np.ones_like(P); prev = np.ones(P.shape[0])
post = P / (noise + 1e-20)
for k in range(P.shape[1]):                                       # decision-directed a-priori SNR (Ephraim-Malah style)
    prio = 0.98 * (prev ** 2) * post[:, max(k - 1, 0)] + 0.02 * np.maximum(post[:, k] - over, 0)
    g = prio / (1 + prio); g = np.maximum(g, gmin); G[:, k] = g; prev = g
G = uniform_filter1d(G, 3, axis=0)                                # light smoothing across frequency
_, y = istft(Z * G, sr, nperseg=N, noverlap=N - H); y = y[:len(a)]
sf.write(sys.argv[2], y.astype(np.float32), sr, subtype="FLOAT")
print(f"noise profile from {q.sum()} frames, reduction up to {red} dB")
