# Vidéo « présentation de l'appli » par un collaborateur (25 nov.)

Demande : deux rushs (WA0033, WA0034, 34 s et 32 s, sans son) : un jeune homme à son ordinateur qui se lève et vient vers la caméra, puis qui montre un maillot de foot, des baskets blanches et des baskets noir et blanc. Il présente l'appli avec SA voix clonée, ton jeune et dynamique (« Yo les gars… »), rythmes alternés comme la voix de la sœur, compréhensible, sans argot bizarre ni verlan, avec appel à l'action. Le fondateur dit que la personne est d'accord.

## Voix

- Une voix masculine avait été clonée le 11 nov. (messages WhatsApp du 27 sept., voir `historique-complet.md`, « Voix masculine »), jugée pas assez claire. Les fichiers ont disparu avec la réinitialisation de l'environnement (25 nov.) : à redemander.
- À demander : 30 à 60 s de sa voix, pièce calme, téléphone à 20 cm, en parlant naturellement (note vocale WhatsApp envoyée en document, ou fichier audio).

## Points à faire valider

- Logos visibles : maillot avec logos de grandes marques, baskets avec logo de marque (règle « pas de grande marque visible »).
- Les articles montrés sont-ils vendus sur PitUp ? Ne pas l'affirmer sans confirmation.

## Réponses du fondateur (25 nov.)

- « GitHub » dans ses messages dictés = **PitUp** (déformation de la dictée). Tous les articles montrés sont vendus sur PitUp. Maillots et logos : « il n'y a pas de souci, tu peux les mettre ».
- Voix : il renvoie les deux messages du 27 sept. (WA0031, WA0032, 50 s et 48 s).
- Montage : cuts et transitions propres ; le passage où il s'approche de la caméra (« il zoome ») → le logo PitUp s'agrandit. En ouverture ou en fin ; en ouverture, rapide (hook ≈ 3 s).
- **Attendre** sa vidéo sur « comment attirer l'attention » avant de monter.

## Leçons d'accroche envoyées le 25 nov.

- Vidéo « Croquette Saumon » (74 s) : phrase qui interpelle d'entrée (« Qu'est-ce que tu fais, frère ? ») + geste brusque vers la caméra ; il nomme le hook (« le but, c'est de vous attraper ») ; un changement de décor ou de plan toutes les 2-3 s ; bruitages marqués ; curiosité entretenue.
- Vidéo des deux filles vues d'en haut (14 s) : angle inhabituel, main qui fonce sur l'objectif et le couvre (interruption), texte affiché tout de suite.
- Application : ouvrir sur le présentateur qui s'avance vers la caméra et la couvre, le logo PitUp jaillit du noir, le tout en 3 s ; puis un article par plan, 2-3 s chacun.
- Plans de ville (Snapchat, 25 nov.) : par la vitre d'une voiture (drapeau du Congo à la fin, 6 s) et dans un minibus (passagers de dos, 3,5 s). Mis de côté pour une autre vidéo, à étalonner.

## Voix clonée, version 1 (25 nov.)

- Référence : WA0031, voix isolée par demucs, 0 à 14,2 s, passe-haut 70 Hz, débruitage léger (afftdn −30), loudnorm −18. Fichier hors dépôt (`scratchpad/audio/gh/ref.wav`).
- Style VoxCPM2 : « voix masculine jeune et dynamique, décontractée et souriante, comme un jeune qui parle à ses potes, claire et bien articulée, rythme vivant ».
- « Yo les gars ! » seul est trop court : le modèle le déforme. Le fusionner avec la phrase suivante.
- Hauteur médiane des prises retenues : environ 121 Hz (écart toléré ±25 Hz).
- Script : « Yo, les gars ! Attendez… regardez-moi ça. / Un maillot de foot, tout propre. / Des baskets blanches, bien clean. / Et celles-là ? Franchement, elles sont lourdes. / Tout ça, c'est sur PitUp. / Plus de cent boutiques de Lubumbashi, direct dans ton téléphone. / Tu commandes, on te livre, et tu paies à la livraison. / Allez, télécharge l'appli. On se capte sur PitUp ! »
- Aperçu envoyé au fondateur. Musique : fichiers perdus avec la réinitialisation, à redemander.
- **Voix v1 refusée** (25 nov.) : timbre pas identique, « PitUp » prononcé « Pito ». Cause : le texte de style de VoxCPM2 écrase le timbre ; la référence ne contenait pas le mot « PitUp ».
- WA0031 et WA0032 (50 s et 48 s) sont le même texte publicitaire lu au « vous ». Il y dit « PitUp » 5 fois par note (Whisper écrit « PITAP »). v2 : mode continuation avec un passage où il dit « PitUp » comme amorce, sans texte de style.
- À corriger dans le script v2 : « Plus de cent boutiques de Lubumbashi, direct dans ton téléphone » enfreint la règle du chiffre. Écrire « Plus de cent boutiques locales nous ont déjà rejoints. »

## Sources de voix reçues de nouveau (25 nov., après la réinitialisation)

- Vidéo TikTok de la sœur (99 s, voix propre, sans musique) : source du clone de la sœur, remise dans `scratchpad/inbox/soeur/src.mp4`.
- Film de lancement v5 : renvoyé comme **cible de clarté** de voix (« le résultat qui m'avait plu »).

## Voix clonée, version 2 (25 nov.)

- Mode continuation (`pitup/tools/vox_cont_batch.py`), sans texte de style. Amorce : WA0031, voix isolée, 0 à 5 s (« Vous êtes à Lubumbashi… »), avec son texte exact. Référence : WA0031, voix isolée, 0 à 18 s, loudnorm seul.
- Orthographe : « Pit-ap » donne la bonne prononciation (Whisper écrit « PitApp », comme sur sa vraie voix) ; « Pitt Up » donne « Pitop » : à ne pas utiliser.
- Échec : une amorce prise à 18,7–23,75 s (« Ouvrez PitUp… ») fait dérailler le modèle (21 s de bruit par phrase). Garder l'amorce du début de la note.
- Prises choisies (c2) : t_0_0, t_1_0, t_2_0, t_3_1, t_4_1, t_7_1, t_8_1. Ressemblance (resemblyzer, contre WA0032) : aperçu v2 0,875 ; aperçu v1 0,808 ; deux extraits réels de 2,5 s entre eux 0,86 à 0,90.
- Hauteur : sa vraie voix a une médiane d'environ 102 Hz (pyin 85–260 Hz). Beaucoup de prises tombent au plancher de 85 Hz (voix grave ou éraillée) : pyin n'est pas fiable pour lui, juger surtout à la ressemblance et au texte.
- Script v2 sans la phrase « +100 » (règle du chiffre). Aperçu envoyé : `scratchpad/apercu_voix_presentateur_v2.m4a` (16,8 s, hors dépôt).
- **Retour sur la v2** (25 nov.) : « 64 % ». Le présentateur attaque ses phrases avec plus d'énergie ; le fondateur exige plus de fluidité, des syllabes moins hachées. Le prénom du présentateur n'est pas écrit dans ce dépôt public.

## Voix clonée, version 3 (25 nov.)

- But : plus d'élan en début de phrase, syllabes liées (retour « 64 % »).
- Mesure du haché : `pitup/tools/voice_chop.py` compte les creux d'énergie courts (50 à 250 ms, 15 dB sous la parole) par seconde. Sa vraie voix : 2,2 à 2,4. Aperçu v2 : 3,4 (d'où le haché entendu). Aperçu v3 : 2,2.
- Recette : `pitup/tools/vox_jobs.py` (un seul chargement du modèle, détecte les dérapages), 25 pas d'inférence au lieu de 10, cfg 2,0. Le script en **3 blocs de 2 à 3 phrases** au lieu de 7 phrases séparées : le modèle lie mieux les phrases entre elles.
- Amorce F : WA0031, voix isolée, 5,72 à 13,82 s, avec son texte exact écrit « Pit-ap est votre application de shopping… » (sa phrase la plus vive, qui contient le nom). Référence : `ref2.wav`.
- Prises retenues : f_0_1, f_1_1, g_0_3. Ressemblance 0,867 (v2 : 0,875). Texte entièrement juste, « PitUp » entendu « PITAP ».
- Choix : `tr_dir.py` (texte), `score_clone.py` (ressemblance), `voice_chop.py` (haché). Écarter « tu perds la livraison », « on s'est capté », un « Pitap ? » qui monte en question.
- **Piège ffmpeg** : avec `-ss` placé après `-i`, les temps des filtres (`afade … st=`) restent ceux du fichier d'origine ; mon fondu de fin a rendu deux amorces muettes, et une amorce muette fait dérailler VoxCPM2 (20 s de bruit). Mettre `-ss`/`-to` **avant** `-i` et vérifier le volume de l'amorce (`volumedetect`).

## Montage v1 (26 nov., sans musique)

- Le fondateur répond « Okay » à la voix v3 (sans pourcentage) : pris comme un accord pour monter.
- `pitup/tools/build_gh.py` → projet `hf/videos/pitup-gh`, 19,0 s. Rushs réétalonnés ensemble (`match_grade.py`) avec deux nouveaux plans tirés de G1 : `hook` (15,9 à 19,2 s, main sur l'objectif à 3,07 s) et `close2` (26,1 à 29,2 s, main sur l'objectif à 2,93 s). Dans G1, la main couvre l'objectif de 19,0 à 20,8 s puis à partir de 29,0 s (temps ffmpeg).
- Déroulé : « Yo les gars ! Attendez… Regardez ça ! » (il s'avance, couvre l'objectif) → logo PitUp 2D qui grandit sur le noir à 2,65 s, son du logo → maillot (souffle) → baskets blanches (déclic + flash) → baskets noires (déclic + flash) → au portable « C'est sur PitUp / Tu commandes » (souffle) → il s'approche « on te livre / Paiement à la livraison » → « Allez, télécharge l'appli. On se capte ! », main sur l'objectif → fin bleue : logo, PitUp, slogan, pi-tup.com, « Disponible sur », badges.
- Sons Mixkit choisis avec `earshot rank` : souffle 1491, déclic 1432, carillon du logo 2573.
- Textes : blancs sur dégradé sombre en haut, 1 à 3 mots, « Paiement à la livraison » sur 2 lignes.
- −14,6 LUFS (voix et sons seuls). Musique à ajouter : `BED=<fichier> python build_gh.py`.
- **Retour sur le montage v1** (26 nov.) : bruitages refusés (« ça donne IA », carillon) ; les plans `close` et `close2` (il refait le geste vers l'objectif) refusés ; combler avec l'appli dans un téléphone ou le logo.

## Montage v2 (26 nov., sans musique ni bruitage)

- Plus aucun bruitage. Plus de flash. Plans `close`/`close2` retirés.
- « Tout ça, c'est sur PitUp » : au portable. « Tu commandes, on te livre, paiement à la livraison » : téléphone 3D réaliste sur fond clair, écran = défilement de Shopping › Vêtements & Mode sur pi-tup.com. « Allez, télécharge l'appli… » : fin bleue (logo, PitUp, slogan, pi-tup.com, « Disponible sur » à « télécharge »). 18,7 s.
- Capture de l'appli : `recordVideo` de Playwright ne filme qu'en 1x, dans un coin de l'image : à ne pas utiliser. Faire une capture image par image (`page.screenshot` à chaque pas de défilement de 9 px, facteur 2), puis assembler à 30 i/s. Les prix sont masqués par un script injecté (règle « aucun prix »). Fichiers hors dépôt (`scratchpad/app/`).
- Encoder les plans avec `-g 30 -keyint_min 30` : sinon HyperFrames signale des images clés trop rares (risque d'image figée).
