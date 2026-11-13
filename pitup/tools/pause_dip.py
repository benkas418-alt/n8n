# Studio pauses: inside each real pause (>= 200 ms under -40 dB), lower the recording's room noise by DIP dB with smooth
# 60 ms ramps that start after the word's decay and end before the next word. Never digital silence. usage: in out [dip_db]
import sys, numpy as np, soundfile as sf
a, sr = sf.read(sys.argv[1], dtype="float32"); dip = float(sys.argv[3]) if len(sys.argv) > 3 else 18.0
F = int(.02 * sr); E = np.array([20 * np.log10(np.sqrt((a[k:k + F] ** 2).mean()) + 1e-9) for k in range(0, len(a) - F, F)])
g = np.ones(len(a), np.float32); low = 10 ** (-dip / 20); R = int(.06 * sr); k = 0; n = 0
while k < len(E):
    if E[k] < -40:
        j = k
        while j < len(E) and E[j] < -40: j += 1
        if j - k >= 10:
            s, e = k * F + int(.04 * sr), j * F - int(.04 * sr)
            if e - s > 2 * R:
                ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, R))
                g[s:s + R] = 1 - (1 - low) * ramp; g[s + R:e - R] = low; g[e - R:e] = low + (1 - low) * ramp; n += 1
        k = j
    else: k += 1
sf.write(sys.argv[2], a * g, sr, subtype="FLOAT"); print(f"pauses lowered: {n} by {dip} dB")
