# Film de lancement (d'après la référence « Meet heyclicky »)

Demande du 17 nov. 2026 : le fondateur envoie deux vidéos de référence et écrit « On peut nous aussi le faire ».
- Référence A : film de lancement d'appli (ciel, nom tapé au clavier, écrans d'appli, cartes en verre sur les nuages, mots qui changent).
- Référence B : objets en pixel art qui tournent, mots cinétiques, voix émotionnelle. À faire après A.

## Recette (version 1)

- Format 1080×1920, 35,4 s. Musique : l'instrumental de la référence A (séparé avec demucs), coupé avant le jingle Instagram (35,5 s). Fichier hors dépôt.
- Voix : la sœur, recette « Motion point », 3 prises par phrase, choix par transcription + hauteur 190–225 Hz (`pitup/tools/score_la.py`).
- Placement des phrases : `pitup/tools/place_la.py` (début de chaque phrase calé sur la musique). Mixage : `motion_mix.py`.
- Montage : `pitup/tools/build_launch.py` → projet HyperFrames `hf/videos/pitup-launch`.

## Script (voix)

1. Découvre PitUp : les boutiques de Lubumbashi, réunies dans ton téléphone.
2. Tu cherches des baskets, une robe, un téléphone ?
3. Tu trouves, tu compares, tu choisis.
4. Mais nous ne faisons pas que te montrer des articles.
5. Tu commandes, la boutique confirme, et nous te livrons.
6. Tu vends ? Ouvre ta propre boutique, depuis ton téléphone.
7. Plus de cent boutiques locales, et le paiement à la livraison.
8. Tes achats. Ta boutique. Ta ville.
9. Découvre PitUp. Le commerce, simplement.

## Scènes

Ciel au lever du jour + vrais produits de l'appli qui montent + « Découvre PitUp » tapé ; bulle « Tu cherches quoi aujourd'hui ? » + 3 pastilles ;
téléphone 3D avec l'enregistrement de la recherche + 2 fenêtres produits ; manifeste avec « Mais » surligné ; cercle de points + phrase tapée ;
« Ouvre ta boutique. » + vrais logos de boutiques + écran de création de boutique ; 3 cartes en verre sur le ciel (+100 boutiques locales, paiement à la livraison, livraison) ;
« Tes achats / Ta boutique / Ta ville » ; fin : logo, « Découvre PitUp » tapé, slogan, pi-tup.com, « Disponible sur », badges.

## Pièges

- `frames.cjs` n'affiche pas les vidéos : vérifier le ciel et les écrans sur le rendu final, pas sur l'aperçu.
- Whisper écrit « 100 » pour « cent » : le repère de mot « cent » n'est pas trouvé, valeur par défaut utilisée.
- Une boîte `overflow:hidden` de 150 px coupe la descendante du « q » à 128 px : prévoir 185 px.

## État

- v1 livrée le 17 nov. (`livrables/PitUp-Film-lancement-v1.mp4`, 35,4 s, −14,3 LUFS, crête −1,2 dB). Retour du fondateur attendu.
- Ensuite : la version de la référence B.
