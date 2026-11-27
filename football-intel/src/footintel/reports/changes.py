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
]


def news_between(start: date, end: date) -> list[str]:
    """Entries dated from `start` to `end`, oldest first."""
    return [text for day, text in NEWS if start.isoformat() <= day <= end.isoformat()]
