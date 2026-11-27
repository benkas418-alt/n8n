"""Side models next to the active one (D105): their 1X2 on a match, and their record.

The record counts only matches played with a pre-match prediction of BOTH the active model
and the side model, so the two are compared on the same matches. A pick is the most likely
outcome; a "good result" is a pick that happened.
"""

import numpy as np

from footintel.models.zoo import SIDE_MODELS

PRE_MATCH = "COALESCE(m.kickoff_utc, m.kickoff_date::timestamptz)"
MIN_MATCHES_NOTE = 100  # below this, the record is a hint, not a proof

RECORD_SQL = f"""
WITH s AS (
  SELECT DISTINCT ON (sp.match_id, mv.name) sp.match_id, mv.name, sp.p_home, sp.p_draw, sp.p_away
  FROM side_predictions sp JOIN model_versions mv ON mv.id = sp.model_version_id
  JOIN matches m ON m.id = sp.match_id
  WHERE sp.predicted_at < {PRE_MATCH}
  ORDER BY sp.match_id, mv.name, sp.predicted_at DESC),
a AS (
  SELECT DISTINCT ON (p.match_id) p.match_id, p.p_home, p.p_draw, p.p_away,
         (p.feature_snapshot ->> 'mkt_p_home')::float AS mh, (p.feature_snapshot ->> 'mkt_p_draw')::float AS md,
         (p.feature_snapshot ->> 'mkt_p_away')::float AS ma
  FROM predictions p JOIN matches m ON m.id = p.match_id
  WHERE p.predicted_at < {PRE_MATCH} AND p.match_id IN (SELECT match_id FROM s)
  ORDER BY p.match_id, p.predicted_at DESC)
SELECT s.name, s.p_home AS sh, s.p_draw AS sd, s.p_away AS sa, a.p_home AS ah, a.p_draw AS ad,
       a.p_away AS aa, a.mh, a.md, a.ma, o.home_goals, o.away_goals
FROM s JOIN a ON a.match_id = s.match_id JOIN match_outcomes o ON o.match_id = s.match_id
WHERE o.home_goals IS NOT NULL AND o.away_goals IS NOT NULL"""


def _outcome(hg: int, ag: int) -> int:
    return 0 if hg > ag else 1 if hg == ag else 2


def _hit(probs, outcome: int) -> bool | None:
    if any(p is None or (isinstance(p, float) and np.isnan(p)) for p in probs):
        return None
    return int(np.argmax(probs)) == outcome


def record(rows: list[dict]) -> list[dict]:
    """Good results of each side model, the active model and the market, on the same matches."""
    out = []
    for name, label in SIDE_MODELS.items():
        mine = [r for r in rows if r["name"] == name]
        res = {"name": name, "label": label, "matches": len(mine), "side": 0, "active": 0,
               "market": 0, "market_matches": 0, "agree": 0}
        for r in mine:
            o = _outcome(r["home_goals"], r["away_goals"])
            side, active = (r["sh"], r["sd"], r["sa"]), (r["ah"], r["ad"], r["aa"])
            res["side"] += bool(_hit(side, o))
            res["active"] += bool(_hit(active, o))
            res["agree"] += int(np.argmax(side) == np.argmax(active))
            mk = _hit((r["mh"], r["md"], r["ma"]), o)
            if mk is not None:
                res["market_matches"] += 1
                res["market"] += mk
        res["note"] = ("" if res["matches"] >= MIN_MATCHES_NOTE else
                       f"indicatif seulement ({res['matches']} matchs)" if res["matches"] >= 20 else
                       f"trop peu de matchs joués ({res['matches']}) : aucune conclusion possible")
        out.append(res)
    return out
