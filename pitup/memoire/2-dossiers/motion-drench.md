# Motion design façon « drench » (27 nov. 2026)

Après « C'est nul ce que tu as fait » sur les motions plats, le fondateur choisit le style de sa référence « drench » (vidéo du 16 nov.) et la musique Sleepy Hallow « Anxiety » (ft. Doechii).

## Ce qu'est « drench » (analysé image par image)

Le logo reste fixe au centre ; derrière lui, le décor change à chaque clic du son (environ toutes les 0,7 s) avec une coupe franche : papier texturé, collage de photos en noir et blanc, page nuit avec micro-typographie (adresse, codes, icônes), ordinateur, personnage de dos, pierre qui flotte dans un studio sombre, grille technique. Étalonnage cinéma, grain.

## Recette v1

- `pitup/tools/build_drench.py` → projet `hf/videos/pitup-drench`, 13,3 s. Livré par `livrer.sh` (charte : 0 erreur ; −14,1 LUFS).
- Musique : « Anxiety » à partir de 13,58 s (129 BPM) ; grille des temps calculée sur le morceau entier (sur un extrait, le premier temps manque). Un décor tous les deux temps (0,93 s). Vrai déclic photo sur une coupe sur deux.
- Logo texte PitUp fixe (navy, bleu ou crème selon le fond), courte phrase dessous : « Les boutiques de Lubumbashi » / « dans ton téléphone. » / « Tu commandes, » / « on te livre, » / « tu paies à la livraison. » / « Livré où tu veux. » (d'après « à l'endroit de votre choix » de la pub du collaborateur).
- Décors : papier crème généré (bruit + fibres, aucune image de tiers) ; collage de ses plans Snapchat de Lubumbashi (drapeau du Congo, taxi jaune, minibus) étalonnés ; page nuit (11°40′ S, 27°28′ E ; LUBUMBASHI / HAUT-KATANGA · RDC ; icônes au trait ; PI-TUP.COM) ; téléphone 3D avec l'appli ; « boutiques » en contour ; maillot et baskets blanches **détourés** flottant dans un studio sombre sous un projecteur (comme la pierre) ; grille technique « COMMANDE ✓ LIVRAISON ✓ / PAIEMENT À LA LIVRAISON ».
- Fin : fond bleu, logo, PitUp, slogan, pi-tup.com, « Disponible sur », badges.

## Pièges

- Détourage (rembg, `/home/user/rembg`, API Python, pas la ligne de commande) : sur l'image entière il prend toute la personne ; recadrer serré sur l'article d'abord. Baskets blanches : `isnet-general-use` ; maillot : `birefnet-general-lite` puis couper les mains sur les bords ; baskets noires : raté avec les deux (garder en photo).
- Le contrôle de charte a bloqué une couleur de projecteur hors palette (#2b3b50) : remplacée par #3b4a63 (déjà dans la charte).
- Couleur crème #efe9dd et micro-typographie 21 px ajoutées à la charte.
