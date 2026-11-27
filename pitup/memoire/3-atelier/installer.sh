#!/usr/bin/env bash
# Remet en place les outils PitUp qui vivent HORS du dépôt (ils disparaissent avec le conteneur).
# usage : bash pitup/memoire/3-atelier/installer.sh etat|skills|voix|son|tout
# Chaque module ne fait rien si l'outil est déjà là. Aucun secret, aucune dépense.
set -u
H=/home/user; SK=${SKILLS_DIR:-$HOME/.claude/skills}
ok() { printf '  ok      %s\n' "$1"; }; ko() { printf '  MANQUE  %s\n' "$1"; }

etat() {
  echo "Outils :"
  [ -x "$H/voxcpm/.venv/bin/python" ] && ok "voix (VoxCPM2) : $H/voxcpm/.venv" || ko "voix : lancer « installer.sh voix »"
  [ -x "$H/fw/bin/python" ] && ok "transcription (faster-whisper) : $H/fw" || ko "transcription : lancer « installer.sh voix »"
  [ -d "$H/leonxlnx/earshot/.venv" ] && ok "écoute (earshot) : $H/leonxlnx/earshot" || ko "écoute : lancer « installer.sh son »"
  command -v ffmpeg >/dev/null && ok "ffmpeg" || ko "ffmpeg"
  command -v npx >/dev/null && ok "npx (HyperFrames se lance par npx, rien à installer)" || ko "npx"
  echo "Compétences : $(ls "$SK" 2>/dev/null | wc -l) dans $SK"
  for s in pitup-content-engine conversion-copywriting-engine viral-psychology-strategist earshot real-sound hyperframes gsap-timeline mockup-device-3d kinetic-typography video-shotcraft; do
    [ -f "$SK/$s/SKILL.md" ] && ok "$s" || ko "$s"
  done
  echo "Disque libre : $(df -h / | awk 'NR==2{print $4}') (HyperFrames refuse de rendre sous 1 Go)"
}

# Copie chaque dossier qui contient un SKILL.md depuis un dépôt public vers ~/.claude/skills.
skills() {
  mkdir -p "$SK" "$H/.skills-src"
  # Les trois compétences du fondateur sont dans le dépôt.
  for d in "$(dirname "$0")/../../skills"/*/; do [ -f "$d/SKILL.md" ] && cp -r "$d" "$SK/" ; done
  for r in Leonxlnx/earshot charlie947/motion-graphics-skills kylezantos/design-motion-principles LottieFiles/motion-design-skill \
           dickwu/apple-design-skill nextlevelbuilder/ui-ux-pro-max-skill bradautomates/claude-video \
           muratcankoylan/agent-skills-for-context-engineering Vincentwei1021/video-shotcraft; do
    d="$H/.skills-src/$(basename "$r")"
    [ -d "$d" ] || git clone -q --depth 1 "https://github.com/$r.git" "$d" || { echo "  échec du clonage : $r"; continue; }
    find "$d" -name SKILL.md -not -path '*/node_modules/*' | while read -r f; do
      n=$(basename "$(dirname "$f")"); [ -e "$SK/$n" ] || cp -r "$(dirname "$f")" "$SK/$n"
    done
  done
  # p5.js 2.4.0 (dessin génératif) dans $H/ext/npm/node_modules (27 nov. : le fondateur garde p5.js et video-shotcraft seulement)
  mkdir -p "$H/ext/npm"; [ -d "$H/ext/npm/node_modules/p5" ] || (cd "$H/ext/npm" && { [ -f package.json ] || npm init -y >/dev/null; } && npm install --silent p5@2.4.0)
  [ -f "$SK/hyperframes/SKILL.md" ] || npx -y skills add heygen-com/hyperframes -g --agent claude-code -y </dev/null >/dev/null 2>&1 || true
  echo "Compétences : $(ls "$SK" | wc -l) dans $SK"
}

voix() {
  [ -x "$H/voxcpm/.venv/bin/python" ] || { mkdir -p "$H/voxcpm" && python3 -m venv "$H/voxcpm/.venv" &&
    "$H/voxcpm/.venv/bin/pip" install -q voxcpm==2.0.3 librosa soundfile; }
  [ -x "$H/fw/bin/python" ] || { python3 -m venv "$H/fw" && "$H/fw/bin/pip" install -q faster-whisper soundfile numpy; }
  etat | sed -n 2,3p
}

son() {
  d="$H/leonxlnx/earshot"
  [ -d "$d" ] || { mkdir -p "$H/leonxlnx" && git clone -q --depth 1 https://github.com/Leonxlnx/earshot.git "$d"; }
  [ -d "$d/.venv" ] || { python3 -m venv "$d/.venv" && "$d/.venv/bin/pip" install -q -e "$d"; }
  etat | sed -n 4p
}

case "${1:-etat}" in
  etat) etat ;; skills) skills ;; voix) voix ;; son) son ;;
  tout) skills; voix; son; etat ;;
  *) echo "usage : installer.sh etat|skills|voix|son|tout"; exit 2 ;;
esac
