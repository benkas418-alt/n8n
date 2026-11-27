"""D110: does the Asian handicap price improve goal rates (margin, 1UP, 2UP, first goal)?
A: rates fitted to fair 1X2 + over 2.5 (current method). B: same + fair Asian handicap.
Run from football-intel/: python scripts/asian_handicap_check.py [path to raw football_data_uk]"""
import sys, numpy as np, pandas as pd
from scipy.optimize import least_squares
from scipy.stats import poisson
from sqlalchemy import text
sys.path.insert(0, "src")


def ll(q, y):
    q = np.clip(np.asarray(q, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(q) + (1 - y) * np.log(1 - q))


def boot(d, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    return np.percentile([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)], [2.5, 97.5])


from footintel.db.session import get_engine
from footintel.analysis.value import path_markets
from footintel.analysis.matchup import _goal_events

G = np.arange(11); D = G[:, None] - G[None, :]; T = G[:, None] + G[None, :]
RAW = sys.argv[1] if len(sys.argv) > 1 else "data/raw/football_data_uk"  # DATA_DIR/raw/football_data_uk
LEAGUES = ["E0", "D1", "SP1", "I1", "F1"]
eng = get_engine()

def grid(lh, la):
    return np.outer(poisson.pmf(G, lh), poisson.pmf(G, la))

def ah_parts(line):
    q = round(line * 4)
    return [(line - .25, .5), (line + .25, .5)] if q % 2 else [(line, 1.0)]

def ah_home_prob(m, line):
    """Fair 'home share' of an Asian handicap bet: 1/fair odds for home."""
    win = push = 0.0
    for l, w in ah_parts(line):
        dd = D + l
        win += w * m[dd > 1e-9].sum(); push += w * m[np.abs(dd) < 1e-9].sum()
    return win / max(1 - push, 1e-9)

def fit(p1, p2, pov, ah=None, start=(1.4, 1.1)):
    def res(x):
        lh, la = np.exp(x); m = grid(lh, la)
        r = [np.tril(m, -1).sum() - p1, np.triu(m, 1).sum() - p2, m[T > 2.5].sum() - pov]
        if ah is not None:
            r.append(ah_home_prob(m, ah[0]) - ah[1])
        return r
    return np.exp(least_squares(res, np.log(start)).x)

def fair2(a, b):
    return (1 / a) / (1 / a + 1 / b)

with eng.connect() as c:
    refs = pd.read_sql(text("""SELECT r.external_id, r.match_id, o.home_goals, o.away_goals FROM match_external_refs r
        JOIN data_sources d ON d.id = r.source_id AND d.code = 'football_data_uk'
        JOIN match_outcomes o ON o.match_id = r.match_id WHERE o.home_goals IS NOT NULL"""), c)
ref = {k: (m, h, a) for k, m, h, a in refs.itertuples(index=False)}

rows = []
for season in range(2021, 2027):
    d = f"{RAW}/{season % 100:02d}{(season + 1) % 100:02d}"
    for lg in LEAGUES:
        try:
            df = pd.read_csv(f"{d}/{lg}.csv", encoding="latin-1")
        except FileNotFoundError:
            continue
        df = df.rename(columns={"Avg>2.5": "Avg_2_5o", "Avg<2.5": "Avg_2_5u"})
        for r in df.itertuples(index=False):
            key = f"{lg}|{season}|{r.HomeTeam}|{r.AwayTeam}"
            if key not in ref:
                continue
            vals = [getattr(r, c, np.nan) for c in ("AvgH", "AvgD", "AvgA", "Avg_2_5o", "Avg_2_5u", "AHh", "AvgAHH", "AvgAHA")]
            rows.append((key, season, lg, *ref[key], *vals))
cols = ["key", "season", "lg", "match_id", "hg", "ag", "H", "Dr", "A", "O", "U", "AHh", "AHH", "AHA"]
X = pd.DataFrame(rows, columns=cols).dropna()
print("matches with 1X2, over 2.5 and Asian handicap (pre-match):", len(X), dict(X.season.value_counts().sort_index()))

out = []
for r in X.itertuples(index=False):
    inv = np.array([1 / r.H, 1 / r.Dr, 1 / r.A]); p = inv / inv.sum()
    pov = fair2(r.O, r.U)
    a = fit(p[0], p[2], pov)
    b = fit(p[0], p[2], pov, (r.AHh, fair2(r.AHH, r.AHA)))
    out.append((r.match_id, r.season, r.hg, r.ag, *a, *b))
R = pd.DataFrame(out, columns=["match_id", "season", "hg", "ag", "ah_", "aa_", "bh", "ba"])

def margin_probs(lh, la):
    m = grid(lh, la)
    return [m[D <= -2].sum(), m[D == -1].sum(), m[D == 0].sum(), m[D == 1].sum(), m[D >= 2].sum()]

cat = np.clip(R.hg - R.ag, -2, 2).to_numpy() + 2
PA = np.array([margin_probs(h, a) for h, a in zip(R.ah_, R.aa_)]); PB = np.array([margin_probs(h, a) for h, a in zip(R.bh, R.ba)])
la = -np.log(np.clip(PA[np.arange(len(R)), cat], 1e-12, 1)); lb = -np.log(np.clip(PB[np.arange(len(R)), cat], 1e-12, 1))
d = lb - la
print("\n1) Écart de buts (gagne de 2+, de 1, nul, perd de 1, de 2+), tous les matchs")
print(f"   n={len(R)} écart B-A {d.mean():+.4f} IC {np.round(boot(d),4)}  (négatif = handicap utile)")
for s in sorted(R.season.unique()):
    m = (R.season == s).to_numpy(); print(f"   saison {s}: n={m.sum()} écart {d[m].mean():+.4f}")
# "Wins by 2 or more" as a plain yes/no, the core of 2UP
for name, sel in (("domicile gagne de 2+", 4), ("extérieur gagne de 2+", 0)):
    y = (cat == sel).astype(float)
    dd = ll(PB[:, sel], y) - ll(PA[:, sel], y)
    print(f"   {name}: écart {dd.mean():+.4f} IC {np.round(boot(dd),4)}")

with eng.connect() as c:
    goals = pd.read_sql(text("""SELECT e.match_id, e.team_id, e.minute, coalesce(e.extra_minute, 0) AS extra, e.detail,
        m.home_team_id, m.away_team_id FROM match_events e JOIN data_sources d ON d.id = e.source_id AND d.code = 'onefootball'
        JOIN matches m ON m.id = e.match_id WHERE e.type = 'goal'"""), c)
    read = pd.read_sql(text("""SELECT DISTINCT r.match_id, m.home_team_id FROM match_external_refs r
        JOIN data_sources d ON d.id = r.source_id AND d.code = 'onefootball' JOIN matches m ON m.id = r.match_id"""), c)
g = _goal_events(goals).sort_values("t"); home_of = dict(zip(read.match_id, read.home_team_id))
act = {}
score = {m: h + a for m, h, a in zip(R.match_id, R.hg, R.ag)}
for mid in set(read.match_id) & set(R.match_id):
    seq = [1 if c == home_of[mid] else -1 for c in g.loc[g.match_id == mid, "credited"]]
    if len(seq) != score[mid]:
        continue  # goal minutes missing or incomplete: never read them as a 0-0
    run = np.cumsum(seq) if seq else np.array([0]); end = run[-1]
    first = "none" if not seq else ("home" if seq[0] == 1 else "away")
    act[mid] = {"first_home": first == "home", "first_away": first == "away", "up1_home": run.max() >= 1,
                "up1_away": run.min() <= -1, "up2_home": run.max() >= 2 or end > 0, "up2_away": run.min() <= -2 or end < 0}
Q = R[R.match_id.isin(act)]
print(f"\n2) 1UP, 2UP, premier but, matchs avec minutes des buts : {len(Q)}")
for k in ("first_home", "first_away", "up1_home", "up1_away", "up2_home", "up2_away"):
    y = np.array([act[m][k] for m in Q.match_id], float)
    pa = np.array([path_markets(h, a)[k] for h, a in zip(Q.ah_, Q.aa_)]); pb = np.array([path_markets(h, a)[k] for h, a in zip(Q.bh, Q.ba)])
    dd = ll(pb, y) - ll(pa, y)
    print(f"   {k:10s} écart B-A {dd.mean():+.4f} IC {np.round(boot(dd),4)}  moyenne annoncée A {pa.mean():.3f} B {pb.mean():.3f} réel {y.mean():.3f}")
