# Motion design simple pour les acheteurs (27 nov. 2026)

Demande : « Travaillons sur un motion design vidéo simple », avec deux vidéos YouTube et un dépôt.
- Références : deux cours de copywriting sur l'accroche (Brandon Storey, « Become a Top 1% Earning Copywriter by Mastering Hooks » ; Alex Cattoni, « How To Write A KILLER HOOK »). YouTube bloque le téléchargement et les sous-titres depuis le conteneur ; le fondateur a choisi la lecture des sous-titres par vidIQ (5 crédits par vidéo). Seul Storey a été lu : le compte n'avait plus que 4 crédits pour Cattoni. À redemander en fichier si besoin.
- Retenu de Storey : l'accroche peut être un mot, une image, un son ou la forme ; une promesse précise pour un problème précis ; la clarté avant l'astuce ; dire tout de suite ce que la personne y gagne ; un appel à l'action net à la fin.
- Dépôt `langchain-ai/lca-managed-agents` : kit d'un cours LangChain sur un « agent designer » (charte dans `brand.json`, contrôle qui bloque les visuels hors charte, rendu SVG → PNG et auto-relecture). Idée à reprendre : une charte PitUp lisible par le code et un contrôle automatique avant livraison. Non installé (clés Anthropic et LangSmith requises).
- Cible choisie par le fondateur : les acheteurs (commander).

## Recette v1

- `pitup/tools/build_md.py` → projet `hf/videos/pitup-md`. 15,7 s, sans voix.
- Musique : Tems « Me & U » à partir de 46,07 s (112 BPM, un temps toutes les 0,53 s). Même morceau que « commande-livraison » (autre passage) : le signaler, en proposer un autre s'il le souhaite.
- Texte calé sur les temps, 1 à 3 mots, taille 144 px (deux lignes plutôt que plus petit) : « Tu cherches / des baskets ? / à Lubumbashi ? (tapé) » → fond bleu « Sans faire / le tour / des boutiques. » → téléphone 3D avec l'appli (Shopping › Vêtements & Mode, prix masqués) « Trouve-les / sur PitUp / Tu commandes. / On te livre. » → fond bleu « Tu paies / à la livraison. » (surligné) → fin : logo, PitUp, slogan, pi-tup.com, « Disponible sur », badges.
- Petite icône PitUp en haut dès la première image (marque visible dans les 3 premières secondes).
- Sons : vrai déclic photo sur un changement de scène sur deux, vrai clavier sur « à Lubumbashi ? ». −14 LUFS.
