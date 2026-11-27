"""D115: Hermès retrained with power-method market inputs (D114) against Hermès with proportional inputs.
Rule fixed before the run (D9): adopt only if the paired 1X2 log loss gain is at least 0.002
and the 95 % interval is entirely below 0.

Run from football-intel/ with DATABASE_URL set: python scripts/power_inputs_check.py
Both walk-forwards use the same database, seasons and models; only the mkt_p_* inputs differ."""
import numpy as np
import pandas as pd

from footintel.analysis.demargin import fair_probs
from footintel.cli import _features
from footintel.db.session import get_engine
from footintel.evaluation.backtest import paired_logloss, walk_forward
from footintel.features import builder

MODELS = ["routed_competition", "market_implied"]
proportional = builder.market_probabilities


def power(h, d, a):
    out = proportional(h, d, a)
    if not np.isnan(out["mkt_p_home"]):
        f = fair_probs([h, d, a])
        out.update(mkt_p_home=f[0], mkt_p_draw=f[1], mkt_p_away=f[2])
    return out


feats = _features(get_engine())
last = int(feats.loc[feats["home_goals"].notna(), "season"].max())
seasons = list(range(last - 5, last))
base = walk_forward(feats, MODELS, seasons)
builder.market_probabilities = power
new = walk_forward(_features(get_engine()), MODELS, seasons)
new = new.assign(model=new["model"] + "_power")
both = pd.concat([base, new], ignore_index=True)
for cand, ref in [("routed_competition_power", "routed_competition"),
                  ("market_implied_power", "market_implied"),
                  ("routed_competition_power", "market_implied_power")]:
    print(paired_logloss(both, cand, ref, samples=2000))
