# Règles non négociables

Chaque règle vient d'une demande ou d'un refus du fondateur. La date est celle de la décision.
Une règle ne se supprime que si le fondateur dit le contraire ; noter alors la nouvelle date.

## Conduite

- Répondre en **français**, aller droit au but, livrer un résultat vérifié.
- **Ne jamais modifier ce qui est validé** quand il demande une autre correction. Un défaut vu en dehors de la demande se signale, il ne se corrige pas seul.
- **Ne jamais livrer un fichier non vérifié.** Dire ce qui a été contrôlé et ce qui ne l'a pas été.
- Demander avant toute dépense ou publication.
- Ne jamais inventer un chiffre, une fonctionnalité ou une source.
- Chaque vidéo est livrée avec sa **description prête à copier**.
- Images livrées en JPEG, une par une (un zip de 44 Mo ne se télécharge pas sur son téléphone).

## Marque et texte

- Écrire « **PitUp** ». Aucune phrase ne commence par « PitUp ». La marque dit « nous ».
- Seul chiffre autorisé : « **+100 boutiques locales** ». Aucun prix. « Paiement à la livraison ».
- Ne pas écrire « disponible dès maintenant ».
- **Phrases complètes** (17 nov.) : chaque phrase dite a un sujet et un verbe, une seule idée ; un chiffre se dit avec ce qu'il veut dire (« +100 boutiques locales nous ont déjà rejoints »), jamais seul.
- **Acheteurs et vendeurs séparés** (17 nov.) : « Tu paies à la livraison » va avec les acheteurs ; « +100 boutiques locales nous ont déjà rejoints » va avec les vendeurs. Ne jamais les mélanger dans une phrase.
- Site : **pi-tup.com**. Applis sur App Store et Google Play ; badges officiels vectoriels seulement.
- Descriptions : simples, sans cliché, sans jeu de mots, sans question artificielle.

## Image

- **Netteté d'abord** (14 nov.) : quand il dit « clair », il veut dire **net**. Un plan flou est refusé, même s'il est le seul à montrer Lubumbashi.
- **Pas de plan déjà publié** (14 nov.) : il reconnaît les plans « vus et revus ». Aucun plan réutilisé dans une même vidéo.
- **Ne jamais faire passer une autre ville pour Lubumbashi** (14 nov.) : bâtiments, taxis, plaques le trahissent. L'identité culturelle passe par ces détails.
- **Continuité de lumière** (14 nov.) : si le plan suivant est de jour, l'ouverture est de jour.
- Interdits : moto, fumeur, supermarché (exception : façade d'Alilac Center), logo de grande marque visible, filigrane TikTok.
- Personnes non filmées en Afrique : gros plans sans décor reconnaissable seulement.
- **Vendeurs PitUp** (14 nov., corrigé le 17 nov.) : boutiques d'habillement, chaussures, accessoires. **Ne pas parler de vente de téléphones** : il n'y a pas encore vraiment de boutique de téléphones. Les étals de vivres ne servent qu'à illustrer la ville ou le commerce en général.
- Visuels de l'appli : vraies captures ou vrais enregistrements d'écran dans un **téléphone 3D**, de face, sans grain ni vignettage. Varier les écrans.
- **Le texte suit le son** (17 nov.) : grosse caisse → le mot tombe d'un coup ; clic de déclencheur photo → la phrase apparaît d'un coup ; clics de clavier → lettre après lettre, une lettre par clic.
- Fin de vidéo : « **Disponible sur** » au-dessus des badges des stores (17 nov.).
- **Pas de liste numérotée** à l'écran (14 nov.) : « ça donne l'effet liste ». Animer les mots.
- Pas de compteur de pages sur les carrousels. Profils sans photo : initiales dans un cercle de couleur.
- Couleur de marque **#1f88c9**. Poppins pour pubs et carrousels, Lexend pour les vidéos produits.
- Aucune image générée par IA qui « rappelle l'IA ».

- **Motion design = notre DA** (17 nov.) : fonds clairs ou dégradé bleu PitUp, Poppins, #1f88c9. Pas de décor photo ou vidéo en fond (ciel, nuages). Les images ne font qu'illustrer, brièvement.
- **Une référence est une inspiration** (17 nov.) : en tirer des idées de mouvement, de transition et de rythme ; ne jamais en copier le décor ni l'univers.
- **Rythme d'un motion** (17 nov.) : 1 à 3 mots à l'écran à la fois ; ils disparaissent et les suivants arrivent aussitôt ; chaque entrée a un mouvement et un son qui lui correspond.

- **Téléphone dans un motion = vrai téléphone 3D réaliste** (17 nov.) : épaisseur, tranche titane, boutons, verre, il tourne en 3D ; l'enregistrement d'écran suit ses mouvements. Modèle : `phone()` dans `pitup/tools/build_launch3.py`.
- **Logo PitUp et éléments graphiques en 2D** (17 nov.) : logo, cartes, pastilles à plat, couleur pleine #1f88c9 ou blanc, sans dégradé ni ombre portée. Seuls le téléphone et les produits ont du relief.
- **Articles détourés** (17 nov.) : produits sans fond, posés sur le fond blanc (ombre douce seulement). Outil : rembg (`isnet-general-use` ou `birefnet-general-lite`, une image par processus, sinon manque de mémoire).

## Son

- **Jamais ElevenLabs.**
- Deux voix seulement : la **sœur** (voix actuelle) et la « jumelle ». Jamais mélangées.
- Recette de voix de référence : voir `2-dossiers/voix-off.md` (recette « Motion point », validée le 14 nov.).
- Jamais d'étirement temporel de la voix.
- **Musique avec paroles possible** (17 nov.) : basse sous la voix pendant le film (vers −17 dB), elle remonte quand le logo arrive.
- **Jamais d'amapiano.** Musique actuelle : Tems « Me & U » (fichier du fondateur, hors dépôt).

## Structure d'une pub (14 nov.)

- Accroche : **un plan large un peu aérien, puis un ou deux plans de détail** (« un grand truc, poup, un petit truc »). Cinq secondes sans texte ni voix.
- Chaque pub fait comprendre **qui** est concerné, **ce que fait** l'appli et **comment**.
- La fin **invite à rejoindre** la plateforme. Elle n'est pas « commande et paie à la livraison ».
- Le numérique se suggère, il ne s'annonce pas.

## Dépôt et confidentialité

- Dépôt public : ni voix, ni musique, ni vidéo de tiers, ni capture de vrais utilisateurs.
- Ne pas mettre son adresse électronique dans une requête vers un service extérieur. Ne jamais lui demander de coller un secret dans la discussion.
- Pousser seulement sur la branche de la session. Pas de pull request sans demande explicite.
