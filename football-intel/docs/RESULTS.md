# Résultats du backtest réel

## Évaluation complète sur échantillons identiques (2026-11-27, D104)

Saisons 2021-2025, chaque saison prédite par un modèle entraîné sur les saisons d'avant.
Segments de `evaluation/backtest.summarize` : `with_odds` = les mêmes matchs pour le modèle et
le marché ; `without_odds` = les matchs sans cotes, où le marché ne peut pas être comparé.

| Modèle | Matchs | Bon résultat | Log loss | Brier | ECE |
|---|---|---|---|---|---|
| marché (`market_implied`), avec cotes | 8 907 | 53,8 % | 0,9707 | 0,5774 | 0,0135 |
| `routed_competition`, avec cotes | 8 907 | 53,6 % | 0,9711 | 0,5774 | 0,0119 |
| `routed_competition`, sans cotes | 1 939 | 54,7 % | 0,9575 | 0,5675 | 0,0182 |

Écart apparié modèle − marché sur les 8 907 matchs : +0,0004 (IC −0,0013 ; +0,0021) : égalité.
Les 0,9687 sur 10 846 matchs des tables D98 et D99 mélangent les deux segments.

Matrice de confusion sur les 8 907 matchs (lignes = résultat réel, colonnes = favori prévu) :

| | modèle : dom. | nul | ext. | marché : dom. | nul | ext. |
|---|---|---|---|---|---|---|
| victoire dom. (3 877) | 3 161 | 32 | 684 | 3 176 | 5 | 696 |
| nul (2 261) | 1 422 | 23 | 816 | 1 445 | 3 | 813 |
| victoire ext. (2 769) | 1 148 | 26 | 1 595 | 1 160 | 0 | 1 609 |

Le nul n'est presque jamais le favori, pour le modèle comme pour le marché : c'est normal pour
un choix « le plus probable », pas une erreur de probabilité (le nul est bien prévu en
moyenne, 24,6 % contre 25,4 % ; voir l'audit plus bas). Calibration par tranche, compétition
et forme : section « Audit du modèle actif contre le marché ».

## Valeur des cotes betPawa RD Congo, par marché (2026-11-27, D103-D104)

Registre : `scripts/betpawa_value.py` et page « Valeur de mes paris ». État au 27/11, base
locale (les cotes de clôture des coupes d'Europe et leurs résultats n'y sont pas encore ;
le cycle du matin les a) :

- Victoire simple : 47 sélections, 17 matchs, écart à la clôture −3,8 % (échantillon trop faible).
- 1UP : 55 sélections, 41 matchs, écart à la clôture −5,2 % sur 19 matchs (trop faible) ;
  valeur au moment du pari −2,8 % (IC −5,1 % ; −0,2 %) sur 23 matchs (indicatif).
- 2UP : 36 sélections, 25 matchs, écart à la clôture +1,9 % sur 11 matchs (trop faible) :
  hypothèse à vérifier, pas un avantage.
- Coupons : 6, mises 14 000 FC, retours 93 663,23 FC, ROI +569 % (IC −4 % ; +1 401 %).

Règle de décision : un marché n'est déclaré favorable qu'avec l'intervalle de l'écart à la
clôture au-dessus de 0 sur au moins 20 matchs de plusieurs compétitions, et un rendement réel
des coupons cohérent. Aucun marché ne la remplit.

## Audit du modèle actif contre le marché (2026-11-27)

Test saison par saison 2021-2025, cinq grands championnats, 8 907 matchs avec cotes ; chaque
saison jugée avec un modèle entraîné sur les saisons d'avant (`routed_competition` contre
`market_implied`). Chiffres « annoncé / réel ».

- Favoris : le modèle les surestime un peu. Favori à 55-65 % : 59,7 / 57,8 ; à 75 % ou plus :
  80,5 / 78,1. Le marché les sous-estime un peu (69,5 / 73,7 entre 65 et 75 %).
- Nuls : bons en moyenne (24,6 / 25,4), mais sous-estimés dans les matchs déséquilibrés
  (nul annoncé sous 22 % : 16,5 / 19,1). Le marché : 17,8 / 17,3.
- Forme : le modèle réagit trop à la forme. Équipe qui reçoit avec au moins 1 point par match
  de mieux sur 5 matchs : victoire 63,6 / 61,5 ; marché 61,4.
- Compétitions : aucun écart net au marché (Liga et Bundesliga −0,0015, Serie A +0,0003,
  Premier League +0,0020, Ligue 1 +0,0026 de log loss, chacun dans le bruit).
- Indépendance : log loss 0,9711 contre 0,9707 pour le marché ; égal saison par saison.
- Correction testée : mélange moitié modèle, moitié marché, poids appris sur les saisons
  d'avant (0,45 à 0,5) : log loss 0,9701 (−0,0011 contre le modèle, IC −0,0020 ; −0,0002 ;
  −0,0007 contre le marché, IC −0,0015 ; +0,0001), meilleur 5 saisons sur 5. Favori à 55-65 % :
  59,5 / 59,4. Sous le seuil de promotion fixé (0,002) ; même idée que le candidat de D54.

## Sélections nationales : modèle Elo (2026-11-16, D82)

Données : 49 941 matchs de sélections (martj42, CC0). Chaque année est jugée avec un modèle appris
sur les années d'avant. Classement Elo à la manière d'eloratings.net (poids par type de match,
100 points pour l'équipe qui reçoit, plus de points pour un écart large), puis buts de Poisson
selon l'écart de classement, appris sur les 12 dernières années, nuls relevés de 10 %.

| Année | Matchs | Log loss du modèle | Log loss naïve | Bon résultat (1, N, 2) |
|---|---|---|---|---|
| 2018 | 935 | 0,937 | 1,063 | 55 % |
| 2019 | 1 156 | 0,836 | 1,039 | 63 % |
| 2020 | 356 | 0,961 | 1,084 | 54 % |
| 2021 | 1 115 | 0,802 | 1,045 | 65 % |
| 2022 | 970 | 0,915 | 1,039 | 58 % |
| 2023 | 1 064 | 0,860 | 1,053 | 62 % |
| 2024 | 1 231 | 0,899 | 1,064 | 59 % |
| 2025 | 1 002 | 0,818 | 1,044 | 63 % |
| 2026 | 801 | 0,883 | 1,049 | 60 % |

Réglages testés sur 2018-2026 : apprentissage des buts depuis 2000 (0,8738), sur 12 ans (0,8733),
sur 8 ans (0,8734) ; relèvement des nuls de 0 % (0,8715), 5 % (0,8709), 10 % (0,8707, nuls prévus
22,9 % pour 22,9 % réels), 15 % (0,8708). Retenu : 12 ans et 10 %.

Limites : aucune cote historique des sélections pour comparer le modèle aux bookmakers ; le
terrain neutre n'est connu que pour les matchs du fichier (les matchs à venir sont comptés à
domicile) ; plus de buts prévus que réels en 2022 (49 % contre 44 % de plus de 2,5 buts).

## Rotation des titulaires contre le marché (2026-11-13, D78)

Données : compositions Transfermarkt (jeu de données CC0 `dcaribou/transfermarkt-datasets`,
arrêté au 6 juillet 2026). 25 241 matchs des 5 grands championnats reliés à notre base,
même score dans 99,99 % des cas. Rotation calculée sur tous les matchs de l'équipe
(championnat, coupes, Europe). Script : `scripts/rotation_experiment.py`.

Deux variables par équipe, connues environ une heure avant le match :
« changements » (titulaires absents du onze du match précédent) et « cadres absents »
(parmi les 11 joueurs les plus titularisés sur les 10 matchs précédents).

Points au-dessus de ce que prévoit le marché, par match et par équipe :

| Cadres absents | Matchs | Contre les cotes d'avant compositions | Matchs | Contre les cotes de clôture |
|---|---|---|---|---|
| 0-1 | 4 633 | +0,044 | 2 373 | +0,031 |
| 2-3 | 20 817 | 0,000 | 11 288 | −0,005 |
| 4-5 | 14 896 | −0,005 | 8 256 | −0,003 |
| 6 ou plus | 3 768 | −0,030 | 2 177 | −0,004 |

Test saison par saison (chaque saison jugée avec les saisons d'avant) :

- Contre les cotes d'avant compositions (22 057 matchs, 2013-2026) : +0,194 millième par
  match (IC −0,155 ; +0,510), 7 saisons sur 11 meilleures que le marché. Le poids des
  « cadres absents » a le même signe chaque saison, mais l'apport n'est pas prouvé.
- Contre les cotes de clôture (12 047 matchs, 2019-2026) : +0,003 millième
  (IC −0,294 ; +0,289). Le marché intègre déjà les compositions.
- Le nombre brut de changements n'est pas lié à un écart : avec 6 changements ou plus,
  l'équipe fait +0,013 point par match par rapport aux cotes d'avant compositions
  (n = 4 189). Seule l'absence des cadres compte.

Lecture : une équipe qui aligne tous ses cadres fait environ 0,04 point de plus par match
que prévu par les cotes publiées avant les compositions, soit environ 1,5 point de
pourcentage de chance de victoire. C'est moins que la marge d'un bookmaker (5 à 8 %).

## Étape 3 : scénarios combinés (2026-11-04, D74)

91 combinaisons, chacune vue au moins 500 fois : la situation d'une équipe face à celle de l'adversaire,
ou deux situations de la même équipe. Elles s'ajoutent aux scénarios simples et aux poids par championnat
(D73). Gain en millièmes de log loss, 2016-2026, IC 95 % bootstrap.

| Variante | Toutes les ligues | 5 grands championnats | Apport des combinaisons |
|---|---|---|---|
| Scénarios simples (D73) | +0,46 | +0,57 | — |
| + combinaisons, poids plein | +0,48 | +0,50 | +0,020 (IC −0,035 ; +0,076) |
| + combinaisons, mi-poids | +0,48 | +0,56 | +0,015 (IC −0,006 ; +0,035) |
| + combinaisons, quart de poids | +0,47 | +0,57 | +0,005 (IC −0,001 ; +0,011) |

Le plus fort poids appris est −0,024 (équipe en forme qui est aussi un outsider). C'est cinq fois moins
qu'un scénario simple. Ce que les scénarios simples ne disent pas, le marché le sait déjà.

## Étape 2 : oubli et poids par championnat (2026-11-04, D73)

Même test que ci-dessous (2016-2026, chaque saison jugée avec les saisons d'avant), gain en millièmes.

| Variante | Toutes les ligues | 5 grands championnats | PL | BL | SA | Liga | L1 |
|---|---|---|---|---|---|---|---|
| Poids communs (D72) | +0,49 | +0,38 (IC −0,26 ; +1,03) | +0,47 | −0,95 | +0,94 | +0,87 | +0,30 |
| Plus poids par championnat, pénalité 1 000 | +0,46 | +0,57 (IC +0,15 ; +1,01) | +0,71 | −0,24 | +1,19 | +0,71 | +0,30 |
| Plus poids par championnat, pénalité 3 000 | +0,33 | +0,44 (IC +0,21 ; +0,70) | +0,49 | −0,10 | +0,80 | +0,64 | +0,27 |

Oubli des vieilles saisons (poids communs) : demi-vie de 8, 4, 2 et 1 saison, gain de +0,48, +0,46, +0,40
et +0,29, contre +0,49 sans oubli. Sur les 3 dernières saisons seules, même ordre : +0,54, +0,50, +0,43 et +0,29,
contre +0,57. Les tendances ne s'usent pas : il n'y a rien à oublier.

## Scénarios qui ajustent le marché (2026-11-04, D72)

`analysis/scenario_adjust.py` : 164 142 matchs de championnat avec cote de marché. Chaque saison de 2016
à 2026 est jugée avec des poids appris sur les saisons d'avant uniquement. Gain = log loss du marché
moins log loss du marché ajusté, en millièmes (positif = l'ajustement fait mieux). IC 95 % bootstrap.

| Scénarios utilisés | Gain | IC 95 % | Saisons gagnées |
|---|---|---|---|
| Les 12 | +0,49 | +0,24 ; +0,72 | 11/11 |
| Sans les grands favoris | +0,29 | +0,09 ; +0,46 | 8/11 |
| Grands favoris seuls | +0,27 | +0,10 ; +0,44 | 10/11 |
| Forme trompeuse (unlucky, lucky, outsider en forme, favori en méforme) | +0,23 | +0,07 ; +0,39 | 9/11 |
| Fatigue (Coupe d'Europe, repos court, calendrier chargé) | +0,03 | −0,04 ; +0,09 | 6/11 |

Le résultat ne dépend presque pas de la pénalité (+0,47, +0,49 et +0,45 pour 50, 200 et 1 000).
L'ajustement moyen d'un match touché est de 0,9 point de probabilité, et de 9 points au plus.
Le gain est petit à côté de la marge de betPawa (4 à 15 %) : il aide à choisir les sélections les plus
sûres, il ne rend pas un pari rentable à lui seul.

## betPawa (Cameroun) contre Pinnacle, saison 2026-27 (2026-10-30, D68)

`scripts/oddspapi_backtest.py` (workflow « betPawa vs Pinnacle backtest », run 41104481324) :
403 matchs joués des 5 championnats depuis le 1er août, 7 038 cotes betPawa, dernière cote
avant le coup d'envoi chez les deux. Cote juste = Pinnacle sans marge (1X2, ±2,5, DC, DNB),
ou tirée du 1X2 et du ±2,5 de Pinnacle par le calcul de D66 (premier but, 2UP, BTTS).
Espérance = cote × probabilité juste − 1, IC 95 % bootstrap.

| Marché | Sélection | n | Espérance | Part des cotes au-dessus de la cote juste |
|---|---|---|---|---|
| 2UP | extérieur | 391 | −0,1 % [−0,5 ; +0,3] | 47 % |
| 2UP | domicile | 391 | −1,3 % [−1,6 ; −0,9] | 34 % |
| 1X2 | nul | 391 | −1,9 % [−2,3 ; −1,5] | 31 % |
| ±2,5 | moins | 391 | −3,1 % [−3,5 ; −2,6] | 15 % |
| DC | 1X / X2 / 12 | 391 chacun | −3,8 % / −4,5 % / −6,6 % | 0 à 2 % |
| BTTS | non / oui | 391 chacun | −4,4 % / −9,5 % | 8 % / 0 % |
| Premier but | domicile / extérieur | 391 chacun | −5,0 % / −5,3 % | 1 % |
| 1X2 | domicile / extérieur | 391 chacun | −6,1 % / −7,0 % | 3 % / 5 % |
| DNB | 1 / 2 | 391 chacun | −9,5 % / −11,4 % | 0 % |
| ±2,5 | plus | 391 | −6,6 % [−6,8 ; −6,3] | 0 % |

Lecture : aucun marché n'est rentable en simple. Le 2UP est le seul à la cote juste, parce que
betPawa le cote presque comme le 1X2 alors qu'il paie plus souvent ; près de la moitié des
2UP extérieur sont au-dessus de la cote juste. Avec le Bonus Gagnant (D67), un combiné de
sélections à la cote juste a une espérance proche du taux de bonus × (1 − probabilité de
gain) : la seule voie positive est un combiné de 2UP choisis au-dessus de la cote juste.
Limites : betPawa Cameroun, pas RD Congo ; la cote juste du 2UP vient d'un calcul (Poisson,
buts dans un ordre aléatoire), un peu optimiste au milieu de l'échelle (D58) ; le « X » du
2UP (−26,5 %) n'est pas lu, sa définition chez betPawa reste à vérifier.

## Modèle contre marché par compétition (2026-10-30, D68)

`scripts/competition_edge.py` : `routed_competition` hors échantillon, saisons 2021-22 à
2026-27. Écart de log loss modèle moins marché (négatif = modèle meilleur), IC 95 %
bootstrap ; CLV des choix du modèle (prix moyen avant clôture, seuil 3 %).

| Compétition | n | contre prix moyen | contre clôture | choix | CLV |
|---|---|---|---|---|---|
| Liga | 1 999 | −0,0012 [−0,0045 ; +0,0018] | +0,0008 [−0,0038 ; +0,0052] | 549 | −1,7 % [−2,4 ; −1,1] |
| Serie A | 1 988 | +0,0002 [−0,0035 ; +0,0040] | +0,0033 [−0,0013 ; +0,0078] | 536 | −2,9 % [−3,4 ; −2,4] |
| Premier League | 1 980 | +0,0024 [−0,0014 ; +0,0064] | +0,0045 [−0,0003 ; +0,0094] | 719 | −2,8 % [−3,2 ; −2,4] |
| Ligue 1 | 1 750 | +0,0023 [−0,0017 ; +0,0063] | +0,0023 [−0,0029 ; +0,0077] | 422 | −2,5 % [−3,2 ; −1,8] |
| Bundesliga | 1 593 | −0,0009 [−0,0051 ; +0,0034] | +0,0025 [−0,0030 ; +0,0079] | 503 | −2,4 % [−3,0 ; −1,8] |

Coupes et compétitions UEFA : aucune cote de marché en base sur ces saisons, pas de mesure.

Lecture : dans aucun championnat le modèle ne fait mieux que le marché. Il est à égalité
avec le prix moyen, un peu derrière la clôture, et ses choix perdent 1,7 à 2,9 % contre la
clôture partout. La piste « un championnat où le modèle est devant » est fermée. Reste
celle des cotes betPawa contre la cote juste (D68).

## Test des xG Understat (2026-10-29)

Question : les buts attendus (xG) améliorent-ils le modèle à cotes ? Script :
`scripts/xg_experiment.py`. Source : fichiers de tirs Understat republiés par
worldfootballR_data sur GitHub (4 championnats, 2014-15 à septembre 2025). Understat n'est
jamais interrogé (son robots.txt interdit tous les robots).

Rattachement : 133 noms d'équipe sur 134 (Pisa manque, absent des saisons testées), 16 030
matchs rattachés, 2 écartés pour score différent. Variables fixées avant tout résultat : xG
pour et contre, moyenne des 10 derniers matchs (au moins 5), et l'écart entre les deux équipes.

Saisons 2021 à 2024, 5 705 matchs de championnat (98,6 % avec xG), hors échantillon :

| Comparaison | Log loss (IC 95 %) |
|---|---|
| Avec xG − modèle actif | +0,0008 [+0,0000 ; +0,0015] |
| Avec xG − sans xG, mêmes lignes d'entraînement | +0,0008 [+0,0001 ; +0,0015] |
| Modèle actif − marché avant clôture | −0,0001 [−0,0023 ; +0,0021] |

CLV au prix moyen (avantage > 3 %) : −2,4 % pour le modèle actif, −2,7 % avec xG.

Lecture : les xG **dégradent** légèrement le modèle. Le marché les intègre déjà, et le modèle
lit déjà les tirs cadrés des 5 derniers matchs, qui portent la même information.

## Cote de clôture (CLV) et mélange modèle-marché (2026-10-29)

Question : le modèle voit-il quelque chose que le marché n'intègre qu'au coup d'envoi ?
Commande : `footintel clv`. Étude détaillée : `scripts/clv_study.py`. Saisons 2021 à 2025,
hors échantillon, 6 528 matchs de championnat avec la cote de clôture Pinnacle (la plus juste
des cotes publiques). Prix pris : moyenne des bookmakers avant clôture.

| Modèle | Log loss − clôture Pinnacle | Paris (avantage > 3 %) | CLV moyenne |
|---|---|---|---|
| Marché avant clôture | +0,0028 [+0,0012 ; +0,0045] | — | — |
| `routed_competition` | +0,0028 [+0,0006 ; +0,0050] | 2 307 | **−2,5 %** [−2,7 ; −2,2] |
| `routed_competition_blend` | +0,0019 [+0,0002 ; +0,0037] | 295 | −2,0 % [−3,1 ; −0,7] |

Lecture :

1. **Pas d'avantage mesuré.** Au prix moyen, la CLV des paris du modèle est négative, IC
   entièrement sous zéro, quel que soit le seuil d'avantage (0, 3, 5 %).
2. **Un vrai signal, trop faible.** Quand le modèle estime une issue au-dessus du marché, la
   cote de cette issue baisse avant le coup d'envoi dans 60,6 % des cas, contre 51,4 % pour
   l'ensemble des issues. Le modèle anticipe donc une partie du mouvement, mais pas assez pour
   couvrir la marge du bookmaker (environ 5 % sur le prix moyen).
3. **Piège écarté : le meilleur prix.** Au prix maximum des bookmakers, la CLV devient positive
   (+1,9 % à 3 %). Mais la même règle sans modèle (probabilité du marché lui-même) fait mieux :
   +4,5 %. Ce gain vient des cotes isolées du maximum, pas du modèle.

Mélange modèle-marché (`routed_competition_blend`, D54) : moyenne géométrique des
probabilités du modèle à cotes et du marché sans marge, poids appris hors échantillon sur les
20 % les plus récents de chaque fenêtre d'entraînement. Backtest 2021-2025 (run 3) :
log loss 0,9649 contre 0,9655, soit −0,0006, sous le seuil D9 de 0,002. Contre le marché :
−0,0009 [−0,0020 ; +0,0003], IC qui contient 0. Non promu.

## Test de « qui marque en premier », saison 2026-27 (2026-10-29)

Question : l'estimation du premier but de la fiche de match (D52) tient-elle sur des matchs
réels ? Script : `scripts/first_goal_check.py`.

Méthode : `routed_competition` entraîné sur les saisons antérieures seulement, puis appliqué
aux matchs de championnat de 2026-27 (hors échantillon). Ses buts attendus donnent, par un
processus de Poisson, P(domicile ouvre le score), P(extérieur), P(aucun but). Le vrai premier
but vient des minutes OneFootball. 322 matchs : 175 ouverts par l'équipe à domicile, 126 par
l'équipe à l'extérieur, 21 sans but.

| Estimation | Log loss (3 issues) |
|---|---|
| Modèle (buts attendus, Poisson) | **0,8448** |
| Part de victoire 1X2 | 0,8610 |
| Fréquences observées (référence naïve) | 0,8766 |

Modèle − référence naïve : −0,0318 [IC 95 % −0,0603 ; −0,0025]. L'équipe que le modèle voit
ouvrir le score l'a fait dans **63,1 %** des 301 matchs avec au moins un but.

| Chance annoncée d'ouvrir le score | n | Annoncé | Observé |
|---|---|---|---|
| 20-30 % | 49 | 26,0 % | 18,4 % |
| 30-40 % | 124 | 35,8 % | 35,5 % |
| 40-50 % | 221 | 45,3 % | 42,1 % |
| 50-60 % | 152 | 54,5 % | 58,6 % |
| 60-70 % | 70 | 64,5 % | 68,6 % |
| 70 % et plus | 24 | 74,9 % | 75,0 % |

Lecture : l'estimation est utile et bien calibrée au centre. Aux extrêmes, elle est un peu
prudente : l'équipe favorite ouvre le score un peu plus souvent qu'annoncé, l'outsider un peu
moins. Échantillon d'une demi-saison : à refaire en fin de saison.

## « Forte en 1re ou en 2e mi-temps » : un trait qui se répète ? (2026-10-29)

Question : une équipe meilleure dans une mi-temps que dans l'autre le reste-t-elle ? Script :
`scripts/half_profile_check.py`. 164 135 matchs de championnat avec score à la pause
(2005-2026), chiffres de chaque équipe moins la moyenne de son championnat et de sa saison.

| Mesure | Saison → saison suivante (7 445 paires) | Matchs impairs → pairs, même saison (8 444) |
|---|---|---|
| Écart de différence de buts 1re − 2e mi-temps | r = 0,045 [0,022 ; 0,068] | r = 0,035 |
| Part des buts marqués après la pause | r = 0,009 [−0,016 ; 0,032] | r = −0,006 |
| Pour comparaison : différence de buts par match | r = 0,469 | — |

Lecture : la force d'une équipe se répète nettement ; son profil par mi-temps presque pas,
même au sein d'une saison. « Marque surtout après la pause » décrit le passé, pas le
prochain match. Les profils par mi-temps et par tranche de 15 minutes (onglet « Moments du
match ») sont affichés avec cet avertissement ; la phrase de la fiche qui en tirait un
scénario est retirée (D59).

## Marchés selon l'ordre des buts (1UP, 2UP, premier but), saison 2026-27 (2026-10-29)

Question : les probabilités 1UP, 2UP, premier but et « ouvre le score et gagne » (onglet
Paris, vérificateur de cotes) tiennent-elles sur les vrais déroulements ? Script :
`scripts/markets_check.py`. Modèle entraîné avant 2026-27, matchs prédits hors échantillon ;
ordre des buts tiré des minutes OneFootball. 150 matchs (Premier League et Liga lus ce jour).

| Log loss | Buts attendus du modèle | Ajusté au 1X2 | Ajusté au 1X2 + plus de 2,5 | Fréquence naïve |
|---|---|---|---|---|
| Premier but (3 issues) | 0,8952 | 0,8862 | 0,8914 | 0,9272 |
| 1UP domicile | 0,6339 | 0,6280 | 0,6353 | 0,6859 |
| 1UP extérieur | 0,6497 | 0,6630 | 0,6537 | 0,6931 |
| 2UP domicile | 0,6059 | 0,6071 | 0,6125 | 0,6730 |
| 2UP extérieur | 0,5690 | 0,5590 | 0,5591 | 0,6318 |
| Domicile ouvre et gagne | 0,5893 | 0,5967 | 0,5966 | 0,6365 |
| Extérieur ouvre et gagne | 0,5217 | 0,5074 | 0,5075 | 0,5731 |

Lecture : les trois calculs battent la fréquence naïve sur chaque marché ; leurs écarts entre
eux sont dans le bruit d'un si petit échantillon. Le site garde l'ajustement 1X2 + plus de
2,5, seul cohérent avec les marchés de buts (« aucun but »). Calibration (6 marchés réunis) :
annoncé 42 %, observé 37 % entre 35 et 50 % ; annoncé 72 %, observé 67 % entre 65 et 80 % :
un peu trop optimiste au milieu. À refaire avec les quatre championnats et la saison complète.

## Test des compositions OneFootball, saison 2026-27 (2026-10-29)

Question : les compositions des matchs précédents (OneFootball, D50) améliorent-elles la
prévision 1X2 des quatre championnats ? Script : `scripts/lineup_experiment.py`.

Variables, calculées pour chaque équipe à partir de ses **matchs précédents** de la saison
seulement (la composition du match lui-même n'est connue qu'une heure avant le coup d'envoi) :
titulaires changés entre ses deux derniers matchs (`rot_last`), titulaires habituels absents
de son dernier match (`core_out_last`), formation du dernier match différente de l'habituelle
(`form_change_last`). Écart domicile − extérieur. Une équipe a besoin de 3 matchs précédents :
205 matchs utilisables (2026-09-03 au 2026-10-26).

Modèles : régression logistique sur les probabilités du marché seules (base), puis avec les
trois variables (candidat). Log loss 1X2, négatif = meilleur, IC 95 % bootstrap apparié.

| Test | Entraînement | Test | Marché | Base | Candidat | Candidat − base |
|---|---|---|---|---|---|---|
| Semaine passée (19 au 26 oct.) | 161 | 44 | 0,9659 | 0,9789 | 0,9593 | −0,0196 [−0,0617 ; +0,0255] |
| Semaine par semaine (4 semaines) | 60 à 161 | 117 | 0,9397 | 0,9713 | 1,0053 | +0,0340 [−0,0024 ; +0,0707] |

Lecture : aucun gain démontré. Sur la semaine passée, le candidat fait mieux mais l'IC contient
0 avec 44 matchs. Sur 117 matchs testés semaine par semaine, il fait **moins bien** que la base.
Les deux modèles entraînés sur si peu de matchs font moins bien que le marché brut. Loin des
300 matchs de test exigés par D9. Le modèle actif ne change pas (D51).

## Test ClubElo (2026-10-28)

Question : la cote ClubElo d'un club, publiée avant le match, améliore-t-elle le modèle actif ?
ClubElo note tous les clubs européens dans un même système, alors que notre Elo (D14, D22) part
de valeurs posées a priori par championnat.

Données : historique ClubElo du dépôt `xgabora/Club-Football-Match-Data` (licence MIT), deux
relevés par mois. Seuls les relevés jusqu'au 2025-06-01 sont utilisés : après, le fichier
contient une continuation provisoire, pas les vraies valeurs ClubElo. Pour chaque match, on
prend le dernier relevé daté **avant** le jour du match (au plus 45 jours avant).

Correspondance des noms : 720 noms identiques, 41 rapprochements automatiques relus, 18 ajouts
manuels. 4 rapprochements faux retirés (Odd → Hodd, Northwich → Norwich, Lewes → Leeds,
Olympiakos Volou → Olympiakos). Couverture des matchs testés (les deux équipes notées) :
Liga et Serie A 100 %, Premier League 94 %, Bundesliga 90 %, Ligue des champions 81 %,
Ligue Europa 64 %, Conference League 34 %. Une valeur absente est remplacée par la médiane,
avec une colonne indicatrice.

Candidats : `routed_competition` + `ce_diff`, `ce_home`, `ce_away` dans les trois parties
(`rc_ce_all`), ou seulement dans la partie sans cotes et les buts (`rc_ce_cups`).
Walk-forward 2021-22 à 2024-25, 7 533 matchs. Écart de log loss 1X2 contre le modèle actif
(négatif = meilleur), IC 95 % bootstrap :

| Segment | n | `rc_ce_all` | `rc_ce_cups` |
|---|---|---|---|
| Tous (règle D9) | 7 533 | −0,0007 [−0,0014 ; +0,0001] | −0,0007 [−0,0015 ; −0,0000] |
| Championnats (avec cotes) | 5 784 | 0,0000 [−0,0003 ; +0,0003] | 0 (inchangé) |
| Coupes d'Europe (sans cotes) | 1 749 | −0,0031 [−0,0062 ; +0,0002] | −0,0031 [−0,0064 ; +0,0001] |
| dont Ligue des champions | 564 | −0,0051 [−0,0106 ; −0,0001] | −0,0051 [−0,0103 ; +0,0002] |
| dont Ligue Europa | 610 | −0,0051 [−0,0105 ; +0,0003] | −0,0051 [−0,0108 ; +0,0008] |
| dont Conference League | 575 | +0,0011 [−0,0042 ; +0,0066] | +0,0011 [−0,0043 ; +0,0066] |

Par saison, les coupes gagnent les 4 années (−0,0014, −0,0039, −0,0062, −0,0013). Marchés de
buts : plus/moins de 2,5 meilleur en championnat (−0,0005 [−0,0009 ; −0,0001]), neutre en
coupe ; BTTS neutre.

**Décision : non promu.** Sur l'ensemble, le gain (0,0007) est sous le seuil de 0,002. Sur les
coupes seules, le gain (0,0031) dépasse le seuil mais l'intervalle touche 0. Les cotes du
marché contiennent déjà l'information ClubElo en championnat. La piste reste ouverte pour les
coupes sans cotes, surtout la Ligue des champions et la Ligue Europa : la Conference League,
mal couverte (34 %), n'en profite pas.

Limite pratique : la vraie série ClubElo s'arrête au 2025-06-01 dans ce fichier. L'utiliser
en production demande l'API `api.clubelo.com`. Depuis ce conteneur, elle répond par une
coupure de connexion (HTTPS) ou HTTP 502 (HTTP), et le site affiche une vérification
anti-robot : non utilisable ici, à retester depuis le VPS.

## Changement de jeu et réentraînement mois par mois (2026-10-26)

À période égale (août au 26 octobre), 4 championnats cibles : 2026-27 a un record de tirs
(28,4/match contre 22,4 à 26,1 de 2015 à 2024) et de tirs cadrés (9,7), et 3,07 buts/match.
2025-26 était au contraire la plus fermée (2,68 buts, 8,4 tirs cadrés). Victoires à domicile
et nuls stables.

Simulation : chaque mois d'août 2024 à octobre 2026, réentraînement du modèle 1X2 à cotes sur
les seuls matchs passés, prédiction du mois. Log loss 1X2 :

| Version | 2025-26 (n = 1 446) | 2026-27 (n = 319) |
|---|---|---|
| Standard (tout l'historique, chaque mois) | 0,9796 | 0,9600 |
| 12 derniers mois × 5 | 0,9796 | 0,9600 |
| Couche adaptative (erreurs des 12 derniers mois, par championnat) | 0,9829 | 0,9667 |
| Marché | 0,9795 | 0,9568 |

Lecture : renforcer les 12 derniers mois ne change rien (écart 0,0000, IC ±0,002) ; la couche
adaptative est moins bonne (elle apprend du bruit). Le changement de jeu touche le volume
(tirs, buts), pas l'issue des matchs ; le 1X2 n'en profite pas.

## Fenêtre d'entraînement : historique complet ou saisons récentes (2026-10-26)

Modèle `routed_competition`, entraîné seulement sur les saisons antérieures au test.
Écart de log loss 1X2 contre l'entraînement actuel (toutes les saisons), IC 95 % bootstrap.

| Entraînement | Test 2025-26 (n = 1 446) | Test 2026-27 (n = 319) |
|---|---|---|
| Toutes les saisons (actuel) | 0,9798 | 0,9599 |
| 3 dernières saisons | −0,0006 [−0,0032 ; +0,0021] | +0,0053 [−0,0027 ; +0,0135] |
| Dernière saison seule | +0,0014 [−0,0050 ; +0,0072] | +0,0064 [−0,0071 ; +0,0197] |
| Toutes, pondération demi-vie 2 saisons | −0,0010 [−0,0034 ; +0,0012] | +0,0030 [−0,0023 ; +0,0085] |
| Marché (référence) | 0,9795 | 0,9568 |

Lecture : aucune fenêtre ne bat l'historique complet de façon fiable ; une seule saison
(environ 9 000 matchs) est la pire variante dans les deux tests. L'entraînement actuel
(jusqu'au 21/10/2026, saison 2025-26 incluse) est conservé.

## Scénarios d'avant-match contre le marché (2026-10-25, analyse n° 22)

Points pris moins points attendus par le marché, à cote égale. Toutes saisons avec cotes
depuis 2005 (4 championnats cibles et championnats de contexte).

| Scénario | n | Écart (pt/match) | IC 95 % | Statut |
|---|---|---|---|---|
| Résultats inférieurs au jeu (tirs cadrés +1,5/match, ≤ 1,2 pt/match) | 7 517 | +0,066 | [+0,038 ; +0,093] | confirmé |
| Repos court (≤ 3 j) face à un adversaire reposé (≥ 5 j) | 4 999 | +0,040 | [+0,008 ; +0,073] | confirmé |
| Outsider en forme (≥ 2 pts/match, < 35 %) | 22 103 | −0,019 | [−0,035 ; −0,003] | confirmé |
| Résultats supérieurs au jeu (≥ 2 pts/match, tirs cadrés négatifs) | 6 123 | −0,039 | [−0,070 ; −0,009] | confirmé |
| En grande forme (≥ 2,4 pts/match) | 28 756 | −0,017 | [−0,031 ; −0,003] | nouveau, à surveiller |
| Coupe d'Europe dans les 7 jours, calendrier chargé, méforme, grands favoris, défense perméable | — | ≈ 0 | contient 0 | aucun effet : le marché en tient compte |

**Test en modèle (2026-10-26)** : `routed_competition_scen` ajoute les 4 scénarios confirmés
(0/1 pour chaque équipe) au modèle à cotes. Walk-forward 2023-24 à 2025-26, 5 465 matchs :
écart de log loss 1X2 −0,0001, IC 95 % [−0,0004 ; +0,0002] (2023 : −0,0005 ; 2024 : 0,0000 ;
2025 : +0,0003). **Rejeté** : gain bien sous le seuil de 0,002 (D9). Le modèle actif, qui
utilise déjà la forme et les tirs cadrés, capte l'essentiel de ces effets.

Lecture : le marché suit un peu trop les résultats récents et pas assez l'équilibre des tirs
cadrés ; il pénalise un peu trop la fatigue. Les effets sont faibles (0,02 à 0,07 point par
match) : ils ne suffisent pas à battre la marge d'un bookmaker seuls. Prochaine étape : les
tester comme variables d'un modèle candidat, avec les règles de promotion D9.

## Candidats phase 6 — calibration des coupes et Dixon-Coles (2026-10-22)

Walk-forward sur 2023-24, 2024-25 et 2025-26 (5 465 matchs testés, dont 1 127 de coupes
d'Europe). Référence : `routed_competition` v1 (actif). Écart = candidat − référence
(négatif = mieux), IC 95 % bootstrap apparié.

| Candidat | Segment | 1X2 | Plus/moins 2,5 | BTTS | Décision |
|---|---|---|---|---|---|
| `routed_competition_cal` (température, branche sans cotes) | coupes | +0.0006 [−0.0001 ; +0.0013] | 0 | 0 | rejeté |
| | championnats | 0 (non concernés) | 0 | 0 | |
| `routed_competition_dc` (Dixon-Coles) | coupes | 0 | 0 | −0.0001 [−0.0007 ; +0.0004] | rejeté |
| | championnats | 0 | 0 | −0.0004 [−0.0006 ; −0.0001] | |

Lecture :
1. **La calibration par température n'aide pas** : ajustée sur la fin de chaque fenêtre
   d'entraînement, elle dégrade légèrement les coupes. L'écart de calibration observé (ECE
   0.03-0.044) n'est pas un simple excès ou défaut de confiance global.
2. **Dixon-Coles** : gain réel mais minime sur BTTS en championnat, sous le seuil de 0.002
   fixé à l'avance (D9/D19). Plus/moins 2,5 est inchangé par construction : la correction
   déplace des probabilités entre 0-0, 1-0, 0-1 et 1-1, qui ont tous au plus 2 buts.
3. Le modèle actif reste `routed_competition` v1. Les deux candidats restent disponibles
   pour une réévaluation avec plus de données.

## Run 13 — moteur de tendances statistiques (2026-10-22)

8 076 tendances (compétitions et 78 équipes des compétitions cibles), fenêtres courte /
moyenne / longue, tests adaptés aux petits échantillons (Fisher, Welch t), Benjamini-Hochberg.
Commandes : `footintel trends run`, `footintel trends evaluate`, `footintel trends report`.

### Persistance hors échantillon (as-of 1er janvier et 1er août, 2010-2025)

Part d'un écart mesuré qui se retrouve dans la fenêtre suivante (pente, IC 95 %) :

| Indicateur | Compétitions (380 matchs) | Équipes (19 matchs) |
|---|---|---|
| Buts par match | +0.52 [+0.46 ; +0.58] | buts marqués +0.35, encaissés +0.37 |
| Plus de 2,5 buts | +0.45 [+0.39 ; +0.52] | +0.29 [+0.28 ; +0.30] |
| Tirs / tirs cadrés | — | +0.53 / +0.52 |
| Points | — | +0.37 [+0.36 ; +0.39] |
| Résultat moins attente Elo | — | **+0.14** [+0.12 ; +0.15] |

Lecture : les indicateurs de jeu (tirs) persistent plus que les résultats ; une série
« au-dessus de son niveau Elo » est surtout du bruit. Avec des tests corrects pour 6 et 19
matchs, aucune tendance d'équipe n'est significative après correction ; 38 signaux émergents
du calcul précédent (tests trop permissifs, corrigés) sont passés « non confirmés ».

### Apport au modèle actif, par catégorie (2021-22 à 2025-26, 9 168 matchs)

| Catégorie | Effet démontré (IC 95 % sous 0) |
|---|---|
| Profil offensif/défensif des équipes | score exact −0.0034, plus/moins 2,5 −0.0013, plus/moins 3,5 −0.0017, BTTS −0.0009, mi-temps 1X2 −0.0011 ; 1X2 coupes −0.0025 |
| Sur/sous-performance vs Elo | très faible (score exact −0.0011) |
| État à la mi-temps | score exact −0.0008 ; **dégrade** le 1X2 en championnat (+0.0003) |
| Profil de scores de la compétition | quasi nul |

Promotion officielle du candidat `routed_competition_scoring` contre l'actif (2023-2025,
5 465 matchs) : **rejetée**. 1X2 −0.0008 [−0.0013 ; −0.0003] et plus/moins 2,5 −0.0014
[−0.0024 ; −0.0004] : gains réels mais sous les seuils fixés (0.002). 2026-27 (283 matchs) :
−0.0014 [−0.0055 ; +0.0025]. Le modèle actif reste `routed_competition` v1.

### Correction de données trouvée pendant ce travail

openfootball : 11 matchs de la C1 2019-20 joués en août 2020 (tournoi de Lisbonne) étaient
datés d'août 2019. L'année est maintenant déduite de la plage de dates déclarée par le
fichier ; les 11 lignes fausses ont été supprimées (journalisé) et remplacées.


## Run 8 — tendances par compétition et apport de chaque niveau (2026-10-22)

Base : 187 167 matchs réels (4 championnats cibles, 24 championnats et divisions de
contexte, C1/C3/C4). Rapport complet : [reports/competitions_2026-10-22.md](reports/competitions_2026-10-22.md).

### Particularités validées hors échantillon

Écart entre le taux observé et un modèle Elo-Poisson qui ignore la compétition, estimé sur
2006-2020 puis vérifié sur 2021-2026 (2 758 tests, correction de Benjamini-Hochberg) :

| Compétition | Effet | 2006-2020 | 2021-2026 |
|---|---|---|---|
| Bundesliga | plus de 2,5 buts | +7.8 pts [+6.3 ; +9.3], n = 4 284 | +10.8 pts, n = 1 584 |
| Bundesliga | les deux marquent | +6.0 pts [+4.5 ; +7.5] | +9.6 pts |
| Ligue des champions | plus de 2,5 buts | +5.5 pts [+2.7 ; +8.2], n = 1 244 | +9.1 pts, n = 753 |
| Premier League | plus de 2,5 buts | +2.3 pts [+0.9 ; +3.6], n = 5 320 | +5.8 pts, n = 1 970 |
| Premier League | plus de 2,5 buts, début de saison | +4.1 pts [+1.8 ; +6.4] | +6.2 pts |
| Serie A | match nul | +1.6 pts [+0.5 ; +2.8], n = 5 320 | +3.5 pts |
| Liga | victoire extérieure | −2.3 pts [−3.5 ; −1.2], n = 5 320 | −3.2 pts |

Effets « robustes » sur 2006-2020 mais **non confirmés** ensuite (exemples) : Premier League,
plus de victoires à domicile en fin de saison ; plus de nuls en milieu de saison.

### Apport prédictif de chaque niveau (2021-22 à 2025-26, 9 168 matchs)

| Niveau ajouté | 1X2 championnats | 1X2 coupes d'Europe | Plus/moins 2,5 | BTTS |
|---|---|---|---|---|
| Tendances de la compétition | aucun effet démontré | −0.0045 [−0.0089 ; −0.0003] | −0.0069 [−0.0090 ; −0.0044] | −0.0044 [−0.0063 ; −0.0028] |
| Phase, tour, manche | aucun effet | aucun effet | +0.0003 (dégrade) | aucun effet |
| Équipes (forme, tirs, fatigue) | −0.0036 [−0.0059 ; −0.0012] | aucun effet | −0.0021 [−0.0035 ; −0.0006] | aucun effet |
| Cotes | −0.0163 [−0.0202 ; −0.0123] | pas de cotes | — | — |

### Décision

Nouveau modèle actif `routed_competition` (cotes + équipes en championnat, tendances de
compétition en coupe, buts par Poisson sur tendances de compétition + attaque/défense des
équipes ; phase exclue). Promu par la règle secondaire fixée avant l'évaluation :
1X2 −0.0005 [−0.0015 ; +0.0005] (non dégradé), plus/moins 2,5 **−0.0116 [−0.0154 ; −0.0076]**
sur 5 465 matchs. Vérification sur la saison 2026-27, jamais utilisée pour un choix
(283 matchs, sous le minimum de décision) : plus/moins 2,5 −0.0268 [−0.043 ; −0.009].

Limite : la configuration a été choisie sur 2021-2025, période qui chevauche le test de
promotion. La vérification 2026-27 réduit ce biais sans l'éliminer ; le suivi en direct
des prochaines semaines est la vraie validation.


## Run 6 — avec coupes d'Europe et championnats de contexte (2026-10-22)

Walk-forward : pour chaque saison testée (2021-22 à 2025-26), les modèles sont entraînés
sur toutes les saisons antérieures, y compris les 13 championnats de contexte. Le test porte
**uniquement sur les compétitions cibles** : 4 championnats et C1, C3, C4.
Soit 9 168 matchs de test réels. Commande : `footintel backtest --seasons 5`.

| Modèle | Log loss | Brier | Précision | ECE | OU 2,5 | BTTS |
|---|---|---|---|---|---|---|
| naive_frequency (référence) | 1.0683 | 0.6461 | 44.5 % | 0.009 | 0.6913 | 0.6897 |
| elo_poisson | 0.9818 | 0.5847 | 53.1 % | 0.014 | 0.6870 | 0.6916 |
| logreg_market_goals (ancien actif) | 0.9722 | 0.5780 | 53.8 % | 0.011 | 0.6870 | 0.6916 |
| **routed_odds_elo (actif)** | **0.9672** | **0.5746** | **54.1 %** | **0.006** | 0.6870 | 0.6916 |
| market_implied (référence, 7 229 matchs avec cotes) | 0.9678 | 0.5753 | 54.0 % | 0.016 | — | — |

Log loss par compétition :

| Compétition | n | Naïf | Elo-Poisson | Actif | Marché |
|---|---|---|---|---|---|
| Premier League | 1 900 | 1.0688 | 0.9772 | 0.9632 | 0.9594 |
| Liga | 1 900 | 1.0661 | 0.9870 | 0.9658 | 0.9669 |
| Serie A | 1 900 | 1.0902 | 0.9946 | 0.9708 | 0.9714 |
| Bundesliga | 1 530 | 1.0708 | 0.9897 | 0.9751 | 0.9750 |
| Ligue des champions | 753 | 1.0299 | 0.9210 | 0.9210 | pas de cotes |
| Ligue Europa | 610 | 1.0589 | 0.9946 | 0.9946 | pas de cotes |
| Conference League | 575 | 1.0556 | 0.9833 | 0.9833 | pas de cotes |

Comparaisons appariées (IC 95 % bootstrap) :

- Coupes d'Europe, `elo_poisson − naïf` : −0.084 [−0.099 ; −0.069], n = 1 938 → gain net.
- Championnats, `routed_odds_elo − marché` : +0.0006 [−0.0015 ; +0.0027] → égalité, pas d'avantage.
- Promotion : `routed_odds_elo − logreg_market_goals` sur 2023-2025 : −0.0056 [−0.0085 ; −0.0026], n = 5 465.

## Ce que le run 6 a appris

1. **Une régression détectée et corrigée.** Ajouter les coupes et les championnats de contexte
   à l'entraînement d'une seule régression logistique a dégradé les championnats :
   +0.0056 [+0.003 ; +0.009] contre le marché, alors que c'était une égalité avant.
   Cause mesurée : beaucoup de lignes sans cotes affaiblissent le poids appris des cotes.
   Entraîner le modèle à cotes **uniquement sur les matchs avec cotes** annule la régression.
2. **Une variante dangereuse écartée.** Le modèle entraîné sur les seuls championnats
   cibles, appliqué aux coupes sans cotes, obtient une log loss de 1.69 : il extrapole.
   D'où le modèle aiguillé : cotes quand elles existent, Elo sinon.
3. **Coupes d'Europe.** Elo-Poisson, alimenté par les championnats de contexte, est le
   meilleur modèle testé. Calibration moins bonne qu'en championnat (ECE 0.03 à 0.044
   contre 0.006 en moyenne) : à surveiller, et à corriger par une calibration dédiée.
4. Marchés de buts : toujours faibles (BTTS sous la référence naïve). Chantier inchangé.

## Run 1 — 4 championnats seuls (2026-10-21)

7 230 matchs. `logreg_market` 0.9683, marché 0.9678, naïf 1.0741, Elo-Poisson 0.9879,
`logreg_core` 0.9820, RF 0.9826, XGBoost 0.9831. RF et XGBoost n'apportaient rien de plus
que la régression logistique.

## LightGBM pour tous les marchés contre Hermès (27/11/2026, D107)

Test saison par saison 2021-2025, mêmes 10 846 matchs, écart de log loss apparié (LightGBM moins Hermès ; négatif = LightGBM meilleur).

| Marché | Tous | Avec cotes (8 907) | Sans cotes (1 939) |
|---|---|---|---|
| 1X2 | +0,0006 (IC −0,0010 ; +0,0022) | — | — |
| Plus de 2,5 buts | −0,0051 (−0,0069 ; −0,0035) | −0,0069 (−0,0089 ; −0,0049) | +0,0030 (−0,0002 ; +0,0062) |
| BTTS | −0,0019 (−0,0032 ; −0,0006) | −0,0022 (−0,0036 ; −0,0009) | −0,0005 (−0,0032 ; +0,0023) |
| Plus de 1,5 buts | −0,0034 (−0,0048 ; −0,0020) | −0,0042 (−0,0060 ; −0,0026) | +0,0001 |
| Plus de 3,5 buts | −0,0043 (−0,0061 ; −0,0026) | −0,0060 (−0,0079 ; −0,0041) | +0,0035 |

Bon côté de plus de 2,5 buts avec cotes : LightGBM 58,0 %, Hermès 56,7 %. BTTS : 55,1 % contre 54,7 %.

## Avant Hermès 1.1 : LightGBM contre les bookmakers, et Hermès 1.1 contre Hermès 1.0 (27/11/2026, D108)

| Plus de 2,5 buts, 2021-2025, 8 907 matchs avec cotes | Écart avec les bookmakers (avant le match) | Bon côté |
|---|---|---|
| Bookmakers (moyenne sans marge) | — | 58,6 % |
| LightGBM | +0,0032 (IC +0,0018 ; +0,0047) | 58,0 % |
| Hermès 1.0 | +0,0101 (IC +0,0078 ; +0,0124) | 56,7 % |

Saison 2026-27 (452 matchs, hors échantillon) : bon côté sur plus de 2,5 buts, bookmakers 62,2 %, Hermès 1.1 60,4 %, Hermès 1.0 57,1 %. 1UP, 2UP et premier but (348 matchs) : Hermès 1.1 = Hermès 1.0.

## Preuves consolidées : handicap asiatique, 1UP/2UP/premier but, où Hermès perd (27/11/2026, D111)

Mêmes matchs pour chaque comparaison (écarts appariés match par match). Cotes moyennes publiées avant le match (colonnes `Avg` de football-data.co.uk, pas la clôture). Matchs à minutes de buts incomplètes ou absentes écartés.

**Handicap asiatique** (`scripts/asian_handicap_check.py`, 7 676 matchs, 2021 à 2026-27). A = taux de buts ajustés au 1X2 et au plus/moins 2,5 ; B = A + handicap.

| Marché | n | Log loss A | Log loss B | Brier A | Brier B | Écart B − A (log loss, IC 95 %) |
|---|---|---|---|---|---|---|
| Écart de buts (5 issues) | 7 676 | 1,4655 | 1,4656 | 0,7443 | 0,7444 | +0,0001 (−0,0002 ; +0,0005) |
| Premier but domicile | 301 | 0,6577 | 0,6575 | 0,2331 | 0,2331 | −0,0001 (−0,0008 ; +0,0006) |
| Premier but extérieur | 301 | 0,6439 | 0,6438 | 0,2266 | 0,2266 | −0,0001 (−0,0008 ; +0,0006) |
| 1UP domicile | 301 | 0,6049 | 0,6044 | 0,2101 | 0,2100 | −0,0005 (−0,0011 ; +0,0002) |
| 1UP extérieur | 301 | 0,6542 | 0,6541 | 0,2311 | 0,2311 | −0,0000 (−0,0008 ; +0,0009) |
| 2UP domicile | 301 | 0,6019 | 0,6010 | 0,2079 | 0,2076 | −0,0009 (−0,0015 ; −0,0002) |
| 2UP extérieur | 301 | 0,5696 | 0,5692 | 0,1935 | 0,1934 | −0,0003 (−0,0010 ; +0,0004) |

Un seul écart sur sept sous zéro (2UP domicile, −0,0009, sous le seuil D9 de 0,002) : bruit probable avec sept tests. Le handicap n'est pas retenu pour ces marchés et ces cinq championnats ; il n'est pas testé ailleurs.

**Calibration 1UP, 2UP, premier but (méthode A, saison 2026-27, 301 matchs complets, six marchés ensemble)**

| Tranche annoncée | n | Annoncé | Réel | Intervalle de Wilson 95 % |
|---|---|---|---|---|
| < 30 % | 284 | 22,0 % | 20,8 % | 16-26 % |
| 30-40 % | 340 | 35,2 % | 34,1 % | 29-39 % |
| 40-50 % | 417 | 45,0 % | 44,1 % | 39-49 % |
| 50-60 % | 349 | 54,7 % | 52,4 % | 47-58 % |
| 60-70 % | 243 | 64,4 % | 65,4 % | 59-71 % |
| > 70 % | 173 | 77,3 % | 80,3 % | 74-86 % |

Chaque tranche contient sa valeur annoncée dans l'intervalle. Réserve : une seule saison, et un match compte dans six marchés liés entre eux, donc les intervalles sont trop étroits. À refaire à 1 000 matchs complets.

**Où Hermès perd face au marché** (`scripts/where_hermes_loses.py`, 8 907 matchs avec cotes, 2021-2025)

- 1X2 : log loss 0,9711 contre 0,9707 (+0,0004, IC −0,0013 ; +0,0021) ; Brier 0,5774 des deux côtés. Aucun championnat, aucune saison, aucune force du favori, aucun écart d'avis où l'écart est significatif.
- Biais : Hermès annonce la victoire à domicile à 45,0 % en moyenne (marché 43,9 %, réel 43,5 %) et la victoire à l'extérieur à 30,4 % (marché 31,3 %, réel 31,1 %). Hermès surestime un peu l'avantage du terrain.
- Quand Hermès donne 3 à 8 points de plus que le marché à la victoire à domicile (2 296 matchs) : Hermès 65,6 %, marché 60,9 %, réel 63,2 %. La réalité tombe entre les deux. Quand Hermès donne 3 à 8 points de moins (551 matchs) : Hermès 29,2 %, marché 33,1 %, réel 29,8 %. Hermès a raison et le marché surestime le favori à domicile.
- Plus de 2,5 buts : Hermès perd dans les cinq championnats (+0,0076 à +0,0130, IC tous au-dessus de 0), annonce 54,2 % contre 52,9 % pour les bookmakers et 53,1 % de réel. C'est déjà corrigé par Hermès 1.1 (D109) quand le prix des bookmakers existe.

## Les deux pistes de D111 sur des saisons indépendantes (27/11/2026, D112)

Règles fixées avant de regarder. Saisons 2016-2020, jamais utilisées pour D111, puis 2026-27.

| Piste | Règle | 2016-2020 | 2026-27 | Verdict |
|---|---|---|---|---|
| 1. Hermès surestime la victoire à domicile | Au-dessus du réel et du marché | Hermès 45,2 %, marché 44,1 %, réel 44,5 % ; Hermès − réel +0,62 point (IC −0,35 ; +1,54) | Hermès 44,4 %, marché 43,2 %, réel 45,8 % | Non confirmée |
| 2. Hermès a raison quand il donne 3 à 8 points de moins au domicile | Log loss Hermès < marché, IC sous 0 | 702 matchs : réel 30,3 %, Hermès 29,7 %, marché 33,8 % ; écart −0,0018 (IC −0,0092 ; +0,0055) | 30 matchs : réel 36,7 % ; écart +0,0219 | Non confirmée |

Hermès donne toujours environ 1 point de plus que le marché à la victoire à domicile, mais rien ne montre que le marché ait raison ou tort sur ce point.

## Calibration du vainqueur par tranches, Hermès et marché (27/11/2026, D113)

17 936 matchs avec cotes, saisons 2016 à 2025, prédictions saison par saison (`scripts/calibration_1x2.py`). Chaque issue de chaque match compte (domicile, nul, extérieur). Intervalle de Wilson à 95 %.

| Tranche | Hermès : n | annoncé | réel | Marché : n | annoncé | réel |
|---|---|---|---|---|---|---|
| 0-10 % | 2 808 | 7,4 % | 7,9 % | 1 862 | 7,4 % | 6,7 % |
| 10-20 % | 9 559 | 15,4 % | 15,8 % | 7 961 | 15,7 % | 14,6 % (hors intervalle) |
| 20-30 % | 16 381 | 25,6 % | 26,3 % (hors intervalle) | 20 184 | 25,8 % | 25,3 % |
| 30-40 % | 10 439 | 33,7 % | 33,0 % | 9 099 | 34,2 % | 33,6 % |
| 40-50 % | 4 936 | 44,7 % | 44,7 % | 5 748 | 44,7 % | 45,8 % |
| 50-60 % | 3 648 | 54,9 % | 55,2 % | 4 088 | 54,8 % | 56,2 % |
| 60-70 % | 2 782 | 64,7 % | 62,3 % (hors intervalle) | 2 623 | 64,7 % | 69,1 % (hors intervalle) |
| 70-80 % | 2 124 | 74,7 % | 73,9 % | 1 638 | 74,5 % | 75,3 % |
| 80-100 % | 1 131 | 84,0 % | 82,2 % | 605 | 83,9 % | 85,8 % |

Plus grand écart : Hermès 2,4 points, marché 4,4 points. Le marché sans marge sous-estime les favoris à 60-70 % (annoncé 64,7 %, réel 69,1 %) et surestime les outsiders à 10-20 %. C'est le biais connu favori-outsider, accentué par notre façon de retirer la marge : la même proportion sur chaque issue. Hermès surestime un peu ses favoris à 60-70 % (64,7 % contre 62,3 %).

## Retrait de la marge : proportionnel, puissance, Shin (27/11/2026, D114)

76 557 matchs 2016-2025, 2 075 matchs 2026-27, prix moyens avant le match (`scripts/margin_methods_check.py`).

| Méthode | Écart de log loss 1X2 contre proportionnel (2016-2025) | 2026-27 | Favoris 60-70 % : annoncé / réel | Outsiders 10-20 % : annoncé / réel |
|---|---|---|---|---|
| Proportionnelle | — | — | 64,5 % / 67,8 % | 16,0 % / 14,4 % |
| Puissance (retenue) | −0,00074 (IC −0,00097 ; −0,00054) | −0,00181 | 64,4 % / 64,9 % | 15,9 % / 15,5 % |
| Shin | −0,00063 (IC −0,00078 ; −0,00049) | −0,00144 | 64,4 % / 65,7 % | 16,0 % / 15,2 % |

Plus de 2,5 buts : puissance −0,00016 (IC −0,00028 ; −0,00005), 2026-27 −0,00090.

## Hermès avec des entrées de marché « puissance » (27/11/2026, D115)

Walk-forward 2021-2025, même base, mêmes modèles ; seules les entrées `mkt_p_*` changent (`scripts/power_inputs_check.py`). Règle D9 fixée avant le calcul.

| Comparaison (log loss 1X2, apparié) | Matchs | Écart moyen | IC à 95 % |
|---|---|---|---|
| Hermès puissance contre Hermès | 10 846 | −0,00002 | −0,00021 ; +0,00016 |
| Marché puissance contre marché proportionnel | 8 907 | −0,00058 | −0,00114 ; −0,00004 |
| Hermès puissance contre marché puissance | 8 907 | +0,00094 | −0,00050 ; +0,00237 |
| Hermès contre marché (rappel, proportionnel) | 8 907 | +0,00039 | −0,00132 ; +0,00210 |

Par saison, Hermès puissance contre Hermès : 2021 −0,00025, 2022 −0,00041, 2023 +0,00049, 2024 +0,00008, 2025 −0,00001. Par ligue : de −0,00062 (Bundesliga) à +0,00039 (Liga). Seuil D9 non atteint : Hermès ne change pas.

## Information arrivée entre le prix du vendredi et la clôture (27/11/2026, D116)

`scripts/late_information_check.py` : 53 270 matchs de 2019-20 à 2025-26, 22 divisions de football-data.co.uk. Prix moyens des bookmakers, marge retirée par la méthode puissance (D114). Écart = log loss du prix du vendredi (ou du mardi) moins log loss du prix de clôture, en millièmes ; positif = la clôture prévoit mieux.

| Championnat | Matchs | Écart | IC à 95 % | Marge à la clôture | Mouvement moyen (points de %) |
|---|---|---|---|---|---|
| Grèce | 1 668 | 8,11 | 3,46 ; 13,21 | 7,3 % | 5,9 |
| Belgique | 2 085 | 7,39 | 3,82 ; 11,15 | 6,3 % | 5,3 |
| Pays-Bas | 2 068 | 6,07 | 2,65 ; 9,36 | 5,7 % | 4,7 |
| Écosse 2 | 1 172 | 5,78 | 1,40 ; 9,98 | 8,2 % | 4,4 |
| Turquie | 2 447 | 5,71 | 2,34 ; 9,55 | 6,5 % | 5,4 |
| Ligue 2 | 2 410 | 5,66 | 2,35 ; 8,69 | 7,0 % | 4,6 |
| Écosse 4 | 1 147 | 5,39 | 0,13 ; 10,33 | 9,2 % | 5,5 |
| Serie B | 2 651 | 5,33 | 2,64 ; 8,40 | 7,0 % | 4,7 |
| Premier League | 2 660 | 3,94 | 1,33 ; 6,40 | 4,3 % | 3,9 |
| Portugal | 2 142 | 3,47 | 0,36 ; 6,63 | 6,2 % | 4,6 |
| League One | 3 711 | 3,33 | 1,06 ; 5,57 | 6,6 % | 4,1 |
| League Two | 3 747 | 3,00 | 0,97 ; 5,05 | 6,7 % | 3,8 |
| Liga 2 | 3 234 | 2,97 | −0,16 ; 5,92 | 7,0 % | 5,1 |
| Écosse 1 | 1 547 | 2,66 | −1,33 ; 6,63 | 6,2 % | 4,7 |
| National League | 3 628 | 2,48 | −0,44 ; 5,50 | 8,5 % | 5,2 |
| Serie A | 2 659 | 2,34 | −0,36 ; 5,19 | 4,9 % | 4,1 |
| Bundesliga | 2 142 | 2,06 | −0,82 ; 5,01 | 4,8 % | 4,0 |
| Ligue 1 | 2 337 | 1,82 | −1,16 ; 4,75 | 5,0 % | 4,4 |
| Liga | 2 660 | 1,78 | −0,93 ; 4,30 | 4,8 % | 4,1 |
| Championship | 3 864 | 1,20 | −0,68 ; 3,22 | 5,4 % | 3,7 |
| 2. Bundesliga | 2 142 | 0,16 | −2,68 ; 2,98 | 6,3 % | 4,2 |
| Écosse 3 | 1 149 | 0,16 | −5,35 ; 5,32 | 9,1 % | 5,5 |
| **Toutes** | **53 270** | **3,48** | | | |

Lecture : entre le vendredi et le coup d'envoi, le prix gagne en moyenne 3,5 millièmes, soit 4 à 9 fois l'écart entre Hermès et le marché (D113 à D115). L'information de dernière minute pèse plus dans les championnats moins suivis. La clôture l'a déjà : un avantage n'est possible que contre un prix qui ne l'a pas encore.
