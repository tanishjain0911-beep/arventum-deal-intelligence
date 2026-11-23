"""Origination Radar: which companies are likely to raise their next round soon?

Method (survival-style panel classification):
  * Take "snapshots" of every known company on a series of cut-off dates.
  * Features use ONLY information available on that date (no look-ahead).
  * Label = did the company announce a new primary round within HORIZON months?
  * Train gradient-boosted trees on past snapshots, test on a later, unseen
    snapshot (walk-forward backtest), then score every company as of today.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from .data import STAGE_RANK, deal_investors, financials, funding_deals

HORIZON_M = 12
FEATURES = [
    "months_since_last", "last_stage_rank", "log_last_amount", "n_prior_rounds",
    "avg_gap_months", "log_total_raised", "n_investors", "has_top_investor",
    "last_had_lead", "sector_heat", "sector_deals_6m", "last_round_debt",
    "has_financials", "log_revenue", "rev_growth", "is_profitable",
]
FEATURE_LABELS = {
    "months_since_last": "Months since last round",
    "last_stage_rank": "Stage of last round",
    "log_last_amount": "Size of last round",
    "n_prior_rounds": "Rounds raised (since 2023)",
    "avg_gap_months": "Typical gap between rounds",
    "log_total_raised": "Total raised",
    "n_investors": "Number of backers",
    "has_top_investor": "Backed by a top-30 investor",
    "last_had_lead": "Last round had a named lead",
    "sector_heat": "Sector momentum (6m vs prior 6m)",
    "sector_deals_6m": "Sector deal volume (6m)",
    "last_round_debt": "Last round was debt",
    "has_financials": "Has public financials",
    "log_revenue": "Latest revenue",
    "rev_growth": "Revenue growth",
    "is_profitable": "Profitable",
}


def _months(a, b):
    return (a - b).dt.days / 30.44 if hasattr(a - b, "dt") else (a - b).days / 30.44


def snapshot(cutoff: pd.Timestamp, fd: pd.DataFrame, inv: pd.DataFrame, fin: pd.DataFrame,
             top_investors: set) -> pd.DataFrame:
    """Feature rows for every company with >=1 round before `cutoff`."""
    past = fd[fd.deal_date < cutoff]
    if past.empty:
        return pd.DataFrame()
    g = past.sort_values("deal_date").groupby("company_id")
    last = g.tail(1).set_index("company_id")
    out = pd.DataFrame(index=last.index)
    out["company"] = last.company
    out["sector"] = last.sector
    out["last_date"] = last.deal_date
    out["last_stage"] = last.stage
    out["months_since_last"] = (cutoff - last.deal_date).dt.days / 30.44
    out["last_stage_rank"] = last.stage.map(STAGE_RANK).astype(float)
    out["log_last_amount"] = np.log1p(last.amount_usd_m)
    out["last_round_debt"] = (last.deal_type == "debt").astype(int)
    out["n_prior_rounds"] = g.size()
    dates = past.groupby("company_id").deal_date
    span = (dates.max() - dates.min()).dt.days / 30.44
    out["avg_gap_months"] = (span / (out.n_prior_rounds - 1)).where(out.n_prior_rounds > 1)
    out["log_total_raised"] = np.log1p(past.groupby("company_id").amount_usd_m.sum(min_count=1))

    pinv = inv[inv.deal_id.isin(past.deal_id)].merge(past[["deal_id", "company_id"]], on="deal_id")
    out["n_investors"] = pinv.groupby("company_id").investor_id.nunique().reindex(out.index).fillna(0)
    out["has_top_investor"] = pinv[pinv.investor.isin(top_investors)].groupby("company_id").size() \
        .reindex(out.index).fillna(0).clip(upper=1)
    last_leads = inv[(inv.is_lead == 1) & inv.deal_id.isin(last.deal_id)].deal_id.unique()
    out["last_had_lead"] = last.deal_id.isin(last_leads).astype(int).values

    # sector momentum: deals in last 6m vs the 6m before
    s6 = past[past.deal_date >= cutoff - pd.DateOffset(months=6)].groupby("sector").size()
    p6 = past[(past.deal_date < cutoff - pd.DateOffset(months=6)) &
              (past.deal_date >= cutoff - pd.DateOffset(months=12))].groupby("sector").size()
    heat = (s6 / p6.reindex(s6.index).replace(0, np.nan)).fillna(1.0)
    out["sector_heat"] = out.sector.map(heat).fillna(1.0)
    out["sector_deals_6m"] = out.sector.map(s6).fillna(0)

    # financials that had been PUBLISHED before the cut-off (no look-ahead)
    known = fin[fin.published < cutoff].sort_values("fy")
    lastf = known.groupby("company_id").tail(1).set_index("company_id")
    prevf = known.groupby("company_id").nth(-2).set_index("company_id") if len(known) else known
    out["has_financials"] = out.index.isin(lastf.index).astype(int)
    out["log_revenue"] = np.log1p(lastf.revenue_inr_cr.reindex(out.index).clip(lower=0))
    growth = (lastf.revenue_inr_cr / prevf.revenue_inr_cr.reindex(lastf.index) - 1) \
        if len(prevf) else pd.Series(dtype=float)
    out["rev_growth"] = growth.reindex(out.index).clip(-1, 10)
    out["is_profitable"] = (lastf.profit_inr_cr.reindex(out.index) > 0).astype(float) \
        .where(out.has_financials == 1)
    return out


def label(snap: pd.DataFrame, cutoff: pd.Timestamp, fd: pd.DataFrame) -> pd.Series:
    end = cutoff + pd.DateOffset(months=HORIZON_M)
    nxt = fd[(fd.deal_date >= cutoff) & (fd.deal_date < end)].company_id.unique()
    return snap.index.isin(nxt).astype(int)


@dataclass
class RadarResult:
    model: object
    backtest: dict
    scores: pd.DataFrame
    importances: pd.Series


def _top_investors(fd, inv, before, n=30):
    ids = fd[fd.deal_date < before].deal_id
    return set(inv[inv.deal_id.isin(ids)].investor.value_counts().head(n).index)


def _build(cutoffs, fd, inv, fin, labelled=True):
    frames = []
    for c in cutoffs:
        s = snapshot(c, fd, inv, fin, _top_investors(fd, inv, c))
        if s.empty:
            continue
        # only companies whose last round is within 4 years (still "alive" in our window)
        s = s[s.months_since_last <= 48]
        s["cutoff"] = c
        if labelled:
            s["y"] = label(s, c, fd)
        frames.append(s)
    return pd.concat(frames) if frames else pd.DataFrame()


def _model():
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                          min_samples_leaf=40, l2_regularization=1.0, random_state=7)


def run(today: pd.Timestamp | None = None) -> RadarResult:
    fd = funding_deals()
    fd = fd[fd.stage != "secondary"]
    inv, fin = deal_investors(), financials()
    today = today or fd.deal_date.max().normalize()
    latest_labelled = today - pd.DateOffset(months=HORIZON_M)

    # ---- walk-forward backtest: train on cut-offs whose label window closed before the test cut-off
    test_cut = latest_labelled.to_period("M").to_timestamp()
    train_end = test_cut - pd.DateOffset(months=HORIZON_M)
    first = fd.deal_date.min() + pd.DateOffset(months=9)
    train_cuts = pd.date_range(first, train_end, freq="MS")
    backtest = {}
    if len(train_cuts) >= 3:
        tr = _build(train_cuts, fd, inv, fin)
        te = _build([test_cut], fd, inv, fin)
        m = _model().fit(tr[FEATURES], tr.y)
        p = m.predict_proba(te[FEATURES])[:, 1]
        te = te.assign(p=p).sort_values("p", ascending=False)
        base = te.y.mean()
        k = 100
        backtest = {
            "test_cutoff": str(test_cut.date()),
            "horizon_months": HORIZON_M,
            "train_snapshots": int(len(tr)),
            "test_companies": int(len(te)),
            "auc": round(float(roc_auc_score(te.y, te.p)), 3),
            "base_rate": round(float(base), 3),
            f"precision_top{k}": round(float(te.y.head(k).mean()), 3),
            f"lift_top{k}": round(float(te.y.head(k).mean() / base), 2) if base else None,
            "precision_top50": round(float(te.y.head(50).mean()), 3),
            "deciles": te.assign(decile=pd.qcut(te.p.rank(method="first", ascending=False), 10,
                                                labels=range(1, 11)))
                        .groupby("decile", observed=True).y.mean().round(3).tolist(),
        }

    # ---- final model: every cut-off whose label window has closed
    all_cuts = pd.date_range(first, latest_labelled, freq="MS")
    full = _build(all_cuts, fd, inv, fin)
    if full.empty or full.y.nunique() < 2:
        raise ValueError(f"Not enough history to train the Radar: data spans {fd.deal_date.min().date()} to "
                         f"{today.date()}, need > {HORIZON_M + 9} months.")
    model = _model().fit(full[FEATURES], full.y)

    now = _build([today], fd, inv, fin, labelled=False)
    now["probability"] = model.predict_proba(now[FEATURES])[:, 1]

    # importance via permutation on the training data (cheap version: AUC drop)
    rng = np.random.default_rng(0)
    sample = full.sample(min(len(full), 20000), random_state=0)
    base_auc = roc_auc_score(sample.y, model.predict_proba(sample[FEATURES])[:, 1])
    imp = {}
    for f in FEATURES:
        x = sample[FEATURES].copy()
        x[f] = rng.permutation(x[f].values)
        imp[FEATURE_LABELS[f]] = base_auc - roc_auc_score(sample.y, model.predict_proba(x)[:, 1])
    importances = pd.Series(imp).sort_values(ascending=False)

    scores = now.reset_index().rename(columns={"index": "company_id"})
    scores = scores.sort_values("probability", ascending=False)
    return RadarResult(model=model, backtest=backtest, scores=scores, importances=importances)


def explain_row(r: pd.Series) -> list[str]:
    """Plain-English signals behind a company's score (rule-based, transparent)."""
    out = []
    m = r.months_since_last
    if 14 <= m <= 30:
        out.append(f"Last raised {m:.0f} months ago — inside the typical 15-30 month fundraising window")
    elif m < 14:
        out.append(f"Raised only {m:.0f} months ago — may be early, but fast follow-ons happen in hot sectors")
    else:
        out.append(f"{m:.0f} months since last round — runway likely stretched")
    if r.get("sector_heat", 1) >= 1.15:
        out.append(f"{r.sector} deal activity up {100 * (r.sector_heat - 1):.0f}% vs the prior 6 months")
    if r.get("has_top_investor", 0) >= 1:
        out.append("Backed by one of the 30 most active investors (strong follow-on support)")
    if r.get("n_prior_rounds", 0) >= 2:
        out.append(f"{int(r.n_prior_rounds)} rounds since 2023 — a repeat fundraiser")
    if pd.notna(r.get("rev_growth")) and r.rev_growth > 0.3:
        out.append(f"Revenue grew {100 * r.rev_growth:.0f}% in latest reported year")
    if r.get("last_round_debt", 0) == 1:
        out.append("Last round was debt — often a bridge ahead of an equity round")
    return out
