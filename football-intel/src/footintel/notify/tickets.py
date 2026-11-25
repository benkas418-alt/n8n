"""Tickets du jour (D69) by e-mail, every morning after the site export (D71).

Plain text, readable on a phone. Same SMTP settings as the weekly report.
"""

from datetime import UTC, date, datetime

from footintel.analysis.tickets import LOCAL_OFFSET
from footintel.names_fr import fr_names
from footintel.notify.briefs import explain_match

SITE = "https://benkassiyfootball.vercel.app"
DAYS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def _hour(kickoff) -> str:
    if not kickoff:
        return "--:--"
    k = kickoff if isinstance(kickoff, datetime) else datetime.fromisoformat(str(kickoff))
    return (k + LOCAL_OFFSET).strftime("%H:%M")


def _day(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{DAYS_FR[d.weekday()]} {d.day:02d}/{d.month:02d}"


def tickets_text(data: dict, today: date, briefs: dict | None = None) -> tuple[str, str]:
    """Subject and body for the next match day (today first). `briefs`: notify.briefs.match_briefs."""
    days = data.get("days") or []
    if not days:
        return ("Tickets du jour — aucun match", "Aucun match de vos équipes dans les deux prochains jours.\n")
    lines = []
    day = days[0]
    if not day["tickets"] and len(days) > 1 and days[1]["tickets"]:
        # Nothing for the owner's teams on the first day: say so, then show the next one.
        lines += [f"{_day(day['date']).capitalize()} : {_few(day.get('n_followed', 0))}, pas de ticket.", ""]
        day = days[1]
    ahead = (date.fromisoformat(day["date"]) - today).days
    when = {0: " (aujourd'hui)", 1: " (demain)"}.get(ahead, "")
    lines += [f"Tickets du {_day(day['date'])}{when}, heure de Lubumbashi.",
              "Uniquement vos équipes : toute la Premier League et la Bundesliga, Inter, Milan, Como, Bologne,",
              "Lazio, Barcelone, Real Madrid, Atlético, Betis, Villarreal et le PSG, dans toutes les compétitions.",
              "Sélections : tous les matchs avec des cotes de bookmakers, et tous ceux de vos 25 sélections.", ""]
    if not day["tickets"]:
        lines.append(f"{_few(day.get('n_followed', 0)).capitalize()} : pas assez pour un ticket à 10 ou plus.")
    missing = day.get("missing") or []
    if missing and day["tickets"]:
        # One line for all the tickets that could not be built (D85).
        tags = [m["tag"] for m in missing]
        names = tags[0] if len(tags) == 1 else ", ".join(tags[:-1]) + " et " + tags[-1]
        plural = len(tags) > 1
        lines += [(f"{'Tickets' if plural else 'Ticket'} {names} non construit{'s' if plural else ''} : "
                   f"il faut au moins {min(m['needs'] for m in missing)} matchs de vos équipes, "
                   f"il y en a {day.get('n_followed', 0)}."), ""]
    for t in day["tickets"]:
        chance = f"passe environ 1 fois sur {round(1 / t['prob'])}" if t["prob"] > 0 else "—"
        lines.append(f"TICKET {t['tag']} — {t['name']} ({len(t['legs'])} sélections)")
        lines.append(f"Cote totale {_odds(t['odds'])} · {chance}")
        for x in t["legs"]:
            mark = "relevée" if x.get("known") else "estimée"
            lines.append(f"  {_hour(x.get('kickoff_utc'))}  {x['match']}")
            lines.append(f"         {x['label']} · cote betPawa {_odds(x['price'])} ({mark}) · cote juste "
                         f"{_odds(x['fair'])} · {round(100 * x['prob'])} % de chances")
        lines.append("")
    # D97: why each match was picked: how the teams play, then why this bet. The scenarios that
    # moved a probability (D72) are part of each match's block.
    picks: dict = {}
    for t in day["tickets"]:
        for x in t["legs"]:
            if x.get("match_id") is None:
                continue
            p = picks.setdefault((x["match_id"], x["key"]), {"key": x["key"], "prob": x["prob"], "tags": []})
            p["tags"].append(t["tag"])
    rows = [r for r in day.get("matches", []) if any(mid == r["match_id"] for mid, _ in picks)]
    if rows:
        lines += ["POURQUOI CES CHOIX, MATCH PAR MATCH",
                  "Le style vient des matchs de la saison, comparés à la moyenne de la compétition.", ""]
        for r in sorted(rows, key=lambda r: str(r.get("kickoff_utc") or "")):
            mine = [p for (mid, _), p in picks.items() if mid == r["match_id"]]
            lines += explain_match(r, mine, (briefs or {}).get(r["match_id"]))
            lines.append("")
    lines += ["Une sélection n'a de valeur que si la cote betPawa dépasse sa cote juste.",
              "Vérifiez chaque cote sur betPawa avant de jouer : les cotes « estimées » viennent de la marge",
              "mesurée, pas de betPawa. " + data.get("note", ""), "",
              f"Toutes les alternatives : {SITE} (onglet Tickets du jour)."]
    n = len(day["tickets"])
    subject = f"Tickets du {_day(day['date'])} — {n} ticket{'s' if n > 1 else ''}"
    # National teams in French, as on the site (D85).
    return fr_names(subject), fr_names("\n".join(lines) + "\n")


def _odds(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def _few(n: int) -> str:
    return "aucun match de vos équipes" if n == 0 else f"{n} match{'s' if n > 1 else ''} de vos équipes"


def local_today() -> date:
    return (datetime.now(UTC) + LOCAL_OFFSET).date()

