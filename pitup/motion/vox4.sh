cd /tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
PY=/home/user/voxcpm/.venv/bin/python; R=audio/soeur/ref.wav
S="voix douce et posée, chaleureuse, avec le sourire"; C="voix claire et naturelle, débit normal, avec le sourire"
$PY tools/vox_clone_texts.py $R "$S" audio/v9/f0 "Télécharge l'appli PitUp dès aujourd'hui." "Télécharge l'appli PitUp dès aujourd'hui." "Télécharge l'appli PitUp dès aujourd'hui." 2>&1 | grep -E "^[0-9] "
$PY tools/vox_clone_texts.py $R "$C" audio/v9/f1 "Télécharge l'appli PitUp dès aujourd'hui." "Télécharge l'appli PitUp dès aujourd'hui." "Télécharge l'appli PitUp dès aujourd'hui." 2>&1 | grep -E "^[0-9] "
$PY tools/vox_clone_texts.py $R "$S" audio/v9/f2 "Télécharge l'appli PitUp." "Télécharge l'appli PitUp." "Télécharge l'appli PitUp." 2>&1 | grep -E "^[0-9] "
echo VOX4DONE
