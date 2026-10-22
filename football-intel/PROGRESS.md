# Suivi d'avancement

Dernière mise à jour : 2026-10-22 (coupes d'Europe). Fichier à mettre à jour à la fin de chaque phase,
pour reprendre le travail après une interruption.

## État par phase

| Phase | État | Détail |
|---|---|---|
| 0 Audit | ✅ | Python 3.13, PostgreSQL 16, 4 CPU, 15 Go RAM. football-data.co.uk joignable ; API-Football exige une clé (403). |
| 1 Architecture | ✅ | docs/ARCHITECTURE.md, docs/DECISIONS.md. |
| 2 Fondations | ✅ | pyproject, config par variables d'environnement, 28 tables, migration Alembic 0001. |
| 3 Données historiques | ✅ | 96 479 matchs réels : 30 649 (4 championnats cibles) + 62 440 (13 championnats de contexte) + 3 390 (C1 2011-26, C3 2020-25, C4 2021-25). Relances sans doublon vérifiées. |
| 4 Collecte automatique | 🟡 | football-data et openfootball : fixtures, résultats, contexte, qualité, retry/backoff, cache disque, verrous, correspondance des noms relue. **Manquent** : saison en cours des coupes d'Europe, coupes nationales, compositions, formations, blessures (API-Football non branché, clé absente). |
| 5 Baseline ML | ✅ | Naïf, Elo-Poisson, marché, régression logistique. |
| 6 ML avancé | 🟡 | RF, XGBoost, modèle aiguillé cotes/Elo (actif), backtest walk-forward, comparaisons appariées. **Manquent** : calibration explicite (isotonique/Platt), Optuna, MLflow, Dixon-Coles, ensemble. |
| 7 Boucle post-match | 🟡 | Évaluation, registre, promotion, rollback, cycle hebdomadaire. **Manquent** : moteur de patterns (table `detected_patterns` vide), détection de dérive, retentatives des statistiques tardives au-delà du rechargement quotidien. |
| 8 Contribution humaine | 🟡 | Saisie CLI/API horodatée et figée, évaluation en justesse. **Manque** : modèle hybride (stacking temporel) et évaluation de l'apport du choix humain. |
| 9 Dashboard | ❌ | Non commencé. API HTTP prête (`/api/status`, `/api/matches/upcoming`, `/api/matches/{id}/predictions`, `/api/metrics/backtest`, `POST /api/user-predictions`). |
| 10 Automatisation et rapports | 🟡 | Planificateur, rapports pré/post-match MD/HTML/CSV, unité systemd. **Manquent** : rapport hebdomadaire, notification Telegram, PDF. |
| 11 Validation finale | 🟡 | 36 tests passent (29 hors ligne, 7 contre les vraies sources). |

## Critères d'acceptation

| # | Critère | État | Preuve |
|---|---|---|---|
| 1 | Initialiser la base | ✅ | `footintel db upgrade` ; tests : downgrade puis upgrade complets |
| 2 | Importer un historique | ✅ | 30 649 matchs réels |
| 3 | Collecte sans doublons | ✅ | relance réelle : +0 / 380 inchangés ; `test_history_import_is_idempotent` |
| 4 | Features sans fuite | ✅ | `test_features_ignore_same_day_and_future_results` |
| 5 | Entraîner un modèle probabiliste | ✅ | `routed_odds_elo` v1 actif, promu contre l'ancien actif (gain 0.0056, IC < 0) |
| 6 | Produire et sauvegarder une prédiction | ✅ (synthétique) | `test_end_to_end_prediction_loop`. En réel : aucun match publié dans `fixtures.csv` le 2026-10-21. |
| 7 | Enregistrer un pronostic humain | ✅ | test e2e ; refus réel après le coup d'envoi via l'API (409) |
| 8 | Associer résultat et prédiction antérieure | ✅ (synthétique) | test e2e |
| 9 | Calculer les métriques | ✅ | backtest réel + évaluation post-match |
| 10 | Backtest chronologique | ✅ | docs/RESULTS.md |
| 11 | Comparer deux versions | ✅ | promotion réelle : v1 promue, `elo_poisson` rejeté, v2 promue |
| 12 | Rapport post-match | ✅ | `reports/postmatch_*.md/.html/.csv` |
| 13 | Tests automatisés | ✅ | `pytest` |
| 14 | Redémarrer selon la documentation | 🟡 | README écrit ; à valider sur le VPS |
| 15 | Mode dégradé sans clé | ✅ | `footintel status` réel : « disabled (no API_FOOTBALL_KEY) » |

## Coupes d'Europe : état réel

| Besoin | État |
|---|---|
| Historique C1 / C3 / C4 | ✅ openfootball (domaine public) |
| Force des adversaires étrangers | ✅ 13 championnats de contexte + Elo commun |
| Prédire les matchs de C1 / C3 / C4 **de la saison en cours** | ❌ aucune source autorisée sans clé ne publie le calendrier 2026-27 |
| Coupes nationales (FA Cup, EFL Cup, Copa, Coppa, Pokal) | ❌ même raison |
| Fiche pré-match (indicateurs observés + manques explicites) | ✅ `footintel report fiche --match-id N` |
| Style, formations, joueurs cadres, absences, xG | ❌ aucune source autorisée connectée ; table `team_match_tactics` prête |

## Prochaine étape concrète

1. Fournir une clé API-Football gratuite, puis brancher `/leagues`, `/fixtures`, `/odds`,
   `/injuries`, `/fixtures/lineups`, `/fixtures/statistics` après vérification des vraies
   réponses : calendrier des coupes 2026-27, coupes nationales, formations, absences.
2. Phase 6 : Dixon-Coles + calibration, pour corriger les marchés de buts (BTTS sous la référence).
3. Phase 9 : dashboard.
