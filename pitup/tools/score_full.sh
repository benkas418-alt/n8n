#!/bin/bash
# Score full voice-over takes with one grid. usage: score_full.sh take1.wav take2.wav ...
S=/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
REF="Ah Lubumbashi ! Notre ville bouge, et ses boutiques aussi. Seulement, entre les embouteillages et les allers-retours, trouver la bonne pièce prend souvent du temps. Alors, on a réuni les boutiques de la ville dans une seule appli. Tu choisis ton article, la boutique confirme, on te le livre, et tu ne paies qu'à la livraison. Sur l'appli PitUp, ta prochaine pièce t'attend déjà. Passe ta première commande, et laisse la ville venir à toi."
for f in "$@"; do
  out=$($S/tools/voice_qa.sh "$f" "ville:v i l b|v iː l b|v j i l b|v i l d|v iː l d|v i l v|v iː l v|v i l l d" "seulement:s a l m|s œ l m|s ə l m|s ɛ l m|s e l m" "alors:a l ɔ|a l o" "notre:n ɔ t ʁ|n o t ʁ" "trouver:t ʁ u v|t ʁ uː v" "lubumbashi:b a ʃ i" 2>/dev/null)
  txt=$(echo "$out" | grep "^text:" | cut -d: -f2-)
  fails=$(echo "$out" | grep -c "^FAIL")
  failw=$(echo "$out" | grep "^FAIL" | grep -oE "(ville|seulement|alors|notre|trouver|lubumbashi) @[0-9.]+s|abrupt|under median|clicks" | tr '\n' ' ')
  wer=$(python3 - "$REF" "$txt" <<'EOF'
import sys, re, unicodedata
n = lambda t: re.sub(r"[^a-z ]", " ", unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()).split()
r, h = n(sys.argv[1]), n(sys.argv[2])
d = [[i + j if i * j == 0 else 0 for j in range(len(h) + 1)] for i in range(len(r) + 1)]
for i in range(1, len(r) + 1):
    for j in range(1, len(h) + 1): d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (r[i-1] != h[j-1]))
print(d[-1][-1])
EOF
)
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "$(basename $f) | word errors $wer | FAIL $fails ($failw) | ${dur}s | $txt"
done
