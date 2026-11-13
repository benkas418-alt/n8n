#!/bin/bash
# Voice-over QA before any delivery. FAIL lines must be zero.
# usage: voice_qa.sh voice.wav "ville:v i l|v iː l" "aussi:o s i"   (word:accepted phone patterns, | = or)
S=/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
V="$1"; shift; OUT=/tmp/vqa_words.json
echo "== 1-2. signal (clipping, abrupt cuts, digital silence)"
python3 - "$V" <<'EOF'
import sys, numpy as np, soundfile as sf
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
clip = int((np.abs(a) >= 0.999).sum()); print(("FAIL" if clip else "ok  "), "clipped samples:", clip, " peak", round(float(np.abs(a).max()), 3))
F = int(0.005 * sr); E = 20 * np.log10(np.array([np.sqrt((a[k:k + F] ** 2).mean()) for k in range(0, len(a) - F, F)]) + 1e-9)
cuts = [i * 0.005 for i in range(1, len(E) - 2) if E[i - 1] > -35 and min(E[i + 1], E[i + 2]) < E[i - 1] - 30 and min(E[i + 1], E[i + 2]) < -50]
print(("FAIL" if cuts else "ok  "), "abrupt cuts (>30 dB drop in 10 ms):", [round(c, 2) for c in cuts])
z = E < -100; runs = []; k = 0
while k < len(z):
    if z[k]:
        j = k
        while j < len(z) and z[j]: j += 1
        if 0.3 < k * 0.005 < len(a) / sr - 0.3: runs.append((round(k * .005, 2), round(j * .005, 2)))
        k = j
    else: k += 1
print(("FAIL" if runs else "ok  "), "digital silence inside the voice:", runs)
EOF
echo "== 3. word clarity (whisper word probability < 0.6)"
/home/user/fw/bin/python - "$V" "$OUT" <<'EOF'
import sys, json, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
n = int(len(a) * 16000 / sr); y = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
r, _ = WhisperModel("medium", compute_type="int8").transcribe(y, language="fr", beam_size=5, word_timestamps=True, initial_prompt="Lubumbashi. PitUp.")
W = [(w.word.strip(), w.start, w.end, w.probability) for s in r for w in s.words]; json.dump(W, open(sys.argv[2], "w"))
print("text:", " ".join(w[0] for w in W))
low = [(w, round(s, 2), round(p, 2)) for w, s, e, p in W if p < 0.6]
print(("WARN" if low else "ok  "), "low-confidence words:", low)
EOF
echo "== 3b. word level evenness (a word > 8 dB under the voice median is masked by the music)"
python3 - "$V" "$OUT" <<'EOF'
import sys, json, numpy as np, soundfile as sf
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1); W = json.load(open(sys.argv[2]))
def lv(s, e):   # loudest 60 ms inside the word: robust to whisper's loose word edges
    x = a[int(s * sr):int(e * sr)]; F = int(.06 * sr)
    if len(x) < F: return -99
    return max(20 * np.log10(np.sqrt((x[k:k + F] ** 2).mean()) + 1e-9) for k in range(0, len(x) - F + 1, F // 3))
L = [(w, s, lv(s, e)) for w, s, e, p in W]; med = float(np.median([l for _, _, l in L if l > -60]))
low = [(w, round(s, 2), round(l - med, 1)) for w, s, l in L if l < med - 8]
print(("FAIL" if low else "ok  "), f"words > 8 dB under median ({med:.1f} dB):", low)
EOF
echo "== 3c. speech rate per sentence + sounds outside words"
python3 $S/tools/qa_rate_gaps.py "$V" "$OUT"
python3 $S/tools/qa_word_ends.py "$V"
echo "== 4. pronunciation (IPA phones of watched words)"
for spec in "$@"; do
  w="${spec%%:*}"; pats="${spec#*:}"
  python3 - "$OUT" "$w" > /tmp/vqa_spans <<'EOF'
import sys, json, re
W = json.load(open(sys.argv[1])); key = sys.argv[2].lower()
for i, (t, s, e, p) in enumerate(W):
    if re.sub(r"[^a-zàâçéèêëîïôûùüÿœ']", "", t.lower()) == key:
        a = W[max(0, i - 2)][1]; b = W[min(len(W) - 1, i + 2)][2]   # two words of context each side: one is not enough for the phone model
        print(f"{max(0, a - 0.03):.2f} {b + 0.05:.2f}")
EOF
  for sp in $(cat /tmp/vqa_spans | tr ' ' ','); do
    s=${sp%,*}; e=${sp#*,}
    ph=$(/home/user/voxcpm/.venv/bin/python $S/tools/phones.py "$V" $s $e 2>/dev/null | grep -E "^[0-9]" | cut -d: -f2-)
    ok=FAIL; IFS='|' read -ra P <<< "$pats"; for p in "${P[@]}"; do [[ "$ph" == *"$p"* ]] && ok="ok  "; done
    echo "$ok $w @${s}s:$ph   (expected: $pats)"
  done
done
