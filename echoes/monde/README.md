# Behind the Truth — prototype « le monde continue sans moi »

Décision D5 de `../ARBITRAGE.md`. Un seul fichier : `index.html`, sans build.
Carte 2D de South City. Pas de 3D : on teste la simulation, pas le rendu.

## Ce que le prototype contient

- 4 quartiers d'ECHOES, le corridor ferroviaire et ses 3 ponts (seul passage vers Trois-Ponts).
- 15 personnages avec horaires de semaine, du samedi et du dimanche.
- 3 histoires qui avancent seules :
  - **Les mardis de Raphaël** (affaire avec cliente) : le notaire n'a pas de maîtresse, il joue et se ruine.
  - **La caisse de l'église** (affaire spontanée, sans client) : on accuse Joël ; c'est Léonie, pour l'hôpital de son fils.
  - **Le déjeuner du dimanche** (pas une affaire) : deux couples amis s'éloignent après une promotion.
- Filature : la distance et la foule du quartier font monter le soupçon. Repéré, la cible change ses habitudes.
- Entretiens : chaque réponse est une vérité, un mensonge, une vérité incomplète ou une erreur sincère.
- Garant (règle de Trois-Ponts) : Léonie ne parle que si Mama Rose vous envoie.
- Vacances à Port-Lys (3 ou 6 jours, téléphone coupé ou disponible). La ville continue pendant ce temps.
- Messages livrés seulement par un moyen crédible : journal, téléphone, note au cabinet, rumeur dans le bon quartier.
- Sauvegarde versionnée, avec une fonction de migration.
- Vue auteur : la vérité objective, et le journal de tout ce qui s'est passé.

Le contenu (personnages, faits, fils, dialogues) est dans un bloc de données séparé (`window.WORLD`).
Le moteur ne contient aucun texte d'histoire (exigence OW-013).

## Tests d'acceptation (partie 17 du cahier des charges) — résultats du 17 nov. 2026

Exécutés dans Chromium, sur ordinateur et sur téléphone, deux parties complètes.

| Test | Résultat |
|---|---|
| Les personnages suivent des emplois du temps | OK (Raphaël : étude lundi 9 h, Trèfle mardi 20 h, maison mercredi 20 h) |
| Les relations changent sans le joueur | OK (Hugo → Patrice : confiance 50 → 15 au jour 4) |
| Une affaire peut apparaître spontanément | OK (dispute à l'église, dimanche midi) |
| Le joueur peut refuser une enquête | OK (refus : l'histoire continue, Raphaël part à l'hôtel au jour 9) |
| Les preuves sont persistantes | OK |
| Les événements évoluent pendant le voyage | OK (6 jours absents : Raphaël parti, Joël exilé, Bastien licencié) |
| Les sauvegardes restaurent l'état du monde | OK (sauvegarde, rechargement de la page, chargement : état identique) |
| Bonne décision = mal évité | OK (rapport juste avant le jour 7 : pas de détournement, Bastien garde sa place) |
| Erreurs JavaScript | Aucune |
| Débordement sur téléphone | Aucun |

Non testé ici : caméra hybride, animations, performances sur téléphone réel. Ce sont des tests Unity.

## Limites connues

- Sur téléphone, la carte est petite : les noms sont difficiles à lire et les personnages difficiles à toucher.
- Personne n'a encore joué. Les tests prouvent que le monde est cohérent, pas qu'il est amusant.
- Les vacances sont un écran de résumé, pas une ville jouable.
