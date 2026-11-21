# PitUp — marketing, contenu et règles d'animation

> Notes tirées de 7 publications Instagram envoyées par le fondateur le 21 novembre 2026.
> Lire avec `pitup/MEMORY.md`. Les règles du fondateur de MEMORY.md passent avant ces conseils.
> Ce qui est marqué **(vidéo)** vient des publications. Ce qui est marqué **(PitUp)** est notre façon de l'appliquer : ce sont des idées à tester, pas des résultats mesurés.

## 1. Cinq notions de marketing (reel De-OcSuiGYe)

| Notion (vidéo) | Ce que ça veut dire | Pour PitUp |
|---|---|---|
| **La vache pourpre** (Seth Godin) | Être remarquable, sinon on est invisible. | Ce qui est remarquable à Lubumbashi : commander dans plus de 100 boutiques depuis son téléphone, se faire livrer et **payer à la livraison**. Le paiement à la livraison doit être dans chaque pub : il lève la peur de payer pour rien. |
| **AIDA** : attention, intérêt, désir, action | L'ordre d'un message qui vend. | Vidéo produit : 1 s d'accroche (« Les sneakers que tout le monde veut… »), puis l'article, puis l'envie (variantes, couleurs), puis l'action (badges des stores, « sur PitUp »). C'est déjà la structure P1 : la garder. |
| **TOFU, MOFU, BOFU** (haut, milieu, bas du tunnel) | Un message différent selon que la personne découvre, compare ou est prête à acheter. | Haut : « PitUp, c'est quoi ? », storytelling, Lubumbashi. Milieu : tutos, vidéos boutiques, « comment ça marche ». Bas : articles précis, nouveautés, Jour PitUp, relance de ceux qui ont l'appli. Publier les trois chaque semaine, pas seulement du haut. |
| **L'effet Lindy** | Une idée qui marche depuis longtemps continuera de marcher. | Préférer les formats éprouvés (avant/après, « 3 pièces pour… », réaction à la livraison) aux effets à la mode. Le concept 3D « Prism » a été rejeté : c'est cohérent avec cette idée. |
| **Product-market fit** | Une offre que les clients adorent et recommandent sans qu'on les pousse. | Le mesurer par les **commandes répétées** et le bouche-à-oreille, pas par les téléchargements. Question à poser aux clientes après la 2e commande : « Comment as-tu connu PitUp ? » |

## 2. Onze biais de l'esprit (reel Df5IXu4he5O)

Règle : s'en servir pour **rendre une vraie offre claire**, jamais pour tromper. Pas de faux compte à rebours, pas de faux « prix barré » (règle du fondateur : jamais de « au lieu de »).

| Biais (vidéo) | Usage honnête pour PitUp |
|---|---|
| **Effet de leurre** | Montrer 3 choix dont un moins intéressant fait choisir le bon. Ex. : 3 sacs côte à côte, le sac mis en avant au milieu. |
| **Ancrage** | Le premier chiffre vu sert de repère. Si un prix est un jour affiché, montrer d'abord l'article le plus cher de la série. |
| **Effet de halo** | Une belle image fait juger tout le reste comme bon. D'où la règle : photos détourées, nettes, au centre. Une seule mauvaise photo abîme toute la vidéo. |
| **Effet projecteur** | Chacun croit être plus observé qu'il ne l'est. Accroche : « Tout le monde remarque tes chaussures. » |
| **Coûts irrécupérables** | On continue ce qu'on a commencé. Côté client : un panier commencé → relance douce. Côté PitUp : ne pas s'acharner sur un format qui ne donne pas de commandes. |
| **Aversion à la perte** | Perdre fait plus mal que gagner fait plaisir. « Plus que 3 en stock » **seulement si c'est vrai** (`stock_quantity` de l'API). |
| **Effet IKEA** | On aime plus ce qu'on a construit soi-même. Faire composer : « Choisis ta tenue en 3 pièces », listes de souhaits. |
| **Dunning-Kruger** | Les débutants surestiment ce qu'ils savent. Pour les boutiques : un tuto simple vaut mieux qu'un long texte (le tuto « Créer sa boutique » va dans ce sens). |
| **Effet Ben Franklin** | Quelqu'un qui nous rend service nous apprécie plus. Demander un avis, une photo de déballage ou un partage à une cliente satisfaite. |
| **Illusion de fréquence** | Une fois qu'on a remarqué un nom, on le voit partout. Répéter le même logo, la même phrase de fin et les mêmes couleurs dans toutes les vidéos. |
| **Loi de la trivialité** | On passe trop de temps sur les petits détails faciles. En réunion : décider d'abord ce qui fait des commandes (offre, boutiques, livraison), la couleur d'un bouton après. |

## 3. Vingt éléments pour le site pi-tup.com (reel DfKl5gIjOcC)

Liste de la vidéo, à vérifier sur pi-tup.com avant d'en parler au développeur :
mode sombre · bandeau cookies (seulement si le site pose des cookies de suivi) · recherche · bouton retour en haut · menu mobile · animations de chargement · effets au survol · barre de progression · boutons copier · version imprimable · header fixe · lien « aller au contenu » · afficher le mot de passe · suivi UTM · message « formulaire envoyé » · messages d'erreur clairs · fenêtres de confirmation · date de mise à jour · FAQ dépliable · bouton contact flottant.

Les plus utiles pour PitUp, dans l'ordre :
1. **Suivi UTM** sur chaque lien de pub (TikTok, Instagram, WhatsApp). Sans lui, on ne sait pas quelle vidéo amène des commandes. Format : `pi-tup.com/?utm_source=tiktok&utm_campaign=noel`.
2. **Bouton contact flottant WhatsApp** (le canal que les clients utilisent déjà).
3. **Barre de progression de la commande** : commandée, préparée, en route, livrée.
4. **FAQ dépliable** : livraison, délais, paiement à la livraison, retours.
5. **Recherche** et **afficher le mot de passe** (beaucoup d'échecs de connexion viennent d'une faute de frappe).

## 4. Idées de design (carrousel Growly, DfewL7EiFpI)

Maquette de tableau de bord par le studio Phenomenon. À reprendre pour **l'espace boutique** de PitUp :
- Un **anneau** avec un seul grand chiffre au centre (ex. : commandes du mois), et autour la part de chaque statut.
- Des **barres de progression** fines plutôt que des tableaux.
- Des **badges** qui récompensent (« 10 commandes livrées », « 0 retard cette semaine ») pour motiver les boutiques.
- Une version téléphone d'abord : la plupart des boutiques gèrent tout depuis leur téléphone.

## 5. Les 18 règles d'animation (reel Dfm1bXkAM6U)

Valables pour l'interface (site, appli) **et** pour le motion design des vidéos (HyperFrames, GSAP).

| # | Règle (vidéo) | Valeur (vidéo) | En GSAP / CSS (PitUp) |
|---|---|---|---|
| 1 | Ce qui **entre** ralentit à la fin | ease-out | `ease: "power2.out"` ; CSS `cubic-bezier(0.2, 0.7, 0.2, 1)` |
| 2 | Menus et petits panneaux rapides | 150 à 250 ms | `duration: 0.2` |
| 3 | Lignes d'une liste en **cascade** | 30 ms entre chaque ligne | `stagger: 0.03` (texte, prix, variantes) |
| 4 | Bouton appuyé légèrement plus petit | `scale(0.97)` | `:active { transform: scale(.97) }` |
| 5 | Ce qui bouge s'**étire** un peu dans le sens du mouvement | 12 % | `scaleX: 1.12` pendant le trajet, retour à 1 à l'arrivée |
| 6 | Trajectoires **en courbe**, pas en ligne droite | — | `motionPath` GSAP ou x et y avec des eases différents |
| 7 | Une **pulsation** confirme une réussite | — | scale 1 → 1.06 → 1 en 300 ms (ex. : badge « Livré ») |
| 8 | Ce qui se **déplace** accélère puis ralentit | ease-in-out | `ease: "power2.inOut"` |
| 9 | Popover qui part de 95 %, jamais de 0 | `scale(0.95) → 1` | avec opacité 0 → 1 |
| 10 | L'élément **sort de son déclencheur** | — | `transform-origin` sur le bouton qui l'ouvre |
| 11 | Il **rentre** dans son déclencheur en se fermant | — | même origine à la fermeture |
| 12 | **Pas de ressort** sur les changements de page | — | pas de `back` ni `elastic` sur les transitions d'écran |
| 13 | Les sorties durent **20 % de moins** que les entrées | entrée 250 ms → sortie 200 ms | — |
| 14 | L'ancien et le nouvel état se **croisent** | en même temps | fondu croisé, pas « l'un puis l'autre » |
| 15 | Les révélations ont du **poids** | masque de révélation | `clip-path: inset()` animé plutôt qu'un changement sec |
| 16 | Une icône en remplace une autre avec **échelle + opacité + flou** | — | `filter: blur(4px)` → 0 avec scale .8 → 1 |
| 17 | **Résistance élastique** en bout de glissement | — | le contenu suit le doigt de moins en moins au-delà du bord |
| 18 | Le **même objet grandit** au lieu d'être remplacé | `layoutId` (Framer Motion) | GSAP Flip (`Flip.getState` / `Flip.from`) |

À retenir pour les vidéos PitUp :
- Entrées de produits : ease-out, 0,4 à 0,6 s en vidéo (plus long que dans une interface, l'œil doit lire), cascade de 30 à 60 ms pour le texte.
- Changements de scène : ease-in-out, **sans rebond** (le fondateur a déjà rejeté ce qui « n'est pas fluide »).
- Une pulsation sur les badges des stores à la fin.
- Garder la règle de MEMORY.md : ne jamais animer `top` et `left`, utiliser x et y.

## 6. Le reste

- **SaaSwave** (reel DcvVp-Qof2x) : publicité pour une formation payante (After Effects, Blender, FL Studio). Rien à reprendre ; les règles du § 5 couvrent l'essentiel.
- **Kitchen de dqnamo** (reel DeO7DugISSR) : composants React et Framer Motion à copier (bouton « maintenir pour supprimer », zone de dépôt magnétique, reçu imprimé). Utile seulement si l'appli PitUp est en React. Lire la licence sur dqnamo.com avant de copier du code. L'idée du **reçu qui s'imprime** ferait une bonne fin de vidéo « ta commande est confirmée ».
