"""Unit tests on pure functions. All inputs are synthetic."""

import math
from datetime import UTC, datetime

import numpy as np
import pandas as pd
import pytest

from footintel.connectors.football_data_uk import external_id, parse_csv, season_code
from footintel.evaluation import metrics as M
from footintel.features import elo
from footintel.features.builder import build_features, market_probabilities
from footintel.logging_setup import mask_secrets
from footintel.models.base import markets_from_lambdas

HEADER_NEW = "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HS,AS,HST,AST,AvgH,AvgD,AvgA,AvgCH,AvgCD,AvgCA,B365H,B365D,B365A,Avg>2.5,Avg<2.5"
HEADER_OLD = "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST,BbAvH,BbAvD,BbAvA,B365H,B365D,B365A"


def test_parse_recent_season_row():
    text = HEADER_NEW + "\nE0,16/08/2024,20:00,Synthetic FC A,Synthetic FC B,2,1,H,1,0,14,10,5,2,1.6,4.2,5.25,1.7,4.1,5.0,1.62,4.3,5.2,1.9,1.95\n"
    [rec] = parse_csv(text, season_start_year=2024)
    assert rec.competition_code == "ENG-PL"
    assert rec.outcome.home_goals == 2 and rec.outcome.result == "H"
    assert rec.home_stats.shots == 14 and rec.away_stats.shots_on_target == 2
    # 20:00 in London in August is 19:00 UTC (BST).
    assert rec.kickoff_utc == datetime(2024, 8, 16, 19, 0, tzinfo=UTC)
    prices = {(o.bookmaker, o.snapshot_label, o.selection): o.price for o in rec.odds}
    assert prices[("market_avg", "pre_closing", "H")] == 1.6
    assert prices[("market_avg", "closing", "H")] == 1.7
    assert prices[("market_avg", "pre_closing", "over")] == 1.9
    assert rec.external_id == external_id("E0", 2024, "Synthetic FC A", "Synthetic FC B")


def test_parse_old_format_uses_betbrain_average_and_no_time():
    text = HEADER_OLD + "\nSP1,27/08/05,Synthetic FC A,Synthetic FC B,0,0,D,9,8,3,4,2.1,3.2,3.4,2.0,3.25,3.5\n"
    [rec] = parse_csv(text, season_start_year=2005)
    assert rec.kickoff_utc is None and rec.kickoff_date.year == 2005
    prices = {(o.bookmaker, o.selection): o.price for o in rec.odds if o.snapshot_label == "pre_closing"}
    assert prices[("market_avg", "H")] == 2.1


def test_parse_flags_inconsistent_rows_and_skips_unknown_divisions():
    text = HEADER_OLD + (
        "\nE0,01/01/20,Synthetic FC A,Synthetic FC B,2,0,A,9,8,3,4,1.0,3.2,3.4,2.0,3.25,3.5"
        "\nXX9,01/01/20,Synthetic FC C,Synthetic FC D,1,0,H,,,,,,,,,,\n"
    )
    [rec] = parse_csv(text, season_start_year=2019)
    codes = {c for c, _ in rec.issues}
    assert {"result_mismatch", "bad_odds"} <= codes
    assert rec.outcome.result == "H"  # recomputed from the score, not from FTR


def test_season_code():
    assert season_code(2024) == "2425" and season_code(2099) == "9900"


def test_elo_is_zero_sum_and_rewards_upsets_more():
    p = elo.EloParams()
    h, a = elo.update(1500, 1500, 1, 0, p)
    assert math.isclose(h + a, 3000)
    upset_gain = elo.update(1300, 1700, 1, 0, p)[0] - 1300
    expected_gain = elo.update(1700, 1300, 1, 0, p)[0] - 1700
    assert upset_gain > expected_gain > 0
    assert elo.goal_multiplier(4) > elo.goal_multiplier(2) > elo.goal_multiplier(1)


def test_market_probabilities_remove_margin():
    mp = market_probabilities(2.0, 3.4, 3.8)
    total = mp["mkt_p_home"] + mp["mkt_p_draw"] + mp["mkt_p_away"]
    assert math.isclose(total, 1.0) and mp["mkt_overround"] > 1.0
    assert all(np.isnan(v) for v in market_probabilities(np.nan, 3.4, 3.8).values())


def _toy_matches():
    rows = [
        # match_id, date, season, home, away, hg, ag
        (1, "2020-08-01", 2020, 1, 2, 2, 0),
        (2, "2020-08-01", 2020, 3, 4, 0, 0),
        (3, "2020-08-08", 2020, 2, 3, 1, 1),
        (4, "2020-08-08", 2020, 4, 1, 0, 3),
        (5, "2020-08-15", 2020, 1, 3, np.nan, np.nan),
    ]
    df = pd.DataFrame(rows, columns=["match_id", "kickoff_date", "season", "home_team_id",
                                     "away_team_id", "home_goals", "away_goals"])
    for c in ("home_shots", "away_shots", "home_sot", "away_sot", "odds_h", "odds_d", "odds_a"):
        df[c] = np.nan
    return df


def test_features_use_only_previous_days():
    f = build_features(_toy_matches()).set_index("match_id")
    assert f.loc[1, "n_prior_h"] == 0 and np.isnan(f.loc[1, "form5_ppg_h"])
    # Match 3 (day 2): team 2 lost its only previous match, team 3 drew.
    assert f.loc[3, "form5_ppg_h"] == 0 and f.loc[3, "form5_ppg_a"] == 1
    assert f.loc[3, "rest_days_h"] == 7
    # Match 5: team 1 has 2 wins, team 3 has one draw at home and one away.
    assert f.loc[5, "form5_ppg_h"] == 3 and f.loc[5, "n_prior_a"] == 2


def test_features_ignore_same_day_and_future_results():
    base = build_features(_toy_matches()).set_index("match_id")
    changed = _toy_matches()
    # Change a result on the same day as match 3 and every later result.
    changed.loc[changed["match_id"] == 4, ["home_goals", "away_goals"]] = [5, 0]
    changed.loc[changed["match_id"] == 5, ["home_goals", "away_goals"]] = [0, 4]
    after = build_features(changed).set_index("match_id")
    feature_cols = [c for c in base.columns if c.endswith(("_h", "_a")) or c.startswith("elo")]
    pd.testing.assert_series_equal(base.loc[3, feature_cols], after.loc[3, feature_cols])
    pd.testing.assert_series_equal(base.loc[4, feature_cols], after.loc[4, feature_cols])


def test_scoring_rules_known_values():
    probs = np.full((4, 3), 1 / 3)
    y = np.array([0, 1, 2, 0])
    assert math.isclose(M.per_row_log_loss(probs, y).mean(), math.log(3))
    assert math.isclose(M.per_row_brier(probs, y).mean(), 2 / 3)
    perfect = np.eye(3)[y]
    assert M.per_row_brier(perfect, y).sum() == 0 and M.accuracy(perfect, y) == 1
    lo, hi = M.bootstrap_mean_ci(np.array([0.1, 0.2, 0.3, 0.4]), samples=200)
    assert lo <= 0.25 <= hi


def test_poisson_markets_are_coherent():
    m = markets_from_lambdas(np.array([1.6, 0.4]), np.array([1.1, 2.5]))
    sums = m[["p_home", "p_draw", "p_away"]].sum(axis=1)
    assert np.allclose(sums, 1.0)
    assert (m["p_over_1_5"] >= m["p_over_2_5"]).all() and (m["p_over_2_5"] >= m["p_over_3_5"]).all()
    assert m.loc[0, "p_home"] > m.loc[0, "p_away"] and m.loc[1, "p_away"] > m.loc[1, "p_home"]


@pytest.mark.parametrize("raw", [
    "headers={'x-apisports-key': 'abc123'}",
    "https://api.telegram.org/bot123456:ABCDEFGHIJKLMNOPQRSTUVWX/sendMessage",
    "postgresql://user:hunter2@localhost/db",
])
def test_secrets_are_masked_in_logs(raw):
    masked = mask_secrets(raw)
    assert "abc123" not in masked and "ABCDEFGHIJKLMNOPQRSTUVWX" not in masked
    assert "hunter2" not in masked


# --- European cups (synthetic text in the real openfootball format) -------------

from footintel.connectors.football_data_uk import parse_new_csv  # noqa: E402
from footintel.connectors.openfootball import parse_score, parse_txt  # noqa: E402
from footintel.ingestion.teams import normalize, similarity  # noqa: E402

OPENFOOTBALL_SAMPLE = """= UEFA Champions League 2030/31

▪ League, Matchday 1
  Tue Sep 16 2030
    18:45  Synthetic FC A (ENG)    v Synthetic FC B (ESP)     2-1 (1-0)
           Synthetic FC C (ITA)    v Synthetic FC D (GER)     0-0
▪ Finals, Round of 16
  Wed Mar 11
    21:00  Synthetic FC A (ENG)    v Synthetic FC D (GER)     4-2 pen. 1-1 a.e.t. (1-1, 0-1)
           Synthetic FC B (ESP)    v Synthetic FC C (ITA)     3-0    [awarded]
▪ Final
  Sat May 30
    21:00  Synthetic FC A (ENG)    v Synthetic FC C (ITA)     1-0 (0-0)
"""


def test_openfootball_parser_reads_cup_specifics():
    recs = parse_txt(OPENFOOTBALL_SAMPLE, "cl.txt", 2030)
    assert len(recs) == 5
    first, ko, awarded, final = recs[0], recs[2], recs[3], recs[4]
    assert first.competition_code == "UEFA-CL" and first.kickoff_date.year == 2030
    assert first.kickoff_utc.hour == 16  # 18:45 CEST
    assert recs[1].outcome.ht_home_goals == 0  # 0-0 has no half-time score written
    # Year is inferred: March belongs to the second calendar year of the season.
    assert ko.kickoff_date.year == 2031 and ko.round == "Finals, Round of 16"
    assert (ko.outcome.home_goals, ko.outcome.away_goals, ko.outcome.result) == (1, 1, "D")
    assert (ko.outcome.pen_home, ko.outcome.pen_away) == (4, 2)
    assert awarded.outcome is None and awarded.status == "cancelled"
    assert final.neutral and not first.neutral


def test_openfootball_score_without_half_time_after_extra_time():
    out, problem = parse_score("8-7 pen. 0-0 a.e.t. (0-0)")
    assert problem is None and out.result == "D" and out.ht_home_goals == 0 and out.pen_home == 8


def test_context_league_identity_includes_the_date():
    text = ("Country,League,Season,Date,Time,Home,Away,HG,AG,Res,AvgCH,AvgCD,AvgCA\n"
            "Synthetia,League,2030/2031,01/08/2030,15:00,Synthetic FC A,Synthetic FC B,1,0,H,2,3,4\n"
            "Synthetia,League,2030/2031,01/12/2030,15:00,Synthetic FC A,Synthetic FC B,2,2,D,2,3,4\n")
    from footintel.connectors import football_data_uk as fd
    fd.NEW_TO_COMPETITION.setdefault("SYN", "SUI-SL")
    recs = parse_new_csv(text, "SYN")
    assert len({r.external_id for r in recs}) == 2  # same pairing twice in one season
    assert all(o.snapshot_label == "closing" for r in recs for o in r.odds)


def test_team_name_similarity_is_conservative():
    assert normalize("Manchester City FC (ENG)") == "man city"
    assert similarity("FC Bayern München (GER)", "Bayern Munich") == 1.0
    # Two clubs of one city must not look identical.
    assert similarity("Real Madrid CF (ESP)", "Ath Madrid") < similarity("Real Madrid CF (ESP)", "Real Madrid")


def test_routed_model_uses_odds_only_where_they_exist():
    from footintel.features.builder import ALL_FEATURES
    from footintel.models.zoo import build

    rng = np.random.default_rng(0)
    n = 400
    df = pd.DataFrame({c: rng.normal(size=n) for c in ALL_FEATURES})
    df["elo_diff"] = rng.normal(0, 100, n)
    df["home_goals"] = rng.poisson(1.4, n).astype(float)
    df["away_goals"] = rng.poisson(1.1, n).astype(float)
    df.loc[: n // 2, ["mkt_p_home", "mkt_p_draw", "mkt_p_away", "mkt_overround"]] = np.nan
    model = build("routed_odds_elo").fit(df)
    out = model.predict(df)
    assert np.allclose(out[["p_home", "p_draw", "p_away"]].sum(axis=1), 1.0)
    no_odds = df["mkt_p_home"].isna()
    elo_only = model.without_odds.predict(df[no_odds])
    assert np.allclose(out.loc[no_odds, "p_home"], elo_only["p_home"])


# --- Competition analysis --------------------------------------------------------

from footintel.analysis import stats as AS  # noqa: E402
from footintel.features.context import add_context, stage_of  # noqa: E402


def test_small_sample_statistics():
    lo, hi = AS.wilson(0, 10)
    assert lo == 0 and 0.2 < hi < 0.35  # no zero-width interval at 0 %
    adj = AS.benjamini_hochberg([0.01, 0.04, 0.03, 0.5])
    assert adj[0] == pytest.approx(0.04) and adj[3] == pytest.approx(0.5)
    assert all(a >= p for a, p in zip(adj, [0.01, 0.04, 0.03, 0.5], strict=True))
    r = AS.residual_test(np.array([1.0] * 60 + [0.0] * 40), np.full(100, 0.5))
    assert r["diff"] == pytest.approx(0.1) and r["ci_low"] > 0


def test_stage_names_from_both_file_formats():
    assert stage_of("Finals, Round of 16", "continental") == "round_of_16"
    assert stage_of("Round of 16", "continental") == "round_of_16"
    assert stage_of("Final", "continental") == "final"
    assert stage_of("Finals, Final", "continental") == "final"
    assert stage_of("Gruppe K", "continental") == "group"
    assert stage_of("League, Matchday 3", "continental") == "league"
    assert stage_of(None, "league") == "league"


def _cup_tie():
    rows = [  # synthetic two-legged tie between teams 1 and 2, plus a league filler
        (1, "2031-02-10", 1, 2, 2.0, 0.0, "Finals, Round of 16", "continental"),
        (2, "2031-03-10", 2, 1, np.nan, np.nan, "Finals, Round of 16", "continental"),
        (3, "2031-02-12", 3, 4, 1.0, 1.0, None, "league"),
    ]
    df = pd.DataFrame(rows, columns=["match_id", "kickoff_date", "home_team_id", "away_team_id",
                                     "home_goals", "away_goals", "round", "competition_type"])
    df["kickoff_date"] = pd.to_datetime(df["kickoff_date"])
    df["season"] = 2030
    df["competition"] = np.where(df["competition_type"] == "league", "L", "C")
    return df


def test_second_leg_knows_the_first_leg_score_only():
    out = add_context(_cup_tie()).set_index("match_id")
    assert out.loc[1, "is_second_leg"] == 0 and out.loc[2, "is_second_leg"] == 1
    # Team 2 hosts the second leg and lost the first 2-0: first-leg difference is -2.
    assert out.loc[2, "first_leg_gd"] == -2
    assert out.loc[1, "is_knockout"] == 1 and out.loc[3, "is_knockout"] == 0
