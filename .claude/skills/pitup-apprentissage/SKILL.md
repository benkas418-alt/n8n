---
name: pitup-apprentissage
description: Auto-apprentissage sur le projet PitUp. À utiliser au début de toute session PitUp, à chaque retour du fondateur (refus, correction, validation, préférence, explication d'un « pourquoi ») et après chaque livraison, pour lire puis mettre à jour la mémoire rangée en trois tiroirs dans pitup/memoire/. Sert à produire un travail qui ressemble de plus en plus à sa vision, sans lui faire répéter ce qu'il a déjà dit.
---

# Auto-apprentissage PitUp

Le but : que chaque session parte de tout ce que les précédentes ont appris sur le fondateur et sur le projet,
et que le travail lui ressemble de plus en plus. Une leçon qui n'est pas écrite est perdue à la fin de la session.

## 1. Au début de la session

1. Lire `pitup/memoire/LISEZ-MOI.md`, puis `1-essentiel/regles.md` et `1-essentiel/fondateur.md`.
2. Lire les dix dernières entrées de `1-essentiel/apprentissages.md`.
3. Ouvrir le fichier de `2-dossiers/` qui correspond à la demande. S'il n'existe pas, le créer avant de produire.
4. Lancer `bash pitup/memoire/3-atelier/installer.sh etat` et n'installer que ce que la demande exige.

## 2. Avant de produire : le passage au crible

Avant de montrer quoi que ce soit, répondre par écrit, pour soi, à ces questions tirées du portrait :

- Qu'a-t-il **déjà refusé** dans ce dossier ? Est-ce que je suis en train de le lui resservir ?
- Qu'a-t-il **validé** ? Est-ce que je risque d'y toucher ?
- S'il a renvoyé un fichier, est-ce que j'utilise bien **ce** fichier ?
- Y a-t-il une limite que je contourne par un substitut ? Si oui, **la dire tout de suite** et proposer deux voies, au lieu d'essayer plusieurs substituts à la suite.

## 3. À chaque retour du fondateur

Un retour, c'est : un refus, une correction, une validation, une préférence, une explication (« tu sais pourquoi je préfère… »), un fichier renvoyé.

1. **Noter le jour même** une entrée dans `1-essentiel/apprentissages.md`, en haut du fichier :
   date · contexte (quelle livraison) · ce qu'il a dit, au plus près de ses mots · ce que j'en retiens · où c'est rangé.
2. **Ranger** ce que j'en retiens selon sa nature :

| Nature du retour | Où l'écrire |
|---|---|
| Règle qui vaut pour tout (« jamais », « toujours ») | `1-essentiel/regles.md`, avec la date |
| Goût, vision, façon de travailler | `1-essentiel/fondateur.md` |
| Décision sur un dossier précis (validé, refusé, état) | le fichier du dossier dans `2-dossiers/` |
| Recette technique, piège, mesure | le fichier du dossier, ou `3-atelier/outils.md` si elle sert partout |

3. **Séparer les faits des interprétations.** Ce qu'il a dit s'écrit tel quel. Ce que j'en déduis porte la mention « (interprétation) » et reste à confirmer.
4. **Ses messages sont dictés** : les mots peuvent être déformés. Noter le sens, et signaler le doute s'il y en a un.

## 4. Faire monter une leçon en règle

- Une observation isolée reste dans le journal.
- Quand **deux retours** vont dans le même sens, ou quand il donne lui-même le « pourquoi », la leçon monte dans `fondateur.md` ou `regles.md`.
- Quand un nouveau retour **contredit** une règle : la demande la plus récente et la plus explicite l'emporte. Ne pas effacer l'ancienne ligne ; la marquer « remplacée le … » avec la raison.
- Ne jamais transformer une validation ponctuelle (« ça, ça va ») en règle générale.

## 5. Après chaque livraison

1. Mettre à jour l'état du dossier dans `2-dossiers/` : ce qui est livré, ce qui est validé, ce qui reste ouvert.
2. Écrire une ligne de méthode si j'ai perdu du temps : qu'est-ce que j'aurais dû demander ou dire plus tôt ?
3. Copier dans `pitup/tools/` tout script nouveau ou modifié.
4. Valider et pousser sur la branche de la session. Ne jamais y mettre voix, musique, vidéos de tiers ni captures de vrais utilisateurs.

## 6. Tenir la mémoire propre

- `LISEZ-MOI.md` et `regles.md` restent courts : ils sont lus à chaque session. Le détail va dans les dossiers.
- Un dossier terminé garde son fichier ; ajouter « Terminé le … » en tête.
- `historique-complet.md` est une archive : on y cherche, on n'y écrit plus.
- Une fois par semaine de travail, relire `apprentissages.md` : regrouper les doublons, faire monter ce qui se répète, sans rien inventer.

## 7. Ce que cette compétence ne fait pas

- Elle n'autorise aucune dépense, publication ou action irréversible : la confirmation du fondateur reste nécessaire.
- Elle ne remplace pas une question quand un point change vraiment le résultat. Une seule question, claire, puis continuer.
