"""Elo ratings for club football. Parameters are documented in docs/FEATURES.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EloParams:
    k: float = 20.0
    home_advantage: float = 60.0
    initial: float = 1500.0
    # Rating for a team that first appears after the first season (usually promoted).
    newcomer: float = 1420.0
    # Share of the distance to the mean kept between seasons.
    season_carry: float = 0.8


def expected_home(elo_home: float, elo_away: float, home_advantage: float) -> float:
    return 1.0 / (1.0 + 10 ** (-(elo_home + home_advantage - elo_away) / 400.0))


def goal_multiplier(goal_diff: int) -> float:
    gd = abs(goal_diff)
    if gd <= 1:
        return 1.0
    if gd == 2:
        return 1.5
    return (11.0 + gd) / 8.0


def update(elo_home: float, elo_away: float, home_goals: int, away_goals: int,
           params: EloParams) -> tuple[float, float]:
    score = 1.0 if home_goals > away_goals else 0.5 if home_goals == away_goals else 0.0
    exp = expected_home(elo_home, elo_away, params.home_advantage)
    delta = params.k * goal_multiplier(home_goals - away_goals) * (score - exp)
    return elo_home + delta, elo_away - delta
