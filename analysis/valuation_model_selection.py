"""Which listed-company characteristics best explain EV/Revenue multiples?

Compares candidate regressions with leave-one-out cross-validation (out-of-sample error,
not in-sample R²), so the Price Finder uses the specification that actually generalises.
Output: data/processed/valuation_model_selection.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "processed" / "comparables.csv")
df = df[(df.ev_revenue > 0) & (df.ev_revenue < 60)].dropna(subset=["revenue_growth", "ebitda_margin"]).copy()
df["growth"] = df.revenue_growth.clip(-0.5, 2.0)
df["margin"] = df.ebitda_margin.clip(-1.0, 0.7)
df["rule40"] = df.growth + df.margin
df["gross"] = df.gross_margin.fillna(df.gross_margin.median()).clip(0, 1)
df["india"] = (df.market == "India").astype(float)
df["y"] = np.log(df.ev_revenue)
# coarse sector families: software-like businesses command structurally higher multiples
SOFTWARE = {"SaaS", "Enterprise Software", "Cybersecurity", "Cloud Infrastructure", "Data Infrastructure",
            "Developer Tools", "Artificial Intelligence", "Semiconductors"}
df["software"] = df.sector.isin(SOFTWARE).astype(float)

SPECS = {
    "growth + margin + india": ["growth", "margin", "india"],
    "rule of 40 + india": ["rule40", "india"],
    "rule of 40 + gross margin + india": ["rule40", "gross", "india"],
    "growth + margin + gross margin + india": ["growth", "margin", "gross", "india"],
    "rule of 40 + gross + software + india": ["rule40", "gross", "software", "india"],
    "growth + margin + gross + software + india": ["growth", "margin", "gross", "software", "india"],
}


def loo_rmse(cols):
    X = np.column_stack([np.ones(len(df))] + [df[c].values for c in cols])
    y = df.y.values
    errs = []
    for i in range(len(df)):
        m = np.ones(len(df), bool)
        m[i] = False
        coef, *_ = np.linalg.lstsq(X[m], y[m], rcond=None)
        errs.append(y[i] - X[i] @ coef)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return float(np.sqrt(np.mean(np.square(errs)))), float(r2), dict(zip(["intercept"] + cols, coef.round(3)))


baseline = float(np.sqrt(np.mean((df.y - df.y.mean()) ** 2)))
results = {"n": len(df), "baseline_rmse_log": round(baseline, 3), "specs": {}}
print(f"n={len(df)}  baseline (predict the mean) RMSE(log) = {baseline:.3f}")
for name, cols in SPECS.items():
    rmse, r2, coef = loo_rmse(cols)
    results["specs"][name] = {"loo_rmse_log": round(rmse, 3), "in_sample_r2": round(r2, 3), "coef": coef}
    print(f"  {name:45s} LOO-RMSE {rmse:.3f}   R² {r2:.2f}   {coef}")
best = min(results["specs"], key=lambda k: results["specs"][k]["loo_rmse_log"])
results["best"] = best
print("best:", best)
(ROOT / "data" / "processed" / "valuation_model_selection.json").write_text(json.dumps(results, indent=2),
                                                                           encoding="utf-8")
