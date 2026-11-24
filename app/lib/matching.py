"""Investor Matchmaker: rank investors for a company profile, with reasons.

Each investor's "taste profile" is built from the deals it joined:
  sector fit   : share of its deals in the client's sector (recency-weighted)
  stage fit    : share of its deals at the same or adjacent stage
  cheque fit   : how close the requested round is to rounds it usually joins
  activity     : recency-weighted number of deals in the last 18 months
  lead bonus   : how often it leads (useful when the client needs a lead)
The score is a weighted geometric blend; weights were chosen on a 2025 validation
window and are evaluated out-of-sample on 2026 deals (see backtest()).
"""
import numpy as np
import pandas as pd

from .data import STAGE_RANK, deal_investors, funding_deals

W = {"sector": 0.35, "stage": 0.2, "cheque": 0.15, "activity": 0.25, "lead": 0.05}
try:  # weights tuned on a validation window by analysis/tune_matching.py (test window kept separate)
    import json as _json
    from pathlib import Path as _P
    _wf = _P(__file__).resolve().parents[2] / "data" / "processed" / "matching_weights.json"
    if _wf.exists():
        W = _json.loads(_wf.read_text(encoding="utf-8"))
except Exception:  # noqa: BLE001
    pass
HALF_LIFE_DAYS = 365


def _history(asof: pd.Timestamp):
    fd = funding_deals()
    fd = fd[fd.deal_date < asof]
    inv = deal_investors()
    inv = inv[inv.investor_type != "Individual"]
    h = inv.merge(fd[["deal_id", "deal_date", "sector", "stage", "amount_usd_m", "company"]], on="deal_id")
    age = (asof - h.deal_date).dt.days
    h["w"] = 0.5 ** (age / HALF_LIFE_DAYS)
    h["stage_rank"] = h.stage.map(STAGE_RANK)
    return h


def rank(sector: str, stage: str, amount_usd_m: float | None, asof: pd.Timestamp | None = None,
         need_lead: bool = False, top: int = 50, history: pd.DataFrame | None = None,
         foreign_only: bool = False, investor_types: list | None = None) -> pd.DataFrame:
    """Rank investors for a deal profile. Optional filters: foreign_only (HQ outside India) and
    investor_types (AI-classified types, e.g. ["Private Equity / Growth", "Corporate / CVC"])."""
    asof = asof or funding_deals().deal_date.max() + pd.Timedelta(days=1)
    h = history if history is not None else _history(asof)
    if h.empty:
        return pd.DataFrame()
    if foreign_only and "is_foreign" in h:
        h = h[h.is_foreign == 1]
    if investor_types and "ai_type" in h:
        h = h[h.ai_type.isin(investor_types)]
    if h.empty:
        return pd.DataFrame()
    srank = STAGE_RANK.get(stage)
    keys = ["investor_id", "investor", "investor_type"]
    g = h.groupby(keys)
    tot_w = g.w.sum()
    # Empirical-Bayes shrinkage: an investor with 1 deal can't "prove" a 100% sector focus.
    # share = (weighted deals in sector + M * market share) / (weighted deals + M)
    M = 3.0
    market_sector = (h.sector == sector).mean()
    sec_w = h[h.sector == sector].groupby(keys).w.sum().reindex(tot_w.index).fillna(0)
    sector_fit = (sec_w + M * market_sector) / (tot_w + M)
    if srank is not None:
        near_mask = (h.stage_rank - srank).abs() <= 1
        market_stage = near_mask.mean()
        near_w = h[near_mask].groupby(keys).w.sum().reindex(tot_w.index).fillna(0)
        stage_fit = (near_w + M * market_stage) / (tot_w + M)
    else:
        stage_fit = pd.Series(0.5, index=tot_w.index)
    if amount_usd_m:
        med = g.amount_usd_m.median()
        cheque_fit = np.exp(-np.abs(np.log((med + 0.1) / (amount_usd_m + 0.1))) / 1.2).fillna(0.3)
    else:
        cheque_fit = pd.Series(0.5, index=tot_w.index)
    recent = h[h.deal_date >= asof - pd.Timedelta(days=548)]
    act = recent.groupby(["investor_id", "investor", "investor_type"]).size().reindex(tot_w.index).fillna(0)
    activity = np.log1p(act) / np.log1p(act.max() or 1)
    lead_rate = g.is_lead.mean()
    lead = lead_rate if need_lead else pd.Series(0.5, index=tot_w.index)

    eps = 0.02
    score = np.exp(W["sector"] * np.log(sector_fit + eps) + W["stage"] * np.log(stage_fit + eps) +
                   W["cheque"] * np.log(cheque_fit + eps) + W["activity"] * np.log(activity + eps) +
                   W["lead"] * np.log(lead + eps))
    out = pd.DataFrame({"score": score, "sector_fit": sector_fit, "stage_fit": stage_fit,
                        "cheque_fit": cheque_fit, "activity_18m": act, "lead_rate": lead_rate,
                        "median_round_usd_m": g.amount_usd_m.median(),
                        "deals_total": g.size(), "deals_in_sector": h[h.sector == sector]
                        .groupby(keys).size().reindex(tot_w.index).fillna(0)}).reset_index()
    out = out[out.activity_18m > 0].sort_values("score", ascending=False).head(top)
    out["match_pct"] = (100 * out.score / out.score.max()).round(0)
    return out


def reasons(row: pd.Series, sector: str, history: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    ex = history[(history.investor_id == row.investor_id) & (history.sector == sector)] \
        .sort_values("deal_date", ascending=False)
    parts = []
    if row.deals_in_sector:
        parts.append(f"{int(row.deals_in_sector)} {sector} deals")
    parts.append(f"{int(row.activity_18m)} deals in last 18 months")
    if pd.notna(row.median_round_usd_m):
        parts.append(f"typical round ${row.median_round_usd_m:.1f}M")
    if row.lead_rate >= 0.4:
        parts.append(f"leads {100 * row.lead_rate:.0f}% of its deals")
    return " · ".join(parts), ex[["deal_date", "company", "stage", "amount_usd_m"]].head(5)


def backtest(start=None, ks=(10, 20, 50)):
    """For each round in the test window (default: the latest 6 months of data): rank investors using ONLY
    prior data, check if a real participant made the top-k.
    Baseline = rank by overall activity alone (what you'd get from 'most active investors' lists)."""
    fd = funding_deals()
    if start is None:  # latest 6 months of deals with complete (AI-extracted) investor lists
        ai = fd[fd.agent != "rules"] if "agent" in fd else fd
        start = str((ai.deal_date.max() - pd.DateOffset(months=6)).date())
    inv = deal_investors()
    inv = inv[inv.investor_type != "Individual"]
    test = fd[(fd.deal_date >= start) & fd.stage.isin(STAGE_RANK)]
    # judge only against complete investor lists: rule-extracted deals carry headline investors only
    if "agent" in test:
        test = test[test.agent != "rules"]
    test = test[test.deal_id.isin(inv.deal_id)]
    hist_cache = {}
    hits = {k: 0 for k in ks}
    base_hits = {k: 0 for k in ks}
    n = 0
    for _, d in test.iterrows():
        month = d.deal_date.to_period("M").to_timestamp()
        if month not in hist_cache:
            hist_cache[month] = _history(month)
        h = hist_cache[month]
        actual = set(inv[inv.deal_id == d.deal_id].investor_id)
        if not actual & set(h.investor_id):
            continue  # all investors are first-timers; no model could know them
        r = rank(d.sector, d.stage, d.amount_usd_m, asof=month, history=h, top=max(ks))
        recent = h[h.deal_date >= month - pd.Timedelta(days=548)]
        base = recent.investor_id.value_counts().head(max(ks)).index.tolist()
        n += 1
        for k in ks:
            hits[k] += bool(actual & set(r.investor_id.head(k)))
            base_hits[k] += bool(actual & set(base[:k]))
    return {"test_deals": n, "period_start": start,
            "model_hit_rate": {k: round(hits[k] / n, 3) for k in ks} if n else {},
            "baseline_hit_rate": {k: round(base_hits[k] / n, 3) for k in ks} if n else {}}
