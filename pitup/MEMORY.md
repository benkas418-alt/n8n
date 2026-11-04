# PitUp — mémoire de projet (vidéos et campagnes)

> À lire en premier dans toute nouvelle session : « Lis `pitup/MEMORY.md` et reprends le travail PitUp ».
> Dernière mise à jour : 4 novembre 2026.

## 1. Contexte

- **PitUp** : marketplace de Lubumbashi (RDC). Les clients commandent dans des boutiques partenaires (**+100 boutiques**, chiffre confirmé). PitUp livre. **Paiement à la livraison** uniquement.
- Site = appli : **pi-tup.com** (applis App Store et Google Play).
- Public cible des vidéos produits : **jeunes de 15 à 25 ans**, surtout les filles (« girly ») pour la mode et la beauté.
- Langue : français. Tutoiement dans les pubs.

## 2. Règles validées par le fondateur (à respecter sans exception)

### Contenu
- **Ne jamais inventer** de chiffres, de fonctionnalités ou de noms. Seul chiffre confirmé : « +100 boutiques ».
- **Pas de prix** dans les vidéos, sauf demande explicite. La dernière consigne (fin octobre) est : « Ne mets pas le prix ». Si un prix est demandé, l'afficher en FC et en $ (1 $ = 2 300 FC), sans « au lieu de ». Le prix PitUp est `customer_price` dans l'API, pas `price`.
- **Pas de grandes marques visibles** (Nike, Adidas, Lacoste, LV…). **Exception** pour la catégorie chaussures : marques autorisées, avec les vrais noms des modèles (Stan Smith, Campus, Samba…).
- Articles **seuls, non portés, sans mains**, produit au centre, de qualité.
- **Badges App Store et Google Play à la fin de toutes les vidéos.**
- Pas de compteurs du type « 1/6 ».
- Groupes d'images en nombre impair (1, 3, 5, 7).
- URL « pi-tup.com » épelée lettre par lettre à la voix, en phonétique française : « pé, i, tiret, té, u, pé, point com ». Jamais « P. I. T. U. P. », que la voix lit à l'anglaise.
- Message du service client : « Bonjour Mademoiselle Grâce, c'est le service client PitUp » (sans « Peter »).

### Voix
- **Ne jamais utiliser ElevenLabs.**
- Voix acceptée : **Rémy** (edge-tts `fr-FR-RemyMultilingualNeural`). Script : `tools/tts_edge_words.py`.
- Voix féminine acceptée : **Vivienne** (`fr-FR-VivienneMultilingualNeural`). Elle a été utilisée pour Octobre Rose.
- Voix refusées : **Liam** (accent québécois). Aucune voix gratuite n'a d'accent africain : le mieux serait une vraie voix enregistrée à Lubumbashi.
- Ne pas modifier la voix (pas d'égaliseur ni de compression) : la garder brute.

### Musique
- Instrumental sous la voix. **Jamais d'amapiano.** Éviter les chansons romantiques (Babydoll, Cheap Cologne, white keys et Has to be you ont été écartées).
- **On peut réutiliser une chanson**, avec un passage différent à chaque fois. L'ancienne règle « une chanson par vidéo » est abandonnée.
- Couper la musique sur les frappes (grille de tempo : `tools/beats_*.py`).
- Bibliothèque d'origine : PitUp-Rise, PitUp-Street, PitUp-Calm, PitUp-Afro (fichiers .wav ou .mp3), Connor Price « I Need Help », Imagine Dragons « Enemy », Kairo Keyz « float 2.0 », Deca OTA « Hallelujah ». Ajouts d'octobre : MARNY « Passer l'hiver », TEZZ (Michael Olise, KANAN, Next Up, SUPRACELL, Coco), OLISE, Kairo Keyz (GANG, WENT UP, Can You Love Me Tonight). **Le fondateur va ajouter de nouvelles musiques** : elles ne sont pas dans le dépôt (droits d'auteur et taille). Il faut les lui redemander.

### Signature sonore
- **Abandonnée (« oublie ça ») le 4 novembre.** Ne pas l'imposer. Le beat synthétique avait été jugé « très IA ». Le piano Salamander (vrais échantillons, CC-BY) passait mieux à l'analyse earshot (p_real 0,94), mais il n'a pas été validé.

## 3. Styles visuels réalisés et retours

| Vidéo | Style | Retour |
|---|---|---|
| Journal (P2), Acheteurs (Pub06), E1 « Comment ça marche » | Papier, journal, Monsieur Peter (bonhomme noir narrateur), voix | Validées après corrections |
| Promo Mini-ventilateurs | Prix FC + $ demandés exceptionnellement | Validée |
| Tendance v2 à v6 | Format « P1 / Ta liste » (graphiste) : produit détouré, grand mot de fond, titres | Validé, puis lassitude (« mêmes articles ») |
| Baskets (catégorie) | P1 avec les noms des modèles | Validée |
| Pour elle | P1 | Refusée : « change la DA, plus de texte, de meilleurs articles » |
| Girly Panorama v1 à v3 | Panoramique sur panneaux pastel, aucun texte, mosaïque, fin PitUp | v3 = la meilleure (catalogue complet, détourage soigné) |
| Storytelling « Grâce » v5 | Dessin, téléphone réaliste avec l'UI PitUp, horloge qui défile, voix Rémy | Corrections faites (horloge, prononciation de l'URL) |
| Octobre Rose v2 | Charte rose, voix Vivienne | Livrée |
| Gourdes style Sony puis 3D, Sacs 3D (Higgsfield) | Pub « Prism » de Sony, Three.js | **Concept rejeté** : « pas fluide, ça s'entre dedans, pas beau » |

À retenir : le fondateur veut des articles **attirants pour les 15-25 ans, variés, jamais déjà vus**, bien détourés, au centre, sans mains ni « autres histoires ».

## 4. Prochaines tâches (au 4 novembre)

1. **Vidéos de présentation d'articles AVEC VOIX.** Ça fait longtemps qu'il n'y a pas eu de publication. Il en faut plusieurs.
2. **Nouvelles vidéos de storytelling** (plusieurs).
3. Attendre les nouvelles musiques du fondateur et les ajouter à la bibliothèque.
4. **Campagne cadeaux de Noël et des fêtes**, à lancer vers mi-novembre (à discuter).
5. Idées de pub retenues, inspirées des grandes marques (voir § 6).

## 5. Méthode technique (recettes testées)

### Catalogue PitUp (API publique, sans connexion)
- `GET https://pi-tup.com/api/v1/marketplace/products/?limit=100&offset=N` : 626 produits, champ `images[]` avec toutes les photos (500 px max), `customer_price` (prix PitUp), `store.store_name`, `category`, `stock_quantity`, `is_in_stock`.
- `GET https://pi-tup.com/api/v1/marketplace/categories/`
- Toujours prendre **la meilleure photo** de chaque produit (souvent pas la principale). Vérifier le stock.

### Images
- **Upscale ×4** : `tools/upscale.py` (Real-ESRGAN en ONNX, modèle `imgdesignart/realesrgan-x4-onnx` sur Hugging Face, à télécharger dans `/root/.cache/esrgan/model.onnx`). Environ 1 min par photo sur CPU.
- **Détourage** : `tools/cut_v6.py` (rembg `isnet-general-use`, agrandissement ×2, nettoyage identique pour tous les objets, en gardant tous les objets d'au moins 12 % de la taille du plus grand). Toujours vérifier sur une planche contact et rejeter les détourages ratés.
- BiRefNet a été testé : pas meilleur sur des photos de 500 px, et manque de mémoire.

### Vidéo
- **HyperFrames** CLI `npx -y hyperframes@0.8.181` (`lint`, `snapshot --at T -o dir`, `render . --quality high --fps 30 -o renders/video.mp4`). Composition 1080×1920, timeline GSAP en pause dans `window.__timelines["main"]`. Ne pas animer `top`/`left` (utiliser x/y).
- Après le rendu : remultiplexer l'audio (`bgm.wav`) dans le MP4, puis encoder en crf 18. La version WhatsApp est une copie du fichier crf 18 (deux passes à 5 800k si le grain alourdit le fichier).
- Sources de chaque vidéo : `pitup/videos/<projet>/index.html`. Ressources communes (polices Poppins, logos PitUp, GSAP, grain) : `pitup/shared-assets/`.
- Three.js : r160 (`npm pack three@0.160.0`). Les GLB se chargent par importmap locale. Le rendu 3D logiciel est lent (environ 20 min pour 30 s).

### Audio
- Grille de tempo : `tools/beats_*.py` (recherche du BPM), puis caler la vidéo sur la montée (drop).
- Mixage : musique à 0,4–0,45 (`bass g≈3`), voix décalée de 300 ms à 1,6, loudnorm en deux passes à −13 LUFS (−14 pour une vidéo avec voix calme).
- Placement de la voix : générer **phrase par phrase** avec les horodatages des mots (WordBoundary), puis caler chaque texte à l'écran sur son mot.
- **earshot** (`github.com/Leonxlnx/earshot`, à installer dans un venv avec torch CPU, environ 1,1 Go de modèles) : il **écoute** à ma place. Vérifier chaque son avant de l'envoyer (`realness` donne p_real, `describe`, `timeline`).

### Outils et crédits
- **Higgsfield** : 3,5 crédits restants (plan gratuit). SAM 3D coûte 1 crédit par objet.
- **vidIQ** : 2 crédits (renouvellement le 31 octobre). Une voix vidIQ coûte 14 crédits.
- Compétences installées dans `~/.claude/skills` (à réinstaller dans une nouvelle session) : earshot, real-sound, watch, ad-creative, copywriting, marketing-psychology, creative-director, competitive-ads-extractor, brainstorming, banner-design, poster-hero, design, brand, design-system, ui-ux-pro-max, slides, ui-styling, ecommerce-image-workflow, motion-design, design-motion-principles, emilkowalski-motion, gsap-timeline, frame-logo-outro, threejs, mockup-device-3d, apple-design, context-compression, paywall-upgrade-cro, brand-guidelines. Sources : ui-ux-pro-max-skill, Leonxlnx/earshot, bradautomates/claude-video, nexu-io/open-design, kylezantos/design-motion-principles, LottieFiles/motion-design-skill, dickwu/apple-design-skill, muratcankoylan/Agent-Skills-for-Context-Engineering.

## 6. Idées de campagne retenues (inspirées des grandes marques)

1. **« Le moment du livreur »** (Amazon, Shein) : vraies réactions de clientes à la livraison, avec leur accord. Nécessite des tournages au téléphone.
2. **« Jour PitUp » mensuel** (11.11 d'Alibaba, Jumia) : une date fixe, un compte à rebours, une offre.
3. **« Commande pour… » avec des prénoms** (Coca-Cola « Share a Coke »).
4. **Slogan sonore répété** (Temu, Shopee) : la signature a été mise de côté pour l'instant.
5. **Bilan PitUp de fin d'année** (Spotify Wrapped), uniquement avec de vraies données.
6. **« Shot by PitUp »** (Apple) : les meilleures photos des boutiques.
7. **La vie après la livraison** (Amazon « Joy Ride »).

Le fondateur a choisi les idées 1, 3, 4 et 7 comme vidéos à produire.

## 7. Où sont les fichiers

- **Dans ce dépôt** (`pitup/`) : cette mémoire, les scripts `tools/`, les sources HTML des 26 vidéos, les ressources communes et les visuels du storytelling.
- **Hors dépôt** (perdus à la fin de la session cloud) : les vidéos livrées (MP4), les musiques, les détourages et les GLB. Les livrables ont été envoyés au fondateur.
- Avant de livrer une vidéo : planche contact des captures, earshot sur l'audio, puis envoi en version WhatsApp.
