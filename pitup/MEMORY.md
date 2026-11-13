# PitUp — mémoire de projet (vidéos et campagnes)

> À lire en premier dans toute nouvelle session : « Lis `pitup/MEMORY.md` et reprends le travail PitUp ».
> Dernière mise à jour : 13 novembre 2026.

## 0. DÉMARRAGE D'UNE NOUVELLE SESSION (à lire en entier, puis appliquer)

Cette section résume l'état actuel. **En cas de contradiction avec une section plus bas (archives), cette section l'emporte.**

### 0.1 Rôle attendu
Directeur artistique, monteur vidéo, ingénieur du son et stratège marketing de PitUp, en même temps. Répondre en **français**. Produire des résultats vérifiés, pas des conseils. Avant chaque tâche : lister les skills utiles et les **charger** (Skill tool), puis appliquer la mécanique de travail (§ « MÉCANIQUE DE TRAVAIL », plus bas).

Skills à mobiliser selon la tâche :
- Marketing et texte : `pitup/skills/pitup-content-engine`, `pitup/skills/conversion-copywriting-engine`, `pitup/skills/viral-psychology-strategist` (dans ce dépôt, à lire avec Read si la session ne les liste pas), plus `copywriting`, `social`, `short-form-video`, `ad-creative`, `marketing-psychology`.
- Vidéo : `hyperframes`, `hyperframes-cli`, `hyperframes-audio`, `motion-design`, `kinetic-typography`, `caption-animation`, `short-form-video`, `media-use`.
- Son : `earshot` (écoute obligatoire avant toute livraison), `real-sound`.
- TikTok : dépôt `sergebulaev/tiktok-skills` (skill `tt-caption-writer` : 3 à 5 hashtags, première ligne visible porteuse, question précise en fin si l'objectif est le commentaire, réglage « Contenu commercial → Ta marque »).

### 0.2 Règles du fondateur (toutes actives)
- **Contenu** : ne jamais inventer de chiffre ni de fonctionnalité. Seul chiffre : « **+100 boutiques locales** ». Pas de prix. **Paiement à la livraison** (à l'écran : « Paiement à la livraison. »). Ne pas écrire « disponible dès maintenant ».
- **Voix de marque** : la marque parle en « **nous** ». **Aucune phrase ne commence par « PitUp »**. Écrire « PitUp » (P et U majuscules).
- **Interdits à l'image** : moto, fumeur, supermarché (exception validée : façade de l'Alilac Center), personnes filmées sans accord évident, **réutilisation d'un même plan dans une vidéo**, logos TikTok ou filigranes (recadrer ou retoucher).
- **Musique** : jamais d'amapiano. Chanson actuelle validée : Tems « Me & U » (fichier fourni par le fondateur, hors dépôt).
- **Voix** : jamais ElevenLabs. Deux voix seulement, jamais mélangées : **la sœur** (choix actuel) et « jumelle ». Jamais d'étirement temporel de la voix. Jamais de collage de prises : une seule prise complète.
- **Méthode** : ne jamais modifier ce qui est validé quand le fondateur demande une autre correction. Signaler un défaut hors demande, ne pas le corriger seul. Demander avant toute dépense. Ne jamais envoyer un fichier non vérifié.
- **Livraison** : chaque vidéo est livrée avec une **description prête à copier**.

### 0.3 Direction artistique actuelle (validée, v44 « Ah, Lubumbashi »)
- Couleur de marque **#1f88c9**. Police **Lexend**. Format 1080 × 1920, 30 i/s.
- **Plans de la ville** : en couleur, étalonnage commun (`tools/grade.py`). Le noir et blanc a été testé puis **abandonné** par le fondateur.
- **Partie appli** (`"app_clear": true` dans la config) : écrans et cartes produits **sans grain, vignettage ni reflet**. Téléphone qui se stabilise **de face**, 8 % plus grand. Fond **bleu ciel lumineux** (dégradé `#8fd3fa → #2a96da`), avec le bleu de marque derrière les titres (contraste ≥ 3:1).
- **Visuels de l'appli = vrai téléphone en 3D** (perspective, épaisseur, reflet, ombre), jamais un écran plat. Modèle CSS : classe `.phone` de `pitup/carousel-rdc/index.html`. Utiliser de **vraies captures** de l'appli ; écrans recréés seulement en attendant les vraies (le fondateur doit fournir celles des services : candidatures, discussion).
- **Carrousels : format 4:3 PAYSAGE (1440 × 1080)**, demandé explicitement par le fondateur (le 3:4 vertical coupait le bas sur sa plateforme). Mise en page en 2 colonnes (texte à gauche, visuel à droite). Rendu `DSF=4 node shot43.js …` → 5760 × 4320. Profils sans photo dans les écrans recréés : **initiales dans un cercle de couleur**.
- **Badges des stores : toujours les fichiers OFFICIELS vectoriels**, jamais redessinés (`pitup/carousel-rdc/appstore.svg` « Download on the App Store », `Google_Play_Store_badge_EN.svg` « GET IT ON Google Play », triangle en couleur). Le badge Apple officiel est noir et blanc (règle d'Apple). Livrer les images en **JPEG qualité 92, une par une** : un zip de 44 Mo ne se télécharge pas sur le téléphone du fondateur.
- **Version 9:16 (1080 × 1920)** des carrousels pour stories, Reels et TikTok : `pitup/carousel-rdc/index916.html`, rendu `DSF=4 node shot916.js …` → 4320 × 7680. Garder 240 px libres en haut et 300 px en bas (boutons des applis). Pour décaler des positions par script, ne jamais toucher `border-top` (regex `(?<![-\w])top:`).
- **Vraies captures des services (13 novembre)** : fil « Projets » (Moon events, Riguene Lewewe) et projet de Henock Nlandu, fournies par le fondateur. Avant usage : effacer les étiquettes « Tarif indicatif … $ » (règle sans prix) et la barre d'état (heure, notifications). Fichiers nettoyés `scr/real_feed.png` et `scr/real_beauty.png` : HORS dépôt (vrais profils de personnes), à redemander au fondateur. Écran « Aucune offre disponible » : ne pas utiliser.
- **Instagram (constaté le 13 novembre)** : un carrousel publié sans toucher au cadrage s'affiche en CARRÉ, et coupe le haut et le bas de toute image plus haute (9:16, 3:4). Livrer d'office une **version carrée 1:1** (`pitup/carousel-rdc/index11.html`, `DSF=3 node shot11.js …` → 4320 × 4320). Pour une version portrait, le fondateur doit choisir le cadrage (icône des flèches) AVANT de sélectionner plusieurs photos. Le 9:16 sert pour les stories et TikTok, pas pour le fil Instagram.
- **Motion « carrousel RDC » (13 novembre)** : `tools/build_mc.py words.json 0.5 34 index.html` (animations calées sur les mots, règles du fondateur : ease-out, lignes décalées de 30 ms, sorties 20 % plus courtes, pas de ressort aux transitions, icônes en fondu + flou, pulsation de réussite, téléphones 3D en courbe), voix `tools/mc_voice.sh` (prise unique de la sœur, débruitage, pauses aux ponctuations), bruitages RÉELS earshot `fit/*` (swish, finger_phone, floss_lid, lip_pop, domino, small_bell) sur les repères d'image, musique Tems instrumentale à 90 s (≠ 40,18 s de Lubumbashi). Leçon voix : « photographe, vidéaste » → le f avale le v ; mettre « vidéaste » après « graphiste ». Aperçu rapide : `node tools/frames.cjs page.html prefix t1 t2…`.
- **Aucun compteur de pages** (« 2/8 ») sur les carrousels : les plateformes l'affichent déjà.
- Ordre des scènes, textes et animations : voir `pitup/cfg/v14_ciel.json` (le dernier plan ajouté est `s_alilac`, tiré d'un TikTok de @djeudy_243 et recadré : créditer ou demander l'accord).

### 0.4 Son « studio » (validé le 13 novembre)
Chaîne complète (scripts dans `pitup/tools/`) :
1. `wiener_denoise.py soeur_6.wav dn.wav 26 2.0` : retire le souffle **aussi sous la voix**.
2. `SRC=dn.wav rebuild_voice_studio.sh out.wav "highpass=f=80,afftdn=nr=14:nf=-60:tn=1,equalizer=f=250:t=q:w=1.0:g=-3,equalizer=f=3200:t=q:w=1.2:g=1.5,highshelf=f=9000:g=-2,deesser=i=0.5" -24` (pauses du plan validé, respiration après « Ah », queue de pièce).
3. `pause_dip.py` à **8 dB** (pas plus : effet de pompage).
4. Retouches validées : « v » de « venir » repris de la voix non débruitée ; fin de « bouge » prolongée (décroissance de 40 ms).
5. Mix : `ORIG_ALL=1 CARVE_DB=4 HIGH_DB=6 mix_duck_end.py … 10`, puis `loudnorm=I=-14:TP=-2:LRA=11`, puis `alimiter=limit=0.56:level=0` sur-échantillonné, AAC `twoloop` 192k.
Jamais d'`aexciter` ni de remontée des aigus : ce réglage créait le grésillement.

### 0.5 Contrôles obligatoires avant chaque envoi
`voice_qa.sh` (0 FAIL réel), transcription whisper (2 erreurs = niveau de référence, dues à « PitUp »), `earshot critique` (0 critique, 0 majeur), true peak du fichier livré ≤ −1 dBTP, planche des images clés. Rapporter les chiffres et dire ce qui n'a pas été vérifié.

### 0.6 Textes et descriptions
Style voulu : **simple, clair, sans cliché ni jeu de mots**. Le fondateur a refusé « en couleur » et les questions artificielles. La promesse doit tenir dans la première ligne visible sur TikTok. Description validée pour « Ah, Lubumbashi » :
```
+100 boutiques locales de Lubumbashi dans une seule appli. Tu commandes depuis chez toi, on te livre, et tu paies à la réception.

Lien en bio 📲

#Lubumbashi #Lushi #RDC #pourtoi #fyp
```

### 0.7 Ce qui n'est PAS dans le dépôt (à redemander au fondateur)
Le dépôt est public : on n'y met ni voix, ni musique, ni vidéos de tiers. Pour reprendre « Ah, Lubumbashi » ou refaire une voix, demander au fondateur le **kit média** (archive qu'il a reçue le 13 novembre) : plans vidéo (`story/v`), prise de la sœur (`audio/v32/soeur_6.wav`) et sa référence (`audio/soeur/`), chanson Tems. Outils à réinstaller si besoin : `hyperframes@0.8.181` (npx), faster-whisper medium, VoxCPM2, earshot (`leonxlnx/earshot`).

### 0.8 Prochaine tâche demandée (13 novembre)
Produire les **2 motion designs de présentation** : tout est prêt dans `pitup/briefs/motion-presentation-2-videos.md` (scripts, style, règles, questions à poser au fondateur). Le carrousel « changement digital en RDC » est livré, avec des **photos de personnes** Pexels (crédits : `pitup/carousel-rdc/credits.md`) ; source : `pitup/carousel-rdc/` (rendu : `node shot.js $PWD/index.html $PWD/out`, polices Poppins dans `pitup/carousel/fonts` si présentes, sinon Google Fonts).

### 0.8 bis Motion carrousel v2
Le fondateur a refusé la v1 (trop explicative). Concept proposé : `pitup/briefs/motion-carrousel-v2-concept.md`, PRODUIT le 13 novembre (`tools/build_mc2.py`, sans voix off, mot « Coupure. »). Mix : musique qui coupe net à l’interrupteur, revient étouffée (filtre 900 Hz) puis s’ouvre quand la ville s’allume ; bruitages réels earshot fit/* + notify/m1, m2. Photo salon : Pexels 20853654.

### 0.8 ter Motion « Lushi, ça bouge » v3 (13 novembre)
Le fondateur a aimé l'idée de la v2 mais jugé les visuels trop pauvres (dessins CSS). v3 = `tools/build_mc3.py` : photos réelles (ampoule Pexels 132340, visage éclairé par le téléphone 8036649, salon 20853654), phrase-pont « Ton téléphone, lui, reste allumé. », produits réels qui se réveillent, viseur photo, recherche tapée, 3 bandes de vrais plans de Lubumbashi (vidéo TikTok @djeudy_243 fournie par le fondateur : Alilac 0-2,2 s, circulation 24,5 s, centre 18,8 s ; recadrés pour ôter le logo, `grade.py`, ralentis par minterpolate) qui passent de la nuit au jour. Palette : bleu nuit #050a14/#12304c + bleu marque, mots-clés en #4fb0ec. Piège GSAP : avec `immediateRender:false`, donner l'état initial en CSS (sinon le texte est visible avant son entrée). Leçon : préférer des images réelles animées aux illustrations dessinées en CSS.

### 0.8 quater Pub « Lushi, ça bouge » en images réelles (13 novembre)
Demande du fondateur : style pub de grande marque (Airtel, Vodacom, Orange, Amazon) : plans FILMÉS de vraies personnes, peu d'effets, rien qui « rappelle l'IA ». `tools/build_ad.py` : 3 bandes de Lubumbashi (« Ici, à Lubumbashi »), puis 5 plans plein cadre avec une ligne chacun (« Tu vends. » marché 37179494, « Tu crées. » couturière 37409118, « Tu coiffes. » tresseuse 20431410, « Tu cherches. » 5355337, « Nous livrons. » 6868889), l'appli sur téléphone 3D (« Tout Lubumbashi. Une seule appli. »), logo. Coupes nettes, zoom lent 6 %, musique seule.
Vidéos Pexels SANS clé : `https://www.pexels.com/download/video/<ID>/` (original, parfois 4K) ou `https://videos.pexels.com/video-files/<ID>/<ID>-hd_1080_1920_30fps.mp4` (le suffixe fps varie : 24, 25, 30). Trouver les ID par recherche web `site:pexels.com/video <sujet>`. Vérifier chaque plan : pas de logo de grande marque (carton Amazon écarté). Dans la vidéo @djeudy_243, le plan de circulation commence à 25,47 s (avant : station-service avec des personnes).

### 0.9 Tâches en attente (ne pas lancer sans demande)
Vidéo « Lundi » ; question d'orthographe « Pitup » / « PitUp » ; retrait éventuel de 47 anciennes images (photos de profil) du dépôt ; plans de boutiques montrant des personnes.

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
- **VoxCPM2** (moteur de VoiceStudio, pip `voxcpm`, CPU, environ 30 s par phrase, modèle `openbmb/VoxCPM2`) : crée une voix à partir d'une description, au format `(description)texte`. Script : `tools/vox_design.py`. Essais du 4 novembre (« jeune femme congolaise, douce et dynamique ») : earshot p_real 0,95 et 0,98, transcription exacte. **Le fondateur doit encore les valider.** Il sait aussi **cloner** une voix à partir de 15 à 30 s d'enregistrement : c'est la piste pour une vraie voix de Lubumbashi, avec l'accord écrit de la personne.

### Voix de l'égérie (clonée, 4 novembre)
- L'égérie de PitUp est la sœur du fondateur. Sa voix est clonée avec **VoxCPM2** (`tools/vox_clone_texts.py`), en mode « référence + style ».
- **Référence** : les 21,3 premières secondes de sa vidéo TikTok (micro studio, sans musique), envoyée dans le chat par le fondateur le 4 novembre. **Le fichier audio n'est pas dans le dépôt** (donnée personnelle) : il faut le redemander au fondateur.
- Style qui marche : `(voix douce et posée, chaleureuse, avec le sourire)`.
- **Écrire « Pitt-Eup » ou « Pite-Eupe » à la place de « PitUp »**, sinon elle dit « Pitop ». Lubumbashi est bien prononcé en mode style.
- À éviter : le mode « continuation » (prompt_wav + prompt_text), qui ajoute la fin de sa phrase de référence (« Je te dis… »), et le mode référence seule, qui déforme Lubumbashi.
- Mesures earshot : p_real d'environ 0,93, timbre proche de l'original (brillance 1 900 à 2 300 Hz contre 2 880 Hz).
- Garder l'**accord écrit** de l'égérie pour l'usage de sa voix clonée.
- En attente de validation : v1 (« Pitt-Eup », plus claire) ou v2 (« Pite-Eupe », plus chaude).

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
- Compétences installées dans `~/.claude/skills` (à réinstaller dans une nouvelle session) : earshot, real-sound, watch, ad-creative, copywriting, marketing-psychology, creative-director, competitive-ads-extractor, brainstorming, banner-design, poster-hero, design, brand, design-system, ui-ux-pro-max, slides, ui-styling, ecommerce-image-workflow, motion-design, design-motion-principles, emilkowalski-motion, gsap-timeline, frame-logo-outro, threejs, mockup-device-3d, apple-design, context-compression, paywall-upgrade-cro, brand-guidelines, voicestudio, et les 15 compétences de motion design de charlie947/motion-graphics-skills (launch-video, reference-to-motion, motion-effects, reel-export…). Le dépôt aedev-tools/adobe-agent-skills (After Effects) exige un Mac avec After Effects : il n'est pas installable ici. Sources : ui-ux-pro-max-skill, Leonxlnx/earshot, bradautomates/claude-video, nexu-io/open-design, kylezantos/design-motion-principles, LottieFiles/motion-design-skill, dickwu/apple-design-skill, muratcankoylan/Agent-Skills-for-Context-Engineering.

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

## Mise à jour du 4 novembre (soir) : vidéos produits avec la voix de l'égérie
- **Voix officielle : « voix 3 »**. Style des phrases produits : `(voix douce et posée, chaleureuse, avec le sourire)`.
- **« PitUp » se dit à l'anglaise, d'un trait** (version C validée le 4 novembre) : écrire « PitUp » normalement, avec le style `(voix claire et naturelle, débit normal, avec le sourire)`. « Pite-Eupe » est **refusé** (trop lent, sonne « érotique »). Seule l'adresse du site est épelée : « pé, i, tiret, té, u, pé, point com ».
- « Les articles sélectionnés ne sont pas flatteurs » : choisir des **pièces tendance façon Europe et États-Unis pour les 15-35 ans** (Mary Jane, Samba, Campus, Asics, Shox, TN, sacs type Longchamp ou Coach, Ray-Ban, Kayali, robe en jean, veste en cuir). Toujours montrer une **planche de candidats à valider** avant de traiter.
- **Marques** : autorisées à l'image (logo visible sur la photo). Nom de marque écrit ou dit **seulement pour les sneakers**.
- **Article en plus de 5 variantes** (couleurs ou modèles) : en faire une **vidéo dédiée**. On montre les variantes et le nom de l'article, puis « Retrouve-les sur PitUp, chez [boutique] ». Candidats : Jordan 4 Nigel Sylvester (MB Ephphatha), Mary Jane (Rogatienne), gourdes (Wees fk), huile de parfum (Maella online shopping), Club de Nuit (Natty boutique), casquettes (ETS GOD BLESS), Stanley (Maison Rossa, tenue en main).
- Les autres articles vont dans des vidéos **Pour elle** et **Pour lui**, au format P1 habituel (`tools/build_voix2.py` + `cfg/*.json`).
- **Mix voix (règle du fondateur)** : la musique baisse dès le premier mot et reste très basse (environ −23 dB), **sans remonter entre les phrases**, jusqu'à la fin de la dernière phrase. Elle reprend pleinement sur la carte de fin, avec environ 3,5 s de musique seule (`tools/mix_duck.py`, `gap: 0.5`).
- **Accroche** : « Les pièces tendance d'Europe et des States… sont déjà à Lubumbashi. » / « Les sneakers que tout le monde veut… sont déjà à Lubumbashi. »
- **Prononciation** : « Nike Shox TL » devient « Night Shocks DL ». Dire « Les Nike Shox, en noir. » Écrire « Asiks » pour Asics.
- Musique : Tiakola « Mode de vie » (134 BPM, gros temps à 29,664 s) pour Femme, Blockkids (130 BPM) pour Homme.
- **Piège** : ne jamais mettre en file d'attente avec `while pgrep -f vox_clone_texts`, parce que les lignes de commande des files d'attente se détectent entre elles et bloquent tout.
- **Vidéos dédiées, refusées par le fondateur** : Jordan 4 (« bizarre ») et Mary Jane (déjà traitées). **Réalisée le 4 novembre** : Club de Nuit, 6 parfums chez Natty boutique, sur Tiakola « Cléopâtre » (113 BPM, temps fort à 17,085 s), `cfg/cdn1.json`. Les photos ne se détourent pas (carte ARMAF devant, rayons derrière) : on les présente en **cartes photo arrondies** (`extra_css` dans la config).
- Accroche validée pour Pour elle : « Les pièces tendance du moment… sont déjà à Lubumbashi. » **Ne pas dire « Europe et States ».**
- Prononciation : « Untold » devient « Untold. Couleur bordeaux. », et « Club Night Woman » devient « Et la Club Night Woman. ».
- **Tuto « Créer sa boutique »** (4 novembre) : `tools/build_tuto.py` + `cfg/tuto1.json`. L'égérie vouvoie (« Vous êtes nombreux à nous avoir demandé… »). Le vrai enregistrement d'écran tourne dans une maquette de téléphone, sur 5 étapes, avec un cercle à chaque appui. **Numéro de téléphone flouté.** Retirés : l'erreur réseau, les photos personnelles de la galerie et le message « Vous avez déjà une boutique ». Musique : Kairo Keyz « float 2.0 ». Les segments d'écran sont découpés par ffmpeg (vitesse ×1,6 à ×4).
- **Tuto v2 (retours du fondateur)** : téléphone en **vraie 3D** (tranche en titane faite de couches CSS, boutons, vitre avec reflet, rotation à chaque étape). **Pas trop de sauts** : vitesse ×1 à ×2, un seul flux d'écran continu avec des fondus (`tools/tuto_master.py`). **Numéro de téléphone visible**, pas flouté (choix du fondateur). Bannière : logo ETS Blessing incrusté dans le champ « Bannière », en entier, sur fond blanc.
- **Jet Lag (Tiakola et Jorja Smith)** : la voix parlée au début (« À courir derrière la prospérité… », de 0 à 7 s) et l'intro **ne sont pas à garder**. Tiakola commence à **16,5 s** (« Je suis dans un rêve… ») ; le beat tombe à 15,0 s, à 120 BPM. Démarrer le morceau à 16,5 s. Utilisé pour le tuto boutique.
- **Transcription** : sur certaines machines, whisper de hyperframes plante (SIGILL). Solution de secours : faster-whisper dans le venv `/home/user/fw` (modèle small, int8), avec l'audio lu par soundfile.
- **5 novembre** : vidéo « PitUp, c'est quoi ? » (`tools/build_quoi.py`, 9 scènes animées : Lubumbashi, problème acheteur, problème vendeur, téléphone 3D, Tu achètes ?, Tu vends ?, +100, appli ou site, drapeau de la RDC), sur Raindance à partir de 13,3 s. Vidéo boutique « Wees fk en lumière » (`cfg/weesfk.json`, format P1), sur Coco à partir de 12,106 s (93,46 BPM). Dans le lot « Yara » (337), la bouteille noire est une **Asad** et non une Yara.
- **Prononciation** : « Wees fk » s'écrit « Wiz, èf, ka ». Ne jamais commencer une phrase par « PitUp » (elle dit « Pitop ») : écrire « bienvenue sur PitUp » ou « sur PitUp ». Pour « tu commandes, on te livre », écrire des phrases courtes séparées par des points. Pour les noms de parfums difficiles (Badée al Oud), dire « un parfum oud » et afficher le vrai nom à l'écran. Faire 3 prises d'une phrase délicate et garder celle que la transcription reconnaît.
- **Vérification de la voix** : faster-whisper `medium`, avec `initial_prompt` pour les noms propres.
- **Disque plein** : les renders intermédiaires (`hf/videos/*/renders`) et les caches pip/uv se suppriment ; les livrables restent dans `livrables/`.
- **Public : jeunes noirs africains (RDC).** Toute personne visible à l'écran doit être noire africaine. Refuser les plans de stock avec des personnes non africaines ou des décors étrangers (montagne enneigée, marché européen).
- **Le fondateur veut de vraies images, pas du graphisme** : un vrai téléphone en main, une vraie carte ou une vue satellite de Lubumbashi, de vraies boutiques. Sources utilisées :
  - satellite Esri (avec crédit) et plan OpenStreetMap (avec crédit) via `tools/mapzoom.py` ;
  - photos des boutiques partenaires prises dans le catalogue de l'API ;
  - vraies captures de pi-tup.com via Playwright (`/marketplace` montre les boutiques, sans prix) ;
  - vidéos libres Mixkit (gratuites, usage commercial permis), uniquement avec des personnes noires ;
  - vidéo de rues de Lubumbashi envoyée par le fondateur, signée « DJEUDY / @djeudy243 » : **son accord est à confirmer avant publication**.
  Pexels, Pixabay et Wikimedia sont bloqués depuis le conteneur.
- La page `/shopping` du site affiche les prix : ne pas l'utiliser.
- **Règle du fondateur (redite deux fois)** : **l'appli et le site apparaissent toujours dans un téléphone 3D**, jamais à plat en plein écran. Le site sur ordinateur apparaît dans un **ordinateur portable 3D** avec la **vraie page `/marketplace`** qui défile (la page d'accueil « Pour vous » n'est pas représentative). Voir `tools/build_quoi3.py` : téléphone et ordinateur en 3D placés à la racine du document, ce qui permet de mettre des vidéos sur l'écran du téléphone.
- Vidéo de DJEUDY : accord confirmé. **Aucun flou ni aucun nom dans une pub** (règle du fondateur) : la signature « Directed by DJEUDY » et le badge « @djeudy243 » sont **effacés et le décor reconstruit** avec LaMa (`tools/lama_wm.py` et `tools/lama_clip.py` ; modèle ONNX dans `/root/.cache/lama/lama.onnx`, à retélécharger depuis HF `Carve/LaMa-ONNX`). Ne jamais utiliser `delogo` ni le flou.
- **5 novembre** : « PitUp, c'est quoi ? » v4 **validée** (« C'est bon, on passe »).
- **7 novembre — succès** : « PitUp, c'est quoi ? » v4 a fait 8 000 vues en 1 jour, environ 600 likes, 22 commentaires, 250 enregistrements et 150 abonnés. **On continue sur cette formule** (histoire racontée + vraies images de Lubumbashi + téléphone 3D), **mais sans redondance artistique** : chaque vidéo a sa propre direction de motion design, inspirée de prompt-motion.com.
- `tools/build_story.py` (config dans `cfg/story_*.json`) propose plusieurs styles :
  - `glass` : cartes et légendes en verre dépoli, mots qui apparaissent un à un ;
  - `kin` : typographie géante évidée (on voit Lubumbashi à travers les lettres) ;
  - `city` : coupes rapides, écrans partagés, légendes discrètes avec trait bleu ;
  - `base` : le style de « c'est quoi ».
  Types de plans disponibles : v, rapid, split, img, cut, phone, lap, mosaic, flag.
- Les **images de Lubumbashi passent en premier** : la vidéo de DJEUDY est nettoyée en entier (`real/lushi_clean.mp4`, via `tools/lama_wm2.py`) et découpée en plans L0 à L39 (`tools/lushi_shots.sh`). En complément : images Mixkit avec uniquement des personnes noires (youth, couple, suit, rooftop, smile, doubt, phoneman, dad), et rayons de boutique sans personne.
- Traces de badge restées après nettoyage sur L12, L14 et L29 : éviter ces plans.
- Le quota hebdomadaire du fondateur est limité : livrer chaque vidéo en une fois, et grouper les retours.
- **7 novembre** : compte GitHub du fondateur **suspendu** (envoi impossible). Sauvegarde de la mémoire et des outils sur une page claude.ai privée « PitUp mémoire projet ». Défilement du site : utiliser `tools/make_pans.py` (défilement fluide, sans saccade). Plan L9 (abribus) : un homme qui fume, **à exclure**.
- **Nouvelles musiques (7 novembre)** : Gaillard Jules « Reculer » (beat à partir de 16 s), Ravyn Lenae « Love Me Not », Mai Mai « Why Me » (énergique dès 12 s). Elles s'ajoutent à Tiakola, que le fondateur aime aussi. **Remix d'OLISE** : le fondateur veut **le couplet de la rappeuse**, en anglais, de **39,8 s à 53 s**. Le caler pour qu'il démarre au moment où la carte de fin arrive.
- Vidéos du 7 novembre : « Vendre » (style glass, Reculer), « Paie à la livraison » (style kin, remix d'OLISE), « Lubumbashi ne s'arrête jamais » (style city, Why Me). Leurs fichiers finaux sont `livrables/PitUp-Story-*-v3`.
- **Retours du 7 novembre (soir)** :
  - jamais deux fois le même plan, ni dans une vidéo ni d'une vidéo à l'autre ;
  - pas d'écran partagé qui coupe les gens au torse ;
  - **pas de moto pour la livraison** (PitUp ne livre pas à moto) : utiliser le monsieur aux cartons (handoff, handoffB, handoffC) ;
  - « Vendre » passe sur Samuel Petra « Blame » ;
  - le fondateur **aime beaucoup « Paie à la livraison »** (style kin).
- **Vidéos de motion design** (musique seule, `pitup/motion/*.html`) :
  - V4 « Le point bleu » (prompts 8 et 9, Tiakola « Wu Tang Clan » à partir de 12 s) ;
  - V5 « Survol 3D » de `/marketplace` (prompt 4, Hallelujah, coup fort à 9,97 s) ;
  - V6 « Lancement verre dépoli » (prompt 3, Tiakola « Mode de vie », coup fort à 6 s).
  Pour le survol 3D : mettre la rotation sur un conteneur parent et faire glisser la page dans ce conteneur (sinon la page sort du cadre).
- **Retours du 7 novembre (motion v2)** :
  - V4 : vraie carte OpenStreetMap de Lubumbashi (`real/osm16.jpg`), long trajet suivi par la caméra (de 7,4 s à 12,4 s), durée 18,5 s. La voix mo_1 est à 13,7 s.
  - V5 : la caméra doit être **très près** de la page (échelle 2,1, inclinaison 14°). Elle suit un trajet lisse de boutique en boutique, puis recule et plonge sur la carte finale.
  - V6 : **plus de robe en jean, sandales, sacs pour femme, parfums, tissus ni bodys.** Utiliser des articles tendance « à l'européenne » vendus sur PitUp : ensemble Nike Tech, survêtement adidas, veste sherpa à capuche, montre DW, baskets cuir, mocassins, polo maille, joggings adidas, plus TN, Shox, Asics, Campus, Samba, veste en cuir, lunettes. Détourages dans `prod/tr/*_s.png`.
  - Toutes les vidéos durent **20 s au maximum**.
- **Retours du 7 novembre (storytelling v5)** : la vidéo Livraison (style kin, OLISE) est **parfaite, ne pas y toucher**. Pour Vendre et Lushi :
  - **Aucun plan déjà vu dans « C'est quoi » v4** : L0=djA, L2=djD, L11=djF, L28=djC et L29=djB sont des doublons exacts, comme box, phapp et toutes les captures phs_*. Vérifier avec une comparaison image par image avant chaque nouvelle vidéo.
  - **Aucun plan répété dans une vidéo** : le montage rapide (`rapid`) joue maintenant chaque plan une seule fois.
  - **Plus de plaque en verre** derrière les textes (`"plate": false` dans la config) : le texte est blanc avec une ombre.
  - Nouvelles captures du téléphone faites à partir des vraies pages de pi-tup.com (`tools/make_pp.py`) : ph_store (boutique MB Ephphatha), ph_swipe (Nike Tech, sherpa, adidas, Ralph Lauren, Timberland), ph_buy (appui sur « Acheter maintenant »), lap_store (boutique sur ordinateur). **Les prix sont masqués automatiquement.**
  - Produits à montrer : des articles beaux et tendance (Nike Tech, montre DW, Timberland, parfum Yara pour « beauté »). Plus de robe en jean.
- **Motion v3 (7 novembre)** :
  - V4 : Wu Tang Clan commence à **4,62 s**, 4 mesures plus tôt (130 BPM). Ne jamais laisser passer la phrase « pour les faire chier » (27,6 s dans la chanson).
  - V5 : le prompt 4 demande que **le site se décompose en pièces détachées**. Les 33 vraies cartes de la page (et l'en-tête) se soulèvent vers la caméra quand elle passe et laissent leur emplacement vide. Vu d'en haut, tout le site flotte en morceaux. Ne pas incliner les pièces (rotationX) : leurs bords se coupent en 3D.
  - V6 : « Nos boutiques, chez toi » montre **les boutiques elles-mêmes** : une grille de 12 photos de profil rondes avec leur nom (logos récupérés sur /marketplace dans `real/stores`). Pas d'articles à cet endroit. Écarter les logos qui affichent des prix, un numéro de téléphone ou un nom délicat.
- **Motion v4 (7 novembre)** :
  - **Mixage de la voix** (`tools/motion_mix.py`) : la musique commence à baisser 0,6 s avant la voix, selon une courbe douce, jusqu'à −20 dB. Pendant la voix, on creuse en plus de 8 dB la bande 300 Hz – 4 kHz de la musique. La musique remonte en 1 s. Toutes les phrases sont mises au même niveau, et la normalisation finale est un simple gain (pas de compression). Viser une voix au moins 12 dB au-dessus de la musique dans cette bande ; le script affiche cette mesure. Ne jamais baisser la musique d'un coup.
  - V4 : le point bleu dans la barre de recherche est le bouton de recherche, avec une loupe blanche à l'intérieur, et le curseur vient cliquer dessus. Le trajet **suit les vraies rues** de la carte (`tools/map_route.py` : masque des couleurs de routes de la carte, puis chemin le moins coûteux ; l'API Overpass n'est pas joignable). Trajet : Route de Kipushi (RN1), Chaussée Mzee Kabila, Avenue Lumumba, puis les rues résidentielles. À l'arrivée, un repère bleu avec une **icône de maison** (sans le mot « maison »).
- **Story v6 (7 novembre)** :
  - Vendre : **les titres sont en blanc uni**, sans mot en dégradé ni effet verre (le fondateur préfère le blanc).
  - Lushi : sur « Bienvenue sur PitUp », **ne pas montrer le drapeau** (il ne servait de référence à rien). On montre **la vraie carte de la RDC** (frontières Natural Earth 50 m, `real/drc/drc.json`), remplie aux couleurs de PitUp : bleu de la marque, motif de logos PitUp, grand logo au centre et point « Lubumbashi » au sud-est. Type de plan `drc` dans `build_story.py`.
- **Motion v5 et Lushi v7 (7 novembre)** :
  - Lushi : **garder le plan aérien de l'hôtel Pullman Karavia** (L14). La carte de la RDC remplace seulement le drapeau, au moment où la voix dit « Bienvenue sur PitUp » (1,54 s dans vc_2, donc à 23,2 s).
  - **Toujours un vrai message.** Les vidéos motion étaient belles mais ne disaient rien. Désormais, la voix guide le spectateur à chaque étape (chercher, choisir, ajouter au panier, se faire livrer, payer à la livraison) et finit par un appel à l'action : « Télécharge l'appli PitUp, ou commande sur pé, i, tiret, té, u, pé, point com ». En marketing, on oriente le regard, l'oreille et le geste du client.
  - Durées : V4 21,5 s, V5 19,5 s, V6 22 s. Une vidéo peut dépasser 20 s quand elle porte un vrai message.
  - Voix dans `audio/v9`. Pièges de VoxCPM : il dit « Téléchargez » ou « On télécharge » au lieu de « Télécharge », et « Je te commande » au lieu de « Tu commandes ». Toujours vérifier chaque prise avec whisper.
- **Volume uniforme (7 novembre)** : le fondateur ne veut pas d'un volume qui monte et descend. Dans `tools/motion_mix.py` :
  - un seul creux continu, de la première phrase à la dernière (les écarts de moins de 5 s sont fusionnés), donc la musique ne remonte jamais entre deux phrases ;
  - sous la narration, un réglage automatique maintient la musique à un niveau constant (±2 dB), même pendant un drop ou un coup fort ;
  - toutes les phrases sont au même niveau ;
  - la musique ne remonte qu'après la dernière phrase.
- **Appel à l'action trop rapide (7 novembre)** : une seule longue phrase (« Télécharge l'appli PitUp, ou commande sur pé, i, tiret, té, u, pé, point com ») sort trop vite, parce que le modèle accélère sur un texte long. En plus, j'avais gardé la prise la plus courte et le style « débit normal ». Règle :
  - couper l'appel en deux phrases calmes séparées par une pause d'environ 0,5 s : « Télécharge l'appli PitUp. » (style C + « débit lent ») et « Ou commande sur pé… i… tiret… té… u… pé… point com. » (style S + « débit lent », avec des points de suspension entre les lettres) ;
  - garder **la prise la plus lente** qui est propre (`audio/v9/e0_1`, `e1_0`), et non la plus courte ;
  - prévoir environ 6,5 s pour l'appel final. Durées des vidéos motion : V4 23,6 s, V5 21,8 s, V6 24,4 s (la dernière image de la carte de fin est tenue plus longtemps).
- **Intonation forcée sur « PitUp » en fin de phrase (7 novembre)** : « Télécharge l'appli PitUp. » sonnait aigu et forcé (voix à 247 Hz au lieu d'environ 195, et +2 demi-tons sur PitUp). Règles :
  - **ne pas finir une phrase courte sur « PitUp »** : mettre le mot au milieu (« Télécharge l'appli PitUp dès aujourd'hui. », prise `audio/v9/f1_1`) ;
  - ne pas ajouter « débit lent » au style C ;
  - **mesurer la courbe de la voix** (librosa.pyin) : la fin doit descendre (demi-tons négatifs) et la hauteur moyenne doit rester proche de celle des autres phrases.
  - Durées actuelles : V4 24,2 s, V5 22,4 s, V6 25 s.
- **Compétence « pitup-content-engine » (10 novembre)**, fournie par le fondateur : elle est installée dans `~/.claude/skills/pitup-content-engine`, avec une copie dans `pitup/skills/`. **La relire avant chaque nouveau script.** Points clés :
  - commencer par une situation humaine que tout le monde reconnaît, **pas par « vendeurs » ou « acheteurs »** ;
  - au moins 5 hooks (visuel + verbal + texte écran), notés avant le choix ;
  - une seule idée par vidéo ;
  - des scènes réelles et faciles à tourner plutôt qu'un rendu de pub IA ;
  - aucun chiffre, délai ou fonctionnalité inventé ;
  - un appel à l'action adapté à l'objectif (pas toujours « télécharge l'appli ») ;
  - chaque vidéo associée à une hypothèse et à un indicateur.
  En cas de nouvelle session, réinstaller la compétence depuis `pitup/skills/`.
- **Trois compétences du fondateur (11 novembre)**, installées dans `~/.claude/skills/`, avec une copie dans `pitup/skills/` à réinstaller à chaque nouvelle session :
  - `pitup-content-engine` : **quoi filmer** (TikTok/Reels, histoires du quotidien, storyboard, publication).
  - `viral-psychology-strategist` : **pourquoi ça marche** (attention, rétention, partage, confiance). Sert aussi au diagnostic d'une vidéo publiée et à l'adaptation TikTok, Facebook, Instagram et LinkedIn.
  - `conversion-copywriting-engine` : **les mots qui font agir** (légendes, publicités, appels à l'action, fiches produits, WhatsApp, pages). Une seule conversion par texte, adaptée au niveau de maturité du public : froid, tiède ou chaud.
  Méthode commune : 5 hooks différents notés, une idée par contenu, une hypothèse et un indicateur, aucun fait inventé.
  **À faire confirmer par le fondateur avant de les écrire :** « une alternative peut être proposée si un produit n'est pas disponible » et « la création de boutique est actuellement libre » (ces deux faits apparaissent dans la compétence copywriting).
  **Tutoiement ou vouvoiement :** les exemples du copywriting vouvoient, alors que les vidéos tutoient. Garder « tu » dans les voix TikTok/Reels ; le vouvoiement reste possible pour Facebook, LinkedIn, WhatsApp et les publicités, si le fondateur le valide.
- **Compétences ajoutées le 11 novembre**, dans `~/.claude/skills/`, à réinstaller depuis GitHub à chaque nouvelle session :
  - coreyhaines31/marketingskills : 53 compétences (social, ad-creative, copywriting, marketing-psychology, offers, referrals, aso, influencer-marketing, video…). Les anciennes versions courtes d'ad-creative, copywriting et marketing-psychology ont été remplacées.
  - ScrapeCreators/social-media-research-skills : 13 compétences (trend-discovery, outlier-post-finder, comment-mining…). **Elles exigent une clé API ScrapeCreators, payante.**
  - Compétences seules : bryllim/fun-sfx (71 bruitages libres), m4nueldeleon/shorts-virales-ia (en espagnol, du rush brut au short), UgurInanc12/stable-audio-3-prompt-writing.
  - iart-ai : `motion-skills` n'est qu'un index. Packs installés : tiktok, ecommerce, ad, explainer, map-animation et kinetic-typography (16 compétences). `launch-video` existait déjà et n'a pas été remplacée.
  - davidpc007/openclaw-marketing-skills **n'est pas installé** : c'est une copie plus ancienne de coreyhaines.
- **Nouvelles musiques (11 novembre)**, dans les uploads de la session et non dans le dépôt : Odeal « Blame U », H.E.R. « Damage », Ella Mai « Boo'd Up », Tems « Me & U », Central Cee « Obsessed With You », « LINKEDIN », Jorja Smith « The One » et « Blue Lights », SamRecks « BACK PACK » et « visa ».
- **Leçons des 6 vidéos de référence (11 novembre)** :
  1. 5 hooks qui marchent dans tous les domaines : « Vous faites encore ça ? », « Faut que je vous raconte un truc », « Regardez la différence », « L'erreur que tout le monde fait », « En 30 secondes je vous montre comment ».
  2. Remplacer « nous » par « vous » : parler du résultat du client ; l'expérience de la marque sert de preuve, pas de titre.
  3. Biladi Jewellery (Lubumbashi), **le modèle idéal pour PitUp** : une vraie cliente, un détail concret (le nom gravé), un geste chaleureux (petite bague offerte + carte de fidélité), et une fin en question (« Et toi, à qui tu l'offrirais ? »).
  4. Format série utile : « Le site que tu vas mettre en favoris, partie 1 » + appel à enregistrer la vidéo.
  5. Tuto express : annoncer la valeur, montrer les étapes en 20 s, puis demander de s'abonner.
  6. Vlog POV humoristique en anglais (camion, colis) : hook visuel absurde, puis le produit.
- **Voix de la jumelle (11 novembre)** : c'est la voix de la vidéo Biladi Jewellery. Elle appartient à la jumelle du fondateur, **qui a donné son accord**. Comme celle de la sœur, cette voix est privée : ne jamais la mettre dans le dépôt.
  - Préparation de la référence : demucs (`htdemucs`, mode 2 pistes) pour retirer la musique, puis les 12,3 premières secondes. Fichier : `scratchpad/audio/jumelle/ref.wav`.
  - Clonage : VoxCPM2. Ressemblance mesurée avec resemblyzer : 0,81 à 0,89. Pour comparaison, la sœur et la jumelle ont 0,70 de ressemblance entre elles.
  - Voix « mixte » :
    - ce qui marche : une référence qui enchaîne les deux voix (`mixref.wav` = 10 s + 10 s, `mixref_c.wav` = 13 s de la sœur + 6,5 s de la jumelle). Le résultat varie d'une prise à l'autre, il faut donc trier chaque prise avec resemblyzer et whisper ;
    - ce qui ne marche pas : déplacer la hauteur et le timbre de la voix actuelle (parselmouth « Change gender »). La voix ne bouge presque pas. De plus, la jumelle paraît plus sombre qu'en réalité à cause de la séparation de la musique : ne pas se fier à sa mesure de timbre.
  - Écoute comparée envoyée : `livrables/voix/`. **En attente du choix du fondateur.**
- **Choix du fondateur (11 novembre) : voix n° 4**, le mélange proche de la voix actuelle. Référence : `scratchpad/audio/jumelle/mixref_c.wav` (13 s de la sœur + 6,5 s de la jumelle), style S. Garder les prises qui mesurent environ 0,80 de ressemblance avec la voix actuelle et 0,69 avec la jumelle (resemblyzer), et dont le texte est bien compris par whisper.
- **Voix masculine (11 novembre)** : deux messages WhatsApp du 27 septembre où un homme lit un script PitUp au vouvoiement (« Vous êtes à Lubumbashi et vous cherchez un produit… »). Hauteur médiane d'environ 100 Hz.
  - Préparation de la référence : demucs, puis 0,6 à 13,6 s du message WA0031, avec un léger débruitage. Fichier : `scratchpad/audio/wa/ref.wav`.
  - Clonage : VoxCPM2, style « voix masculine posée et chaleureuse, avec le sourire ». Ressemblance de 0,88 à 0,95 (ses deux messages entre eux : 0,79).
  - Piège : il dit parfois « téléchange » au lieu de « télécharge » ; toujours vérifier avec whisper.
  - Voix privée : ne jamais la mettre dans le dépôt. **Identité et accord de la personne à confirmer avant toute publication.**
- **Voix validées (11 novembre)** : le fondateur valide **les 4 voix produites** : mixte centrée, mixte proche de la voix actuelle (n° 4), mixte proche de la jumelle, et jumelle. La voix actuelle (la sœur) reste disponible. Les faire tourner d'une vidéo à l'autre.
- **Série de 4 vidéos « visibilité » (11 novembre)**, objectif likes, partages et commentaires, car les commandes commencent à arriver :
  - **Duels** « Tu ne peux en garder qu'un » : voix de la jumelle, musique Central Cee à partir de 30 s.
  - **Devine ce que c'est** (zoom extrême puis révélation) : voix actuelle, musique Ella Mai à partir de 169 s.
  - **5 idées cadeaux pour ton gars** : voix mixte centrée, musique Tems à partir de 83 s.
  - **3 boutiques à suivre** (MB Ephphatha, Vb business, Tout est grâce) : voix n° 4, musique SamRecks à partir de 122 s.
  - Nouveaux types de plans dans `build_story.py` : `vs`, `shop`, `zoom`.
  - Captures téléphone neuves : `tools/make_pp2.py` repère et efface le prix bleu automatiquement, même quand il est à moitié caché.
  - Choix des prises : `tools/pick_takes.py`. **Le lancer avec `python -I`**, sinon `tools/av.py` masque la bibliothèque `av` de whisper.
  - Kit de publication : `pitup/kit-publication-4-videos.md`. Livrables : `livrables/PitUp-{duels,devine,cadeaux,boutiques}-v1.mp4`.
  - Ne pas montrer de copies de marques de luxe (une montre type Rolex a été écartée au profit d'une Casio).
- **Carrousel 4:5 (11 novembre)**, fait à la demande du fondateur, dans le style de la référence fibetech mais dans la DA PitUp (bleu #1f88c9, Poppins, fond clair, illustrations plates maison) : couverture + 6 slides, au vouvoiement. Fichiers : `pitup/carousel/index.html`, rendu avec `shot.js` (Playwright, 1080 × 1350).
- **Disque plein (11 novembre)** : le quota d'espace de la session était atteint, ce qui faisait planter Chromium (« Target crashed »). Il faut supprimer `/root/.cache/hyperframes/history`, `/tmp/hyperframes-extract-cache-0`, les fichiers MASTER et les anciennes versions. Vérifier `df -h /` avant chaque gros rendu.
- **Piège** : `pkill -f "<texte>"` tue aussi la commande shell qui contient ce texte. Viser le processus avec un motif plus précis.
- **Fluidité des voix (11 novembre)**. Le fondateur trouve les voix lentes, chuchotées et peu naturelles. Causes trouvées :
  1. le style « voix douce et posée » demandait littéralement une voix lente et feutrée ;
  2. l'enregistrement de référence de la sœur est lui-même lent et posé (son texte dit « quand tu ralentis et que tu poses ta voix ») ;
  3. chaque phrase était générée séparément, donc l'intonation repartait de zéro à chaque phrase.
  **Nouvelle méthode** (`tools/vox_cont.py`) :
  - mode « continuation » de VoxCPM2 : `prompt_wav_path` + `prompt_text` (transcription exacte de la référence, `audio/*/ref.txt`, ou `ref_cont.wav` coupé en fin de phrase pour la sœur) ;
  - **tout le script d'un seul souffle**, 20 étapes au lieu de 10 ;
  - **aucune consigne de style**, car dans ce mode elle est lue à voix haute ;
  - pas de points de suspension, des virgules à la place.
  Résultat : débit de 6,6 à 7,5 syllabes par seconde au lieu de 5,3 (français naturel), sur un texte qui dure 12 s au lieu de 16 s. Piège : certaines prises basculent vers une voix grave d'environ 100 Hz ; il faut les écarter en mesurant la hauteur.
  Test d'écoute envoyé : `livrables/voix-test/` (1 = ancienne méthode, 2 = jumelle, 3 = voix actuelle). **En attente de l'avis du fondateur.**
  Pour aller plus loin : un nouvel enregistrement de 1 à 2 minutes, lu avec énergie (style créatrice TikTok), au calme, pour chaque voix.
- **Catalogue (11 novembre)** : 632 produits, avec le catalogue complet dans `prod/api_products_live.json`. Ne plus réutiliser les 16 mêmes détourages. Articles tendance pour les jeunes, encore jamais montrés : maillots (Congo, PSG, Barça), Jordan 4 et 11, Air Force (Kobe, Foamposite), New Balance, crocs, pantalon baggy, casquettes Ralph Lauren et Lacoste, parfum Asad, The North Face.
- **Carrousel v2 (11 novembre)** :
  - vrais écrans de l'appli dans des téléphones (marketplace, boutique, Jordan 4, maillot Congo) et vraie carte OSM avec le trajet ;
  - **pas de compteur de slides**, car les réseaux en affichent déjà un ;
  - rendu en 2160 × 2700 (double résolution) ;
  - ne pas montrer l'écran d'accueil de l'appli : il affiche la publication d'une autre personne avec un tarif.
- Voix des vidéos de motion design : `tools/motion_mix.py` place les phrases à des instants fixes, avec la musique à 20 % sous la voix. Les phrases sont mo_0 à mo_3 et moc_0/moc_2 (moc_1 est rejetée : on entend « Bah on est sur PitUp »). Les fichiers finaux sont `livrables/PitUp-Motion-*-voix.mp4`.
- **Piège** : ne jamais mettre en attente avec `pgrep -f "hyperframes ... render"` quand la ligne de commande d'une autre file contient la même chaîne (blocage). Enchaîner les rendus dans un seul script.

## Série « classe » (11 novembre, soir) : leçons du fondateur

- **Vidéo « Ah, Lubumbashi » (v4 validée en attente d'avis)** : ouverture = **vue d'en haut de Lubumbashi au coucher de soleil** (pas de carte, ni RDC, ni Afrique, ni plan OSM). Le fondateur aime l'ambiance coucher de soleil (783bff05, 2bd06155) : la garder. On ne fait pas une présentation de la ville : 3 ou 4 plans courts, nets, puis l'appli.
- **Badges TikTok** : la reconstruction (LaMa, ou pixels des images voisines via `tools/tiktok_fill.py`) laisse du flou ou des fantômes sur les voitures. Méthode retenue : `tools/crop_clean.py` = léger zoom (×1,2–1,25) ancré à l'opposé du badge, seule une fine bande au bord est comblée. Plans propres aussi dans le film Haut-Katanga (6629895a) en bandes 1080×640 (`crop=777:460:8:58`), vérifiées image par image.
- **Plans L0–L39 (vidéo DJEUDY)** : contiennent des **petits cercles résiduels** de l'ancien filigrane (L24, L14, L8…). Ne plus les utiliser.
- **Netteté** : mesurer chaque plan (variance du laplacien). `tools/sharp_trim.py` garde la partie nette (enlève les fondus) ; `tools/fit_clips.py` ralentit un plan trop court (répétition d'images, jamais de fondu d'images, qui floute).
- **Ne jamais réutiliser un plan d'une vidéo à l'autre dans une même série.**
- **Voix de la jumelle** : timbre fidèle seulement avec ses **vrais enregistrements récents** (Biladi, voix isolée avec Demucs) : `audio/jumelle/ref_b.wav` + `ref_b.txt` (amorce de continuation) et `ref_mid.wav` (22 s, timbre), via `tools/vox_cont2.py`, 20 étapes. Similarité 0,93, hauteur 227 Hz comme elle. Une référence de 55 s est trop lourde pour le processeur. Le mode « clone + consigne de style » descend parfois à 190 Hz (« voix grave »).
- **Voix de la sœur (Samedi)** : le fondateur préfère la **méthode de la première version** (continuation sur `ref_cont.wav`, `motion/vox13b.py`). Écarter les prises qui tombent vers 100 Hz (2 sur 5) et vérifier l'accroche mot à mot.
- **Rythme** : `tools/rhythm.py` (plan par phrase : débit cible, pause après) ; ne coupe que dans une vraie pause (≥ 50 ms), sinon garde les phrases liées ; ralentissement limité à ×0,84–0,86 pour ne pas abîmer le timbre. « Ah » de l'accroche : l'allonger et ajouter un souffle avant « Lubumbashi ».
- **Textes** : phrases complètes avec verbes. **Fin d'appel à l'action** : pas toujours « Télécharge l'appli » ; annoncer la disponibilité et inviter à **passer sa première commande**. Ne jamais commencer une phrase par « PitUp ».
- **Descriptions** : à fournir avec chaque vidéo, prêtes à copier, **sans répéter l'accroche** (`livrables/descriptions-a-copier.md`).

## Corrections du 11 novembre (soir) — à appliquer partout

- **Voix** : jamais d'étirement temporel (Rubber Band) : le fondateur l'entend comme un **grésillement**. Rythme = pauses seulement (`tools/rhythm.py` avec KMIN 1.0). Filtre doux validé (« version C ») : `highpass=f=80,lowpass=f=8500,afftdn=nr=10:nf=-45,equalizer=f=3500:t=q:w=1.5:g=-2`.
- **Débit** : pour ralentir sans artefact, amorcer la continuation avec le passage le plus posé de la personne (`audio/jumelle/ref_calm.wav` + `ref_calm.txt`, passage « certificat ») ; ~6,8 syl/s au lieu de 8,5.
- **Deux voix seulement** : la jumelle et la sœur. **Jamais de voix mixée.** Samedi = sœur (méthode continuation de la 1re version) ; Lubumbashi = jumelle.
- **« Ah » d'accroche** = soupir de fatigue (pas une préposition) : un seul « Aaah » descendant (235 → 180 Hz), allongé par PSOLA (Praat overlap-add), puis un souffle avant « Lubumbashi ».
- **Mots** : ne pas écrire « disponible dès maintenant » (l'appli existe depuis longtemps). Préférer « ta prochaine pièce t'attend déjà sur l'appli PitUp ».
- **Accroches** : introduire naturellement (« Et si… ») ; la phrase d'accroche entière doit être visible sur la **première image** (couverture TikTok).
- **Tenues cohérentes** : couleurs qui vont ensemble (costume vert + chemise blanche + mocassins noir/vert + montre). Pas de bleu avec des chaussures vertes. Produits de jeunes : tendance européenne/américaine, couleurs sobres (uni, bicolore). Crocs oui ; pas de babouches ; sweat déjà trop vu. Pas de copies de marques de luxe (Rolex, Van Cleef, motif LV). Pas de fumeur (photo Y-3 écartée).
- **Détourage** : `rembg` (modèle isnet-general-use) + ne garder que l'objet principal ; fond `#F1EFEC` avec ombre douce.
- **Téléphone 3D** : swipe de pages produit tendance (`story/v/ph_trend.mp4` : maillot Congo, Jordan 4, Samba, Shox) ; effacer la ligne « 0.0 (0 avis) • 0 vendus ».
- **Badges TikTok** : `tools/crop_clean.py` en zoom automatique (argument 0) : le badge sort entièrement du cadre, **aucune zone reconstruite** (le fondateur voit le flou des zones refaites).
- **Musique** : plus présente sous la voix (≈ −13 dB) et qui **monte nettement** quand la voix s'arrête (`mix_duck.py` : LO 0.10, HI 0.72). Rythmée (R&B, rap) et jamais déjà utilisée : Raindance (Lubumbashi), Kairo Keyz « float 2.0 » (Samedi).
- **Budget** : le fondateur a consommé beaucoup de sa limite hebdomadaire. Avancer vidéo par vidéo, valider par un court extrait avant tout rendu complet.

### Motion design : leçons du 11 novembre (soir)
- **Rejeté** (« bas de gamme, IA ») : la vidéo md1. Elle avait une chemise peu flatteuse, des bruitages « pop » de dessin animé, une carte colorée et trop d'illustration.
- **Bonne direction** : la typographie pure, comme la référence « marq ».
  - Un mot par temps de la musique, en coupe sèche, avec des fonds crème et marine en alternance et un seul accent or.
  - Les coupes accélèrent. Le dernier mot s'écrit lettre par lettre pendant le break, et le logo arrive sur le drop.
- **Sons** : jamais de pop. Chaque coupe a un son grave et sourd (« thock », vers 80 Hz), avec une montée de bruit avant le drop et un impact grave sur le logo.
- **Produits** : n'en montrer un que s'il est vraiment beau. Sinon, rien que des mots.
- Projet : `scratchpad/hf/videos/pitup-md2`, généré par `scratchpad/motion/md2/build.py`. Musique : JBEE « 4AM » à partir de 14 s (drop à 27,55 s). Police : Outfit. Mixage final à −14 LUFS.
- **Retours sur la v2 (soir du 11 novembre)** :
  - pas de musique avec paroles : prendre l'instrumental d'une référence. Pour cela, séparer la voix avec demucs (`htdemucs --two-stems=vocals`, voix à −60 dB et moins).
  - de vrais bruits de clavier pour le texte tapé (Mixkit 1387, un clavier mécanique au son chaud).
  - respecter la DA PitUp : bleu #1f88c9, fond clair, Poppins, texte marine #0d1b2a et mot d'accent en bleu.
- **v3** (`scratchpad/motion/md2/build3.py`, `hf/videos/pitup-md3`) :
  - musique de la référence n° 3 (cf82, 107,7 BPM, temps de 0,5585 s), montée [7,26 ; 14,06] + [17,95 ; fin] ;
  - « simplement. » tapé pendant le silence, puis le logo sur l'impact (29,45 s).
- **Logo signature** : la flèche (la forme vide du P) monte du bas le long de sa tige, entre dans le P, dépasse un peu, puis se cale avec un léger rebond. Le mot « PitUp », le slogan et pi-tup.com arrivent ensuite.
  - Le découpage se fait avec `motion/md2/logo_split.py` : un P plein, la flèche, et des masques « dedans » et « dehors » sur un canevas de 1500 × 1900.
  - Le fondateur va envoyer la documentation sur les 4 déclinaisons du logo.
- **Logo signature, version affinée** (12 novembre) :
  - La flèche creuse un vrai trou transparent dans le P : le P porte un masque CSS (`-webkit-mask-composite: xor`) qui se déplace avec la flèche blanche.
  - Ne jamais faire une copie bleue de la flèche. Sur un fond en dégradé, cette copie laisse des traces visibles.
  - La queue de la flèche est prolongée dans la tige, à l'intérieur du P seulement, pour que le rebond (`back.out(1.35)`, 0,85 s) ne laisse aucun liseré.
  - Badges officiels sous pi-tup.com : App Store (SVG de Wikimedia, en anglais) et Google Play (PNG officiel, en anglais), 100 px de haut. tools.applemarketingtools.com n'est pas joignable depuis la session.
- **Attention aux fins de vidéos téléchargées** : une vidéo téléchargée depuis TikTok ou Instagram se termine par le jingle et l'animation du logo de la plateforme. La référence n° 3 (cf82) a le jingle Instagram à partir de 26,7 s (silence, puis « boum » à 29,45 s). Ne jamais utiliser cette partie. Toujours regarder les dernières secondes d'une référence avant d'en prendre la musique.
- **v4** (`motion/md2/build4.py`, `hf/videos/pitup-md4`, 15 s) :
  - musique réelle seulement, de 7,26 s à 22,4 s ;
  - « simplement. » est tapé pendant le vrai break (16,40–17,95 s), sous « le commerce, » en bleu ;
  - le logo arrive sur le retour du beat (18,0 s) ;
  - « fièrement / congolais. » : le fondateur veut cette fierté congolaise dans la vidéo.
- **Texte tapé au clavier** (12 novembre) :
  - Écrire « Le commerce » avec une majuscule et sans virgule, avec « simplement. » en dessous.
  - Le texte tapé est un seul écran. Chaque lettre garde sa place finale, apparaît à sa frappe (0,11 s, légère montée et léger zoom), et le curseur suit la dernière lettre.
  - Ne plus enchaîner un écran par lettre : cela saute à l'œil.
  - Une phrase longue passe sur deux lignes (`|` dans le texte) au lieu de rétrécir la police.
- **Motion design n° 2 « Bonjour. »** (12 novembre, `motion/md2/build5.py`, `hf/videos/pitup-md5`, 18,5 s) :
  - inspiré de la référence « Luca Radez » (9db8) ; musique = son instrumental, de 10,12 s à la fin naturelle (28,6 s), le logo sur le coup à 25,48 s. Le jingle de plateforme à 30,5 s est exclu.
  - 4 scènes numérotées en police mono (IBM Plex Mono) : « Bonjour. » sur marine avec des lignes de construction ; « On est / PitUp. » tapé, avec le point bleu qui saute et « LE COMMERCE, SIMPLEMENT. » ; sur bleu, « Acheter à Lushi, devient un jeu d'enfant. » avec des icônes qui changent ; une roue « Tu trouves ● Sneakers… +100 boutiques. » qui avance d'un cran par temps ; puis le logo signature et les badges.
- **« Bonjour. » v2** (`motion/md2/build6.py`, `hf/videos/pitup-md6`, 20,6 s) :
  - l'ouverture est un carrousel de salutations : « Bonjour » (français), « Jambo » (swahili), « Mbote » (lingala), avec la langue en petit, en police mono ;
  - un swipe horizontal (`power4.inOut`, 0,5 s) avec un souffle à chaque changement, et le curseur qui clignote après chaque mot ;
  - le point bleu arrive seulement à la fin, après « Mbote » ;
  - la musique commence à 7,99 s pour laisser 4,3 s à l'ouverture.
- **Police de la marque : Lexend.** Le logo « PitUp » et le slogan sont en Lexend (comparaison faite le 12 novembre : forme du « t », du « P » et du « U »). Les textes des vidéos utilisent Lexend (police variable 300–700, `assets/fonts/lexend.woff2`), et non plus Poppins. Les petits textes des coins et les sous-titres aussi : **pas de police mono** (le fondateur la trouve « robotique »).
- **Ouverture des salutations, version validée** (`build7.py`, `hf/videos/pitup-md7`) : un swipe **vertical** (`power4.inOut`, 0,55 s), dans l'ordre Mbote (lingala), Jambo (swahili), puis Bonjour (français), suivi du point bleu.
- **Son du swipe** : le souffle synthétique est refusé. On utilise le son grave et sourd des coupes, à l'arrivée de chaque mot.
- **Registre de la marque** : écrire « Nous sommes PitUp », jamais « On est PitUp ». Quand la marque parle d'elle-même, elle dit « nous ». La vidéo « Mbote » finale est `livrables/PitUp-Motion-Mbote-final.mp4`.
- **Chiffre clé** : écrire « +100 boutiques **locales** » (ou « plus de 100 boutiques locales »), jamais « +100 boutiques » seul.
- Salutations Mbote / Jambo / Bonjour : **ne pas écrire le nom de la langue** en dessous.
- Vidéo finale : `livrables/PitUp-Motion-Mbote-final-v2.mp4`.
- **Musiques sans paroles** : les instrumentaux des références sont épuisés (cf82 et 9db8 sont déjà utilisés ; marq et e352 font moins de 10 s ; DataSave n'a que la voix ; Kreatively a une musique faible avec la fin Instagram). Les chansons du fondateur n'ont aucun passage instrumental de plus de 6 s (vérifié avec demucs). Source retenue : Mixkit, gratuit et sans paroles (`assets.mixkit.co/music/<id>/<id>.mp3`). « Sweet September » (282, R&B, 152 BPM, drop à 12,655 s) est utilisé pour le n° 3. Candidats suivants : « Torey » (304), « Find Me Outside » (258), « Complicated » (281), « RnB » (224).
- **Motion design n° 3 « Commande »** (`motion/md2/build8.py`, `hf/videos/pitup-md8`, 22,6 s), style Kreatively :
  - la question lumineuse « Tu cherches encore une boutique sérieuse ? » ;
  - une barre de recherche en verre, tapée puis effacée ;
  - « Plus besoin de chercher. » ;
  - des cartes en éventail sous « +100 boutiques locales. » ;
  - le bouton « + » qui devient « Commander », un tap, puis « Commande envoyée ✓ » ;
  - la checklist de suivi, puis « Livrée. Payée à la livraison. » ;
  - le logo signature.
- **Motion design n° 4 « Identité »** (`motion/md2/build9.py`, `hf/videos/pitup-md9`, 14,6 s), style de la référence Moverunion (e352) : une coupe par temps (136 BPM, 0,441 s). Musique = l'instrumental de la référence, phrase de 12 temps jouée deux fois, avec son silence et son coup final sur le logo (pas de jingle). 19 plans :
  - construction du logo, déclinaisons en carrés, affiches « COMMERCE & LIVRAISON » et « LE COMMERCE, SIMPLEMENT. », tampons « PitUp » ;
  - carton en 3D CSS avec scotch « PitUp », sac blanc et tote marine, drapeau, panneau, profil PitUp dans un téléphone ;
  - grands mots « Livré. », « Local. », « Fiable. » ;
  - 3 plans de vraie rue de Lubumbashi (`real/lushi_clean.mp4`) avec le logo blanc ;
  - puis le logo signature.
  - Ne pas inventer de chiffre (« 24/7 » a été retiré du profil).
- **Vrais visuels de marque fournis par le fondateur** (12 novembre, dans les uploads de la session) :
  - une photo de profil : rond blanc, P bleu, « Pitup » bleu dessous ;
  - un mockup de tote bag noir avec le grand P bleu et le lockup « Pitup » ;
  - une icône d'app : carré arrondi noir, P bleu, « Pitup » blanc en Poppins Bold.
  - La DA comporte donc aussi du **noir et du bleu**.
  - Le mot-symbole s'écrit **« Pitup »** (u minuscule) sur ces visuels, alors que `logo_word_white.png` montre « PitUp ». **À faire confirmer.**
- **Identité v2** : le tote réel est utilisé en deux cadrages verticaux, le sac entier et un gros plan sur le P. La photo est posée sur un dégradé sombre, avec des fondus de 220 px. Les supports qu'on possède en vrai valent mieux que les objets dessinés en CSS.
- **Identité, option A** (choix du fondateur, 12 novembre ; `livrables/PitUp-Motion-Identite-A.mp4`, 9,5 s). On reprend les images de la référence Moverunion (e352), en 34 plans de 5 images à 30 i/s.
  - Chaîne de traitement :
    1. `motion/md2/mov_clean.py` efface la surcouche Instagram et le pseudo « @OBRAZUR / Solomun • Can't Stop » (LaMa, zone fixe x 492–680, y 292–445 en 720 × 1280), puis passe le rouge (teinte < 14 ou > 168, saturation > 140, luminosité > 90) en bleu PitUp.
    2. `mov_marks.py` + `mov_apply.py` repèrent leur logo par corrélation de gabarit, sur un masque blanc, noir ou bleu. Ils effacent **tout le rectangle** (marge 10 px, ou 24 px pour les logos noirs et bleus), puis posent l'icône PitUp dans la même couleur. Ils effacent aussi les petits textes « moverunion ».
    3. `mov_fix.py` refait l'avatar en rond bleu uni et passe en bleu la peinture rouge sombre.
  - Plans remplacés : le camion et le drapeau par la rue de Lubumbashi (sans moto), la sangle par le vrai tote, les tampons et les déclinaisons recréés en CSS.
  - Textes réécrits en surcouche HTML : « pitup » vertical, « COMMERCE & LIVRAISON », le profil, « Livré. ».
  - Composition : `build10.py`. La musique de la référence est **Solomun « Can't Stop »** (info du filigrane).
- **Lubumbashi v11, retours du 12 novembre** :
  - **Voix trop rapide, pauses non respectées** : après un point, la voix ne s'arrêtait que 0,14 à 0,18 s. `tools/punct_pause.py` insère du silence (jamais d'étirement) au point le plus silencieux entre deux mots. Cibles : environ 0,75 s après un point et 0,38 s après une virgule. Quand whisper place mal les mots, on peut forcer l'instant de coupe. Résultat `audio/v8/v13_cielP.wav` (21,2 s devenues 27,8 s), et la table de décalage est dans `.map.json`.
  - **Musique imperceptible** : `tools/mix_bed.py` place la musique environ 9 dB sous la voix (contre environ 24 dB avant). Sous la voix, il creuse seulement sa bande 300 Hz–3 kHz, puis la musique remonte en entier à la fin. Mixage final à −14 LUFS.
  - **Plans flous** : les couchers de soleil sont des téléchargements TikTok en 576 px. Il faut des sources nettes : les fichiers d'origine, ou un agrandissement par IA (payant, accord requis).
- **Pauses de ponctuation, méthode corrigée** (le fondateur a entendu des silences au milieu de mots) : `tools/punct_pause2.py` (lancer avec `/home/user/fw/bin/python`).
  - Les candidats sont les creux d'énergie à moins de 0,32 s de la frontière donnée par whisper.
  - Une coupe n'est gardée que si whisper, réécoutant 1,3 s de chaque côté, entend le bon dernier mot à gauche et le bon premier mot à droite.
  - Les cas douteux sont vérifiés avec une fenêtre de 2 s, puis forcés (5e valeur). Attention : `initial_prompt` fausse la réécoute.
  - Coupes validées pour `v13_cielP2.wav` : 2,15 / 3,92 / 5,13 / 5,60 / 6,39 / 7,46 / 7,72 / 9,35 / 10,36 / 12,04 / 13,06 / 13,97 / 15,91 / 17,33 / 18,79 / 19,88.
- **Lubumbashi v11 livrée** (`livrables/PitUp-Ah-Lubumbashi-v11.mp4`, 31 s ; `cfg/v14_ciel.json`, projet `hf/videos/pitup-v14-ciel`) :
  - Netteté : agrandissement IA **local et gratuit** avec Real-ESRGAN general-x4v3 (ONNX, `/root/.cache/esrgan/g4.onnx`, téléchargé de HF `Heliosoph/realesrgan-onnx`). Script `tools/esrgan_clip.py` : réduire en 540 × 960, agrandir ×4, puis repasser en 1080 × 1920. Compter environ 4 s par image sur ce processeur. Higgsfield n'a que 1,5 crédit (forfait gratuit), donc pas d'agrandissement payant possible.
  - Plans : couchers de soleil agrandis (accroche et « Notre ville bouge »), puis un montage de jour net tiré du film de DJEUDY (`story/v/day_lushi.mp4` : vue d'en haut à 21,2 s, passage piéton à 22,73 s, marcheurs à 24,47 s). Le panneau politique « Un peuple, un destin » (vers 1 s) est écarté.
  - Starts des scènes : on prend le premier mot de chaque phrase, décalé par la table des pauses, moins 0,12 s.
  - Carte de fin : « +100 boutiques locales à Lubumbashi ».
- **Disque** : la session plafonne vers 39 Go utilisés. Avant un rendu, garder au moins 2 Go libres. On peut supprimer les séparations demucs, les images intermédiaires et les copies `assets/v` des anciens projets.
- **Lubumbashi v12** (`livrables/PitUp-Ah-Lubumbashi-v12.mp4`) :
  - **Premier plan** : vue aérienne de jour (`story/v/air_lushi.mp4`) tirée du film de DJEUDY : le rond-point (0,02–0,78 s), le lac et les bâtiments (10,34–10,80 s), l'avenue vue d'en haut (17,88–18,16 s). Ralenti ×2 par interpolation (`minterpolate mci`), puis Real-ESRGAN. Éviter 0,8–1,5 s (boulevard avec panneau politique).
  - **Articles des cartes** : toujours **détourés**, seuls, sur fond `#F1EFEC` avec ombre douce (`story/img/c_d_*.jpg`) : Crocs camo, parfum Yara (Lattafa), Adidas Campus vertes, montre au cadran blanc. La veste en cuir et la main au bracelet sont retirées (le fondateur les jugeait peu lisibles).
  - rembg : la commande en ligne est cassée, il faut passer par l'API Python système (`from rembg import remove, new_session`).
- **Lubumbashi v13** (`livrables/PitUp-Ah-Lubumbashi-v13.mp4`) : les cartes montrent Crocs, Parfum (Yara), Nike Air Max 95 et Montre (Rolex Day-Date cadran bleu glacier). Ces deux nouvelles photos ont été fournies et choisies par le fondateur, qui lève ici la règle « pas de Rolex ». Le texte dit seulement « Montre », sans nom de marque.
  - **Détourage d'un objet tenu en main** : rembg échoue, car la main est prise avec l'objet ou l'objet est rogné. On passe à un **masque géométrique** mesuré sur la photo : cercle du boîtier, trapèzes pour le bracelet avec fondu aux bouts, rectangle pour la couronne.
  - Ombres de sol des chaussures : seuil alpha 235, puis on coupe à la main la traînée d'ombre.
- **Lubumbashi v14** (`livrables/PitUp-Ah-Lubumbashi-v14.mp4`) : **plus aucun coucher de soleil** (flous même agrandis) et **plus de rond-point** (déjà trop vu).
  - Séquences de jour tirées du film de DJEUDY, agrandies par Real-ESRGAN, construites avec `tools/seq_clip.py` (segments avec ralenti) :
    - `open_hotel` : l'hôtel Pullman et le lac (10,34–10,80 s), la ville vue d'en haut (21,20–22,20 s), le boulevard vitré (25,30–25,70 s) ;
    - `city_bouge` : agent, taxis, marcheurs, ouvriers, rue commerçante « DIGITAL », minibus ;
    - `city_piece` : jeune femme, deux hommes près d'un camion, hommes sur un camion, arrêt de bus.
  - Plans à écarter dans ce film :
    - 6,10–6,67 s : tache ronde de l'ancien filigrane ;
    - 13,90–14,97 s : tricycles à moteur ;
    - 18,17–18,57 s : motos ;
    - 9,83–10,30 s et 22,70–23,23 s : affiches avec des visages, peut-être politiques ;
    - 17,87–18,16 s : moto au milieu de l'avenue.
  - **Détourage de chaussures sombres sur fond sombre** : utiliser le modèle rembg `birefnet-general-lite` (bien meilleur qu'isnet), puis reboucher les trous fermés (remplissage depuis le bord). Le fondateur avait jugé le détourage isnet des Air Max 95 « très mal fait ».
- **Reproche du fondateur (12 novembre)** : je reprenais toujours les mêmes plans (film de DJEUDY, déjà vu dans les vidéos publiées, dont celle à 10 000 vues), au lieu d'exploiter toute la bibliothèque. **Règle** : avant de monter, inventorier toutes les vidéos fournies et choisir des plans neufs. Les vidéos 1049431f et b7f9ecd7 sont aussi de DJEUDY.
- **Film « Haut-Katanga » (6629895a, 1024 × 576, 184 s)** : une mine de plans neufs, à recadrer en 9:16 au centre (les badges TikTok restent hors cadre).
  - Coupes : stade vu du ciel 0–3,03 s ; cathédrale vue du ciel 27,87–32,13 ; monument 32,13–35,43 ; ville vue du ciel 39,43–42,07 ; avenue vue du ciel 42,07–44,10 ; taxi jaune 52,90–55,10 ; gare 81–83,6 (reflet orange au début) ; train 83,6–86 ; centre commercial vu du ciel 119,27–122,6 ; rue Vodacom 138,1–142,07 ; boutique de vêtements 143,2–151,8 ; supermarché 168,7–176,8.
  - Les plans en voiture (104–119 s) montrent le tableau de bord.
- Lubumbashi v15 : ouverture hôtel (DJEUDY) puis stade, puis ville vue du ciel ; « bouge » = cathédrale, taxi, gare, centre commercial, Vodacom ; « bonne pièce » = boutique de vêtements et supermarché. Outil `tools/seq_clip2.py` (plusieurs sources, recadrage 9:16).
- **Agrandissement IA refusé** (12 novembre) : Real-ESRGAN lisse tout. Sur un recadrage vertical de 324 px agrandi plus de 3 fois, le fondateur a vu des plans flous, « les choses ne sont plus visibles ».
  - **Règle** : pas d'agrandissement IA. Les plans en paysage restent en paysage, presque à leur taille d'origine, empilés par 3 dans l'écran vertical (bandes de 1080 × 640, beat `split`).
  - Film Haut-Katanga : recadrage `crop=777:460:120:62`, qui évite les deux filigranes (« TikTok @adishiyetu » en haut à gauche puis en bas à droite, « Jeremiebe.rdc » en haut à droite), puis lanczos et `unsharp=5:5:0.35`.
- `build_story.py` accepte maintenant un poids `w` par beat, pour qu'un beat dure plus longtemps que ses voisins.
- **Lubumbashi v16** (`livrables/PitUp-Ah-Lubumbashi-v16.mp4`) :
  - l'hôtel en plein écran, puis [stade | ville vue du ciel | monument] ;
  - [cathédrale | gare | centre commercial] puis [taxi | Vodacom | train] ;
  - [boutique de vêtements ×2 | supermarché] puis [supermarché ×3].
- **Règles du 12 novembre (après v16)** :
  - **Un plan ne sert qu'une fois** dans une vidéo. Pas deux plans de la même gare.
  - **Étalonnage uniforme** (dépôts fournis par le fondateur : color-grade-ai, VideoColorMatch, agentic-color-grader, huemancer). Méthode `tools/grade.py` :
    1. Mesurer chaque plan sur 8 images.
    2. Corriger la balance des blancs « shades of gray » p = 6 à 70 %, les niveaux (percentiles 1,5 % et 99,2 %) et le gamma, pour une médiane de 0,45.
    3. Appliquer une même signature à tous : courbe en S douce, saturation ×1,10, chaleur légère (R ×1,025, B ×0,965).
    4. Une LUT 33³ par plan, appliquée avec ffmpeg `lut3d`, sans scintillement.
  - **Cohérence texte–image (copywriting)** : ce qu'on montre doit illustrer ce que la voix dit. « Trouver la bonne pièce » = vêtements en boutique, jamais un supermarché ni de la nourriture.
- **Lubumbashi v17** (`livrables/PitUp-Ah-Lubumbashi-v17.mp4`) :
  - la gare n'apparaît qu'une fois ; le 2e plan de gare est remplacé par la tour de verre bleue et l'immeuble à piscine (Haut-Katanga, 87,45–89,45 s) ;
  - « bonne pièce » = séquence boutique de vêtements (142,0–151,75 s, ralentie ×1,13), coupée en 3 bandes simultanées.
- **Lubumbashi v18** (`livrables/PitUp-Ah-Lubumbashi-v18.mp4`) :
  - **Nouvelle phrase** : « Seulement, entre les embouteillages et les allers-retours, trouver la bonne pièce prend souvent du temps. » Le contexte local est réel, chacun s'y reconnaît. Seule cette phrase a été régénérée (jumelle, `vox_cont2`, ref_calm + ref_mid ; la prise n° 2 est à 229 Hz, contre 224 Hz pour l'ancienne phrase). Elle a été filtrée (filtre C), mise au même volume et insérée dans `v13_ciel.wav`, ce qui donne `audio/v8/v14_ciel.wav`, puis `v14_cielP.wav` avec les pauses.
  - **Pauses sans coupure brutale** (« calages ») : `punct_pause2.py` fait un fondu de sortie de 45 ms et un fondu d'entrée de 30 ms (en cosinus), et remplit la pause avec le **bruit de fond** de la prise, jamais un silence numérique.
  - **Mixage** : la voix est 11 dB au-dessus de la musique (`mix_bed.py`, 8e argument), pour mieux comprendre le début.
  - **Plans** : la cathédrale n'apparaît plus qu'une fois. La ville vue du ciel avec le lac (42,15 s) remplace le doublon. Les embouteillages sont illustrés en 2 bandes : l'avenue encombrée vue du ciel (44,15 s) et la ville avec le terril (92 s).
  - **Cartes produits** : chaque carte porte la pastille de catégorie de l'appli (« Vêtements & mode », ou « Beauté » pour le parfum) et l'étiquette « Tendance » (`chip` et `tag` dans `build_story`).
  - **Téléphone** : pas d'enregistrement qui glisse. On affiche des pages produits **fixes**, qui s'enchaînent par coupes nettes (`story/v/ph_static.mp4`).

## Voix off : pauses sans coupe audible (v21 Lubumbashi)
- Ne jamais remplir une pause avec un souffle synthétique ni laisser un silence numérique : le fond change et l'oreille entend la coupe.
- Outil `tools/punct_pause3.py` : fondu cos long vers le silence à chaque coupe vérifiée, puis UN fond de pièce constant (bruit rose -60 dBFS) sous toute la voix.
- Éviter l'accumulation de « et » : un seul « et », le reste lié par des virgules. « et on » se prononce d'un souffle : régénérer la phrase plutôt que couper.
- Textes à l'écran : « Paiement à la livraison. » (pas « Payé »).
- Avant chaque livraison : earshot (`/home/user/leonxlnx/earshot/.venv/bin/python -m earshot critique <mp4>`, puis describe/match sur les passages suspects) + whisper mot par mot (score < 0.6 = mot mal articulé). Viser true peak <= -1 dBTP sur la voix : un collage avec gain doit passer par un limiteur (« Seulement » écrêté en v23).
- Jamais de pause sans ponctuation (« la ville | dans » donnait « villeu »). Couper le souffle de génération avant le 1er mot d'une prise VoxCPM.
- Fin de vidéo : musique tenue jusqu'au logo (HI=1.5 FADE=0.4 dans mix_bed), pas de long fondu.

## MÉCANIQUE DE TRAVAIL (obligatoire avant chaque livraison)
1. Lire la demande → lister les compétences/outils utiles (bibliothèque de skills : earshot, real-sound, hyperframes-audio, media-use, caption-animation, conversion-copywriting-engine, pitup-content-engine…) et les charger avant d'agir.
2. Écrire la liste de ce qu'il faut vérifier pour CETTE demande, avec un critère mesurable par point.
3. Produire plusieurs candidats quand c'est une génération (voix : 6 prises), les noter tous avec les mêmes critères, garder le meilleur.
4. Voix : `tools/voice_qa.sh voice.wav "ville:v i l b|..."` doit sortir zéro FAIL :
   saturation (0 échantillon écrêté), coupes brutales (aucune chute > 30 dB en 10 ms), silence numérique, mots < 0.6 de confiance,
   phonèmes IPA des mots surveillés (`tools/phones.py`, wav2vec2 espeak) — whisper corrige en silence, les phonèmes non.
5. Mix final : `earshot critique` sans --fast → 0 critique / 0 majeur. Images : extraire et regarder les frames clés.
6. Ne livrer qu'après 4 et 5 ; rapporter les chiffres, et dire clairement ce qui n'a pas pu être vérifié.
Leçon Lubumbashi : « Notre ville bouge » = `v i l ə b` (villeu), « de la ville dans » = `v iː n` (pas de l) : défauts des prises sources, invisibles pour whisper.
- RÈGLE : ne JAMAIS modifier ce que le fondateur a validé (plans, ordre, animations) quand il demande une autre correction. Un défaut repéré hors de la demande → le SIGNALER, ne pas le corriger seul. Les plans de supermarché restent exclus.
- Voix v26 : `tools/level_words.py` (remonte seulement les mots > 4 dB sous la médiane, max +6 dB) avant `punct_pause3.py` ; couper au DÉBUT du creux de silence (sinon le fondu d'entrée écrase la consonne suivante, ex. le « t » de « trouver ») ; fondu de sortie ≥ 50 ms, fin de prise tronquée → décroissance exponentielle 120 ms. QA : `voice_qa.sh` inclut le niveau par mot (3b) et 2 mots de contexte pour les phonèmes.
- Version légère : CRF 19 (≈ 74 Mo pour 31 s, SSIM médian 0,967). À 7 Mb/s les vues aériennes perdent trop (SSIM 0,86).
- v27 Lubumbashi : les prises VoxCPM ont des défauts en DÉBUT et FIN de prise (syllabe parasite « dizə » avant « Notre », « s » de 160 ms + claquement avant « Seulement », clic 30 ms après « aussi »). `qa_rate_gaps.py` (dans voice_qa.sh) mesure le débit par phrase, les sons hors des mots et les clics ; chaque son signalé est vérifié aux phonèmes. Ouverture visée ≤ 7,5 syll/s.
- Après tout changement de durée de voix : revérifier que chaque plan tombe sur son mot (embouteillages → trafic). Ralenti nécessaire → `minterpolate mci`, jamais duplication d'images.
- v28 Lubumbashi (choix du fondateur) : musique NETTEMENT plus basse sous la voix (instrumental à −24 dB sous la voix, `tools/mix_duck_end.py` marge 16), puis à la fin de la voix la musique remonte et passe à la version ORIGINALE chantée (paroles) au même instant du morceau. Exception assumée à la règle « sans paroles » : paroles seulement après la voix.
- Prises VoxCPM par continuation : les ~100 premières ms contiennent un RESTE du prompt (−30/−35 dB, ~75 ms) avant le 1er vrai son → grésillement entendu sur « Seul- » et « Alors » (v28). Toujours couper au vrai début de la parole (montée nette du niveau), vérifier aux phonèmes que le 1er phonème est intact.
- v30 Lubumbashi : voix générée EN UNE SEULE PRISE (texte entier, `vox_cont2` 20 steps, ~100 s par prise), 11 prises notées avec `tools/score_full.sh` (erreurs de mots, phonèmes, coupes, clics, niveaux) → fullBC_0. Assemblage `tools/assemble_v30.py` : aucune coupe dans les mots, pauses seulement dans les silences aux ponctuations, pause « respiration » après « Ah » au vrai point Ah/L (0,31 s). Plus de collage de prises : c'était la source des doublons/grésillements.
- v31 Lubumbashi (rythme narratif validé sur demande) : silences cibles aux ponctuations — « Ah… » 0,6 s, après « Lubumbashi ! » 0,8 s, virgules 0,45 s, points 0,9–0,95 s, « commande | et » 0,35 s ; calculés = cible − silence déjà présent (`tools/assemble_v31.py`). Jamais d'étirement temporel de la voix.
- v32 Lubumbashi : voix de la SŒUR (demande du fondateur), une seule prise complète (`tools/vox_cont.py` sur `audio/soeur/ref_cont.wav`, mots jetables « Bon, alors. » / « Voilà, merci. » retirés par `tools/prep_soeur.py`, 8 prises → soeurT_6). `tools/assemble_v32.py` : pauses narratives placées par alignement texte↔whisper, dans le PREMIER silence ≥ 40 ms après le mot (whisper date parfois le mot suivant trop tard → ne jamais prendre le minimum global). Exceptions vérifiées aux phonèmes : « seulement-entre » lié (pas de pause), départ craqué (vocal fry) avant « la boutique » sauté. Fond continu au niveau du souffle propre de la prise (−49 dB). Fin chantée HIGH_DB=6 pour qu'un moment ressorte (earshot).
- v33 Lubumbashi (choix du fondateur) : chanson ORIGINALE (avec la voix de Tems) dès le début, basse sous la voix off (marge 14 dB, bande 300 Hz–3 kHz creusée de 6 dB pendant la voix), puis remontée à la fin (HIGH_DB=6). `ORIG_ALL=1 CARVE_DB=6 HIGH_DB=6 tools/mix_duck_end.py … 14` → v37 : marge 10 dB, CARVE_DB=4 (musique plus présente, 0 erreur de mot ; à 8 dB des mots se perdent). Intelligibilité vérifiée (whisper, confiance 0,93).
- v34 Lubumbashi : voix « claire » (le fondateur trouvait un son de magnétophone). Chaîne DSP sur la prise brute : `highpass=f=100,afftdn=nr=18:nf=-50:tn=1,equalizer=f=170:t=q:w=1.0:g=-5,equalizer=f=350:t=q:w=1.0:g=-5,equalizer=f=4500:t=q:w=1.2:g=3,aexciter=amount=2:drive=6:blend=0:freq=6000:ceil=16000,highshelf=f=8000:g=3,deesser=i=0.4,agate=threshold=0.006:ratio=1.8:range=0.25:attack=5:release=120` (recaler la latence : 1188 échantillons). Mesuré : présence 3–6 kHz −12 → −2 dB, air 8–12 kHz −30 → −14 dB, souffle −46 → −50 dB, p_real 0,83 → 0,94. NE PAS utiliser VoiceFixer : il change les phonèmes (« Passe » → « basse », « boutique » → « potsik »). Ancien filtre C (lowpass 8,5 kHz) = son étouffé : abandonné.
- v35 Lubumbashi : fins de mots « coupées net » avant les pauses (Lubumbashi !, bouge,) = prises qui finissent sec (chute 25–35 dB en 30 ms). Correction : retirer la porte de bruit (agate) de la chaîne, ajouter `tools/room_tail.py` (petite pièce RT60 0,35 s, wet −17 dB) APRÈS l'insertion des pauses → les mots s'éteignent en 150–200 ms. Détecteur `tools/qa_word_ends.py` ajouté à voice_qa.sh. Maîtrise finale : `loudnorm=I=-14:TP=-2` dynamique (jamais volume+alimiter : l'AAC recrée +3 dBTP de crêtes) → −15,4 LUFS, −1,5 dBTP après encodage.
- v36 Lubumbashi : « Ah » + VRAIE inspiration de la sœur (`audio/soeur/full.wav` 45,47–45,87 s, earshot « inhale » z 5,75 ; `tools/add_breath.py`, −13 dB sous la parole) + léger silence + « Lubumbashi ! ». Pause « Lubumbashi | Notre » : elle enchaîne sans silence ; le seul silence est la fermeture du t de « Notre » (piège !). Couper au creux de fin de « -shi » (1,045 s) et raccourcir le long murmure du N à 80 ms (sinon après une pause on entend « une autre »). Calage des scènes : si le début mesuré au niveau sonore dépasse l'horaire whisper de > 0,2 s (mot doux), prendre l'horaire whisper.
- Encodage AAC : l'encodeur ffmpeg a créé UN clic de +5 dBTP (8 échantillons) sur une piste propre (v37). Toujours : limiteur sur-échantillonné (`aresample=192000,alimiter=limit=0.56,aresample=48000`), PCM 16 bits, `-c:a aac -aac_coder twoloop`, puis mesurer le true peak DU FICHIER LIVRÉ (ebur128 peak=true + earshot) AVANT de l'envoyer.

- Visuels de l'appli : le branding couleur reste sur la ville, le fond et les textes. Les écrans de l'appli et les cartes produits restent le plus clairs possible : aucun grain, vignettage ou reflet par-dessus. Le téléphone se stabilise de face. Le fond de toute la partie appli est un bleu ciel lumineux, sans bords marine (flag `app_clear` dans la config de build_story).

- Voix « studio » (13 novembre) : ne plus utiliser aexciter ni highshelf +3 (ils créaient le grésillement : 50 % de l'énergie entre 3 et 10 kHz). Chaîne : `highpass=f=80,afftdn=nr=24:nf=-55:tn=1,equalizer=f=250:g=-3,equalizer=f=3200:g=1.5,highshelf=f=9000:g=-2,deesser=i=0.5`, room tail à -22 dB, puis `tools/pause_dip.py` (souffle des pauses -18 dB). Script : `tools/rebuild_voice_studio.sh`. Encodage : `alimiter` avec `level=0`, sinon il remonte le volume (+1,4 dBTP).
- Souffle sous la voix (13 novembre) : la prise d'origine n'a que 16 dB entre voix et souffle. Débruiter la prise brute avec `tools/wiener_denoise.py soeur_6.wav out 26 2.0` (profil appris dans les silences, retiré aussi sous la voix), puis `SRC=out tools/rebuild_voice_studio.sh` avec afftdn nr=14, room tail -24, `pause_dip.py` à 8 dB seulement (18 dB créait un effet de pompage). Le débruitage affaiblit le « v » de « venir » : remettre ce mot depuis la voix non débruitée (fondu de 20 ms).
- Fin de mot coupée par le débruitage (ex. « bouge », 13 novembre) : prolonger la consonne finale dans la pause par recouvrement de ses 60 dernières ms, au même niveau, avec une décroissance exponentielle (tau 40 ms). Le timing ne change pas.
