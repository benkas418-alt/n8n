# Motion design dessiné avec p5.js (27 nov. 2026)

Demande : « Fais aussi un motion design avec les outils de p5.js. »

## Recette v1

- `pitup/tools/build_p5.py` → projet `hf/videos/pitup-p5`, 14,7 s, sans voix. p5.js 2.4.0 copié dans `assets/p5.min.js`.
- Idée : 240 points bleus = des boutiques qui apparaissent sur un plan de la ville, se relient en réseau, volent former le « P » du logo PitUp (points tirés de `icon_white.png`) sur fond bleu, s'ouvrent en anneau qui bat sur chaque temps, puis se regroupent dans le logo de la fin, au même endroit et à la même taille.
- Texte (phrases validées du film de lancement) : « Les boutiques / de Lubumbashi, / réunies / dans ton téléphone. » → logo en points + PitUp → « Tu commandes. / On te livre. / Tu paies / à la livraison. » → fin (logo, slogan, pi-tup.com, « Disponible sur », badges).
- Musique : Tems « Me & U » à partir de 106,07 s (3e usage de ce morceau : le signaler). Vrai déclic photo sur un changement de scène sur deux.
- Livré par `pitup/tools/livrer.sh` : contrôle de charte passé (0 erreur), −13,9 LUFS.

## Pièges p5.js dans HyperFrames

- Chaque image doit dépendre du temps seulement : p5 en `noLoop()`, positions tirées d'avance (graine fixe, côté Python).
- Ne pas dessiner dans un `onUpdate` de GSAP : un `seek` qui supprime les événements ne l'appelle pas (canvas vide). Dessiner dans un **modifier** d'une interpolation `clock.t` de 0 à la durée : il tourne à chaque rendu.
- `p5.disableFriendlyErrors = true` avant `new p5(...)` ; la page doit avoir `<meta charset="UTF-8">` (sinon p5 2.x plante sur une expression régulière).
- Aperçu Playwright : `page.goto` n'est jamais résolu sur ces pages (chargement sans fin) ; lancer `goto` sans l'attendre, patienter 3 s, puis `seek` et capture avec un délai maximal (`scratchpad/app/t4.cjs`). Servir le dossier en HTTP (`python3 -m http.server`), pas en `file://`.

## Retour du fondateur (27 nov.)

- **v1 refusée** : « C'est nul ce que tu as fait. » Trop plat (fonds unis, texte centré), sans matière, lumière, profondeur ni détail éditorial ; loin de ses références « drench » et « I make things move ». Musiques proposées pour la suite : Sleepy Hallow « Anxiety » (ft. Doechii), Doechii « Anxiety », « LINKEDIN », Jorja Smith « Blue Lights » (COLORS), Sam Recks « Visa », Michael Olise « Raindance » (Dave & Tems), THIZZY52 « Balotelli », « Olise » (remix). Fichiers hors dépôt : `scratchpad/inbox/mus27/`.
