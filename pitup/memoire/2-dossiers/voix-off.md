# Dossier : voix off

## Recette de référence (validée le 14 nov. 2026)

Le fondateur a renvoyé `PitUp-Motion-point-voix.mp4` : « Celle-ci, elle est claire, la clarté que moi je cherche… elle humanise vraiment la voix. »

1. **Génération phrase par phrase**, clone de la sœur en mode « référence + style » :
   `pitup/tools/vox_clone_texts.py audio/soeur/ref.wav "voix claire et naturelle, débit normal, avec le sourire" sortie "phrase 1" "phrase 2" …`
   (VoxCPM2, cfg 2, 10 pas, environ 40 s par phrase sur ce processeur).
2. **Trois prises par phrase.** Garder celle dont le texte est exact (transcription whisper) et dont la hauteur reste entre 195 et 220 Hz. Écarter les prises à 245–275 Hz.
3. **Aucun traitement** : ni débruitage, ni égaliseur, ni pause ajoutée. Voix brute.
4. **Silences entre phrases** : 0,3 s dans un même sujet, 0,55 à 0,6 s entre deux sujets.
5. **Mixage** : `pitup/tools/motion_mix.py bed.wav out.wav places.json` (phrases au même niveau, musique à −20 dB d'un seul tenant, bande 300 Hz–4 kHz creusée de 8 dB, gain linéaire).
6. Caler l'image sur les mots (temps des mots par whisper).

## Ce qui a été refusé

- **Mode « continuation » d'un seul bloc + chaîne studio** (`vox_cont.py` + `mc_voice.sh`) : « pas assez claire, robotique » (14 nov.).
  Mesures face à la vraie voix : intonation 7 demi-tons contre 12, 30 % de pauses ajoutées contre aucune, aigus à −22 dB contre −11 dB.
- Pauses ajoutées à chaque virgule : effet « liste lue ».
- Étirement temporel : entendu comme un grésillement.
- ElevenLabs : interdit.

## Pièges connus

- « PitUp » se dit à l'anglaise, d'un trait (« pit-ap »). Ne pas finir une phrase courte sur ce mot.
- Fautes fréquentes du modèle : « à vente », « Est-ce que tu as », « Je cherche », « Il faut juste », « Téléchargez ». Toujours transcrire chaque prise.
- Une consigne de style entre parenthèses est **lue à voix haute** en mode continuation.
- « photographe, vidéaste » : le f avale le v.
- La transcription corrige en silence ; pour un mot douteux, vérifier les phonèmes (`pitup/tools/phones.py`).
- Changer de passage de référence, de réglage cfg ou de ponctuation n'élargit pas l'intonation (12 prises testées).

## Si la voix ne convient toujours pas

La seule voie sûre est un vrai enregistrement : la sœur lit le texte au téléphone (pièce calme, téléphone à 20 cm). Le montage se recale sur ses mots.

## Fichiers hors dépôt nécessaires

`audio/soeur/ref.wav` (21,3 s de sa vidéo TikTok), `audio/soeur/full.wav` (99 s). À redemander au fondateur ; garder son accord écrit.

## Histoire détaillée

Les essais d'octobre et novembre (voix Rémy, Vivienne, voix dessinées, v21 à v44 de « Ah, Lubumbashi ») sont dans `historique-complet.md` : chercher « Voix », « v3 » ou « studio ».
