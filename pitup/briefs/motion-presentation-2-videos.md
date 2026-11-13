# Brief : 2 motion designs de présentation PitUp

Demande du fondateur (13 novembre 2026). À produire dans une nouvelle session, après lecture de la section 0 de `pitup/MEMORY.md`.

## Objectif

Deux vidéos courtes qui présentent PitUp en peu de mots. Chaque vidéo répond aux questions qu'un inconnu se pose :

| Question | Réponse à faire passer |
|---|---|
| Quoi ? | Une appli pour acheter, vendre et trouver un pro. |
| Qui ? | Les clients, les vendeurs (boutique en ville, stock à la maison, boutique perso), les prestataires (graphiste, photographe, vidéaste, maquilleuse, coiffeuse). |
| Où ? | Lubumbashi, en RDC. |
| Comment ? | Tu commandes, la boutique confirme, nous livrons, tu paies à la livraison. Pour un service : tu publies ton besoin, des pros postulent, tu choisis. |
| Pourquoi ? | Gagner du temps, éviter les allers-retours, trouver la bonne personne. |
| Quand ? | Maintenant, depuis ton téléphone. Ne pas écrire « disponible dès maintenant ». |

Ton : clair, court, professionnel. Pas de cliché ni de jeu de mots. Texte à l'écran en français, tutoiement, la marque parle en « nous ».

## Références envoyées par le fondateur

4 vidéos dans le chat du 13 novembre (à redemander si besoin). Ce qu'elles ont en commun :
- typographie animée **mot par mot**, grands mots centrés (« we don't build… ») ;
- éléments d'interface qui apparaissent et s'animent (cartes, boutons, curseur), sur fond blanc ou bleu ciel (« Meet heyclicky », « Book a project ») ;
- fonds très sobres : blanc cassé, ou bleu nuit dégradé ;
- logo final qui se construit, puis signature.

Vidéos déjà faites dans ce style : `PitUp-Motion-*` (dossier `pitup/motion/`). Ne pas reprendre les mêmes plans.

## Vidéo A — « En 20 secondes » (typographie, fond bleu nuit)

Format 1080 × 1920, 18 à 22 s. Mots qui arrivent un par un, rythme calé sur la musique.

1. « Lubumbashi. »
2. « Tu veux acheter, »
3. « vendre, »
4. « ou trouver un pro ? »
5. « Une seule appli. » Le logo PitUp se construit.
6. « +100 boutiques locales. »
7. « Des graphistes, photographes, maquilleuses… »
8. « Tu commandes. Nous livrons. »
9. « Tu paies à la livraison. »
10. Fin : « pi-tup.com », badges Google Play et App Store.

## Vidéo B — « L'appli en action » (interface, fond blanc et bleu ciel)

Format 1080 × 1920, 20 à 25 s. Un téléphone de face (règle `app_clear` : écran net, sans grain), un curseur qui navigue.

1. Titre : « Voici l'appli qui connecte Lubumbashi. »
2. Barre de recherche : on tape « baskets ». Des cartes produits apparaissent (boutiques locales).
3. Onglet « Services » : cartes graphiste, photographe, maquilleuse.
4. Un client publie « Photographe pour un mariage ». Trois candidatures arrivent.
5. Commande : « La boutique confirme », « Nous livrons », « Paiement à la livraison ».
6. Fin : « Acheter. Vendre. Trouver un pro. », « pi-tup.com », badges.

## Règles à respecter

- Aucune phrase ne commence par « PitUp ». Pas de prix. Seul chiffre : « +100 boutiques locales ».
- Couleur #1f88c9, police Lexend (vidéos) ; le carrousel du 13 novembre utilise Poppins comme les affiches du fondateur.
- Interfaces : recréer des écrans propres (voir `pitup/carousel-rdc/index.html`, classes `.ui`, `.cand`, `.bub`). Ne pas reprendre les captures des affiches : elles contiennent un prix (150 $) et des fautes (« Disigner », « dispibles »).
- Musique : jamais d'amapiano, demander au fondateur s'il veut une voix off ou seulement de la musique.
- Contrôles avant envoi : section 0.5 de `MEMORY.md` (images clés, earshot, true peak).

## Points à confirmer avec le fondateur avant de produire

1. Le service « prestataires / freelances » est-il déjà ouvert à tous, ou « bientôt » (son affiche dit « Commence bientôt ») ? La réponse change le mot « Quand ».
2. Les métiers à citer : la liste ci-dessus vient de ses affiches. En ajouter d'autres ?
3. L'adresse du site : ses affiches écrivent à la fois « pi-tup.com » et « pit-up.com ». La mémoire retient **pi-tup.com**.
4. Voix off (voix de la sœur) ou musique seule.

---

# Tâche liée : carrousel « changement digital en RDC » avec des personnes

Le fondateur veut des **photos de personnes** (banques d'images libres de droits) dans le carrousel livré le 13 novembre (`pitup/carousel-rdc/`).

- Source choisie par le fondateur : **Pexels** (licence gratuite, usage commercial, sans mention obligatoire). Il faut une **clé API Pexels gratuite** (pexels.com/api). Le 13 novembre, le formulaire sécurisé n'a pas abouti : la redemander avec l'outil `request_credential` (hôte `api.pexels.com`), ou demander au fondateur de l'ajouter dans les réglages de l'environnement. Pexels lit la clé dans l'en-tête `Authorization`, sans préfixe : vérifier qu'une clé au format « Bearer » fonctionne, sinon passer par les réglages.
- Unsplash et Pexels refusent les téléchargements sans clé, et Openverse ne donne que des résultats hors sujet.
- Une photo par page, de personnes noires africaines, lumineuses, à détourer ou en plein cadre :
  1. couverture : jeune femme souriante avec un téléphone (comme l'affiche « Prépare-toi à un changement digital ») ;
  2. vendeuse devant son stock à la maison, ou dans une petite boutique ;
  3. personne qui reçoit un colis à sa porte ;
  4. créatif au travail (ordinateur, appareil photo) ;
  5. mosaïque : photographe, graphiste, vidéaste, maquilleuse, coiffeuse (une photo par tuile) ;
  6. pro qui regarde son téléphone ;
  7. client qui discute sur son téléphone ;
  8. groupe ou duo souriant.
- Garder les textes, l'ordre et les écrans recréés du carrousel actuel (déjà conformes aux règles). Noter la page Pexels de chaque photo dans `pitup/carousel-rdc/credits.md`.
- Vérifié le 13 novembre (bibliothèque `ngandu-dev/pexels`) : Pexels lit la clé **brute** dans l'en-tête `Authorization`, sans « Bearer ». Le formulaire `request_credential` ajoute « Bearer » par défaut : préférer l'ajout de la clé par le fondateur dans les réglages de l'environnement (secret réseau pour `api.pexels.com`, sans préfixe). Appel : `GET https://api.pexels.com/v1/search?query=...&orientation=portrait&per_page=15`.
- Règles Pexels : créditer quand c'est possible (« Photos : Pexels » dans la description suffit pour un carrousel).
