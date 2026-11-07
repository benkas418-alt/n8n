cd /tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
PY=/home/user/voxcpm/.venv/bin/python; R=audio/soeur/ref.wav
S="voix douce et posée, chaleureuse, avec le sourire"; C="voix claire et naturelle, débit normal, avec le sourire"
gen(){ n=$1; st=$2; t=$3; $PY tools/vox_clone_texts.py $R "$st" audio/v9/$n "$t" "$t" 2>&1 | grep -E "^[0-9] "; }
gen a0 "$S" "Tu cherches quelque chose à Lubumbashi ?"
gen a1 "$S" "Tape-le dans la recherche."
gen a2 "$S" "Choisis ton article, et ajoute-le au panier."
gen a3 "$S" "Et on te le livre, partout dans la ville, jusque chez toi."
gen a5 "$C" "Télécharge l'appli PitUp, ou commande sur pé, i, tiret, té, u, pé, point com."
gen b0 "$S" "Plus de cent boutiques de Lubumbashi, réunies au même endroit."
gen b1 "$S" "Vêtements, chaussures, accessoires : fais ton choix, sans te déplacer."
gen b2 "$S" "Tu commandes, on te livre."
gen b4 "$C" "Télécharge l'appli maintenant, sur pé, i, tiret, té, u, pé, point com."
gen c0 "$C" "Bienvenue sur PitUp, le marché de Lubumbashi."
gen c1 "$S" "Nos boutiques partenaires viennent à toi."
gen c2 "$S" "Tu cherches un article ? Tu le trouves en un instant."
gen c3 "$S" "Ensembles, sneakers, montres… tout est là."
gen c4 "$S" "Tu commandes. On te livre."
gen c6 "$C" "Télécharge l'appli maintenant, ou va sur pé, i, tiret, té, u, pé, point com."
echo VOX2DONE
