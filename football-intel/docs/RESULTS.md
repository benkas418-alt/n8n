# Résultats du backtest réel

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
