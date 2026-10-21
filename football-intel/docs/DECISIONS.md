# Décisions techniques

| # | Décision | Raison | À revoir si |
|---|---|---|---|
| D1 | Projet Python autonome dans `football-intel/`, hors des paquets pnpm du monorepo n8n. | Aucune interaction avec l'outillage n8n (installations, hooks de commit). | Le projet obtient son propre dépôt (recommandé). |
| D2 | PostgreSQL pour tout, y compris les tests (base `footintel_test`). | Requêtes `DISTINCT ON`, contraintes et fuseaux fidèles à la production. | Besoin d'un mode portable sans serveur. |
| D3 | Heure `Time` de football-data.co.uk interprétée en Europe/London. | Non documenté ; site britannique ; cohérent avec les heures de Premier League connues. | Un écart est constaté avec une autre source. |
| D4 | Sans heure de coup d'envoi, la limite d'une prédiction est minuit UTC du jour du match. | Plus tôt que tout coup d'envoi réel : aucune prédiction ne peut être postérieure au match. | — |
| D5 | Identité d'un match football-data = `DIV|saison|domicile|extérieur`. | Une affiche de championnat n'a lieu qu'une fois par saison et par terrain ; la clé survit aux reports de date. | Ajout de coupes (plusieurs matchs possibles) : la clé inclura le tour. |
| D6 | Cotes historiques « pre-closing » utilisées comme connues avant le match. | La source les collecte avant les matchs (heure exacte non fournie). Les cotes de clôture ne sont **pas** utilisées comme features. | — |
| D7 | Marge retirée proportionnellement. | Méthode simple et standard. | La méthode de Shin améliore la calibration au backtest. |
| D8 | Un seul modèle actif à la fois ; modèle composite pour 1X2 + buts. | Une prédiction = une version identifiable. | Besoin de modèles spécialisés par marché ou compétition. |
| D9 | Promotion : ≥ 300 matchs de test, gain de log loss ≥ 0,002, IC 95 % bootstrap apparié entièrement < 0. Référence : le modèle actif, ou la référence naïve s'il n'y en a pas ou si la configuration est identique. | Seuils définis avant toute évaluation, dans la config. | — |
| D10 | Variables standardisées bornées à ±5. | Un test a montré qu'une feature quasi constante produisait des probabilités de 99,9999 %. Effet nul sur le backtest réel (0,9683 avant et après). | — |
| D11 | Dashboard reporté (phase 9) ; l'API HTTP est livrée d'abord. | Le parcours de données et d'évaluation devait être validé avant l'interface. | — |
| D12 | Pronostic humain évalué en justesse seulement (pas de log loss). | Un choix 1X2 n'est pas une probabilité ; convertir la confiance en probabilité est l'objet du modèle hybride (phase 8). | — |
