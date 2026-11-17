# ECHOES = Behind the Truth — arbitrage entre les deux briefs

Sources :
- **A** — « ECHOES — Prompt de production (3D, monde ouvert) », 27 p., 17 nov. 2026.
- **B** — « Behind the Truth » : cahier des charges v4.0, GDD technique v2.0, étude de référence.

Les deux documents décrivent le même jeu. Ils s'accordent sur l'essentiel, mais se contredisent
sur six points. Chaque point ci-dessous dit ce qui bloque, puis ce que je recommande.
Statut : décisions 1 à 4 **validées le 17 nov. 2026** (voir en bas). Points 5 et 6 : recommandations en attente.

## Ce qui est déjà commun (aucune décision à prendre)

- Détective privé, enquêtes psychologiques pour adultes, conséquences qui durent.
- La vérité d'une affaire est écrite à l'avance ; le chemin pour la trouver peut varier.
- Caméra : troisième personne pour se déplacer, première personne pour examiner.
- Les personnages se souviennent ; un témoin mal traité peut se fermer.
- Interrogatoires : contradictions, preuves présentées, pression qui coûte cher.
- Trois façons de dire faux, dans les deux textes : mentir, dire une vérité incomplète, croire sincèrement une chose fausse.
- Les deux recommandent de commencer petit : un quartier, une enquête qui marche.

## Ce que chaque document apporte et que l'autre n'a pas

| A (ECHOES) apporte | B (Behind the Truth) apporte |
|---|---|
| L'Écho : la reconstitution montre l'hypothèse du joueur, pas la vérité | Plusieurs villes, voyages, vacances |
| Besoin, blessure, phrase de défense ; deux jauges | Emplois du temps, relations qui changent sans le joueur |
| Règle des trois suspects | Événements spontanés, affaires refusables |
| Provenance des preuves (légitime, grise, illégale) | Filature et surveillance détaillées |
| L'Accordeur et la révélation en cinq paliers | Modèle de données (PNJ, preuves, sauvegardes) |
| Règles d'écriture des retournements | Éditeur d'affaires avec validateur automatique |

Ces apports s'emboîtent bien. Le champ « informations supposées » de B est exactement
ce dont l'Écho de A a besoin pour construire ses scènes.

## Les six contradictions

### 1. Le nom
A dit ECHOES, B dit Behind the Truth.
**Recommandation :** titre commercial **Behind the Truth**. « L'Écho » reste le nom de la mécanique centrale.

### 2. Moteur, rendu et plateformes — le point le plus grave
A : Unreal Engine 5, photoréaliste, 4K, PC et consoles.
B : Unity, PC + Android + iOS, mêmes règles sur toutes les plateformes.
On ne peut pas avoir les deux : un monde ouvert photoréaliste conçu pour UE5 ne tourne pas
sur un téléphone Android moyen. Il faut choisir la cible d'abord, le moteur ensuite.
**Recommandation :** Unity, rendu **réaliste mais stylisé** (pas photoréaliste). PC d'abord,
puis un test de performance mobile tôt, comme B le demande. On abandonne l'objectif « 4K natif ».
Raison : ton public naturel (Lubumbashi, Afrique centrale) joue surtout sur Android.

### 3. Le monde : une ville dense ou plusieurs villes
A : une seule ville fictive (South City), 6 km², « des portes où frapper plutôt que des kilomètres ».
B : quatre villes, voyages internationaux, vacances à Honolulu.
**Recommandation :** **une ville d'abord**, comme B le dit lui-même pour le prototype.
Les voyages viennent seulement si la première ville prouve que l'enquête est amusante.

### 4. Ville réelle ou fictive
A interdit toute personne ou organisation réelle nommée. B propose Lubumbashi, Paris,
New York, Honolulu, et des « entreprises minières ».
**Recommandation :** une **ville fictive inspirée de Lubumbashi**, avec des noms inventés
(entreprises, administrations, quartiers). On garde l'identité, on évite les procès et les
lectures politiques. Les quatre quartiers de South City (reconnaissance, appartenance,
liberté, contrôle) se transposent sans effort à une ville de ce type.

### 5. Simulation automatique ou écriture à la main
B veut des événements spontanés et des histoires secondaires qui avancent seules.
A interdit de générer les dialogues des scènes majeures, les mobiles et les retournements.
**Recommandation :** **les deux, avec une frontière stricte.** La simulation déplace les gens,
modifie les relations et déclenche des situations prévues par les auteurs. Elle n'invente jamais
un fait, un mobile ou une réplique importante. B dit la même chose (« pas de génération
arbitraire de faits ») : il faut juste l'écrire comme règle de production.

### 6. Combien de suspects
L'exemple « 20 ans de mensonges » de B met six personnes au même niveau.
A impose trois suspects par affaire.
**Recommandation :** **trois suspects, toujours.** Les autres personnes deviennent des témoins,
des complices ou des proches. Le réseau de secrets de B reste possible ; seul le nombre de
personnes accusables est limité.

## Règle de contenu commune (la plus stricte des deux s'applique)

- Aucun mineur sexualisé, sous aucune forme, même suggérée ou racontée. B prévoit des
  personnages de 16-17 ans dans des affaires de harcèlement en ligne : ils peuvent être
  victimes ou témoins, jamais montrés dans un contexte sexuel.
- Violences sexuelles : un sujet d'enquête (témoignage, conséquences), jamais une scène jouée.
- Intimité entre adultes : non graphique, cadrée comme une preuve.
- Les boutiques mobiles ont leurs propres règles de contenu adulte : à vérifier avant de
  figer ce qu'on montre sur Android et iOS.

## Ordre de travail proposé

1. **Fait** — prototype gris de l'Écho et des interrogatoires (`prototype/`). À faire jouer.
2. **Prototype « le monde continue sans moi »** (navigateur, sans 3D lourde) : 15 personnages
   avec emplois du temps, relations qui changent, une affaire, départ en voyage, retour,
   conséquences visibles. Il teste la promesse principale de B pour un coût faible.
3. **Prototype Unity de déplacement** : caméra hybride, un quartier, test sur un téléphone Android réel.
4. **Tranche verticale** : un quartier habité, une enquête complète, l'Écho en 3D.

Ne pas lancer l'étape 3 avant que les étapes 1 et 2 aient été jouées par de vraies personnes.

## Décisions validées (17 nov. 2026)

| # | Décision |
|---|---|
| D1 | Titre : Behind the Truth. « L'Écho » reste la mécanique centrale. |
| D2 | Moteur : Unity. Rendu réaliste stylisé. PC d'abord, test mobile Android tôt. |
| D3 | Une seule ville pour commencer. |
| D4 | Ville : **South City** (fictive, celle d'ECHOES), avec ses quatre quartiers. Pas de ville réelle. |
| D5 | Prochaine construction : le prototype « le monde continue sans moi » (`monde/`). |

## Direction artistique (document reçu le 17 nov. 2026) — recommandation en attente

Le document propose trois niveaux : AAA réaliste, ultra-réaliste, réalisme optimisé.

**Recommandation : réalisme optimisé**, sur Unity URP. C'est la suite logique de D2.

- Ultra-réaliste et AAA réaliste exigent capture faciale, scans de visages et grandes équipes. Ce n'est pas compatible avec Android en même temps.
- Le budget graphique va aux **visages et aux intérieurs** : c'est là que l'enquête se joue (lecture des émotions, pièces qui racontent leurs occupants). Les rues et la foule restent sobres.
- Expressions ambiguës : un menteur n'a pas d'animation « mensonge ». Règle reprise telle quelle.
- URP seul, pas HDRP : le document le dit lui-même, les deux ne cohabitent pas dans un projet.

Trois points du document contredisent des décisions déjà prises :
1. Il redécrit quatre villes réelles (Lubumbashi, Paris, New York, Honolulu). D3 et D4 disent : une ville, South City, fictive. Les autres villes restent hors périmètre.
2. Il dit « photoréaliste ». D2 dit « réaliste stylisé ».
3. Plages : maillots révélateurs et nudité non explicite. À vérifier contre les règles de Google Play et de l'App Store avant de figer quoi que ce soit, car le jeu vise le mobile. Règle ECHOES maintenue : aucune image de corps sans raison d'enquête.

Premier test visuel proposé (avant toute ville) : dans Unity URP, un intérieur (le cabinet), un visage en gros plan
qui joue nervosité / tristesse / méfiance, éclairage jour puis nuit et pluie. Mesure sur un téléphone Android moyen réel.
