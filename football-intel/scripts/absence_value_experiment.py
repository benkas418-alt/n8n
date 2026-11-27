"""D117: does the value of the players missing from the starting XI add to the market?

Run from football-intel/, with the database of a daily cycle:
    curl -LO https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/transfermarkt-datasets.duckdb
    python scripts/absence_value_experiment.py transfermarkt-datasets.duckdb

D78 counted the missing regulars. This test weights each player by his Transfermarkt market
value, taken from the last estimate dated before the match (no later information).
For each team and match:
- core: the 11 players who started most often in the team's 10 previous games (all
  competitions);
- xi_ratio: log of (value of today's XI / value of the core XI). Below 0 = a weaker XI;
- out_share: share of the core XI's value that does not start.
The line-ups are known about one hour before kick-off.

Rules fixed before the run:
- Against the closing price (taken after the line-ups): the market misses this information
  only if the season-by-season gain has a 95 % interval entirely above 0.
- Against the Friday price (taken before the line-ups): an interval above 0 means that the
  information is real but arrives late. It can then only help against a bookmaker that moves
  late (next step: betPawa prices with their time).
- Hermès changes only under rule D9, in a separate test.
"""

import sys

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
from rotation_experiment import TM_LEAGUES, link, our_matches, walk_forward

from footintel.analysis.demargin import fair_probs
from footintel.db.session import get_engine


def tables(path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    c = duckdb.connect(path, read_only=True)
    games = c.sql("""SELECT CAST(game_id AS INTEGER) game_id, competition_id, date,
                            home_club_id, away_club_id, home_club_goals hg, away_club_goals ag
                     FROM games""").df()
    xi = c.sql("""SELECT game_id, club_id, list(player_id) players FROM game_lineups
                  WHERE type = 'starting_lineup' GROUP BY 1, 2""").df()
    vals = c.sql("""SELECT player_id, date, market_value_in_eur v FROM player_valuations
                    WHERE market_value_in_eur > 0""").df()
    return games, xi, vals


def absences(games: pd.DataFrame, xi: pd.DataFrame, vals: pd.DataFrame) -> pd.DataFrame:
    clubs = set(games.loc[games.competition_id.isin(TM_LEAGUES), "home_club_id"])
    xi = xi[xi.club_id.isin(clubs)].merge(games[["game_id", "date"]], on="game_id")
    xi = xi[xi.players.apply(len) >= 10].sort_values(["club_id", "date"])
    xi["date"] = pd.to_datetime(xi.date)
    rows, pairs = [], []
    for club, g in xi.groupby("club_id"):
        sets = [frozenset(p) for p in g.players]
        for i, (gid, day) in enumerate(zip(g.game_id, g.date, strict=True)):
            if i < 10:
                continue
            counts = pd.Series([p for s in sets[i - 10:i] for p in s]).value_counts()
            core = frozenset(counts.index[:11])
            rows.append((club, gid, day, core, sets[i]))
            pairs.extend((p, day) for p in core | sets[i])
    pv = pd.DataFrame(pairs, columns=["player_id", "date"]).drop_duplicates()
    pv = pv.astype({"player_id": "int64", "date": "datetime64[ns]"})
    vals = vals.astype({"player_id": "int64", "date": "datetime64[ns]"}).sort_values("date")
    pv = pd.merge_asof(pv.sort_values("date"), vals, on="date", by="player_id",
                       allow_exact_matches=False)
    value = {(p, d): v for p, d, v in zip(pv.player_id, pv.date, pv.v, strict=True)
             if not np.isnan(v)}
    out = []
    for club, gid, day, core, today in rows:
        vc = [value.get((p, day)) for p in core]
        vt = [value.get((p, day)) for p in today]
        if sum(v is None for v in vc) > 2 or sum(v is None for v in vt) > 2:
            continue  # too many players without an earlier estimate
        core_v = sum(v for v in vc if v)
        today_v = sum(v for v in vt if v)
        missing_v = sum(value.get((p, day)) or 0 for p in core - today)
        out.append({"club_id": club, "game_id": gid, "xi_ratio": np.log(today_v / core_v),
                    "out_share": missing_v / core_v})
    return pd.DataFrame(out)


def power_probs(d: pd.DataFrame) -> pd.DataFrame:
    for lab in ("pre_closing", "closing"):
        p = [fair_probs([h, dr, a]) if not np.isnan(h) else None
             for h, dr, a in zip(d[f"{lab}_H"], d[f"{lab}_D"], d[f"{lab}_A"], strict=True)]
        for k, s in enumerate("hda"):
            d[f"{lab}_p{s}"] = [x[k] if x else np.nan for x in p]
    return d


def bands(d: pd.DataFrame, label: str) -> None:
    """Points above the market's expectation by strength of today's XI, both sides pooled."""
    rows = []
    for side, o in (("home", "away"), ("away", "home")):
        pts = np.where(d[f"{side}_goals"] > d[f"{o}_goals"], 3,
                       np.where(d.home_goals == d.away_goals, 1, 0))
        exp = 3 * d[f"{label}_p{side[0]}"] + d[f"{label}_pd"]
        rows.append(pd.DataFrame({"r": d[f"xi_ratio_{side}"], "diff": pts - exp}))
    r = pd.concat(rows).dropna()
    r["band"] = pd.cut(r.r, [-10, -0.5, -0.25, -0.1, 0.1, 10],
                       labels=["onze à -40 % ou moins", "-22 à -40 %", "-10 à -22 %",
                               "habituel (±10 %)", "plus fort"])
    print(r.groupby("band", observed=True)["diff"].agg(["count", "mean"]).round(3))


def main(path: str) -> None:
    games, xi, vals = tables(path)
    ab = absences(games, xi, vals)
    linked = link(games, our_matches(get_engine()))
    for side in ("home", "away"):
        part = ab.rename(columns={"club_id": f"{side}_club_id", "xi_ratio": f"xi_ratio_{side}",
                                  "out_share": f"out_share_{side}"})
        linked = linked.merge(part, on=["game_id", f"{side}_club_id"], how="left")
    d = linked.dropna(subset=["xi_ratio_home", "xi_ratio_away"]).copy()
    d = power_probs(d)
    d["y"] = np.select([d.home_goals > d.away_goals, d.home_goals == d.away_goals], [0, 1], 2)
    d["ratio_diff"] = d.xi_ratio_home - d.xi_ratio_away
    d["share_diff"] = d.out_share_home - d.out_share_away
    print(f"Team-matches with values: {len(ab)}; linked league matches: {len(d)}")
    for label in ("pre_closing", "closing"):
        dl = d.dropna(subset=[f"{label}_ph"])
        print(f"\nLeague matches with {label} prices: {len(dl)} "
              f"({dl.kickoff_date.min():%Y-%m} to {dl.kickoff_date.max():%Y-%m})")
        print(f"\n== Points above the market ({label}) by value of today's XI")
        bands(dl, label)
        print(f"\n== Season by season, against {label} prices")
        walk_forward(dl, ["ratio_diff", "share_diff"], label)


if __name__ == "__main__":
    main(sys.argv[1])
