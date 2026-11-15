# Dossier : pub « Rejoignez-nous » (novembre 2026)

**État au 15 nov.** : v10 livrée en deux versions (format cinéma et plein écran). Le fondateur n'a pas encore choisi. Texte, voix, scènes d'appli et fin sont validés ; seule l'ouverture reste ouverte.

## Ce qui est validé (ne plus y toucher)

- **Texte de la voix** (« le texte est vraiment bon ») :
  « Ici, on a toujours su vendre, créer, se débrouiller. Aujourd'hui, tout ça passe aussi par le téléphone. Tu as des articles à la maison ? Un petit stock ? Une grande boutique ? Publie-les sur PitUp, et les clients viennent à toi. Tu es graphiste, photographe, maquilleuse, couturier ? Montre tes travaux, et postule aux offres de projets. Et ceux qui cherchent te trouvent, au même endroit. Vendeurs, prestataires, acheteurs : rejoignez-nous. Une plateforme fièrement congolaise, pour les Congolais. »
- **Voix** : recette « Motion point » (voir `voix-off.md`), prises `p2_0 p1_1 p0_2 p0_3 p0_4 p2_5 p2_6 p0_7 p2_8`, voix placée à 5,0 s.
- **Scènes d'appli** : mots animés (pas de liste), téléphone 3D avec enregistrements d'écran réels.
- **Fin** : femme en pagne, puis photo libre d'une main levant le drapeau de la RDC, traits bleu/jaune/rouge, bandes aux couleurs du drapeau vers le logo.
- **Plans vendeurs** : vêtements sur portant à la maison, inventaire de vêtements, boutique avec mur de baskets.

## Déroulé (42 s)

| Temps | Image |
|---|---|
| 0–5 s | Ouverture de Lubumbashi, sans texte ni voix |
| 5–11,7 s | Marché, étal, femme au téléphone (« Vendre. Créer. Se débrouiller. », « Tout passe par le téléphone. ») |
| 11,7–19,1 s | À la maison ? Un petit stock ? Une grande boutique ? puis appli vendeurs |
| 19,1–26,4 s | Graphiste, photographe, maquilleuse, couturier, puis appli prestataires |
| 26,4–29,4 s | Appli acheteurs (page Marché, puis fiche « maillot Congo DRC ») |
| 29,4–33,25 s | Trois portraits : Vendeurs. Prestataires. Acheteurs. Rejoignez-nous. |
| 33,25–36,9 s | Fièrement congolaise. Pour les Congolais. |
| 36,9–41,7 s | Logo, pi-tup.com, badges |

## L'ouverture : historique des dix essais

| Version | Ouverture | Verdict du fondateur |
|---|---|---|
| v1 | Stade, gare, avenue (archives) | Flou |
| v2 | Vues aériennes de Kigali | « Pas ceux de Lubumbashi » |
| v3–v5 | Trois plans de marché (Afrique de l'Ouest) | Taxis pas de Lushi |
| v6 | Taxi jaune d'archive | « Vraiment flou » |
| v7 | Vues aériennes d'archive (rond-point, lac) | « Déjà vu et revu », flou |
| v8 | Deux triptyques de bandes tirés de sa vidéo | Veut un grand plan puis un détail |
| v9 | Rond-point aérien + avenue au couchant | Pas de jour ; pas tiré de sa vidéo |
| v10 | Alilac Center, minibus jaune, immeuble vitré, tirés de sa vidéo, de jour | En attente |

**Cause de fond** : toutes les vidéos de Lubumbashi reçues sont des fichiers TikTok compressés (576 px). Sa vidéo de référence (@djeudy_243) est en paysage 1024 × 576. En plein écran vertical elle est agrandie 3,3 fois. Pour du plein écran net il faut le fichier d'origine.

## Fabrication

- Projet HyperFrames : `hf/videos/pitup-rj` dans le dossier de travail de la session (non versionné).
- Constructeur : `pitup/tools/build_rj2.py out.html` (format cinéma) ; `FULL=1 …` pour le plein écran.
- Mixage : `pitup/tools/motion_mix.py bed.wav out.wav places.json`, puis bruitages réels (swish, pop, tap).
- Rendu : `npx -y hyperframes@0.8.181 render . --quality high --fps 30 -o renders/x.mp4`.
- Son livré : −16,8 LUFS, crête −1,3 dB.

## Sources des plans (Pexels, libres)

Marché 27165158, étal 27165159, femme au téléphone 7100960, portant à la maison 8581122, inventaire 8484954, boutique 7679830, graphiste 7967290, photographe 8497005, maquilleuse 6109694, couturière 37409118, portraits 9690753 / 7754484 / 7123826, pagne 6193477, drapeau (photo) 12371836.

## Points ouverts à lui rappeler

- Accord ou crédit de @djeudy_243 pour ses images.
- Accord des vrais utilisateurs visibles dans les captures de projets.
- La voix dit « couturier », l'image montre une couturière.
- « Postule aux offres » : l'écran « Opportunités de projets » affichait « Aucune offre disponible ».
