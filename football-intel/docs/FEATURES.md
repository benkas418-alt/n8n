# Features

Règle générale : pour un match du jour J, toutes les features sont calculées avec
l'état à la fin du jour J-1. Les résultats du jour J ne sont intégrés qu'après.
Test : `tests/test_unit.py::test_features_ignore_same_day_and_future_results`.

Suffixe `_h` = équipe à domicile, `_a` = équipe à l'extérieur.

| Feature | Définition | Données manquantes |
|---|---|---|
| `elo_home`, `elo_away` | Elo avant le match. K = 20, avantage domicile 60, multiplicateur selon l'écart de buts (1 ; 1,5 ; (11+écart)/8). | Jamais manquant. Départ 1500 la première saison, 1420 pour une équipe qui apparaît ensuite (souvent promue). Entre deux saisons, 80 % de l'écart à 1500 est conservé. |
| `elo_diff` | `elo_home - elo_away` (sans l'avantage domicile). | — |
| `form5_ppg`, `form10_ppg` | Points par match sur les 5 / 10 derniers matchs, toutes compétitions suivies. | NaN si aucun match antérieur ; moyenne sur les matchs disponibles sinon. |
| `gf5`, `ga5` | Buts marqués / encaissés par match, 5 derniers matchs. | Idem. |
| `venue5_ppg` | Points par match sur les 5 derniers matchs à domicile (pour `_h`) ou à l'extérieur (pour `_a`). | NaN si aucun. |
| `shots5_for`, `shots5_against`, `sot5_for`, `sot5_against` | Tirs et tirs cadrés pour / contre, moyenne des 5 derniers matchs. | Les matchs sans statistiques sont ignorés ; NaN si aucun. |
| `rest_days` | Jours depuis le dernier match suivi, plafonnés à 30. | NaN pour le premier match. |
| `n_prior` | Nombre de matchs antérieurs de l'équipe dans la base. | 0. Sert au contrôle « données suffisantes » (minimum 5). |
| `mkt_p_home/draw/away` | Probabilités implicites des cotes 1X2, marge retirée proportionnellement : `(1/cote) / Σ(1/cote)`. Cote utilisée : dernier relevé `fixtures@` antérieur à l'heure de prédiction, sinon moyenne du marché avant clôture, sinon Bet365 avant clôture. | NaN si une des trois cotes manque. |
| `mkt_overround` | `Σ(1/cote)` : la marge brute du bookmaker. | Idem. |

Traitement dans les modèles ML : imputation par la médiane du pli d'entraînement **et**
colonne indicatrice de valeur manquante, puis standardisation bornée à ±5 écarts-types.

## Pas encore construites (données indisponibles)

xG/xGA, occasions créées, absences, suspensions, compositions, importance des joueurs,
matchs européens récents, densité du calendrier multi-compétitions : la source actuelle
ne fournit pas ces données. Elles dépendent d'API-Football.
