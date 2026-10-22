# footintel — Football Intelligence & Prediction System

Plateforme personnelle de collecte de données football, de prédiction probabiliste
et d'évaluation mesurable. Version 0.1 : premier parcours complet de bout en bout,
sans interface graphique (CLI + API HTTP).

> Aucun système ne prédit le football avec certitude. Les probabilités quantifient
> l'incertitude ; leur qualité se mesure (log loss, Brier, calibration) et se compare
> à des références (fréquences naïves, marché des bookmakers).

## Ce qui fonctionne aujourd'hui (vérifié le 2026-10-21)

- Import de 30 649 matchs réels (Premier League, Liga, Serie A, Bundesliga, 2005-06 à 2026-27)
  depuis football-data.co.uk : résultats, tirs, cartons, corners, cotes avant clôture et de clôture.
- Coupes d'Europe : 3 390 matchs (C1 2011-26, C3 2020-25, C4 2021-25) depuis openfootball,
  plus 13 championnats de contexte (62 440 matchs) pour estimer la force des clubs étrangers.
- Fiche pré-match : indicateurs observés seulement, liste explicite des données manquantes.
- Tendances par compétition : profils par saison et segment, écarts à une référence qui ignore
  la compétition, évolutions, correction des tests multiples, validation hors échantillon,
  et mesure de l'apport prédictif de chaque niveau d'analyse. Voir docs/RESULTS.md.
- Collecte idempotente (relancer ne crée aucun doublon), journal des collectes, verrous par tâche.
- Features calculées sans fuite temporelle (Elo, forme, tirs, repos, cotes du marché).
- Modèles : fréquences naïves, Elo-Poisson, régression logistique, Random Forest, XGBoost,
  marché (cotes sans marge), composite 1X2 + buts.
- Backtest chronologique par saison, comparaisons appariées avec intervalle de confiance bootstrap.
- Registre de modèles : versions, empreinte SHA-256, promotion selon critères fixés à l'avance,
  retour arrière.
- Prédictions sauvegardées avec le snapshot des variables, la version du modèle et l'heure.
- Pronostics personnels horodatés, refusés après le coup d'envoi.
- Évaluation post-match, rapports pré-match et post-match (Markdown, HTML, CSV).
- Planification (APScheduler, fuseau Africa/Lubumbashi), API HTTP, sauvegarde/restauration.
- Mode dégradé sans clé API.

Ce qui n'est **pas** encore fait est listé dans [PROGRESS.md](PROGRESS.md).

## Installation (Linux / VPS)

Prérequis : Python ≥ 3.12, PostgreSQL ≥ 14, [uv](https://docs.astral.sh/uv/) (ou pip).

```bash
cd football-intel
uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]"

# Base de données (adapter le mot de passe)
sudo -u postgres psql -c "CREATE ROLE footintel LOGIN PASSWORD 'CHANGE_ME';"
sudo -u postgres createdb -O footintel footintel
sudo -u postgres createdb -O footintel footintel_test   # pour les tests

cp .env.example .env        # puis remplir DATABASE_URL et ADMIN_TOKEN
.venv/bin/footintel db upgrade      # migrations Alembic
.venv/bin/footintel db seed         # sources et compétitions
```

## Premier démarrage

```bash
F=.venv/bin/footintel
$F ingest history --first 2005          # ~2 min, télécharge 88 fichiers une seule fois
$F ingest context --first 2005          # 13 championnats de contexte (~4 min)
$F ingest european                      # C1, C3, C4 depuis 2011
$F ingest fixtures                       # matchs à venir + cotes
$F backtest --seasons 5                  # évaluation chronologique
$F models train routed_odds_elo          # crée une version candidate
$F models promote <id> --seasons 3       # promue seulement si les critères sont remplis
$F predict                               # prédit les matchs des 7 prochains jours
$F report prematch
```

## Usage quotidien

| Action | Commande |
|---|---|
| Matchs à venir | `footintel upcoming` |
| Mon pronostic | `footintel user-predict <match_id> H 4 --score 2-1 --over25 yes --btts yes --reason "..."` |
| Cycle du matin (fixtures, prédictions, rapport) | `footintel run morning` |
| Cycle du soir (résultats, évaluation, rapport) | `footintel run evening` |
| Contrôle qualité | `footintel run nightly` |
| Réentraînement + validation | `footintel run weekly` |
| Fiche pré-match | `footintel report fiche --match-id <id>` |
| Tendances par compétition + apport de chaque niveau | `footintel analyze` (~10 min) |
| Tendances statistiques (scores, équipes) | `footintel trends run` puis `footintel trends report --competition ENG-PL` (ou `--team`, `--category`, `--date`) |
| Apport des tendances par marché | `footintel trends evaluate` (~15 min) |
| État du système | `footintel status` |
| Revenir au modèle précédent | `footintel models rollback` |
| Sauvegarde | `footintel db backup` |
| API HTTP | `footintel serve` (http://127.0.0.1:8000/docs) |
| Planificateur | `footintel scheduler` |

Restauration : `pg_restore --clean --no-owner -d "$DATABASE_URL_SANS_+psycopg" data/backups/<fichier>.dump`.

## Tableau de bord

`footintel serve` puis ouvrir http://127.0.0.1:8000/ (redirige vers `/dashboard/`).

| Espace | Question à laquelle il répond |
|---|---|
| Vue générale | Qu'est-ce qui change, qu'est-ce qui est confirmé, que vaut le modèle, que manque-t-il ? |
| Compétitions | Évolution par saison avec intervalle de confiance, saison récente contre référence, matrice des scores (cliquable → matchs), distribution des buts, mi-temps, indicateurs de jeu, tendances et particularités. |
| Équipes | Production offensive et défensive sur 6 matchs contre la référence de l'équipe, tirs, tendances significatives, derniers matchs. |
| Analyse pré-match | Probabilités 1X2 contre le marché, scores classés par probabilité, facteurs, fiabilité, fiches des deux équipes. |
| Performance | Log loss, Brier, comparaisons appariées, log loss par compétition, courbes de calibration, apport mesuré des niveaux et tendances, historique des versions, résultats réels. |

Les données non collectées (minutes des buts, xG, tactique, compositions) apparaissent comme
telles, jamais comme zéro. Le serveur écoute sur 127.0.0.1 par défaut : passer par un reverse
proxy avec TLS pour un accès distant.

## Planification sur le VPS

Le fichier [deploy/footintel-scheduler.service](deploy/footintel-scheduler.service) lance
le planificateur avec systemd. Horaires par défaut (Africa/Lubumbashi) :
matin 09:00, soir 23:30, nuit 03:00, lundi 04:00 (réentraînement).
Modifiables avec `SCHEDULE_MORNING="0 8 * * *"` etc.

## Tests

```bash
.venv/bin/pytest -m "not live"   # unitaires + intégration (base footintel_test, données synthétiques)
.venv/bin/pytest -m live         # appelle les vraies sources pour vérifier les colonnes utilisées
```

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — composants et flux
- [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) — sources testées, couverture, limites
- [docs/FEATURES.md](docs/FEATURES.md) — définition de chaque variable
- [docs/DECISIONS.md](docs/DECISIONS.md) — décisions techniques et hypothèses
- [docs/RESULTS.md](docs/RESULTS.md) — résultats du backtest réel
- [PROGRESS.md](PROGRESS.md) — état d'avancement par phase
