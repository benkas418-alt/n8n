# Résultats du backtest réel

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
