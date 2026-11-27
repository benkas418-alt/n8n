"""Changes made with the owner, in plain French, for the weekly report.

One entry for each change that alters what he sees or bets: the date it went live and one or
two sentences on what changed and why. The weekly report lists the entries of its week. Add an
entry with each decision of docs/DECISIONS.md that changes the tickets, the site or the model.
"""

from datetime import date

NEWS: list[tuple[str, str]] = [
    ("2026-11-21", ("Le site affiche des anneaux de résultats, une barre par ticket et un bouton "
                   "« Copier le ticket ».")),
    ("2026-11-21", ("Le DC 2UP ne va plus dans les tickets, à ta demande. Les paris « pas de nul » nomment "
                   "maintenant les deux équipes, par exemple « Betis ou Real Madrid (pas de nul) ».")),
    ("2026-11-21", ("Manchester City, Chelsea et Aston Villa ne vont plus dans les tickets : tu les trouves "
                   "trop instables. Leurs matchs restent visibles dans Matchs.")),
    ("2026-11-25", ("Le courriel des tickets explique chaque match : le style des deux équipes, leur forme, "
                   "et pourquoi le modèle a choisi ce pari plutôt que la victoire simple. Ce bilan compare "
                   "aussi chaque semaine à la précédente et dit pourquoi un pari a perdu.")),
    ("2026-11-27", ("Test d'un réseau de neurones (apprentissage profond) sur 5 saisons : il fait moins bien que le modèle actuel et que les bookmakers. Il n'est pas mis en service. Tes 45 cotes betPawa du 24 au 26/11 sont enregistrées.")),
    ("2026-11-27", ("Deux autres méthodes testées sur 5 saisons, venues des dépôts que tu as envoyés : LightGBM et les réglages d'un modèle de sélections. Elles font au mieux aussi bien que les bookmakers, pas mieux : rien n'est changé. Notre modèle des sélections fait déjà 62,6 % de bons résultats sur les matchs officiels.")),
    ("2026-11-27", ("Tes cotes betPawa ont maintenant un registre : pour chaque sélection, la cote proposée, la cote juste, le résultat et le gain. Une sélection relevée deux fois ne compte qu'une fois. C'est lui qui dira, marché par marché, si betPawa paie au-dessus de la cote juste.")),
    ("2026-11-27", ("Le registre betPawa sépare tes vrais paris (tes coupons) des simples relevés de cotes, et calcule pour tes paris le gain net et le ROI par marché et par compétition.")),
    ("2026-11-27", ("Tes 6 coupons sont enregistrés avec leur mise et leur paiement. Le bilan de la semaine montre maintenant l'argent réel, coupon par coupon, à part de la qualité des cotes prises.")),
    ("2026-11-27", ("Nouvelle page « Valeur de mes paris » (menu, Analyses) : tes coupons, ton gain cumulé, la qualité des cotes que tu prends marché par marché, et les données qui manquent.")),
    ("2026-11-28", ("Sur la page d'un match, l'encadré « Ce que disent les modèles » montre côte à côte le modèle "
                   "actuel, LightGBM et les bookmakers, et combien de fois chacun a vu juste sur les mêmes "
                   "matchs. Seul le modèle actuel fait tes tickets.")),
    ("2026-11-28", ("Le modèle des tickets s'appelle maintenant Hermès 1.0 sur tout le site. Les "
                   "entraînements de chaque semaine gardent ce numéro : c'est toi qui décides quand il change.")),
    ("2026-11-28", ("Nouveau bouton « Hermès / LightGBM » en haut du site. Sur LightGBM, la page Aujourd'hui, "
                   "les matchs, les tickets et Vérifier une cote suivent l'avis de LightGBM. Ton e-mail du matin "
                   "reste sur Hermès. Sur 5 saisons, LightGBM voit un peu mieux les buts (plus de 2,5 buts, "
                   "les deux équipes marquent) quand il y a des cotes ; pour le vainqueur, les deux font jeu égal.")),
    ("2026-11-28", ("Hermès passe en 1.1 : le vainqueur reste celui d'Hermès ; pour les buts (plus/moins, les "
                   "deux équipes marquent), le site prend l'avis des bookmakers sans leur marge quand il existe, "
                   "sinon celui de LightGBM si le match a des cotes, sinon Hermès. La page du match dit qui a "
                   "donné les buts.")),
    ("2026-11-28", ("Le calcul du 27/11 a échoué à cause d'une nouvelle table ajoutée la veille : pas d'e-mail ce "
                   "jour-là et le site est resté sur les données du 26/11. C'est corrigé et testé ; tes données "
                   "n'ont rien perdu.")),
    ("2026-11-28", ("Les tableaux « Après le premier but » et « par tranche de 15 minutes » ne comptent plus "
                   "un match dont les minutes des buts manquent comme un 0-0. Le handicap asiatique a été testé "
                   "pour mieux estimer 1UP, 2UP et premier but : il n'apporte rien, rien n'est changé.")),
    ("2026-11-28", ("Dans l'onglet Moments du match, le site dit maintenant combien de matchs il a écartés parce "
                   "que les minutes des buts manquaient.")),
    ("2026-11-28", ("Les cotes justes « marché » sont plus exactes : la marge des bookmakers est maintenant retirée "
                   "davantage sur les outsiders que sur les favoris, comme ils la répartissent en réalité. Un "
                   "favori à 1,50 environ a une cote juste un peu plus basse qu'avant ; un outsider, un peu plus "
                   "haute. Testé sur 78 000 matchs.")),
]


def news_between(start: date, end: date) -> list[str]:
    """Entries dated from `start` to `end`, oldest first."""
    return [text for day, text in NEWS if start.isoformat() <= day <= end.isoformat()]
