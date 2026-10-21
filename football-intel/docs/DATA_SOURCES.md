# Sources de données

Tout ce qui suit a été vérifié par de vrais appels le 2026-10-21.

## football-data.co.uk — active

| Élément | Constat |
|---|---|
| Accès | Libre, sans clé. `https://www.football-data.co.uk/mmz4281/{yyYY}/{DIV}.csv` (redirection 302 vers `football-data.co.uk`). |
| Couverture testée | E0 (Premier League), SP1 (Liga), I1 (Serie A), D1 (Bundesliga) : saisons 2005-06 à 2026-27 en HTTP 200. |
| Coupes et UEFA | **Non couvertes** (FA Cup, EFL Cup, Copa del Rey, Coppa Italia, DFB-Pokal, C1, C3). |
| Colonnes | Doc : `notes.txt`. Résultat (FTHG, FTAG, FTR, mi-temps), tirs (HS/AS), tirs cadrés (HST/AST), fautes, corners, cartons, arbitre, cotes 1X2, plus/moins de 2,5 buts, handicap asiatique. |
| Heure | Colonne `Time` à partir de 2019-20 seulement. Fuseau non documenté : hypothèse Europe/London. |
| Cotes | « Pre-closing » (collecte avant le match, heure exacte non fournie) et « closing » (suffixe `C`). Moyenne du marché : `Avg*` depuis 2019-20, `BbAv*` avant. |
| xG, compositions, blessures | **Absents.** Aucune feature n'est construite sur ces données. |
| Matchs à venir | `fixtures.csv` : quelques jours à l'avance seulement. Le 2026-10-21 (mercredi), aucun match des 4 ligues suivies. |
| Conditions | Page `disclaimer.php` : pas de restriction d'usage personnel trouvée ; site financé par des bookmakers ; rappel de la loi locale sur les paris et de l'âge légal. À relire avant tout usage commercial. |

## API-Football (api-sports.io) — connecteur prévu, désactivé

- `GET https://v3.football.api-sports.io/status` sans clé : **HTTP 403**, corps
  `{"get","parameters","errors":{"token":"Missing application key..."},"results","paging","response"}`.
- Une clé gratuite est nécessaire (inscription : https://dashboard.api-football.com/register).
  Les quotas et la couverture du plan gratuit (saisons accessibles, cotes) n'ont pas pu être
  vérifiés sans clé : à confirmer dès qu'une clé est fournie.
- Les identifiants de ligues ne sont **pas** codés en dur : ils seront lus via `/leagues`.
- C'est la seule source testée qui pourrait couvrir les coupes nationales, la C1 et la C3,
  les compositions, les événements et les blessures.

## openfootball (football.json) — écartée pour l'instant

- Domaine public (README du projet).
- `2024-25/uefa.cl.json` existe (189 matchs) mais le score de la finale manque ;
  `2025-26/uefa.cl.json`, `uefa.el.json`, `en.facup.json`, `de.cup.json` : HTTP 404.
- Couverture trop lacunaire pour les coupes. Peut servir plus tard de calendrier secondaire.

## Mode dégradé

Sans `API_FOOTBALL_KEY`, le système fonctionne entièrement sur football-data.co.uk et
les données déjà en base. `footintel status` et `/api/status` l'indiquent explicitement.
