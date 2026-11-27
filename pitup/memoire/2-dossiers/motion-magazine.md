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

## v2 (27 nov.) : volume et fiches article PitUp

- Retour sur la v1 : « Faut donner du volume au journal. Ressembler chaque page à une page ou fenêtre d'article PitUp. » + 11 photos d'articles (`scratchpad/appimg/ref2/`, hors dépôt).
- Fiche article reproduite d'après une vraie page produit de pi-tup.com (`/marketplace/product/…`, capture Playwright) : barre blanche (icône PitUp, profil), « ← Produit », photo dans une carte arrondie, carte blanche avec pastille « Vêtements & Mode », nom de l'article, « Les livraisons sont assurées par PitUp », « Paiement à la livraison », « Achat sécurisé », boutons « Ajouter au panier » / « Acheter maintenant ». **Sans prix** (règle) et **sans nom de boutique** (inconnu : ne pas inventer). Couleurs de l'appli ramenées à la charte (bleu #1f88c9, pas de vert).
- Articles : New Balance 9060, pull torsadé Ralph Lauren, mocassins en daim, polos en maille zippés, cardigans en maille, Timberland 6 pouces. Restent en réserve : mocassins en cuir, New Balance 1906R, pulls Ralph Lauren à losanges, polos col ouvert.
- Volume : couverture rigide bleue (#1672ab, ombre #0d2846) sous un bloc de 24 feuilles grises décalées (1,1 × 1,5 px et −2 px en profondeur chacune) : la tranche se voit grâce à l'inclinaison ; ombre de reliure à gauche de chaque page.
- 19,9 s, −14,0 LUFS, charte : 0 erreur.
