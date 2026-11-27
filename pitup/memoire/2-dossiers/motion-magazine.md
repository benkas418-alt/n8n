# Motion « le magazine PitUp » (27 nov. 2026)

Demande : « un autre motion design encore plus beau » (après le motion « drench » v7, validé : « tout le reste est parfait »).

## Concept

Tiré de sa référence « I make things move » (une vraie feuille en 3D sous une lumière de fenêtre) : un magazine posé sur une table sombre, des raies de lumière de fenêtre qui glissent, la caméra qui flotte, les pages qui tournent en 3D sur leur reliure, tous les deux temps.

## Recette v1

- `pitup/tools/build_mag.py` → projet `hf/videos/pitup-mag`, 18,5 s. Livré par `livrer.sh` (charte : 0 erreur ; −13,9 LUFS).
- Musique : Jorja Smith « Blue Lights » (COLORS), à partir de 39,87 s (92 BPM, un temps toutes les 0,65 s). Nouveau morceau (règle : changer de musique d'une vidéo à l'autre). Vrai déclic photo sur une page tournée sur deux.
- Pages : couverture (titre PitUp, « ÉDITION LUBUMBASHI », « RDC · 2026 », Alilac Center et avenue en couleurs vives, « Les boutiques de Lubumbashi, / dans ton téléphone. ») → AIR MAX 95 (détourée, ombre sur le papier) → SAMBA (photo) → LA PETITE ROBE NOIRE (détourée) → MONTRES (photo Rolex) → BASIQUES (t-shirts unis détourés) → dernière page « Tu commandes. / On te livre. / Tu paies à la livraison. » (une ligne par temps) + PitUp bleu → fin bleue avec badges.
- Technique : `perspective` CSS + pages `rotateY(-178°)` autour de la reliure, `backface-visibility: hidden`, ombre de pli pendant la rotation ; raies de lumière = deux `repeating-linear-gradient` flous (crème en `soft-light`, nuit en sombre) qui glissent en sens contraire ; caméra = `rotateX` 26 → 14°, `rotateZ` −8 → −3°, échelle 1,06 → 1,18 sur tout le film. Pas de numéro de page (règle).
- Images : celles du motion « drench » (ses 8 photos + appli, plans de Lubumbashi étalonnés `vivid()`).
