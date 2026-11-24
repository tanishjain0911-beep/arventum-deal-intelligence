"""Price Finder: valuation benchmarking for a private tech company.

Three independent methods, shown together as a banker's "football field":
  1. Listed peers (sector)  : EV/Revenue of listed comparables in the same sector,
                              less a private-company (illiquidity) discount.
  2. Growth-adjusted peers  : regression of log(EV/Revenue) on revenue growth and
                              EBITDA margin across ALL listed comps, applied to the client.
  3. Private-market deals   : multiples implied by Indian private rounds in our database
                              (disclosed valuation / latest reported revenue).
All inputs and every comparable are shown so a banker can audit the number.
"""
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import pandas as pd

from .data import comparables, deals, financials

PRIVATE_DISCOUNT = 0.25   # typical DLOM range 20-30%
USD_INR = 88.0


@dataclass
class Valuation:
    ranges: list = field(default_factory=list)       # dicts: method, low, mid, high (INR cr)
    peers: pd.DataFrame = None
    private_comps: pd.DataFrame = None
    regression: dict = None
    notes: list = field(default_factory=list)


def _clean_comps(df):
    df = df[(df.ev_revenue > 0) & (df.ev_revenue < 60)].copy()
    df["growth"] = df.revenue_growth.clip(-0.5, 2.0)
    df["margin"] = df.ebitda_margin.clip(-1.0, 0.7)
    df["gross"] = df.gross_margin.clip(0, 1)
    return df


def growth_regression(df):
    """OLS: log(EV/Rev) = a + b*growth + c*EBITDA margin + d*gross margin + e*India.
    Specification chosen by leave-one-out CV (analysis/valuation_model_selection.py)."""
    d = df.dropna(subset=["growth", "margin"]).copy()
    d["gross"] = d.gross.fillna(d.gross.median())
    X = np.column_stack([np.ones(len(d)), d.growth, d.margin, d.gross, (d.market == "India").astype(float)])
    y = np.log(d.ev_revenue.values)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    resid_sd = float(np.std(y - pred))
    return {"intercept": coef[0], "growth": coef[1], "margin": coef[2], "gross": coef[3], "india": coef[4],
            "r2": float(r2), "resid_sd": resid_sd, "n": int(len(d))}


def sector_gross_margin(sector: str) -> float:
    c = _clean_comps(comparables())
    s = c[c.sector == sector].gross.dropna()
    return float(s.median()) if len(s) else float(c.gross.median())


@lru_cache(maxsize=1)
def _private_multiples_all() -> pd.DataFrame:
    """Vectorised: each valued round joined to the latest revenue published within ~6 months of it."""
    d = deals()
    d = d[d.valuation_usd_m.notna()][["deal_id", "company_id", "company", "sector", "deal_date", "stage",
                                       "valuation_usd_m", "source_url"]]
    fin = financials().dropna(subset=["revenue_inr_cr"])
    fin = fin[fin.revenue_inr_cr > 1][["company_id", "fy", "fiscal_year", "revenue_inr_cr", "published"]]
    m = d.merge(fin, on="company_id")
    m = m[m.published <= m.deal_date + pd.Timedelta(days=200)]
    if m.empty:
        return pd.DataFrame()
    m = m.sort_values("fy").groupby("deal_id").tail(1)
    m["valuation_inr_cr"] = (m.valuation_usd_m * USD_INR / 10).round()
    m["ev_revenue"] = m.valuation_inr_cr / m.revenue_inr_cr
    m["deal_date"] = m.deal_date.dt.date
    return m[["company", "sector", "deal_date", "stage", "valuation_inr_cr", "revenue_inr_cr", "fiscal_year",
              "ev_revenue", "source_url"]].reset_index(drop=True)


def private_multiples(sector: str | None):
    """EV/Revenue implied by private rounds with a disclosed valuation and a reported revenue."""
    out = _private_multiples_all()
    if out.empty:
        return out
    out = out[(out.ev_revenue > 0.2) & (out.ev_revenue < 80)]
    if sector:
        same = out[out.sector == sector]
        if len(same) >= 4:
            return same.sort_values("deal_date", ascending=False)
    return out.sort_values("deal_date", ascending=False)


def value_company(sector: str, revenue_inr_cr: float, growth: float, ebitda_margin: float,
                  market_scope: str = "Both", gross_margin: float | None = None) -> Valuation:
    v = Valuation()
    if gross_margin is None:
        gross_margin = sector_gross_margin(sector)
        v.notes.append(f"Gross margin not given; using the {sector} peer median of {gross_margin:.0%}.")
    comps = _clean_comps(comparables())
    if market_scope != "Both":
        scoped = comps[comps.market == market_scope]
    else:
        scoped = comps

    # ---- 1. sector peers
    peers = scoped[scoped.sector == sector]
    if len(peers) < 3:
        peers = comps[comps.sector == sector]
        v.notes.append("Few listed peers in the chosen market; using both India and global peers.")
    if len(peers) >= 2:
        q1, q2, q3 = peers.ev_revenue.quantile([0.25, 0.5, 0.75])
        k = (1 - PRIVATE_DISCOUNT) * revenue_inr_cr
        v.ranges.append({"method": "Listed sector peers (25th-75th pct, after 25% private discount)",
                         "low": q1 * k, "mid": q2 * k, "high": q3 * k,
                         "multiple": f"{q1:.1f}x - {q3:.1f}x EV/Revenue (median {q2:.1f}x)"})
    v.peers = peers.sort_values("ev_revenue", ascending=False)

    # ---- 2. growth-adjusted regression across all comps
    reg = growth_regression(comps)
    v.regression = reg
    india = 1.0 if market_scope == "India" else 0.5 if market_scope == "Both" else 0.0
    log_m = reg["intercept"] + reg["growth"] * np.clip(growth, -0.5, 2) + \
        reg["margin"] * np.clip(ebitda_margin, -1, 0.7) + reg["gross"] * np.clip(gross_margin, 0, 1) + \
        reg["india"] * india
    sd = reg["resid_sd"] * 0.674  # +/- one inter-quartile half-width
    k = (1 - PRIVATE_DISCOUNT) * revenue_inr_cr
    v.ranges.append({"method": "Growth, margin & gross-margin adjusted (regression on listed comps)",
                     "low": np.exp(log_m - sd) * k, "mid": np.exp(log_m) * k, "high": np.exp(log_m + sd) * k,
                     "multiple": f"{np.exp(log_m):.1f}x implied EV/Revenue (R² {reg['r2']:.2f}, n={reg['n']})"})

    # ---- 3. private market multiples
    pm = private_multiples(sector)
    v.private_comps = pm
    if len(pm) >= 3:
        q1, q2, q3 = pm.ev_revenue.quantile([0.25, 0.5, 0.75])
        scope = "same sector" if (pm.sector == sector).all() else "all sectors"
        v.ranges.append({"method": f"Indian private rounds ({scope}, n={len(pm)})",
                         "low": q1 * revenue_inr_cr, "mid": q2 * revenue_inr_cr, "high": q3 * revenue_inr_cr,
                         "multiple": f"{q1:.1f}x - {q3:.1f}x valuation/revenue (median {q2:.1f}x)"})
    else:
        v.notes.append("Not enough Indian private rounds with both valuation and revenue disclosed.")
    return v


def blended_range(v: Valuation):
    if not v.ranges:
        return None
    lows = [r["low"] for r in v.ranges]
    mids = [r["mid"] for r in v.ranges]
    highs = [r["high"] for r in v.ranges]
    return float(np.median(lows)), float(np.median(mids)), float(np.median(highs))
