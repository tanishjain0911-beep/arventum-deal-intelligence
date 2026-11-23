"""Synthetic end-to-end test of the Origination Radar (no database needed).

Simulates 1,500 companies raising rounds on noisy ~20-month cycles (some die), then runs the full
radar pipeline. The model must (a) run end to end, (b) learn the cycle (AUC well above 0.5),
and (c) beat or match the months-since-last-round heuristic.
Run: python tests/test_radar_synthetic.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from lib import radar  # noqa: E402

rng = np.random.default_rng(42)
STAGES = ["seed", "series-a", "series-b", "series-c", "series-d"]
SECTORS = ["SaaS", "FinTech & Payments", "HealthTech", "E-commerce & D2C"]
rows, inv_rows, did = [], [], 0
for cid in range(1500):
    t = pd.Timestamp("2021-01-01") + pd.Timedelta(days=int(rng.integers(0, 900)))
    cycle = rng.normal(20, 4)
    stage = 0
    alive = True
    while t < pd.Timestamp("2026-11-01") and alive:
        did += 1
        rows.append({"deal_id": did, "company_id": cid, "company": f"C{cid}", "sector": SECTORS[cid % 4],
                     "deal_date": t, "stage": STAGES[min(stage, 4)], "deal_type": "equity",
                     "amount_usd_m": float(2 * (stage + 1) ** 2 * rng.lognormal(0, 0.3))})
        for k in range(int(rng.integers(1, 4))):
            inv_rows.append({"deal_id": did, "is_lead": int(k == 0), "investor_id": int(rng.integers(0, 200)),
                             "investor": f"I{int(rng.integers(0, 200))}", "investor_type": "Institutional"})
        stage += 1
        alive = rng.random() > 0.15
        t = t + pd.Timedelta(days=int(max(4, rng.normal(cycle, 3)) * 30.44))
fd = pd.DataFrame(rows)
inv = pd.DataFrame(inv_rows)
fin = pd.DataFrame(columns=["company_id", "company", "sector", "fiscal_year", "revenue_inr_cr", "profit_inr_cr",
                            "source_url", "published", "fy"]).astype({"published": "datetime64[ns]", "fy": float,
                                                                      "revenue_inr_cr": float, "profit_inr_cr": float})
radar.funding_deals = lambda: fd
radar.deal_investors = lambda: inv
radar.financials = lambda: fin

res = radar.run(today=pd.Timestamp("2026-11-01"))
s = res.backtest.get("summary", {})
print("folds:", len(res.backtest.get("folds", [])), "summary:", s)
print("top features:", res.importances.head(5).round(4).to_dict())
print("scored companies:", len(res.scores))
ok = s and s["mean_auc"] > 0.65 and s["mean_auc"] >= s["mean_auc_heuristic"] - 0.02 and len(res.scores) > 100
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
