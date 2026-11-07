cd /tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
PY=/home/user/voxcpm/.venv/bin/python; R=audio/soeur/ref.wav
S="voix douce et posée, chaleureuse, avec le sourire, débit lent"; C="voix claire et naturelle, posée, débit lent, avec le sourire"
$PY tools/vox_clone_texts.py $R "$C" audio/v9/e0 "Télécharge l'appli PitUp." "Télécharge l'appli PitUp." "Télécharge l'appli PitUp." 2>&1 | grep -E "^[0-9] "
$PY tools/vox_clone_texts.py $R "$S" audio/v9/e1 "Ou commande sur pé… i… tiret… té… u… pé… point com." "Ou commande sur pé… i… tiret… té… u… pé… point com." "Ou commande sur pé… i… tiret… té… u… pé… point com." 2>&1 | grep -E "^[0-9] "
echo VOX3DONE
