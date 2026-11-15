# Dossier : images, plans et écrans de l'appli

## Avant de retenir un plan : cinq questions

1. Est-il **net** ? Mesurer (variance du laplacien sur une image 1080 × 1920). Repère : plan 4K libre ≈ 240 ; en dessous de 100 le fondateur voit du flou.
2. Montre-t-il **Lubumbashi**, ou un décor neutre ? Jamais une autre ville reconnaissable (bâtiments, taxis, plaques).
3. A-t-il **déjà été publié** ? Si oui, non.
4. La **lumière** suit-elle le plan voisin (jour avec jour) ?
5. Contient-il un interdit (moto, fumeur, supermarché, logo de grande marque, filigrane, affiche politique) ?

## Plans de Lubumbashi disponibles (tous issus de TikTok, 576 px)

Dossier de travail `story/v/` (hors dépôt).

| Fichier | Contenu | Netteté | Statut |
|---|---|---|---|
| `air_lushi` | Rond-point du monument, lac et hôtel, vus du ciel | 204 | **Déjà publié, refusé** |
| `day_lushi` | Avenue vue du ciel, passants, minibus | 168 | Déjà publié ; affiches politiques |
| `street_golden` | Avenue au coucher du soleil, drapeau | 79–133 | Refusé (pas de jour) |
| `top_roundabout` | Rond-point du marché vu du ciel | 38–56 | Jugé pas net |
| `hk_bouge` | Cinq plans de 0,8 s dont le taxi jaune | < 10 | « Vraiment flou » |
| `ae_*`, `s_*`, `jd_*`, `L*`, `hk_open`, `sun_*` | Stade, gare, cathédrale… | < 55 | Flous, ne plus utiliser |
| Vidéo de @djeudy_243 (`inbox/alilac/src.mp4`) | 20 plans de rue, de jour | paysage 1024 × 576 | **Source demandée par le fondateur** |

Vidéo de @djeudy_243, plans utilisables (début en secondes) : Alilac Center 0,05 ; rue aux taxis-bus 9,0 ; immeuble vitré 10,18 ; pêcheurs au lac 11,48 ; portière de minibus 17,78 ; minibus et receveur 22,62 ; pirogue 27,45.
À écarter : 2,27 (logo Toyota), 3,27 et 6,8 (motos), 13,03 (Airtel), 18,73 (Africell, moto), 20,7 (panneaux).
Filigrane TikTok : en haut à gauche jusqu'à 5,2 s, puis en bas à droite.

## Sources libres

- Pexels sans clé : photo `https://images.pexels.com/photos/ID/pexels-photo-ID.jpeg?auto=compress&cs=tinysrgb&w=2400` ; vidéo `https://www.pexels.com/download/video/ID/` ou `https://videos.pexels.com/video-files/ID/ID-hd_1080_1920_30fps.mp4` (le suffixe varie).
- Trouver les ID par recherche web `site:pexels.com/video <sujet>`.
- **Rien de filmé en RDC** sur Pexels, Pixabay ou Wikimedia (vérifié le 14 nov.). Getty vend des vues aériennes de Lubumbashi (payant). Pikwizard propose des images générées par IA : à éviter.
- Un clip HDR (bt2020) fait échouer le rendu : vérifier `ffprobe color_transfer` et repasser en bt709.

## Écrans de l'appli

- Enregistrements d'écran réels (`story/v/`, hors dépôt) : `phapp` (création de boutique), `ph_vb`, `ph_teg`, `ph_store` (pages boutique), `phs_full` (page Marché avec recherche), `ph_congo` (maillot Congo DRC), `ph_jordan`, `ph_market2`…
- Captures de projets : effacer « Tarif indicatif … $ » et la barre d'état avant usage. Vrais utilisateurs visibles : accord à obtenir.
- Ne pas montrer l'écran « Opportunités de projets » tant qu'il affiche « Aucune offre disponible ».
- Une vidéo dans le téléphone 3D : élément `<video class="clip">` à la racine, avec les mêmes transformations que le cadre du téléphone (voir `pitup/tools/build_rj2.py`).

## Étalonnage

`pitup/tools/grade.py entrée sortie` : même rendu de couleur pour tous les plans d'une vidéo.
