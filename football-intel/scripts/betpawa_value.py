"""Are betPawa prices above the fair price? Text report of D68, D101-D104.

Run from football-intel/: python scripts/betpawa_value.py [--ledger reports/betpawa_ledger.csv]

The work is in `footintel.analysis.betpawa_value` (the site's "Valeur" page uses the same
report). Three data sets, never mixed: market observations (reference/betpawa_prices.csv),
played selections (betpawa_coupon_legs.csv) and coupons (betpawa_coupons.csv). Three measures,
never mixed: EV at placement, CLV at the close, and ROI counted per coupon.
"""

import argparse
import sys

sys.path.insert(0, "src")
from footintel.analysis.betpawa_value import (  # noqa: E402
    build_report,
    collect,
    write_ledger,
)
from footintel.db.session import get_engine  # noqa: E402


def pct(x: float | None) -> str:
    return "—" if x is None else f"{x:+.1%}"


def line(name: str, s: dict) -> str:
    out = (f"{name}: {s['selections']} sélections, {s['matches']} matchs, {s['competitions']} compétitions"
           + (f", {s['coupons']} coupons" if s["coupons"] else "")
           + (f", cotes {s['odds_min']:.2f} à {s['odds_max']:.2f}" if s["odds_min"] else ""))
    if s["won"] or s["lost"]:
        out += f" ; résultats betPawa : {s['won']} gagnées, {s['lost']} perdues"
    for key, label in (("clv", "CLV"), ("ev_place", "EV au placement")):
        st = s[key]
        if st["mean"] is None:
            out += f" ; {label} : indisponible"
            continue
        out += f" ; {label} moyenne {pct(st['mean'])} sur {st['n']}"
        if st["ci"]:
            out += f" [{pct(st['ci'][0])} ; {pct(st['ci'][1])}]"
        if st["warning"]:
            out += f" ({st['warning']})"
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="reports/betpawa_ledger.csv", help="one row per selection (D101)")
    args = ap.parse_args()
    engine = get_engine()
    rep = build_report(engine)
    m = rep["money"]
    print("1. COUPONS (argent réel, un pari par coupon)")
    print(f"  {m['coupons']} coupons : {m['won']} gagnés, {m['lost']} perdus, {m['refunded']} remboursés, "
          f"{m['open']} en cours.")
    if m["stakes"]:
        print(f"  Mises {m['stakes']:,.0f} FC, retours {m['returned']:,.2f} FC, net {m['net']:+,.2f} FC, "
              f"ROI {pct(m['roi'])}.")
        if m["roi_ci"]:
            print(f"  Intervalle du ROI (coupons rééchantillonnés) : {m['roi_ci'][0]:+.0%} à {m['roi_ci'][1]:+.0%}.")
    for h in rep["history"]:
        print(f"    {h['date']} coupon {h['coupon']} : net {h['net']:+,.2f} FC, cumul {h['cumulative']:+,.2f} FC")
    print("\n2. SÉLECTIONS JOUÉES (qualité des cotes prises ; l'argent est compté au point 1)")
    for name, s in rep["played"].items():
        print("  " + line(name, s))
    print("  Par compétition :")
    for name, s in rep["competitions"].items():
        print("    " + line(name, s))
    c = rep["counts"]
    print(f"\n3. OBSERVATIONS DE MARCHÉ ({c['prices']} cotes, {c['selections']} sélections distinctes)")
    for name, s in rep["observed"].items():
        print("  " + line(name, s))
    print("  Par plage de cotes :")
    for name, s in rep["bands"].items():
        print("    " + line(name, s))
    print(rep["reference"])
    print("\n4. ALERTES DE DONNÉES" + ("" if rep["alerts"] else " : aucune"))
    for a in rep["alerts"]:
        print(f"  - {a}")
    d = collect(engine)
    write_ledger(d["obs"] + d["played"], args.ledger)


if __name__ == "__main__":
    main()
