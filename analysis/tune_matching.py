"""Tune Investor Matchmaker weights on a validation window, report on an untouched test window.

  validation: rounds between (end - 12 months) and (end - 6 months)  -> pick weights
  test      : rounds in the last 6 months                            -> report (never used for tuning)
Output: data/processed/matching_tuning.json (+ writes the chosen weights to data/processed/matching_weights.json)
"""
import functools
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from lib import data, matching  # noqa: E402

matching._history = functools.lru_cache(maxsize=64)(matching._history)  # one history per month, reused

fd = data.funding_deals()
end = fd.deal_date.max()
val_start, test_start = end - pd.DateOffset(months=12), end - pd.DateOffset(months=6)


def score(w, start, stop):
    matching.W = w
    res = matching.backtest(start=str(start.date()))
    # backtest runs to the end of data; for validation restrict by re-running on a truncated frame
    return res


def window_backtest(w, start, stop, ks=(10, 20, 50)):
    matching.W = w
    inv = data.deal_investors()
    inv = inv[inv.investor_type != "Individual"]
    test = fd[(fd.deal_date >= start) & (fd.deal_date < stop) & fd.stage.isin(data.STAGE_RANK)]
    test = test[test.deal_id.isin(inv.deal_id)]
    hits, base, n = {k: 0 for k in ks}, {k: 0 for k in ks}, 0
    for _, d in test.iterrows():
        month = d.deal_date.to_period("M").to_timestamp()
        h = matching._history(month)
        actual = set(inv[inv.deal_id == d.deal_id].investor_id)
        if not actual & set(h.investor_id):
            continue
        r = matching.rank(d.sector, d.stage, d.amount_usd_m, asof=month, history=h, top=max(ks))
        recent = h[h.deal_date >= month - pd.Timedelta(days=548)]
        b = recent.investor_id.value_counts().head(max(ks)).index.tolist()
        n += 1
        for k in ks:
            hits[k] += bool(actual & set(r.investor_id.head(k)))
            base[k] += bool(actual & set(b[:k]))
    return n, {k: hits[k] / n for k in ks}, {k: base[k] / n for k in ks}


grid = []
for s, st, ch, a in itertools.product([0.15, 0.3, 0.45], [0.0, 0.15, 0.3], [0.0, 0.15], [0.25, 0.45, 0.7]):
    w = {"sector": s, "stage": st, "cheque": ch, "activity": a, "lead": 0.05}
    n, m, b = window_backtest(w, val_start, test_start)
    obj = (m[10] + m[20] + m[50]) / 3
    grid.append((obj, w, m, b, n))
    print(f"val obj {obj:.3f}  {w}", flush=True)
grid.sort(key=lambda g: -g[0])
best = grid[0]
n_t, m_t, b_t = window_backtest(best[1], test_start, end + pd.Timedelta(days=1))
default = {"sector": 0.35, "stage": 0.2, "cheque": 0.15, "activity": 0.25, "lead": 0.05}
_, m_d, _ = window_backtest(default, test_start, end + pd.Timedelta(days=1))
out = {"validation_window": [str(val_start.date()), str(test_start.date())], "validation_deals": best[4],
       "best_weights": best[1], "validation_hit_rate": best[2], "validation_baseline": best[3],
       "test_window_start": str(test_start.date()), "test_deals": n_t,
       "test_hit_rate": m_t, "test_baseline_hit_rate": b_t, "test_hit_rate_default_weights": m_d}
(ROOT / "data" / "processed" / "matching_tuning.json").write_text(json.dumps(out, indent=2, default=str),
                                                                   encoding="utf-8")
(ROOT / "data" / "processed" / "matching_weights.json").write_text(json.dumps(best[1]), encoding="utf-8")
print(json.dumps(out, indent=2, default=str))
