# Insert the sister's REAL inhale (from her own recording) into the pause after "Ah", at REL dB under the speech level.
# usage: add_breath.py voice.wav out.wav pause_start_s gap_before_s [rel_db=-13]
import sys, subprocess, numpy as np, soundfile as sf
src, dst, p0, gap = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]); REL = float(sys.argv[5]) if len(sys.argv) > 5 else -13
B = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad/audio/soeur/full.wav"
r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "45.47", "-t", "0.40", "-i", B, "-af", "highpass=f=150,afftdn=nr=10:nf=-50,lowpass=f=11000",
                    "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True).stdout
b = np.frombuffer(r, np.float32).copy(); sr = 48000
fi, fo = int(.04 * sr), int(.08 * sr); b[:fi] *= np.linspace(0, 1, fi) ** 2; b[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
a, _ = sf.read(src, dtype="float32"); F = int(.01 * sr)
E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9); sp = np.median(E[E > -40])
g = 10 ** ((sp + REL - 20 * np.log10(np.sqrt((b ** 2).mean()) + 1e-12)) / 20); i0 = int((p0 + gap) * sr)
a[i0:i0 + len(b)] += b * g; sf.write(dst, a, sr); print(f"breath {len(b)/sr:.2f}s at {p0+gap:.2f}s, level {sp+REL:.1f} dB (speech {sp:.1f})")
