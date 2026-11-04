"""Tickets du jour (D69) by e-mail, every morning after the site export (D71).

Plain text, readable on a phone. Same SMTP settings as the weekly report.
"""

from datetime import UTC, date, datetime

from footintel.analysis.tickets import LOCAL_OFFSET

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


def tickets_text(data: dict, today: date) -> tuple[str, str]:
    """Subject and body for the next match day (today first)."""
    days = data.get("days") or []
    if not days:
        return ("Tickets du jour — aucun match", "Aucun match de vos équipes dans les deux prochains jours.\n")
    lines = []
    day = days[0]
    if not day["tickets"] and len(days) > 1 and days[1]["tickets"]:
        # Nothing for the owner's teams on the first day: say so, then show the next one.
        lines += [f"{_day(day['date']).capitalize()} : {_few(day.get('n_followed', 0))}, pas de ticket.", ""]
        day = days[1]
    when = "aujourd'hui" if day["date"] == today.isoformat() else _day(day["date"])
    lines += [f"Tickets du {_day(day['date'])} ({when}), heure de Lubumbashi.",
              "Uniquement vos équipes : toute la Premier League et la Bundesliga, Inter, Milan, Como, Bologne,",
              "Lazio, Barcelone, Real Madrid, Atlético, Betis, Villarreal et le PSG, dans toutes les compétitions.", ""]
    if not day["tickets"]:
        lines.append(f"{_few(day.get('n_followed', 0)).capitalize()} : pas assez pour un ticket à 10 ou plus.")
    for m in day.get("missing", []):
        if day["tickets"]:
            lines.append(f"Pas de ticket {m['tag']} ({m['name']}) : il faut au moins {m['needs']} matchs de vos "
                         f"équipes, il y en a {day.get('n_followed', 0)}.")
    if day.get("missing") and day["tickets"]:
        lines.append("")
    for t in day["tickets"]:
        chance = f"1 chance sur {round(1 / t['prob'])}" if t["prob"] > 0 else "—"
        lines.append(f"TICKET {t['tag']} — {t['name']} ({len(t['legs'])} sélections)")
        lines.append(f"Cote totale {t['odds']:.2f} · {chance} · espérance avec bonus {t['ev']:+.1%}")
        for x in t["legs"]:
            mark = "relevée" if x.get("known") else "estimée"
            lines.append(f"  {_hour(x.get('kickoff_utc'))}  {x['match']}")
            lines.append(f"         {x['label']} @ {x['price']:.2f} ({mark}) · juste {x['fair']:.2f}"
                         f" · proba {x['prob']:.0%}")
        lines.append("")
    # D72: the scenarios that moved a probability, in plain words.
    in_tickets = {x["match_id"] for t in day["tickets"] for x in t["legs"] if "match_id" in x}
    seen = [m for m in day.get("matches", []) if m.get("scenarios") and m["match_id"] in in_tickets]
    if seen:
        lines += ["CE QUE LA MACHINE A REMARQUÉ", "Situations déjà vues souvent par le passé, qui ont changé le pronostic :"]
        for m in seen:
            lines.append(f"- {m['match']}")
            lines += [f"    {n['text']}" for n in m["scenarios"]]
        lines.append("")
    lines += ["Une sélection n'a de valeur que si la cote betPawa dépasse sa cote juste.",
              "Vérifiez chaque cote sur betPawa avant de jouer : les cotes « estimées » viennent de la marge",
              "mesurée, pas de betPawa. " + data.get("note", ""), "",
              f"Toutes les alternatives : {SITE} (onglet Tickets du jour)."]
    n = len(day["tickets"])
    subject = f"Tickets du {_day(day['date'])} — {n} ticket{'s' if n > 1 else ''}"
    return subject, "\n".join(lines) + "\n"


def _few(n: int) -> str:
    return "aucun match de vos équipes" if n == 0 else f"{n} match{'s' if n > 1 else ''} de vos équipes"


def local_today() -> date:
    return (datetime.now(UTC) + LOCAL_OFFSET).date()

