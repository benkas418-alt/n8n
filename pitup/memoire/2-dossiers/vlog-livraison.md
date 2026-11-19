# Vidéo « vlog livraison » avec des plans de Lubumbashi

Demande du 19 nov. 2026 : « Un autre en mode vlog livraison avec des plans de la ville de Lubumbashi. »

## Limite dite d'avance (19 nov.)

- Plans de ville disponibles : trajet en voiture (Snapchat, net, 9,6 s), vidéo de @djeudy_243 (paysage 1024×576 : agrandie ×3,3 en vertical, et déjà utilisée dans « Rejoignez-nous » v10 ; crédit ou accord à obtenir). Les anciens plans TikTok sont flous ou déjà publiés.
- Rushs de livraison déjà utilisés dans la vidéo commande-livraison (ne pas les resservir tels quels).
- Proposé : liste de plans à filmer (option A, recommandée) ou version immédiate avec le peu de plans disponibles (option B).

## Script proposé (voix de la sœur, à valider)

« Aujourd'hui, on livre à Golf Tshamalale. » / « La commande vient d'une boutique du centre-ville. » / « Le colis est prêt. On y va. » / « Lubumbashi, en plein après-midi. » / « Ta commande arrive. » / « Tu vérifies, tu paies à la livraison. » / « Encore une livraison réussie. Ta prochaine commande, c'est sur PitUp. »
Quartier de livraison donné par le fondateur le 19 nov. : **Golf Tshamalale**. Type de boutique : à confirmer. Choix A (filmer) ou B (version immédiate) : pas encore donné.

## v1 livrée (19 nov.)

- Choix du fondateur : « Prends la vidéo des chaussures au niveau de la voiture. Vante un peu le client (avait une belle énergie par exemple). » (option B).
- `pitup/tools/build_vlog.py` + `place_vl.py`, projet `hf/videos/pitup-vlog`, 26,5 s, plein écran, étalonnage commun (`match_grade.py`).
- Plans : trajet Snapchat découpé en 3 rues (0,2-3,1 / 3,1-6,4 / 6,4-9,5 s, recadré sans l'autocollant), chaussures dans la voiture (L2 : 0,4 / 3,6 / 8,0 / 16,5 s).
- Voix : « Aujourd'hui, on livre à Golf Tshamalale. Une paire de baskets, commandée sur PitUp. On traverse Lubumbashi. Le client découvre sa paire. Il vérifie chaque détail. Il avait une belle énergie ! Encore une livraison réussie. » + appel et fin déjà validés.
- Sons : whoosh aux 1er et 4e changements, flash + déclic sur « commandée sur PitUp », son du logo. Musique : Raindance (Dave & Tems) à partir de 141,65 s (refrain ; l'intro à 13,3 s avait servi le 5 nov.). −14,5 LUFS.

## v2 essai (19 nov.)

- Retour sur la v1 : voix « trop normale… préparée », vouloir « spontané » ; « d'autres plans de la ville vers midi… en voiture, à pied, plusieurs petits plans mélangés » ; récit « elle est d'abord partie récupérer le colis à la boutique, puis… voir le client » (dicté « collier », compris « colis »). « C'est juste un essai… demain, je pars livrer et je vais prendre toutes les images possibles pour faire le vlog. »
- Fait : `build_vlog2.py` + `place_vs.py`, 31 s. 16 plans courts : trajet Snapchat en 6 morceaux, 5 plans de rue de @djeudy_243 recadrés en vertical (Alilac, rue, immeuble vitré, portière de minibus, minibus) — doux, et accord de @djeudy à obtenir avant toute publication —, colis (L5), chaussures (L2, début décalé à 0,9 s pour éviter un doigt devant l'objectif). Même étalonnage pour tous. Voix spontanée (voir `voix-off.md`). Raindance au refrain.
