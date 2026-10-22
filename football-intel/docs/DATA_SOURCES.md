# Sources de données

Tout ce qui suit a été vérifié par de vrais appels les 2026-10-21 et 2026-10-22.

## Actives

### football-data.co.uk — championnats

| Élément | Constat |
|---|---|
| Accès | Libre, sans clé. `/mmz4281/{yyYY}/{DIV}.csv` (format complet) et `/new/{PAYS}.csv` (un fichier par pays, toutes saisons). |
| Cibles | E0, SP1, I1, D1 : 2005-06 à 2026-27. Résultats, mi-temps, tirs, tirs cadrés, fautes, corners, cartons, cotes avant clôture et de clôture. |
| Contexte (format complet) | F1, N1, P1, B1, T1, SC0, G1 : 2005-06 à 2026-27, mêmes colonnes. |
| Contexte (`/new/`) | AUT, SWZ, DNK, NOR, SWE, POL : depuis 2012. **Résultats et cotes de clôture seulement**, pas de statistiques ni de cotes avant match. |
| Heure | Colonne `Time` à partir de 2019-20 ; fuseau non documenté (hypothèse Europe/London). |
| Matchs répétés | En Écosse, Suisse, Autriche, au Danemark, une affiche se rejoue sur le même terrain dans la saison : la clé des championnats de contexte inclut la date. |
| xG, compositions, blessures | **Absents.** |
| Conditions | `disclaimer.php` : pas de restriction d'usage personnel trouvée. À relire avant tout usage commercial. |

### openfootball / champions-league — coupes d'Europe

| Élément | Constat |
|---|---|
| Licence | Domaine public. |
| Couverture | C1 2011-12 à 2025-26 (15 saisons) ; C3 2020-21 à 2024-25 ; C4 2021-22 à 2024-25. 3 390 matchs importés, nombre identique à l'en-tête de chaque fichier. |
| Manque | **Saison en cours 2026-27 absente.** C3 2025-26 et C4 2025-26 absentes. Aucune cote, aucune statistique, aucune composition. |
| Format | Score à 90 minutes, prolongation, tirs au but ; « [awarded] » et « [cancelled] » écartés ; finale sur terrain neutre. Heures en heure d'Europe centrale. |
| Noms d'équipes | 224 noms. Correspondance avec football-data : automatique si sûre, sinon alias manuel relu (`reference/team_aliases.csv`, 35 alias). 2 erreurs automatiques trouvées à la relecture (PSG → Paris FC, Başakşehir → Istanbulspor) et corrigées. 72 clubs de pays non importés (Tchéquie, Serbie, Croatie, Chypre…) restent des équipes à part, avec peu d'historique. |

## Prévue, désactivée

### API-Football (api-sports.io)

Sans clé : HTTP 403, enveloppe `{get, parameters, errors, results, paging, response}`.
C'est la **seule source testée légalement utilisable** qui pourrait fournir : la saison en cours
des coupes d'Europe, les coupes nationales, les compositions, les formations, les événements,
les statistiques par joueur, les blessures et suspensions. Couverture et quotas du plan gratuit
non vérifiables sans clé. Inscription : https://dashboard.api-football.com/register

### football-data.org

Sans clé : HTTP 403 (« restricted »). Clé gratuite à l'inscription (https://www.football-data.org/client/register).
Couverture du plan gratuit non vérifiée sans clé. Candidat de secours pour le calendrier
et les résultats de la C1.

## Écartées

| Source | Test | Raison |
|---|---|---|
| ESPN (`site.api.espn.com`) | HTTP 200 sans clé ; C1 depuis 2005 avec compositions, formations depuis ~2010, 28 statistiques d'équipe, cotes. | **Conditions d'utilisation Disney/ESPN** : interdiction d'extraire les contenus « using a robot, spider, script, or other automated means […] compiling, building […] any collection of data, data set or database ». Non utilisée malgré sa richesse. |
| Understat (xG) | HTTP 200. | `robots.txt` : `Disallow: /` pour tous les robots. |
| FBref | HTTP 403. | Accès bloqué. |
| TheSportsDB (clé publique « 3 ») | HTTP 403. | Clé publique refusée. |
| ClubElo | `Fixtures API deactivated` ; classement du jour HTTP 502. | Service indisponible lors des tests. À retester : il donnerait la force de tous les clubs européens. |
| openfootball football.json | C1 2024-25 seulement, finale sans score. | Couverture trouée ; le dépôt `champions-league` est utilisé à la place. |

## Mode dégradé

Sans clé API, le système fonctionne sur football-data.co.uk et openfootball, plus les données
déjà en base. `footintel status` et `/api/status` l'indiquent explicitement.
