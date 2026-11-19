# Vidéo « Une commande, du début à la fin » (acheteurs)

Ouvert le 18 nov. 2026. Choisie parmi les idées du 18 nov. : c'est la vidéo qui peut le plus faire monter les commandes (confiance).

## Supports théoriques envoyés par le fondateur (18 nov.)

Il a écrit : « Utilise-les comme support théorique. » Ce sont des leçons, pas des modèles à copier.
- **C** (51 s, créatrice de contenu) : « important / pas important » question par question. Ce qui compte : le hook (« 3 secondes pour capter l'attention »), scripter ses vidéos (« on ne scripte pas avec l'IA »), publier régulièrement, les mots-clés (remplacent les hashtags), montrer des visages (« ça te rend plus humain et ça crée du lien »), un montage soigné sans être expert. Pas important : hashtags, heure de publication, tendances, audio à la mode. Forme : une question courte, une réponse d'un mot, un tableau qui se remplit en haut de l'écran.
- **D** (30 s) : site de référence des effets de montage (galerie avec cas concrets).
- **E** (21 s) : quatre transitions à maîtriser : film burn, masque flicker, flash blanc, whip (transition par mouvement rapide).

- **F** (59 s, 18 nov., graphiste) : cinq sites d'inspiration. Are.na (section Motion : titres, jeux typo, composition, textures) ; Eyecannndy (« iCandy » : bibliothèque de techniques de caméra et de montage, avec le nom de chaque effet) ; Color-hex (palettes ; « tu gardes une DA cohérente du début à la fin ») ; Behance (projets d'artistes : typos, compositions, couleurs) ; Cari (section esthétiques : nom exact d'une « vibe » et images pour un moodboard).

## Ce que j'en retiens (interprétation, à confirmer)

- Hook en 3 secondes ; script écrit à la main pour Lubumbashi ; un visage réel quand c'est possible (le livreur, la cliente) ; montage net.
- Format question / réponse courte qui avance comme un tableau : convient aux questions des acheteurs (« Je paie quand ? À la livraison. »).
- Transitions entre rushs réels et motion : whip, flash blanc, masque flicker, film burn, calées sur le son.

## Matériel

- Rushs de livraison reçus le 18 nov. (4 fichiers WhatsApp, 576×1024 sauf un en 720×1280) : pantalon « Big One » remis au bord de la route (net de 3,3 à 6,8 s), chaussures sorties d'un sachet dans une voiture (net partout), colis remis à une cliente (plus doux), paiement en billets dans la voiture (vidéo couchée : ffmpeg la redresse, recadrer après). Mains seulement, pas de visage reconnaissable. Fichiers hors dépôt.
- Enregistrement d'écran d'une commande dans l'appli : à demander (sans données de vrais clients).

## v1 livrée (18 nov.)

- `pitup/tools/build_cmd.py` + `place_cl.py`, projet `hf/videos/pitup-commande`, 24 s.
- Script : « Commander en ligne à Lubumbashi ? Voici comment ça se passe. Tu choisis ton article dans l'application. La boutique confirme ta commande. Ensuite, nous te livrons. Tu vérifies ton article. Et tu paies à la livraison. » + fin validée du film de lancement (« Découvre PitUp. Le commerce, simplement. »).
- Rushs dans des cadres arrondis 880×1100 sur le fond PitUp (résolution WhatsApp trop faible pour le plein écran). Transitions : flicker à l'ouverture, whip entre rushs, flash blanc sur le paiement. Suivi de commande 2D en haut (Choisir, Confirmer, Livrer, Payer) qui s'allume à chaque étape.
- Musique « What Did I Miss? », départ à 61,54 s du morceau, −17 dB sous la voix, −13 dB au logo (`LOGO_DB=-13`), pleine après la dernière phrase.
- Piège : la retranscription entendait « Des coups » pour « Découvre » ; cause : le souffle du logo tombait sur le mot. Les sons du logo sont maintenant placés avant la phrase.

## v2 (19 nov.)

- Retour : remplacer l'ouverture « au lieu de la première vidéo avec le sachet blanc qui gêne ». Nouveau rush (VID-20260829-WA0199, 15 s) : colis emballé posé sur un sac bleu, sur une table de billard, puis déballage. Retenu : de 3,0 à 6,7 s (net, pas de visage ; une personne apparaît au fond après 6 s). Petite étiquette rose avec un logo de marque, à peine visible.
- Leçon (interprétation) : un emballage plastique qui couvre l'article gêne ; l'ouverture doit montrer un colis propre ou l'article.

## v3 (19 nov.)

- Retour : « J'ai l'impression qu'il manque quelque chose. » Mon diagnostic, validé (« 1 et 2 ») : (1) le colis ouvert au début n'était jamais dévoilé ; (2) la fin ne disait pas quoi faire.
- Corrigé : sur « Tu vérifies ton article », les baskets blanches découvertes dans la boîte (même rush que l'ouverture, 0 à 1,25 s, ralenti ×1,6). Phrase d'appel ajoutée avant le logo : « Ta prochaine commande, c'est sur PitUp. » Le suivi de commande disparaît à cette phrase. 26,5 s, −14,6 LUFS.
- Proposé, en attente d'un rush : un visage (client content à la réception, avec accord).
- Méthode (interprétation) : quand il dit « il manque quelque chose », chercher une promesse ouverte sans réponse (attente installée, appel à l'action) et proposer deux ou trois pistes classées.

## v4 (19 nov.)

- Le fondateur envoie sans commentaire un trajet en voiture dans les rues de Lubumbashi (Snapchat, 1080×1920, très net, 9,6 s). Placé sur « Ensuite, nous te livrons » (1,0 à 3,2 s du fichier), recadré pour sortir l'autocollant « interdit de fumer » du tableau de bord. Suivent les chaussures dans la voiture puis la remise du colis.

## v5 (19 nov.) : théorie de design appliquée (accord « Ok »)

- Échelle typographique 34 / 55 / 89 / 144 / 233 px (base 34 × 1,618) : chaque texte prend le plus grand palier qui tient ; texte au-dessus d'un cadre ou d'un téléphone : 144 au plus. Phrases longues coupées sur plus de lignes pour garder le grand palier.
- Entrées « pop » avec anticipation et dépassement (départ à 86 %, `back.out(1.7)`, 0,3 s). Suivi de commande en 34 px, liseré blanc sur l'étape active (lisible sur fond bleu).

## v6 plein écran (19 nov.)

- Demande : « Et si les vidéos prenaient tout l'espace, au lieu d'une partie ». Fait avec `FULLRUSH=1` (rushs 1080×1920 dans `assets/rushf/`, mots en blanc sur un dégradé sombre en haut, accent bleu clair #8fd0ff, whip sur toute la largeur). Le trajet est recadré pour sortir l'autocollant.
- Limite dite d'avance : rushs WhatsApp de 576 px agrandis ×1,9, un peu plus doux que dans les cadres. Les deux versions (v5 cadres, v6 plein écran) sont livrées pour qu'il compare.

## v7 (19 nov.)

- Base plein écran (v6). Bruitages remplacés par ceux des références C (« important / pas important ») et E (« 4 transitions ») : whoosh sur chaque entrée de rush et avant le logo, swish sur les glissés, pops sur les mots, déclic sur les phrases d'un coup. Contrôle earshot : whoosh détectés, lecture « réel ».
- Phrase 2 : « Voici comment ça se passe avec PitUp. » (prise p10) ; écran « avec PitUp. » + logo ; logo 2D en haut dès la première image. Indices de scènes remplacés par une recherche par texte (`T("…")`).

## v8 (19 nov.)

- Suivi des 4 étapes retiré (« ça fait IA »). Rien d'autre ne change.
