# Atelier : outils, compétences et contrôles

## Remettre l'atelier en place

```bash
bash pitup/memoire/3-atelier/installer.sh etat     # ce qui est là, ce qui manque, disque libre
bash pitup/memoire/3-atelier/installer.sh skills   # compétences (testé le 15 nov. : 55 remises en place)
bash pitup/memoire/3-atelier/installer.sh voix     # VoxCPM2 + faster-whisper (environ 3 Go ; non re-testé sur conteneur neuf)
bash pitup/memoire/3-atelier/installer.sh son      # earshot (environ 3 Go ; non re-testé sur conteneur neuf)
```

N'installer que le module utile à la demande : la voix et le son pèsent 3 Go chacun et le disque est petit.

## Quel outil pour quel travail

Tous les scripts sont dans `pitup/tools/`. Chaque script porte son mode d'emploi dans ses premières lignes.

| Travail | Outil |
|---|---|
| Monter une pub ou un film de marque | `build_rj2.py` (dernier en date), `build_ad2.py`, `build_ad.py` |
| Monter un motion design | `build_mc3.py`, `build_mc.py` (calé sur les mots) |
| Monter une vidéo produit ou une story | `build_story.py` + `pitup/cfg/*.json` |
| Rendre la vidéo | `npx -y hyperframes@0.8.181 render . --quality high --fps 30 -o renders/x.mp4` |
| Aperçu rapide d'images clés | `node frames.cjs page.html prefixe t1 t2…` (les vidéos ne jouent pas dans cet aperçu) |
| Générer la voix | `vox_clone_texts.py` (recette validée) ; `vox_cont.py` (ancien mode, refusé) |
| Juger une prise de voix | transcription whisper, `phones.py` (phonèmes), `voice_human.py` (écart à la vraie voix), `voice_qa.sh` |
| Mixer voix et musique | `motion_mix.py` (recette validée) ; `mix_duck_end.py` (ancien) |
| Écouter un son sans oreilles | `cd /home/user/leonxlnx/earshot && .venv/bin/python -m earshot critique fichier.wav` |
| Étalonner les plans | `grade.py entrée sortie` |
| Ralentir un plan | `minterpolate=fps=60:mi_mode=mci,setpts=N*PTS,fps=30` (jamais de duplication d'images) |
| Retirer un filigrane | recadrage d'abord ; sinon `lama_wm.py`, `tiktok_clean.py` |
| Carrousels | `pitup/carousel-rdc/` (`index11.html` carré, `index916.html` vertical) |

## Compétences à charger selon la demande

- **Texte, script, description** : `pitup-content-engine`, `conversion-copywriting-engine`, `viral-psychology-strategist`.
- **Vidéo** : `hyperframes`, `gsap-timeline`, `kinetic-typography`, `mockup-device-3d`, `frame-logo-outro`, `design-motion-principles`.
- **Son** : `earshot`, `real-sound`, `hyperframes-audio`.
- **Apprentissage** : `pitup-apprentissage` (toujours).

## Contrôles avant chaque livraison

1. **Image** : extraire 10 à 20 images clés et les regarder (textes lisibles, rien qui se chevauche, aucun interdit, plan net).
2. **Voix** : chaque prise transcrite ; le mix final transcrit aussi (tous les mots reconnus par-dessus la musique).
3. **Son** : `ffmpeg -i fichier -af ebur128=peak=true -f null -` sur le fichier livré. Viser −14 à −17 LUFS, crête sous −1 dB.
4. **Rendu** : aucun clip HDR (`ffprobe color_transfer` doit dire bt709 ou smpte170m) ; plus de 1 Go de disque libre.
5. **Rapport** : dire ce qui a été vérifié, ce qui ne l'a pas été, et les défauts connus.

## Fichiers hors dépôt (à redemander au fondateur)

- Voix : `audio/soeur/ref.wav`, `audio/soeur/full.wav`, référence de la « jumelle ».
- Musique : Tems « Me & U » et les autres morceaux fournis.
- Plans vidéo : dossier `story/v/`, vidéo de @djeudy_243.
- Captures et enregistrements d'écran de l'appli montrant de vrais utilisateurs.
- Il existe un **kit média** (archive du 13 nov.) qu'il a reçu : le lui redemander en premier.

## Environnement

- Sessions dans un conteneur cloud éphémère : tout ce qui n'est pas poussé sur la branche est perdu.
- Le dossier de travail (`scratchpad`) n'est pas durable : y fabriquer, mais ranger les scripts et les notes dans le dépôt.
- Disque très limité (environ 1 Go libre) : supprimer les anciens rendus et les téléchargements au fur et à mesure.

## Sites d'inspiration (envoyés par le fondateur, 18 nov.)

- Are.na (motion, typo, composition), Eyecannndy (nom et exemple de chaque effet de montage), Color-hex (palettes), Behance (projets de designers), Cari (esthétiques nommées, moodboards).
- Usage : chercher une idée de mouvement ou de transition, puis l'appliquer dans la DA PitUp (jamais copier un univers).

## Théorie de design envoyée par le fondateur (19 nov.)

- **Échelle typographique** (vidéo « stop guessing text sizes ») : choisir une taille de base, puis multiplier ou diviser par un ratio fixe (1,618 = nombre d'or ; ratio plus grand = hiérarchie plus marquée, plus « premium »). Pour nos vidéos : 34 → 55 → 89 → 144 → 233 px (base 34, ratio 1,618). Appliqué dans `build_cmd.py` (variable `SCALE`).
- **Quatre styles d'une même affiche** : audacieux (deux couleurs qui contrastent, titre exagéré), minimaliste (peu d'éléments, texte petit, beaucoup d'espace), affiche de film (sombre, lumière dramatique, couleurs 60-30-10), éditorial (la photo raconte la même histoire que le texte, deux typographies).
- **Règle 60-30-10 pour PitUp** : 60 % fond clair, 30 % bleu #1f88c9, 10 % accent (bleu nuit #0d1b2a du texte).
- **20 principes d'UX et d'animation** (capture Instagram) : les 12 principes d'animation (anticipation, follow-through, ease in/out, arcs, action secondaire, timing, exagération…) et les lois d'UX (Fitts, Hick, Miller, Doherty, Postel, Jakob). Loi de Jakob : « ton appli doit marcher comme celles qu'on connaît » (ex. panier en haut à droite).

## Retirer des autocollants d'un plan filmé en voiture (19 nov.)

- Demande : enlever les autocollants du pare-brise et « reconstruire ces parties, pas flouter ».
- Ce qui ne marche pas sur un plan tenu à la main : masque fixe, alignement ECC sur le tableau de bord, reconstruction par images voisines (la rue et les autocollants bougent presque ensemble).
- Ce qui marche : `pitup/tools/sticker_track_lama.py in.mp4 out.mp4 masks.json ref t0 t1` : chaque autocollant suivi par sa propre texture (corrélation, recherche locale, chaînée), LaMa à chaque image, bords fondus, léger mélange avec les images voisines. Masques à tracer sur l'image lue par OpenCV (débit variable : les numéros d'image diffèrent de ffmpeg).
- Limite : légère différence de teinte possible dans les grandes zones refaites ; vérifier en zoom.

## Réinitialisation de l'environnement (25 nov.)

- Le scratchpad, les fichiers envoyés (musiques, voix de référence de la sœur) et les outils installés ont disparu. Réinstallé : `installer.sh voix` + `son`, demucs dans le venv voxcpm, OpenCV système, extras d'écoute d'earshot (torch CPU).
- Ressources graphiques réutilisables dans le dépôt : `pitup/shared-assets/` (icône blanche, logo texte, slogan, polices Poppins, gsap) et `pitup/carousel-rdc/` (badges App Store et Google Play).
- À redemander au fondateur : référence de la voix de la sœur, musiques (Tems « Me & U », Raindance, Drake…).

## Inventaire du dépôt (25 nov.) : ce qui n'est PAS perdu

- Logos de 24 boutiques : `pitup/videos/pitup-story/assets/shops/` (+ `names.json`). Autres logos : `pitup/tools/shoplogo.cjs <nom>` les cherche sur pi-tup.com.
- Écrans de l'appli : `appshot.cjs` (accueil, marketplace, shopping, produit, boutique), `cartshot.cjs`, `loginshot.cjs`, `cardlogo.cjs` capturent pi-tup.com en vue mobile (site joignable depuis le conteneur). Ce sont des captures fixes : un enregistrement d'écran filmé reste à demander.
- Photos réelles et articles : `pitup/videos/pitup-story/assets/real/` et `st/`.
- Voix : `phones.py` (phonèmes, pour vérifier « pit-ap »), `voice_human.py`, `prep_soeur.py`, `room_tail.py`, `add_breath.py`, `wiener_denoise.py`, `voice_qa.sh`, `vox_cont*.py`.
- Mixage et rythme : `mix_duck.py`, `mix_bed.py`, `beats*.py`, `music.py`.
- Téléphone 3D : `glbshot.cjs` (le modèle .glb n'est pas dans le dépôt).
- Notes marketing du 21 nov. (présentes seulement sur master) : copiées dans `2-dossiers/marketing-et-motion.md`.
- Aucune autre branche distante ne contient de fichier PitUp absent de notre branche, à part `ccr-66613461-5optll` (`pitup/tiktok-veille/`, un workflow de veille TikTok).

## Dépôts envoyés le 27 nov. (étudiés, clonés dans `/home/user/ext/`)

| Dépôt | Ce que c'est | Pour nous |
|---|---|---|
| `Vincentwei1021/video-shotcraft` (Apache-2.0) | Compétence Claude Code : 125 fiches de plans animés avec le code de démonstration (Remotion), une méthode en 6 étapes (capture des vraies pages, découpage, calage sur le rythme, sons, contrôle image par image), un outil de recherche de bruitages sur Freesound | **Utile.** Fiches à adapter en HyperFrames : `speed-ramp-freeze` (ralenti), `logo-shrink-wordmark-lockup` et `white-flash-logo-simplify-cut` (fins de logo), `radial-ripple-phone-chips`, `deck-deal-flyin`, `card-stack` (articles), `flying-words`, `lead-word-zoom-assemble` (texte), `beat-cut-moves` (coupes sur le rythme), `crash-zoom-punch`. Les fiches sont en chinois. Installée comme compétence (`installer.sh skills`). |
| — son outil `assets/scripts/sfx-source.py` | Recherche de vrais enregistrements sur Freesound, sans clé, licence CC0 par défaut | **Utile, avec accord du fondateur.** Ex. : un vrai déclencheur d'appareil argentique (« Pentax K1000 Camera Shutter », fs:579883, CC0). `python3 -I assets/scripts/sfx-source.py search "camera shutter click" --max-duration 2`. Ses sons de modèle (`template/public/audio`) viennent de Mixkit : ne pas les utiliser (règle « aucun bruitage de banque »). |
| `processing/p5.js` (v2.4.0, installé dans `/home/user/ext/npm/node_modules/p5/lib/p5.min.js`) | Bibliothèque de dessin génératif sur canvas (particules, formes, bruit) | Possible pour des fonds ou des effets génératifs dans la DA. Charger depuis jsdelivr avec une version exacte ; en mode `noLoop()` et redessiner à partir du temps de la timeline GSAP, sinon le rendu HyperFrames (qui saute d'image en image) n'est pas reproductible. |
| `danielwh2/cuelume` (v0.2.10) | 14 sons d'interface synthétisés en direct (Web Audio) pour sites web | **Installé** (27 nov., à sa demande) dans `/home/user/ext/npm`. Pas pour les vidéos : sons fabriqués par code, bannis le 26 nov. Pour l'appli PitUp elle-même (retours sonores des boutons). |
| `elevenlabs/skills` | Compétences pour l'API ElevenLabs (voix, sons, musique, doublage) ; clé API obligatoire | **Installé** (27 nov., à sa demande) : 13 compétences `elevenlabs-*` dans `~/.claude/skills`. La règle « jamais ElevenLabs » reste en vigueur : ne pas s'en servir pour une vidéo tant qu'il ne l'a pas levée explicitement. Aucune clé n'est configurée. |

