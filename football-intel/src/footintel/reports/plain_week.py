"""The week in plain French for the owner (D80, D97): the weekly e-mail body.

It explains rather than lists: each lost selection with the chance the site gave it (a normal
miss or a real surprise), the tickets won against what the site's own chances expected, each
type of bet, the misses of his teams set against the bookmakers' view, four weeks of the site
against the bookmakers, whether the site's percentages hold, and what changed in the model.
Short sentences, one figure at a time. The technical report stays as an attachment.
"""

import math
from datetime import date, datetime, timedelta

from footintel.analysis.tickets import FOLLOWED, _team_followed, national_followed
from footintel.names_fr import fr_names
from footintel.notify.tickets import SITE
from footintel.reports.changes import news_between

_STATE = {"gagné": "gagné ✅", "perdu": "perdu ❌", "en cours": "pas encore réglé ⏳"}
LEAGUES_FR = {"ENG-PL": "Premier League", "GER-BL": "Bundesliga", "ITA-SA": "Serie A", "ESP-LL": "Liga",
              "FRA-L1": "Ligue 1", "other": "les autres championnats"}


def _pct(p: float) -> str:
    return f"{round(100 * p)} %"


def _odds(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def _n(x: float) -> str:
    return str(round(x)) if abs(x - round(x)) < 0.05 else f"{x:.1f}".replace(".", ",")


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'s' if n > 1 else ''}"


def market_name(key: str | None) -> str:
    """Family of a bet, as the owner says it on betPawa."""
    if not key:
        return "Autre"
    if key[0] in "+-":
        return f"{'Plus' if key[0] == '+' else 'Moins'} de {key[1:].replace('.', ',')} buts"
    kind = key.split("_")[0]
    return {"1": "Victoire", "2": "Victoire", "X": "Nul", "1X": "Double chance", "X2": "Double chance",
            "12": "Pas de nul", "1UP": "1UP", "2UP": "2UP", "DC1UP": "DC 1UP", "DC2UP": "DC 2UP",
            "FG": "Premier but", "BTTS": "Les deux marquent" if key.endswith("Y") else "Une équipe ne marque pas",
            }.get(kind, "Autre")


def why_lost(p: float | None) -> str:
    """Was this miss normal for the chance the site gave, or a real surprise?"""
    if p is None:
        return ""
    if p >= 0.75:
        return f"le site le donnait à {_pct(p)}, un des choix les plus sûrs : ce raté est une vraie surprise."
    if p >= 0.6:
        return (f"le site le donnait à {_pct(p)} : ce genre de pari perd environ {10 - round(10 * p)} fois sur 10, "
                "ce raté reste normal.")
    return f"le site le donnait à {_pct(p)} : un pari risqué, qui perd presque une fois sur deux."


def _in(day: str, start: date, end: date) -> bool:
    return start.isoformat() <= day <= end.isoformat()


def _is_mine(m: dict) -> bool:
    if m["competition"].startswith("INT-"):
        return national_followed(m | {"source": "marché" if m.get("market") else "modèle"})
    return m["competition"] in FOLLOWED and (_team_followed(m["home"], m["competition"])
                                             or _team_followed(m["away"], m["competition"]))


def _favourite(probs: list[float], home: str, away: str) -> tuple[str, float]:
    i = max(range(3), key=lambda k: probs[k])
    return (home, "le nul", away)[i], probs[i]


def _sees(name: str, p: float) -> str:
    return f"voyait le nul ({_pct(p)})" if name == "le nul" else f"voyait {name} gagner ({_pct(p)})"


def _tickets_section(week: list[dict], before: list[dict]) -> tuple[list[str], dict]:
    played = [t for d in week for t in d["tickets"]]
    prev = [t for d in before for t in d["tickets"]]
    lines = ["1. TES TICKETS : POURQUOI ILS ONT GAGNÉ OU PERDU"]
    if not played:
        return lines + ["Aucun ticket cette semaine (pas de match de tes équipes, ou pas de calcul ce jour-là).", ""], {}
    won = sum(t["state"] == "gagné" for t in played)
    settled = [t for t in played if t["state"] != "en cours"]
    line = f"{_plural(won, 'ticket')} gagné{'s' if won > 1 else ''} sur {len(played)}"
    if prev:
        pw = sum(t["state"] == "gagné" for t in prev)
        line += f" (la semaine d'avant : {pw} sur {len(prev)})"
    lines.append(line + ".")
    # Expected wins from the site's own chances: shows whether losing most long tickets is normal.
    probs = [math.prod(x["prob"] for x in t["legs"]) for t in settled if all(x.get("prob") for x in t["legs"])]
    if probs and len(probs) == len(settled):
        exp = sum(probs)
        real = sum(t["state"] == "gagné" for t in settled)
        verdict = ("c'est ce qu'annonçaient ses chances" if abs(real - exp) <= max(1.0, 0.5 * exp)
                   else "mieux que ses chances" if real > exp else "moins bien que ses chances")
        lines.append(f"D'après ses propres chances, le site attendait environ {_n(exp)} ticket(s) gagné(s) "
                     f"sur ces {len(settled)} : tu en as {real}, {verdict}.")
        lines.append("Rappel : un ticket de 5 sélections à 60 % chacune ne passe qu'environ 1 fois sur 13. "
                     "Perdre la plupart des longs tickets est normal ; le ticket Court passe le plus souvent.")
    for d in week:
        if not d["tickets"]:
            continue
        lines.append(f"\n{date.fromisoformat(d['date']):%d/%m} :")
        for t in d["tickets"]:
            lines.append(f" • Ticket {t['tag']} · {t['name']} (cote {_odds(t['odds'])}, "
                         f"{len(t['legs'])} matchs) : {_STATE[t['state']]}")
            for x in t["legs"]:
                if x["won"] == 0:
                    lines.append(f"   ❌ {x['match']} {x['score']}, « {x['label']} » : {why_lost(x.get('prob'))}".rstrip())
            if t["state"] == "en cours":
                lines.append(f"   ⏳ En attente : {', '.join(x['match'] for x in t['legs'] if x['won'] is None)}.")
    # Each type of bet: won against what the site expected.
    by: dict[str, list] = {}
    for t in played:
        for x in t["legs"]:
            if x["won"] is not None:
                by.setdefault(market_name(x.get("key")), []).append(x)
    lines.append("\nPar type de pari (toutes tes sélections réglées de la semaine) :")
    stats = {}
    for name, xs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        w = sum(x["won"] for x in xs)
        exp = sum(x["prob"] for x in xs if x.get("prob")) if all(x.get("prob") for x in xs) else None
        stats[name] = (w, len(xs), exp)
        tail = f" ; le site en attendait environ {_n(exp)}" if exp is not None else ""
        lines.append(f" • {name} : {w} gagné{'s' if w > 1 else ''} sur {len(xs)}{tail}.")
    return lines + [""], stats


def _teams_section(week: list[dict], before: list[dict]) -> list[str]:
    mine, prev = [m for m in week if _is_mine(m)], [m for m in before if _is_mine(m)]
    lines = ["2. TES ÉQUIPES : CE QUE LE SITE PRÉVOYAIT, ET POURQUOI IL S'EST TROMPÉ"]
    if not mine:
        return lines + ["Aucun match de tes équipes terminé cette semaine.", ""]
    right = sum(m["model_right"] for m in mine)
    line = f"Le site a trouvé le bon résultat {right} fois sur {len(mine)}"
    if prev:
        line += f" (la semaine d'avant : {sum(m['model_right'] for m in prev)} sur {len(prev)})"
    lines.append(line + ".")
    missed = sorted((m for m in mine if not m["model_right"]), key=lambda m: m["date"])
    surprise = [m for m in missed if m.get("market") and not m["market_right"]]
    alone = [m for m in missed if m.get("market") and m["market_right"]]
    if missed:
        lines.append(f"Sur ses {len(missed)} ratés : {len(surprise)} surprise(s) pour tout le monde (les bookmakers "
                     f"se trompaient aussi) et {len(alone)} erreur(s) du site seul (les bookmakers voyaient juste).")
    for m in missed:
        name, p = _favourite(m["model"], m["home"], m["away"])
        if m.get("market"):
            bname, bp = _favourite(m["market"], m["home"], m["away"])
            other = ("les bookmakers se trompaient aussi" if not m["market_right"]
                     else "les bookmakers, eux, voyaient juste")
            book = f" ; {other} : ils {_sees(bname, bp)}"
        else:
            book = " ; pas de cotes de bookmakers pour comparer"
        lines.append(f" ❌ {m['home']} – {m['away']} {m['score']} : le site {_sees(name, p)}{book}.")
    return lines + [""]


def _books_section(matches: list[dict], today: date) -> list[str]:
    lines = ["3. LE SITE CONTRE LES BOOKMAKERS, SEMAINE APRÈS SEMAINE", "(Tes championnats, matchs avec des cotes.)"]
    tot_s = tot_b = tot_n = 0
    for w in range(3, -1, -1):
        end = today - timedelta(days=7 * w)
        start = end - timedelta(days=6)
        xs = [m for m in matches if m["competition"] in FOLLOWED and m["market_right"] is not None
              and _in(m["date"], start, end)]
        if not xs:
            continue
        s, b = sum(m["model_right"] for m in xs), sum(m["market_right"] for m in xs)
        tot_s, tot_b, tot_n = tot_s + s, tot_b + b, tot_n + len(xs)
        tag = " (cette semaine)" if w == 0 else ""
        lines.append(f" • Du {start:%d/%m} au {end:%d/%m}{tag} : site {s} sur {len(xs)}, bookmakers {b} sur {len(xs)}.")
    if not tot_n:
        return lines + ["Pas assez de matchs terminés avec des cotes.", ""]
    if abs(tot_s - tot_b) <= max(3, tot_n // 15):
        lines.append(f"Sur ces semaines : site {tot_s}, bookmakers {tot_b}, sur {tot_n} matchs. À égalité : le site "
                     "suit les bookmakers, il ne les bat pas. Ton seul avantage possible reste une cote betPawa "
                     "au-dessus de la cote juste.")
    else:
        better = "le site" if tot_s > tot_b else "les bookmakers"
        lines.append(f"Sur ces semaines : site {tot_s}, bookmakers {tot_b}, sur {tot_n} matchs. Avantage {better}, "
                     "mais un mois reste court : il faut plusieurs mois pour conclure.")
    return lines + [""]


def _honest_section(matches: list[dict]) -> list[str]:
    lines = ["4. LES POURCENTAGES DU SITE SONT-ILS HONNÊTES ? (4 dernières semaines, tous les championnats)"]
    groups = ((0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 1.01))
    shown = 0
    for lo, hi in groups:
        xs = [m for m in matches if lo <= max(m["model"]) < hi]
        if len(xs) < 8:
            continue
        p = [max(m["model"]) for m in xs]
        exp, real = sum(p), sum(m["model_right"] for m in xs)
        tol = max(1.5, 1.5 * math.sqrt(sum(q * (1 - q) for q in p)))
        verdict = ("c'est ce qu'il annonçait" if abs(real - exp) <= tol
                   else "mieux qu'annoncé" if real > exp else "moins bien qu'annoncé : le site était trop sûr de lui")
        band = "70 % ou plus" if hi > 1 else f"{round(100 * lo)} à {round(100 * hi)} %"
        lines.append(f" • Favori donné à {band} : il a gagné {real} fois sur {len(xs)}. "
                     f"Le site en annonçait environ {_n(exp)} : {verdict}.")
        shown += 1
    if not shown:
        lines.append("Pas encore assez de matchs pour juger.")
    else:
        lines.append("Si une ligne dit « moins bien qu'annoncé » plusieurs semaines de suite, baisse ta confiance "
                     "dans ces pourcentages.")
    return lines + [""]


def _model_section(today: date, retrained: bool, scenario: dict | None) -> list[str]:
    lines = ["5. CE QUI A CHANGÉ DANS LE MODÈLE CETTE SEMAINE"]
    lines.append(" • Le modèle a été réentraîné avec les résultats de la semaine." if retrained
                 else " • Pas de réentraînement cette semaine : le modèle est le même.")
    if scenario and scenario.get("check"):
        when = str(scenario.get("learnt_at", ""))[:10]
        leagues = scenario["check"].get("leagues", {})
        on = [LEAGUES_FR.get(k, k) for k in scenario.get("active_leagues", []) if k in leagues]
        off = [LEAGUES_FR.get(k, k) for k, v in leagues.items() if v.get("gain", 0) <= 0]
        fresh = when and (today - datetime.fromisoformat(when).date()).days <= 7
        head = ("Contrôle des ajustements par situations (forme trompeuse, gros favoris), refait cette semaine"
                if fresh else f"Ajustements par situations, contrôlés le {when[8:10]}/{when[5:7]}")
        lines.append(f" • {head} : actifs en {', '.join(on) or 'aucun championnat'}.")
        if off:
            lines.append(f"   Coupés en {', '.join(off)} : sur les 5 dernières saisons, ils n'y faisaient pas mieux "
                         "que les bookmakers. Là, le site suit les bookmakers sans rien changer.")
    news = news_between(today - timedelta(days=6), today)
    if news:
        lines.append(" • Changements décidés avec toi :")
        lines += [f"   - {n}" for n in news]
    return lines + [""]


def plain_week(tickets: list[dict], matches: list[dict], today: date, retrained: bool = False,
               scenario: dict | None = None) -> tuple[str, str]:
    """(subject, body). `tickets`: bilan.ticket_results over 14 days; `matches`:
    bilan.forecast_results over 28 days; `scenario`: the scenario weights file, if any."""
    start = today - timedelta(days=6)
    week_t = [d for d in tickets if _in(d["date"], start, today)]
    prev_t = [d for d in tickets if _in(d["date"], start - timedelta(days=7), start - timedelta(days=1))]
    week_m = [m for m in matches if _in(m["date"], start, today)]
    prev_m = [m for m in matches if _in(m["date"], start - timedelta(days=7), start - timedelta(days=1))]

    lines = [f"Ta semaine en clair — du {start:%d/%m} au {today:%d/%m}", ""]
    tk, stats = _tickets_section(week_t, prev_t)
    lines += tk + _teams_section(week_m, prev_m) + _books_section(matches, today) + _honest_section(matches) \
        + _model_section(today, retrained, scenario)

    lines.append("6. À RETENIR")
    weak = [(n, w, k, e) for n, (w, k, e) in stats.items() if e is not None and k >= 4 and w < e - 1.5]
    for n, w, k, e in weak:
        lines.append(f" • {n} : {w} sur {k} cette semaine, en dessous des {_n(e)} attendus. Une semaine ne suffit "
                     "pas à conclure ; si ça se répète, on le retire des tickets comme le DC 2UP.")
    lines.append(" • Un pari ne vaut le coup que si betPawa paie plus que la « cote juste » du site.")
    lines.append(" • Moins de matchs dans un ticket = moins de marge perdue : préfère le ticket Court.")
    lines += ["", f"Tout le détail sur le site, onglets Hier et Bilan : {SITE}",
              "(La pièce jointe contient les détails techniques : tu peux l'ignorer.)"]

    played = [t for d in week_t for t in d["tickets"]]
    won = sum(t["state"] == "gagné" for t in played)
    subject = f"Ta semaine — {won} ticket(s) gagné(s) sur {len(played)}, et pourquoi" if played else "Ta semaine en clair"
    return subject, fr_names("\n".join(lines))
