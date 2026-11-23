"""Coverage audit: how many of the market's deals did we capture?

Entrackr's weekly report states the number of funding deals each week. We compare it with
the number of primary rounds (equity + debt) in our database dated in the same week
(report week = the 7 days ending on the report date). The ratio is our recall estimate.
Output: data/processed/coverage.json, data/processed/coverage_weekly.csv
"""
import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    con = sqlite3.connect(ROOT / "db" / "deals.db")
    wk = pd.read_sql("SELECT week_end, deal_count, total_usd_m FROM weekly_totals", con, parse_dates=["week_end"])
    d = pd.read_sql("SELECT deal_date, amount_usd_m FROM deals WHERE deal_type IN ('equity','debt')", con,
                    parse_dates=["deal_date"])
    con.close()
    rows = []
    for _, w in wk.iterrows():
        start = w.week_end - pd.Timedelta(days=6)
        m = d[(d.deal_date >= start) & (d.deal_date <= w.week_end)]
        rows.append({"week_end": w.week_end.date(), "reported_deals": w.deal_count, "our_deals": len(m),
                     "reported_usd_m": w.total_usd_m, "our_usd_m": round(m.amount_usd_m.sum(), 1)})
    cov = pd.DataFrame(rows)
    if cov.empty:
        print("no weekly reports parsed yet")
        return
    cov["deal_recall"] = (cov.our_deals / cov.reported_deals).clip(upper=1.5)
    cov["usd_recall"] = (cov.our_usd_m / cov.reported_usd_m).clip(upper=1.5)
    cov.to_csv(ROOT / "data" / "processed" / "coverage_weekly.csv", index=False)
    summary = {
        "weeks_compared": int(len(cov)),
        "reported_deals_total": int(cov.reported_deals.sum()),
        "our_deals_total": int(cov.our_deals.sum()),
        "deal_recall_pct": round(100 * cov.our_deals.sum() / cov.reported_deals.sum(), 1),
        "usd_recall_pct": round(100 * cov.our_usd_m.sum() / cov.reported_usd_m.sum(), 1),
        "median_weekly_deal_recall_pct": round(100 * cov.deal_recall.median(), 1),
    }
    (ROOT / "data" / "processed" / "coverage.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(cov.tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
