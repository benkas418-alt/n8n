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

# Tâche liée : carrousel « changement digital en RDC » avec des personnes — FAITE (13 novembre)

Version avec photos livrée : 11 photos Pexels (téléchargées directement depuis images.pexels.com, sans clé API), liste et liens dans `pitup/carousel-rdc/credits.md`. Les photos ne sont pas dans le dépôt : les retélécharger avec `curl "https://images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?auto=compress&cs=tinysrgb&w=1600" -o ph/<ID>.jpg`.
Méthode qui marche sans clé : recherche web `site:pexels.com <sujet>` → l'ID est à la fin de l'adresse de la page → serveur d'images. Unsplash et Pexels bloquent les navigateurs automatiques et l'API demande une clé (suspendue chez Pexels).
