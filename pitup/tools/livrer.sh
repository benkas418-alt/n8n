#!/usr/bin/env bash
# Render a HyperFrames project, check it against the PitUp charter, and copy it to the deliverables only if it passes.
# usage: livrer.sh <project dir> <Deliverable-Name.mp4> [charte_lint options: --script build.py --musique name:start]
set -euo pipefail
PROJ=$1; NAME=$2; shift 2
SP=/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
HERE=$(cd "$(dirname "$0")" && pwd)
rm -rf /root/.cache/hyperframes/history/* /tmp/hyperframes-extract-cache-0
mkdir -p "$PROJ/renders" "$SP/livrables"
OUT="$PROJ/renders/${NAME%.mp4}.mp4"
(cd "$PROJ" && npx -y hyperframes@0.8.181 render . --quality high --fps 30 -o "renders/${NAME%.mp4}.mp4" > "$SP/render_last.log" 2>&1) || { tail -20 "$SP/render_last.log"; exit 1; }
if python3 "$HERE/charte_lint.py" "$PROJ" --video "$OUT" "$@"; then
  cp "$OUT" "$SP/livrables/$NAME"; echo "livré : $SP/livrables/$NAME"
else
  echo "non livré : corriger les erreurs de charte ci-dessus"; exit 1
fi
