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

- **Échelle typographique** (vidéo « stop guessing text sizes ») : choisir une taille de base, puis multiplier ou diviser par un ratio fixe (1,618 = nombre d'or ; ratio plus grand = hiérarchie plus marquée, plus « premium »). Pour nos vidéos : 34 → 55 → 89 → 144 → 233 px (base 34, ratio 1,618).
- **Quatre styles d'une même affiche** : audacieux (deux couleurs qui contrastent, titre exagéré), minimaliste (peu d'éléments, texte petit, beaucoup d'espace), affiche de film (sombre, lumière dramatique, couleurs 60-30-10), éditorial (la photo raconte la même histoire que le texte, deux typographies).
- **Règle 60-30-10 pour PitUp** : 60 % fond clair, 30 % bleu #1f88c9, 10 % accent (bleu nuit #0d1b2a du texte).
- **20 principes d'UX et d'animation** (capture Instagram) : les 12 principes d'animation (anticipation, follow-through, ease in/out, arcs, action secondaire, timing, exagération…) et les lois d'UX (Fitts, Hick, Miller, Doherty, Postel, Jakob). Loi de Jakob : « ton appli doit marcher comme celles qu'on connaît » (ex. panier en haut à droite).
