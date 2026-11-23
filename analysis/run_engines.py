"""Run all analytics engines against the current database and save their outputs + backtests.

Outputs (data/processed/):
  radar_scores.csv, radar_backtest.json, radar_importance.csv
  matching_backtest.json
  valuation_example.json
"""
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from lib import matching, radar, valuation  # noqa: E402

OUT = ROOT / "data" / "processed"


def section(name):
    def deco(fn):
        def run():
            t = time.time()
            print(f"\n== {name}")
            try:
                fn()
            except Exception:  # noqa: BLE001
                traceback.print_exc(limit=3)
            print(f"   ({time.time() - t:.0f}s)")
        return run
    return deco


@section("Origination Radar")
def do_radar():
    res = radar.run()
    print(json.dumps(res.backtest, indent=1))
    print(res.importances.round(4).head(10))
    cols = ["company", "sector", "last_stage", "last_date", "months_since_last", "n_prior_rounds", "probability"]
    print(res.scores[cols].head(15).to_string(index=False))
    res.scores.to_csv(OUT / "radar_scores.csv", index=False)
    (OUT / "radar_backtest.json").write_text(json.dumps(res.backtest, indent=2), encoding="utf-8")
    res.importances.rename("auc_drop").to_csv(OUT / "radar_importance.csv")


@section("Investor Matchmaker")
def do_matching():
    top = matching.rank("FinTech & Payments", "seed", 2)
    print(top[["investor", "investor_type", "match_pct", "deals_in_sector", "activity_18m",
               "median_round_usd_m"]].head(12).to_string(index=False))
    bt = matching.backtest()
    print(bt)
    (OUT / "matching_backtest.json").write_text(json.dumps(bt, indent=2), encoding="utf-8")


@section("Price Finder: SaaS, Rs 150 cr revenue, 50% growth, 10% EBITDA margin")
def do_valuation():
    v = valuation.value_company("SaaS", 150, 0.5, 0.10, "Both")
    for r in v.ranges:
        print(f"  {r['method']:70s} Rs {r['low']:,.0f} - {r['high']:,.0f} cr  ({r['multiple']})")
    print("  blended:", valuation.blended_range(v))
    print("  regression:", {k: round(x, 3) for k, x in v.regression.items()})
    print("  notes:", v.notes)
    (OUT / "valuation_example.json").write_text(json.dumps(
        {"input": {"sector": "SaaS", "revenue_inr_cr": 150, "growth": 0.5, "ebitda_margin": 0.1},
         "ranges": v.ranges, "regression": v.regression, "notes": v.notes,
         "n_private_comps": 0 if v.private_comps is None else len(v.private_comps)}, indent=2, default=float),
        encoding="utf-8")


if __name__ == "__main__":
    which = sys.argv[1:] or ["radar", "matching", "valuation"]
    for w in which:
        {"radar": do_radar, "matching": do_matching, "valuation": do_valuation}[w]()
