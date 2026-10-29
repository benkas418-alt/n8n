"""Unit tests on pure functions. All inputs are synthetic."""

import math
from datetime import UTC, date, datetime

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


# --- Trend engine ----------------------------------------------------------------

from footintel.analysis import events as EV  # noqa: E402
from footintel.analysis.trend_engine import _test as trend_test, classify  # noqa: E402
from footintel.features.trend_features import team_trend_features  # noqa: E402


def test_unknown_data_is_not_zero():
    d = pd.DataFrame({"home_goals": [1.0, 0.0], "away_goals": [0.0, 0.0],
                      "ht_home_goals": [np.nan, 0.0], "ht_away_goals": [np.nan, 0.0],
                      "home_shots": [np.nan, np.nan], "away_shots": [np.nan, np.nan]})
    ind = {i.name: i for i in EV.MATCH_INDICATORS}
    assert EV.evaluate(ind["nil_nil"], d).tolist() == [0.0, 1.0]
    fh = EV.evaluate(ind["first_half_goals"], d)
    assert np.isnan(fh.iloc[0]) and fh.iloc[1] == 0.0  # unknown half time stays unknown
    assert EV.evaluate(ind["shots"], d).isna().all()  # not provided: never 0


def test_small_windows_do_not_look_significant():
    rng = np.random.default_rng(0)
    ref = rng.choice([0.0, 1.0, 3.0], 76, p=[0.37, 0.27, 0.36])
    assert trend_test("mean", np.zeros(6), ref) > 0.01  # six defeats: not overwhelming evidence
    assert trend_test("rate", np.ones(6), np.r_[np.ones(30), np.zeros(46)]) > 0.001


def test_status_rules():
    def row(window, diff, p):
        return {"trend_key": "k", "window": window, "abs_diff": diff, "status": None,
                "p_value": p, "n": 400}
    rows = [row("short", 0.1, 1e-6), row("medium", 0.08, 1e-6)]
    classify(rows, {})
    assert rows[0]["status"] == "rising"
    rows = [row("short", 0.1, 1e-6), row("medium", 0.0, 0.9)]
    classify(rows, {})
    assert rows[0]["status"] == "emerging"
    rows = [row("short", 0.0, 0.9), row("medium", 0.0, 0.9)]
    classify(rows, {"k": "emerging"})
    assert rows[0]["status"] == "unconfirmed"


def test_team_trend_features_use_earlier_matches_only():
    rng = np.random.default_rng(1)
    n = 120
    df = pd.DataFrame({"match_id": range(n), "kickoff_date": pd.date_range("2030-01-01", periods=n, freq="3D"),
                       "home_team_id": rng.integers(1, 6, n), "competition": "X", "season": 2030,
                       "competition_type": "league", "elo_home": 1500.0, "elo_away": 1500.0,
                       "neutral_venue": False, "home_team": "Synthetic FC A", "away_team": "Synthetic FC B"})
    df["away_team_id"] = (df.home_team_id % 5) + 1
    for c in ["home_goals", "away_goals", "home_sot", "away_sot"]:
        df[c] = rng.integers(0, 4, n).astype(float)
    df["ht_home_goals"], df["ht_away_goals"] = np.minimum(df.home_goals, 1), np.minimum(df.away_goals, 1)
    a = team_trend_features(df)
    b = df.copy()
    b.loc[b.match_id >= 90, ["home_goals", "away_goals"]] = [9.0, 0.0]
    bb = team_trend_features(b)
    assert np.allclose(a.iloc[:91].fillna(-1), bb.iloc[:91].fillna(-1))
    assert a["tt_conversion_38_h"].iloc[0] == pytest.approx(0.30)  # first match gets the prior


def test_telegram_splits_long_text_and_hides_the_token(caplog):
    import httpx

    from footintel.config import Settings
    from footintel.notify import telegram

    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200 if len(seen) == 1 else 403, json={"ok": len(seen) == 1})

    token = "123456:" + "S" * 35  # real tokens have this shape
    s = Settings(telegram_bot_token=token, telegram_chat_id="42")
    text = "\n".join(f"ligne {i} " + "x" * 90 for i in range(100))  # ~10 000 characters
    assert telegram.send(Settings(telegram_bot_token=None, telegram_chat_id=None), text) == 0
    with caplog.at_level("INFO"):
        sent = telegram.send(s, text, transport=httpx.MockTransport(handler))
    assert sent == 1 and len(seen) == 2  # stops at the first refusal
    assert all(len(r.read()) < 4300 for r in seen)
    own = "".join(r.getMessage() for r in caplog.records if r.name.startswith("footintel"))
    assert token not in own
    # httpx prints the URL; the production log handler masks it.
    assert token not in mask_secrets(caplog.text)
    digest = telegram.summary_from_markdown("# Titre\n\n| a | b |\n|---|---|\n- point\n")
    assert digest == "Titre\n- point"


def test_drift_levels_need_psi_and_mean_shift_together():
    from footintel.analysis import drift

    rng = np.random.default_rng(0)
    same = rng.normal(0, 1, 2000)
    assert drift.psi(same, rng.normal(0, 1, 2000)) < 0.05
    assert drift.psi(same, rng.normal(1, 1, 2000)) > 0.25
    assert drift.level(0.5, 0.05) != "strong"  # shape change without a mean shift
    assert drift.level(0.5, 0.6) == "strong"


def test_input_drift_compares_with_the_same_window_one_year_earlier():
    from footintel.analysis import drift

    days = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    month = days.month.to_numpy()
    # Seasonal pattern repeated each year, plus a real shift in the last 60 days.
    goals = 2.5 + 0.5 * np.sin(month / 12 * 2 * np.pi)
    goals = np.where(days > days[-1] - pd.Timedelta(days=60), goals + 1.0, goals)
    rng = np.random.default_rng(1)
    f = pd.DataFrame({"kickoff_date": days, "is_target": True,
                      "comp_goals_mean": goals + rng.normal(0, 0.2, len(days)),
                      "shots5_for_h": 12 + 3 * np.sin(month / 12 * 2 * np.pi) + rng.normal(0, 1, len(days))})
    out = drift.input_drift(f).set_index("feature")
    assert out.loc["comp_goals_mean", "level"] == "strong"
    assert out.loc["shots5_for_h", "level"] == "stable"  # seasonal only: not flagged
    assert out.loc["shots5_for_h", "n_reference"] == 60


def _synthetic_picks(n: int, informative: bool, seed: int = 0) -> pd.DataFrame:
    """Picks on synthetic matches. The model ignores a hidden factor; an informed user sees it."""
    rng = np.random.default_rng(seed)
    base = rng.dirichlet([4, 3, 3], size=n)
    hidden = rng.normal(0, 1.2, n)
    logits = np.log(base) + np.stack([hidden, np.zeros(n), -hidden], axis=1)
    true_p = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
    result = np.array([rng.choice(3, p=p) for p in true_p])
    signal = hidden if informative else rng.normal(0, 1.2, n)
    pick = np.where(signal > 0.4, "H", np.where(signal < -0.4, "A", "D"))
    return pd.DataFrame({"kickoff": pd.date_range("2025-01-01", periods=n, freq="6h"),
                         "p_home": base[:, 0], "p_draw": base[:, 1], "p_away": base[:, 2],
                         "pick": pick, "confidence": np.clip(np.abs(signal) * 2 + 1, 1, 5).round(),
                         "result": np.array(list("HDA"))[result]})


def test_hybrid_needs_200_picks_and_only_adopts_a_reliable_gain():
    from footintel.analysis import hybrid

    assert hybrid.evaluate(_synthetic_picks(150, True))["status"] == "insufficient_data"
    informed = hybrid.evaluate(_synthetic_picks(1500, True))
    assert informed["status"] == "evaluated" and informed["verdict"] == "adopt"
    assert informed["n_test"] == 1400 and informed["ci_high"] < 0
    noise = hybrid.evaluate(_synthetic_picks(1500, False))
    assert noise["verdict"] == "no_reliable_gain"
    small = hybrid.evaluate(_synthetic_picks(300, True))
    assert small["n_test"] == 200 and small["verdict"] in ("too_few_test_picks", "no_reliable_gain")


def test_hybrid_never_scores_a_pick_with_a_fit_that_saw_it():
    from footintel.analysis import hybrid

    df = _synthetic_picks(400, True)
    oos = hybrid.out_of_sample(df)
    assert len(oos) == 300
    first_scored = oos["kickoff"].min()
    assert (df.sort_values("kickoff")["kickoff"].iloc[hybrid.MIN_TRAIN] == first_scored)


def test_dixon_coles_rho_zero_is_plain_poisson_and_rho_is_recovered():
    from footintel.models.base import score_matrix
    from footintel.models.baseline import fit_rho

    assert np.allclose(score_matrix(1.4, 1.1, 0.0), score_matrix(1.4, 1.1))
    m = score_matrix(1.4, 1.1, -0.1)
    assert m.sum() == pytest.approx(1.0) and m[0, 0] > score_matrix(1.4, 1.1)[0, 0]
    rng = np.random.default_rng(3)
    lh, la = rng.uniform(0.8, 2.0, 6000), rng.uniform(0.6, 1.6, 6000)
    goals = []
    for h, a in zip(lh, la, strict=True):
        p = score_matrix(h, a, -0.12).ravel()
        k = rng.choice(len(p), p=p)
        goals.append(divmod(k, 11))
    hg, ag = np.array(goals).T
    assert fit_rho(lh, la, hg, ag) == pytest.approx(-0.12, abs=0.05)


def test_temperature_calibration_softens_overconfident_cup_probabilities():
    from footintel.models.base import GOAL_COLS, PROB_COLS
    from footintel.models.zoo import RoutedCompetitionAware

    class Fixed:
        def __init__(self, cols, values):
            self.cols, self.values = cols, values

        def predict(self, df):
            return pd.DataFrame([self.values] * len(df), columns=self.cols, index=df.index)

    m = RoutedCompetitionAware("t", calibrate_without_odds=True)
    m.without_odds = Fixed(PROB_COLS, [0.7, 0.2, 0.1])
    m.with_odds = Fixed(PROB_COLS, [0.5, 0.3, 0.2])
    m.goals = Fixed(GOAL_COLS, [1.0] * len(GOAL_COLS))
    df = pd.DataFrame({"mkt_p_home": [np.nan, 0.5]})
    m.temperature_ = 1.5
    out = m.predict(df)[PROB_COLS].to_numpy()
    assert out[0, 0] < 0.7 and out[0, 2] > 0.1 and out[0].sum() == pytest.approx(1.0)
    assert np.allclose(out[1], [0.5, 0.3, 0.2])  # matches with odds are untouched


def test_models_saved_before_new_options_still_predict():
    """Pickled versions lack attributes added later; they must predict as before."""
    from footintel.models.base import GOAL_COLS, PROB_COLS
    from footintel.models.zoo import RoutedCompetitionAware

    class Fixed:
        def __init__(self, cols, values):
            self.cols, self.values = cols, values

        def predict(self, df):
            return pd.DataFrame([self.values] * len(df), columns=self.cols, index=df.index)

    m = RoutedCompetitionAware("old")
    del m.temperature_, m.calibrate_without_odds
    m.without_odds = Fixed(PROB_COLS, [0.7, 0.2, 0.1])
    m.with_odds = Fixed(PROB_COLS, [0.5, 0.3, 0.2])
    m.goals = Fixed(GOAL_COLS, [1.0] * len(GOAL_COLS))
    out = m.predict(pd.DataFrame({"mkt_p_home": [np.nan]}))
    assert np.allclose(out[PROB_COLS].to_numpy()[0], [0.7, 0.2, 0.1])


def _oldb_match(mid, home, away, finished, results=(), goals=(), group="1.Spieltag",
                when="2026-09-16T21:00:00", when_utc="2026-09-16T19:00:00Z"):
    """Same shape as a real /getmatchdata answer. Synthetic teams and scores."""
    return {"matchID": mid, "matchDateTime": when, "matchDateTimeUTC": when_utc,
            "matchIsFinished": finished, "group": {"groupName": group},
            "team1": {"teamName": home}, "team2": {"teamName": away},
            "matchResults": [{"resultTypeKind": k, "pointsTeam1": a, "pointsTeam2": b}
                             for k, a, b in results],
            "goals": [{"matchMinute": mi, "scoreTeam1": a, "scoreTeam2": b, "isPenalty": pen}
                      for mi, a, b, pen in goals]}


def test_openligadb_results_are_checked_against_the_goal_list():
    from footintel.connectors.openligadb import parse_matches

    data = [
        _oldb_match(1, "Synthetic FC A ", "Synthetic FC B", True,
                    [("HalfTime", 1, 0), ("After90Minutes", 2, 1)],
                    [(10, 1, 0, False), (60, 1, 1, False), (88, 2, 1, False)]),
        # Extra time and a shoot-out: the 1X2 result uses the 90-minute score.
        _oldb_match(2, "Synthetic FC C", "Synthetic FC D", True,
                    [("HalfTime", 0, 0), ("After90Minutes", 1, 1), ("AfterExtraTime", 1, 1),
                     ("AfterPenalties", 4, 3)],
                    [(50, 1, 0, False), (93, 1, 1, False), (None, 1, 1, True), (None, 2, 1, True)],
                    group="Achtelfinale"),
        # Result contradicts the goal list: no result is stored.
        _oldb_match(3, "Synthetic FC E", "Synthetic FC F", True,
                    [("HalfTime", 0, 0), ("After90Minutes", 0, 0)],
                    [(20, 1, 0, False), (70, 2, 0, False)]),
        # Goals without minutes: the number of goals must match.
        _oldb_match(4, "Synthetic FC G", "Synthetic FC H", True,
                    [("HalfTime", 1, 0), ("After90Minutes", 3, 0)],
                    [(None, 0, 0, False)] * 3),
        _oldb_match(5, "Synthetic FC A", "Synthetic FC C", False, group="Finale"),
    ]
    recs = {int(r.external_id.split("|")[2]): r for r in parse_matches(data, "UEFA-EL", 2026, "uel2026")}
    a = recs[1]
    assert a.home_team == "Synthetic FC A" and a.round == "League, Matchday 1"
    assert (a.outcome.home_goals, a.outcome.away_goals, a.outcome.result) == (2, 1, "H")
    assert a.kickoff_date == date(2026, 9, 16) and a.kickoff_utc == datetime(2026, 9, 16, 19, 0, tzinfo=UTC)
    b = recs[2].outcome
    assert recs[2].round == "Round of 16" and b.result == "D" and (b.pen_home, b.pen_away) == (4, 3)
    assert recs[3].outcome is None and recs[3].status == "scheduled"
    assert recs[3].issues[0][0] == "result_inconsistent"
    assert recs[4].outcome.home_goals == 3 and not recs[4].issues
    assert recs[5].round == "Final" and recs[5].neutral and recs[5].outcome is None


def test_football_data_org_parse_keeps_only_safe_results():
    from footintel.connectors.football_data_org import parse_matches

    def m(mid, status, score=None, stage="LEAGUE_STAGE"):
        return {"id": mid, "utcDate": "2026-09-16T19:00:00Z", "status": status, "matchday": 2,
                "stage": stage, "homeTeam": {"name": "Synthetic FC A"},
                "awayTeam": {"name": "Synthetic FC B"}, "score": score or {}}

    data = {"matches": [
        m(1, "FINISHED", {"duration": "REGULAR", "fullTime": {"home": 1, "away": 2},
                          "halfTime": {"home": 0, "away": 1}}),
        m(2, "FINISHED", {"duration": "PENALTY_SHOOTOUT", "fullTime": {"home": 2, "away": 2},
                          "regularTime": {"home": 1, "away": 1}, "penalties": {"home": 5, "away": 4},
                          "halfTime": {"home": 0, "away": 0}}, stage="LAST_16"),
        # Extra time without the 90-minute score: no guessed result.
        m(3, "FINISHED", {"duration": "EXTRA_TIME", "fullTime": {"home": 2, "away": 1}}),
        m(4, "TIMED"),
    ]}
    recs = {int(r.external_id.split("|")[2]): r for r in parse_matches(data, "UEFA-CL", 2026)}
    assert recs[1].outcome.result == "A" and recs[1].round == "League, Matchday 2"
    assert recs[1].kickoff_date == date(2026, 9, 16)  # 21:00 in Paris
    o = recs[2].outcome
    assert (o.home_goals, o.aet_home_goals, o.pen_home, o.result) == (1, 2, 5, "D")
    assert recs[2].round == "Round of 16"
    assert recs[3].outcome is None and recs[3].issues[0][0] == "result_inconsistent"
    assert recs[4].status == "scheduled" and recs[4].outcome is None


def _scenario_rows(n=6000, seed=0, planted=0.0):
    """Synthetic team rows: market price drawn at random, results drawn from that price.
    `planted` adds a true win-probability shift to teams in the 'unlucky' scenario."""
    rng = np.random.default_rng(seed)
    p_win = rng.uniform(0.15, 0.75, n)
    p_draw = np.full(n, 0.25)
    unlucky = rng.random(n) < 0.2
    true_win = np.clip(p_win + planted * unlucky, 0.01, 0.74)
    u = rng.random(n)
    points = np.where(u < true_win, 3.0, np.where(u < true_win + p_draw, 1.0, 0.0))
    return pd.DataFrame({
        "match_id": np.arange(n), "kickoff_date": pd.date_range("2010-01-01", periods=n, freq="D"),
        "season": 2010, "competition": "ENG-PL", "team_id": 1, "is_home": rng.random(n) < 0.5,
        "form5_ppg_s": np.where(unlucky, 1.0, 1.6), "form5_ppg_o": 1.4, "gf5_s": 1.2, "gf5_o": 1.2,
        "ga5_s": 1.2, "ga5_o": 1.2, "sot5_for_s": np.where(unlucky, 6.0, 4.0), "sot5_for_o": 4.0,
        "sot5_against_s": 4.0, "sot5_against_o": 4.0, "rest_days_s": 7.0, "rest_days_o": 7.0,
        "games_14d_s": 2.0, "games_14d_o": 2.0, "europe_7d_s": 0.0, "europe_7d_o": 0.0,
        "p_win": p_win, "p_draw": p_draw, "points": points, "expected_points": 3 * p_win + p_draw})


def test_scenarios_detect_a_planted_effect_and_ignore_price_selection():
    from footintel.analysis.stories import scenario_table

    as_of = pd.Timestamp("2026-10-25")
    none = scenario_table(_scenario_rows(planted=0.0), as_of).set_index(["scenario", "window"])
    planted = scenario_table(_scenario_rows(planted=0.12), as_of).set_index(["scenario", "window"])
    assert none.loc[("unlucky", "all"), "status"] == "no_effect"
    assert planted.loc[("unlucky", "all"), "status"] == "confirmed"
    assert planted.loc[("unlucky", "all"), "observed"] > 0.2
    # Big favourites are only a price selection here: no effect at equal price.
    assert none.loc[("big_home_favourite", "all"), "status"] in ("no_effect", "insufficient_data")


def test_story_flow_labels_read_the_half_time_score():
    from footintel.analysis.stories import _flow

    row = lambda hg, ag, hh, ha: {"home_goals": hg, "away_goals": ag,  # noqa: E731
                                  "ht_home_goals": float(hh), "ht_away_goals": float(ha)}
    assert "comeback_home" in _flow(row(2, 1, 0, 1))
    assert "home_lead_lost" in _flow(row(1, 2, 1, 0)) and "comeback_away" in _flow(row(1, 2, 1, 0))
    assert "away_recovered_draw" in _flow(row(3, 3, 1, 0)) and "open_second_half" in _flow(row(3, 3, 1, 0))
    assert _flow(row(0, 0, 0, 0)) == ["goalless"]
    assert _flow({"home_goals": 1, "away_goals": 0, "ht_home_goals": np.nan,
                  "ht_away_goals": np.nan}) == ["half_time_unknown"]


def test_value_markets_are_consistent():
    from footintel.analysis.value import market_probabilities

    pred = {"p_home": 0.5, "p_draw": 0.27, "p_away": 0.23, "p_over_1_5": 0.75, "p_over_2_5": 0.5,
            "p_over_3_5": 0.27, "p_btts": 0.52, "exp_home_goals": 1.6, "exp_away_goals": 1.0}
    m = {x["key"]: x["prob"] for x in market_probabilities(pred)}
    assert m["1X"] == pytest.approx(0.77, abs=1e-4) and m["12"] == pytest.approx(0.73, abs=1e-4)
    assert m["O2.5"] + m["U2.5"] == pytest.approx(1.0)
    # Leading at some point is at least as likely as winning, and both teams can lead.
    assert m["1UP_1"] >= m["1"] - 1e-3 and m["1UP_2"] >= m["2"] - 1e-3
    assert m["1UP_1"] + m["1UP_2"] > 1 - m["X"]


def test_odds_api_parse_keeps_complete_h2h_markets_only():
    from datetime import UTC, datetime

    from footintel.connectors.the_odds_api import parse_events

    def book(key, prices):
        return {"key": key, "last_update": "2026-11-03T10:00:00Z",
                "markets": [{"key": "h2h", "outcomes": [{"name": n, "price": p} for n, p in prices]}]}

    data = [{"id": "e1", "sport_key": "soccer_uefa_champs_league", "commence_time": "2026-11-04T20:00:00Z",
             "home_team": "Home FC", "away_team": "Away FC",
             "bookmakers": [book("pinnacle", [("Home FC", 1.9), ("Draw", 3.6), ("Away FC", 4.2)]),
                            book("partial", [("Home FC", 1.8), ("Away FC", 4.0)]),
                            book("bad", [("Home FC", 1.0), ("Draw", 3.5), ("Away FC", 4.0)])]}]
    ev = parse_events(data, datetime(2026, 11, 3, 10, 5, tzinfo=UTC))[0]
    assert ev.commence_utc.hour == 20 and {o.bookmaker for o in ev.odds} == {"pinnacle"}
    assert sorted(o.selection for o in ev.odds) == ["A", "D", "H"]
    assert ev.odds[0].snapshot_label == "oddsapi@2026-11-03T10:05"


def test_market_consensus_removes_each_margin_and_keeps_best_price():
    from footintel.analysis.value import market_consensus

    m = market_consensus([("a", "H", 2.0), ("a", "D", 3.5), ("a", "A", 4.0),
                          ("b", "H", 2.1), ("b", "D", 3.4), ("b", "A", 3.8), ("c", "H", 2.5)])
    assert m["n_bookmakers"] == 2 and m["best"]["H"] == 2.5
    assert m["1"] + m["X"] + m["2"] == pytest.approx(1.0, abs=1e-3)
    assert market_consensus([]) is None


def _of_player(name, pid):
    return {"name": name, "nickName": name.split()[-1], "link": {"urlPath": f"/en/player/x-{pid}"}}


def _of_team(name, first_id):
    # Rows from the forwards to the goalkeeper: 4-3-3.
    sizes, rows, n = [3, 3, 4, 1], [], first_id
    for size in sizes:
        rows.append({"players": [_of_player(f"{name} P{n + i}", n + i) for i in range(size)]})
        n += size
    return {"teamName": name, "variant": {"$case": "formation", "formation": {"rows": rows}}}


def onefootball_match_page(home="Synth One", away="Synth Two"):
    """Synthetic match data in the onefootball.com page shape (no real content)."""
    def comp(case, body):
        return {"contentType": {"$case": case, case: body}}

    return {"props": {"components": [
        comp("matchScore", {"timePeriod": "Full time", "homeTeam": {"name": home, "score": "1"},
                            "awayTeam": {"name": away, "score": "0"}}),
        comp("matchLineup", {"title": "LINE-UPS (CONFIRMED)", "variant": {"$case": "lineup", "lineup": {
            "homeTeam": _of_team(home, 1), "awayTeam": _of_team(away, 100)}}}),
        comp("matchEvents", {"events": [
            {"teamSide": 0, "name": "Goal", "timeline": "45+2'", "type": {"$case": "goal", "goal": {
                "scorer": {"name": f"{home} P2"}, "assistant": {"name": f"{home} P5"}}}},
            {"teamSide": 1, "name": "Yellow card", "timeline": "60'", "type": {"$case": "card", "card": {
                "type": 0, "player": {"name": f"{away} P101"}}}},
            {"teamSide": 1, "name": "Substitution", "timeline": "70'", "type": {"$case": "substitution",
                "substitution": {"playerIn": {"name": "Bench Man"}, "playerOut": {"name": f"{away} P100"}}}},
            {"teamSide": 0, "name": "Other", "timeline": "80'", "type": {"$case": "var", "var": {}}}]}),
        comp("matchStats", {"stats": [{"title": "Possession", "home": 55, "away": 45},
                                      {"title": "Total shots", "home": 12, "away": 7},
                                      {"title": "Shots on target", "home": 5, "away": 2},
                                      {"title": "Duels won", "home": 40, "away": 38}]}),
    ]}}


def test_onefootball_parses_lineups_events_and_stats():
    from footintel.connectors.onefootball import formation_of, parse_cards, parse_match

    assert formation_of([1, 3, 2, 4, 1]) == "4-2-3-1"
    assert formation_of([3, 3, 4]) is None  # no goalkeeper row
    page = parse_match("42", onefootball_match_page())
    assert page.finished and page.home.formation == "4-3-3" and len(page.away.starters) == 11
    assert [page.home.starters[i].position for i in (0, 3, 6, 10)] == ["A", "M", "D", "G"]
    assert page.home.starters[0].external_id == "1"
    goal, card, sub = page.events  # the unknown event type is left out
    assert (goal.type, goal.minute, goal.extra_minute, goal.other_player) == ("goal", 45, 2, "Synth One P5")
    assert (card.side, card.detail) == (1, "Yellow card") and sub.player == "Bench Man"
    assert page.stats == {"home": {"possession_pct": 55, "shots": 12, "shots_on_target": 5},
                          "away": {"possession_pct": 45, "shots": 7, "shots_on_target": 2}}
    cards, more = parse_cards({"lists": [{"matchCards": [
        {"link": "/en/match/7", "kickoff": "2026-10-25T16:30:00Z", "timePeriod": "Full time",
         "homeTeam": {"name": "A"}, "awayTeam": {"name": "B"}},
        {"link": "/en/news/1", "kickoff": "2026-10-25T16:30:00Z", "homeTeam": {"name": "A"},
         "awayTeam": {"name": "B"}}]}]})
    assert [(c.external_id, c.finished) for c in cards] == [("7", True)] and more is None
