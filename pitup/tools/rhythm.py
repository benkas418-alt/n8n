# Gives a one-pass take a directed rhythm: each sentence gets its own tempo (pitch kept, Rubber Band) and its own
# pause after it. The intonation stays continuous because the sentences come from a single take.
# usage: rhythm.py take.wav out.wav '[[rate_syl_per_s, pause_after], ...]'   (needs audio/v13/score.json)
import json, subprocess, sys, os
import soundfile as sf, numpy as np
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
src, dst, plan = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]); KMIN = float(sys.argv[4]) if len(sys.argv) > 4 else 0.70
sc = json.load(open(f"{SP}/audio/v13/score.json"))[src]
a, sr = sf.read(src, dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
st = sc["starts"]; rows = sc["sentences"]; n = len(rows); assert len(plan) == n and None not in st
ends = [st[i] + rows[i]["dur"] for i in range(n)]
# cut points sit in the silence between sentences, a little after the last word so release tails stay
# whisper word times can be 0.1 s late: cut in the middle of the longest measured silence near each boundary
FR = int(0.01 * sr); E = np.array([np.sqrt((a[k:k + FR] ** 2).mean()) for k in range(0, len(a) - FR, FR)])
Z = np.array([np.mean(np.abs(np.diff(np.sign(a[k:k + FR])))) / 2 for k in range(0, len(a) - FR, FR)])
QUIET = max(0.01, 0.08 * float(np.median(E[E > 0.02])) if (E > 0.02).any() else 0.01)
def quiet_cut(lo, hi, need=0):
    lo_, hi_ = max(0, int(lo * 100)), min(len(E), int(hi * 100)); best, run = None, 0
    for k in range(lo_, hi_):
        if E[k] < QUIET and not (Z[k] > 0.12 and E[k] > 0.003):   # a weak hiss (s, ch, f) is speech, not silence
            run += 1
            if best is None or run > best[0]: best = (run, k - run + 1)
        else: run = 0
    if best is None or best[0] < need: return None if need else ((lo_ + int(np.argmin(E[lo_:hi_]))) / 100 if hi_ > lo_ else lo)
    return (best[1] + best[0] / 2) / 100
he = sc.get("head_end")
c0 = quiet_cut(he - 0.25 if he is not None else 0.0, st[0] + 0.05)
# a boundary is cut only inside a real pause (>= 50 ms) between the last word and the next sentence;
# when the voice runs two sentences together, they stay joined (no cut, no inserted pause)
bnd = [quiet_cut(ends[i] - 0.02, st[i + 1] + 0.06, need=5) for i in range(n - 1)]
tl_ = sc.get("tail"); cend = min(len(a) / sr, quiet_cut(ends[-1] - 0.1, tl_ + 0.05) if tl_ else ends[-1] + 0.25)
groups, g0 = [], 0
for i in range(n - 1):
    if bnd[i] is not None: groups.append((g0, i)); g0 = i + 1
groups.append((g0, n - 1))
edges = [c0] + [bnd[gb] for ga, gb in groups[:-1]] + [cend]
print("cuts", [round(c, 2) for c in edges], "groups", groups)
out, starts, t, words = [], [None] * n, 0.0, []
for gi, (ga, gb) in enumerate(groups):
    ca, cb = edges[gi], edges[gi + 1]; seg = a[int(ca * sr): int(cb * sr)]
    # optional: [rate, pause, gap, src_time] inserts a breath of `gap` s at `src_time` (e.g. after a sigh)
    ins = [(pl[3], pl[2]) for pl in plan[ga:gb + 1] if len(pl) > 3 and ca < pl[3] < cb]
    for at, gap in sorted(ins, reverse=True):
        c = int((at - ca) * sr); seg = np.concatenate([seg[:c], np.zeros(int(gap * sr), np.float32), seg[c:]])
    k = max(KMIN, min(1.08, min(plan[j][0] / rows[j]["rate"] for j in range(ga, gb + 1))))
    if KMIN >= 1.0: k = 1.0   # pauses only: the founder hears time-stretching as a crackle, so the voice is never stretched
    if abs(k - 1.0) < 1e-3: s_ = seg.astype(np.float32)
    else:
        sf.write("/tmp/rh_in.wav", seg, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/rh_in.wav", "-af", f"rubberband=tempo={k:.4f}:pitch=1:transients=smooth:formant=preserved:pitchq=quality",
                        "/tmp/rh_out.wav"], check=True)
        s_, _ = sf.read("/tmp/rh_out.wav", dtype="float32"); s_ = s_ if s_.ndim == 1 else s_.mean(1)
    shift = lambda x: sum(g for at, g in ins if at <= x)
    for j in range(ga, gb + 1): starts[j] = round(t + (st[j] - ca + shift(st[j])) / k, 3)
    for w, si, wa, wb in sc["wt"]:
        if ga <= si <= gb: words.append([w, round(t + (wa - ca + shift(wa)) / k, 3), round(t + (wb - ca + shift(wa)) / k, 3)])
    out.append(s_); t += len(s_) / sr
    if gi < len(groups) - 1: p_ = np.zeros(int(plan[gb][1] * sr), np.float32); out.append(p_); t += len(p_) / sr
    print(f"group {ga}-{gb} x{k:.2f} pause {plan[gb][1] if gi < len(groups) - 1 else 0}")
y = np.concatenate(out); fade = int(0.03 * sr); y[-fade:] *= np.linspace(1, 0, fade)
sf.write(dst, y, sr)
last_end = round(words[-1][2], 3) if words else t
json.dump({"words": words, "starts": starts, "end": round(last_end, 3), "dur": round(len(y) / sr, 3)}, open(dst + ".json", "w"))
print("starts", starts, "end", round(last_end, 2), "dur", round(len(y) / sr, 2))
