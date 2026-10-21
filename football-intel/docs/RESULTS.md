# Résultats du backtest réel (2026-10-21)

Walk-forward : pour chaque saison testée (2021-22 à 2025-26), les modèles sont entraînés
sur les saisons 2006-07 à la saison précédente. 2005-06 sert d'amorçage. 4 championnats,
7 230 matchs de test réels. Commande : `footintel backtest --seasons 5`.

| Modèle | Log loss | Brier | Précision | ECE | OU 2,5 log loss | BTTS log loss |
|---|---|---|---|---|---|---|
| naive_frequency (référence) | 1.0741 | 0.6500 | 43.6 % | 0.014 | 0.6915 | 0.6894 |
| elo_poisson | 0.9879 | 0.5888 | 52.6 % | 0.021 | 0.6886 | 0.6905 |
| logreg_core (sans cotes) | 0.9820 | 0.5847 | 53.1 % | 0.013 | — | — |
| rf_core | 0.9826 | 0.5851 | 53.1 % | 0.017 | — | — |
| xgb_core | 0.9831 | 0.5854 | 53.1 % | 0.014 | — | — |
| logreg_market_goals (actif) | 0.9683 | 0.5754 | 53.9 % | 0.011 | 0.6886 | 0.6905 |
| market_implied (référence) | 0.9678 | 0.5753 | 54.0 % | 0.016 | — | — |

Les lignes `rf_core` et `xgb_core` viennent du premier backtest, lancé avant la borne
±5 sur les variables standardisées (D10). Les autres viennent du backtest lancé après.
Sur les modèles présents dans les deux runs, l'écart est ≤ 0,0001.

Différences appariées de log loss (IC 95 % bootstrap) :

- `logreg_market_goals − naive` : −0.106 [−0.115 ; −0.096] → nette amélioration.
- `logreg_core − market` : +0.014 [+0.011 ; +0.018] → sans les cotes, le modèle est **moins bon que le marché**.
- `logreg_market_goals − market` : +0.0005 [−0.0014 ; +0.0024] → **pas de différence démontrée** avec le marché.

## Lecture

1. Le moteur apporte une information réelle par rapport aux fréquences historiques.
2. Il ne bat pas le marché. Avec les cotes en entrée, il le reproduit ; sans elles, il est
   en dessous. Aucun avantage de pari ne peut en être déduit.
3. Random Forest et XGBoost n'apportent rien par rapport à la régression logistique sur ces
   features : leur complexité n'est pas justifiée à ce stade.
4. Marchés de buts : Elo-Poisson bat à peine la référence en plus/moins de 2,5 et est
   **moins bon** qu'elle en BTTS. Chantier prioritaire de la phase 6 (Dixon-Coles,
   attaque/défense par équipe).
5. Le modèle actif est le mieux calibré (ECE 0.011).
