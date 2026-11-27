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

## Version « motion propre » v1 (27 nov.)

- Demande : « au lieu de faire sortir ça en journal, tu peux le faire sortir en motion, animation de texte durant des apparitions… un truc très propre ».
- `pitup/tools/build_clean.py` → projet `hf/videos/pitup-clean`, 19,2 s, même musique (« Blue Lights » dès 39,87 s, même contenu). Livré par `livrer.sh` (charte : 0 erreur ; −13,9 LUFS).
- Déroulé : fond clair DA ; icône + logo PitUp au centre, puis le logo remonte, petit, en haut ; « Les boutiques / de Lubumbashi, » avec l'Alilac Center et l'avenue en cartes arrondies qui glissent des côtés ; « dans ton téléphone. » ; carrousel des six fiches article PitUp (entrée par la droite avec rotation 3D de 28°, sortie à gauche ; dans la fiche, photo qui se pose, nom révélé par masque, lignes puis boutons en cascade) ; promesse « Tu / commandes. » / « On te livre. » / « Tu paies » / « à la livraison. » (surligné) avec trois icônes au trait (panier, camion, billet) qui arrivent une par temps ; fin bleue.
- Mots longs passés sur deux lignes pour rester en 144 px (« de / Lubumbashi, », « Tu / commandes. »).
- Retour : « Certes mais c'est très plat » (+ 9 vidéos de référence, `scratchpad/inbox/ref28/`, hors dépôt).

## Motion propre v2 « profondeur » (27 nov.)

- Ce que les 9 références ont en commun (et que la v1 n'avait pas) : un faisceau de lumière et des halos, des cartes d'interface qui flottent en 3D, une caméra qui avance, des mises au point (flou → net), des reflets sur un sol brillant, un fond sombre qui fait ressortir les cartes claires.
- `pitup/tools/build_depth.py` → projet `hf/videos/pitup-depth`, 19,2 s. Il réutilise `ICO`, `fiche()`, `PROD` et le CSS de la fiche de `build_clean.py`. Même musique (« Blue Lights » dès 39,87 s) : à signaler. Livré par `livrer.sh` : charte 0 erreur, −13,9 LUFS, crête −2,6 dB.
- Déroulé :
  - fond bleu nuit #0d1b2a avec halo bleu et sol en perspective ; un faisceau crème balaie l'écran et révèle « PitUp » par une mise au point ;
  - l'icône PitUp reste en haut ; trois photos de Lubumbashi (Alilac, avenue, tour) flottent à trois profondeurs et la caméra avance entre elles pendant « Les boutiques / de Lubumbashi, / dans ton téléphone. » ;
  - les six fiches article PitUp sur un carrousel circulaire 3D (rayon 760 px) qui arrive du fond puis tourne d'une fiche tous les deux temps ; fiche de face nette, les autres floues, plus sombres et en biais ; reflet sous chaque fiche ;
  - promesse mot par mot avec mise au point (flou 22 px → net) ; fin bleue avec badges.
- Pièges techniques (notés dans `3-atelier/outils.md`) :
  - une opacité < 1 sur un conteneur `preserve-3d` aplatit toute la scène : mettre l'opacité sur chaque fiche ou photo ;
  - un dessin image par image piloté par un « clock » GSAP s'exécute avant les autres tweens du même instant : il affichait l'état de l'image précédente. Calculer angle, profondeur et opacité directement à partir du temps.
- Retour sur la v2 : « C'est trop peu » (voir `1-essentiel/apprentissages.md`, 27 nov.).

## Motion « duo » (27 nov., en cours)

- Ce que ses références apportent :
  - r9 (DataSave, en français) : accroche par une question sur un vrai problème (« Et si tes forfaits Internet ne se perdaient plus… »), puis « Eh bien, ton rêve vient d'être réalisé… Découvre DataSave ».
  - r4 : « Still looking for an editor? » puis une barre de recherche qui tape la question.
  - r1 et r2 : texte qui arrive avec la voix ou au curseur.
  - r5 : un mot à la fois, fond clair et fond foncé en alternance, mot clé plus gros en couleur.
- Texte (acheteurs ; F = sœur, G = garçon) :
  - F : « Tu fais encore le tour de toute la ville pour trouver tes habits ? »
  - G : « Ça, c'est fini. Tout est sur PitUp. »
  - F : « Des baskets, des pulls, des mocassins, des montres… »
  - G : « Les boutiques de Lubumbashi, direct dans ton téléphone. »
  - F : « Tu choisis, tu commandes… »
  - G : « On te livre. »
  - F : « Et tu paies à la livraison. »
  - G : « Allez, télécharge l'appli ! »
- Image :
  - fond clair, grand logo PitUp plat fondu dans le fond (#e4eef7 sur #f5f8fb, ou #3aa2df sur le bleu), qui dérive lentement ;
  - coupes franches vers le bleu PitUp pour les répliques du garçon ;
  - un mur de ses 19 articles en 4 colonnes qui défilent en sens contraire ; à chaque catégorie dite (baskets, pulls, mocassins, montres), ses pièces ressortent et le mot s'affiche dans une pastille bleue ;
  - la fiche article PitUp monte sur « téléphone » ; sur « Tu choisis », la photo change vite ; sur « tu commandes », le bouton « Acheter maintenant » s'enfonce.
- Outils : `pitup/tools/build_duo.py`, `pitup/tools/pick_duo.py` (choix des prises : texte exact, ton, ressemblance, haché).
- Voix :
  - sœur : recette du 14 nov. (`vox_clone_texts.py`, référence = 21,3 premières secondes de sa vidéo TikTok, `scratchpad/inbox/soeur/src.wav`) ;
  - garçon : recette v3 du présentateur (`vox_jobs.py`, amorce F + `ref2.wav`).
- Musique : Dave & Tems « Raindance » (nouvelle).
- Mémoire : VoxCPM (environ 8 Go) et Whisper medium (3 Go) en même temps font tuer le processus. Les lancer l'un après l'autre.
