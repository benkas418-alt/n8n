# Résultats du backtest réel

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
