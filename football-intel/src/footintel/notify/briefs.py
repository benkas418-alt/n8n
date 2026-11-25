"""Why each match of the tickets was picked, in plain French (D97).

For each match of the day's tickets: how the two teams play (style measured this season, last
results), what the site expects from the meeting, and why the model chose this bet rather than
the plain result. `match_briefs` reads the database; `explain_match` only formats, so it is
tested without one.
"""

import logging

from sqlalchemy import Engine, text

log = logging.getLogger(__name__)

_MATCH_SQL = """SELECT m.id, m.kickoff_date, c.code AS competition, m.home_team_id, m.away_team_id,
                       th.name AS home, ta.name AS away
                FROM matches m JOIN competitions c ON c.id = m.competition_id
                JOIN teams th ON th.id = m.home_team_id JOIN teams ta ON ta.id = m.away_team_id
                WHERE m.id = :m"""
_PRED_SQL = """SELECT exp_home_goals, exp_away_goals FROM predictions WHERE match_id = :m
               ORDER BY predicted_at DESC LIMIT 1"""


def match_briefs(engine: Engine, match_ids: list[int]) -> dict[int, dict]:
    """Style, form, key facts and match-up sentences of each match. A match that fails is
    left out: the e-mail must go out even if one profile cannot be read."""
    from footintel.analysis.matchup import match_insights

    out: dict[int, dict] = {}
    for mid in match_ids:
        try:
            with engine.connect() as conn:
                m = conn.execute(text(_MATCH_SQL), {"m": mid}).mappings().first()
                pred = conn.execute(text(_PRED_SQL), {"m": mid}).mappings().first()
            if not m:
                continue
            ins = match_insights(engine, dict(m), dict(pred) if pred else None)
            out[mid] = {"teams": {s: {"name": ins["teams"][s]["name"],
                                      "labels": [x["text"] for x in ins["teams"][s]["profile"]["labels"]],
                                      "figures": ins["teams"][s]["profile"]["figures"],
                                      "form": [f["result"] for f in ins["teams"][s]["form_all"]][:5]}
                                  for s in ("home", "away")},
                        "matchup": ins.get("matchup", []), "facts": ins.get("key_facts", [])}
        except Exception as e:  # noqa: BLE001 - one bad profile must not stop the e-mail
            log.warning("brief for match %s failed: %s", mid, e)
    return out


def _form(results: list[str]) -> str:
    if not results:
        return ""
    w, d, lost = results.count("V"), results.count("N"), results.count("D")
    parts = [f"{w} victoire{'s' if w > 1 else ''}" if w else "", f"{d} nul{'s' if d > 1 else ''}" if d else "",
             f"{lost} défaite{'s' if lost > 1 else ''}" if lost else ""]
    return f"{', '.join(p for p in parts if p)} sur ses {len(results)} derniers matchs"


def _num(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def team_line(t: dict) -> str:
    """'Arsenal : aime avoir le ballon, clinique devant le but ; 2,7 buts marqués et 0,8 encaissé
    par match ; 4 victoires, 1 nul sur ses 5 derniers matchs.'"""
    bits = []
    f = t.get("figures") or {}
    style = [x[0].lower() + x[1:] for x in t.get("labels", [])]
    if f.get("formation") and f.get("formation_share", 0) >= 0.5:
        style.insert(0, f"joue en {f['formation']}")
    if style:
        bits.append(", ".join(style))
    if f.get("goals_for") is not None and f.get("goals_against") is not None:
        gf, ga = f["goals_for"], f["goals_against"]
        # French: "1,4 but marqué", "2,7 buts marqués".
        bits.append(f"{_num(gf)} but{'s' if gf >= 2 else ''} marqué{'s' if gf >= 2 else ''} et "
                    f"{_num(ga)} encaissé{'s' if ga >= 2 else ''} par match")
    if t.get("form"):
        bits.append(_form(t["form"]))
    return f"{t['name']} : {' ; '.join(bits)}." if bits else ""


def _side(key: str, home: str, away: str) -> str | None:
    tail = key.split("_")[-1]
    return home if tail == "1" else away if tail == "2" else None


def why_choice(key: str, prob: float, row: dict) -> str:
    """Why this bet rather than the plain result, from the match's own probabilities."""
    home, away = row["match"].split(" – ", 1) if " – " in row["match"] else (row["match"], "")
    p1, p2 = row.get("p1"), row.get("p2")
    px = 1 - p1 - p2 if p1 is not None and p2 is not None else None
    team = _side(key, home, away)
    win = (p1 if team == home else p2) if team and p1 is not None else None
    pc = f"{round(100 * prob)} %"
    kind = key.split("_")[0]
    if key in ("1", "2"):
        return f"Victoire simple de {team or home} : {pc}. Le choix le mieux payé quand le favori est net."
    if key in ("1X", "X2"):
        t = home if key == "1X" else away
        w = p1 if key == "1X" else p2
        extra = f" La victoire seule n'a que {round(100 * w)} % : le nul couvert fait la différence." if w is not None else ""
        return f"{t} ne perd pas : {pc}.{extra}"
    if key == "12":
        nul = f" (le nul n'a que {round(100 * px)} %)" if px is not None else ""
        return f"Le site attend un vainqueur{nul} : {pc}, sans avoir à choisir lequel."
    if kind in ("1UP", "2UP") and team:
        n = 1 if kind == "1UP" else 2
        cmp = f", contre {round(100 * win)} % pour la victoire simple" if win is not None else ""
        return (f"{kind} {team} gagne si {team} gagne, mais aussi si {team} mène de {n} but{'s' if n > 1 else ''} "
                f"à un moment puis se fait rejoindre : {pc}{cmp}. Plus sûr, pour une cote proche.")
    if kind in ("DC1UP", "DC2UP"):
        n = 1 if kind == "DC1UP" else 2
        what = {"1X": f"{home} ou nul", "X2": f"{away} ou nul", "12": f"{home} ou {away}"}[key.split("_")[1]]
        return (f"Double chance « {what} », payée aussi dès qu'une équipe couverte mène de {n} but{'s' if n > 1 else ''} : "
                f"{pc}. Le pari le plus sûr de ce match, à petite cote.")
    if kind == "FG" and team:
        return f"{team} marque le premier but : {pc}. Il ne faut pas que {team} gagne, juste qu'il ouvre le score."
    if key == "BTTS_Y":
        return f"Les deux équipes marquent : {pc}. Les deux attaques marquent et les deux défenses encaissent."
    if key == "BTTS_N":
        return f"Une des deux équipes ne marque pas : {pc}. Une défense solide ou une attaque faible."
    if key[0] in "+-":
        line = key[1:].replace(".", ",")
        n = int(float(key[1:]) + 0.5)
        if key[0] == "+":
            return f"Plus de {line} buts : {pc}. Il faut au moins {n} buts dans le match, peu importe qui marque."
        ok = f"un {n - 1}-0 ou un {n - 2}-1" if n > 2 else "un 1-0 ou un 0-0"
        return f"Moins de {line} buts : {pc}. Il passe tant qu'il n'y a pas {n} buts ou plus : {ok} suffit."
    return f"{pc} de chances."


def explain_match(row: dict, picks: list[dict], brief: dict | None) -> list[str]:
    """Lines of one match: teams, the meeting, each pick of the tickets and where the figure comes from."""
    out = [f"• {row['match']}"]
    if brief:
        out += [f"   {line}" for line in (team_line(brief["teams"]["home"]), team_line(brief["teams"]["away"])) if line]
        meet = [s for s in brief.get("matchup", []) if not s.startswith(("Premier but :", "Ouverture du score",
                                                                          "Cette saison, quand"))][:1]
        out += [f"   Le match : {s}" for s in meet] + [f"   À noter : {s}" for s in brief.get("facts", [])[:1]]
    for p in picks:
        out.append(f"   Le choix (ticket{'s' if len(p['tags']) > 1 else ''} {', '.join(p['tags'])}) : "
                   f"{why_choice(p['key'], p['prob'], row)}")
    src = ("chances tirées des cotes des bookmakers, leur marge retirée" if row.get("source") == "marché"
           else "chances du modèle seul, sans cotes de bookmakers pour vérifier : moins sûr")
    out.append(f"   D'où vient le chiffre : {src}.")
    out += [f"   Ajustement : {n['text']}" for n in row.get("scenarios", [])]
    return out
