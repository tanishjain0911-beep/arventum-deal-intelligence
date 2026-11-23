"""Market Pulse: sector-level market intelligence computed from the deal database.

All functions return plain DataFrames / dicts, so they can feed a dashboard, a PDF, or a weekly email.
"""
import numpy as np
import pandas as pd

from .data import STAGE_ORDER, deal_investors, deals, funding_deals, weekly_totals

FOCUS = None  # set lazily from pipeline.sectors to avoid import cycles


def _focus():
    global FOCUS
    if FOCUS is None:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
        from sectors import ARVENTUM_FOCUS
        FOCUS = ARVENTUM_FOCUS
    return FOCUS


def monthly(sector: str | None = None) -> pd.DataFrame:
    """Deals and $ raised per month (primary rounds), optionally for one sector."""
    fd = funding_deals()
    if sector:
        fd = fd[fd.sector == sector]
    m = fd.assign(month=fd.deal_date.dt.to_period("M").dt.to_timestamp()) \
        .groupby("month").agg(deals=("deal_id", "count"), usd_m=("amount_usd_m", "sum"),
                              median_usd_m=("amount_usd_m", "median"))
    return m.asfreq("MS", fill_value=0)


def sector_heat(asof: pd.Timestamp | None = None, window_m: int = 6) -> pd.DataFrame:
    """Momentum per sector: last `window_m` months vs the prior `window_m` months (deal count and $)."""
    fd = funding_deals()
    asof = asof or fd.deal_date.max()
    cur = fd[(fd.deal_date > asof - pd.DateOffset(months=window_m)) & (fd.deal_date <= asof)]
    prev = fd[(fd.deal_date > asof - pd.DateOffset(months=2 * window_m)) &
              (fd.deal_date <= asof - pd.DateOffset(months=window_m))]
    a = cur.groupby("sector").agg(deals=("deal_id", "count"), usd_m=("amount_usd_m", "sum"))
    b = prev.groupby("sector").agg(deals_prev=("deal_id", "count"), usd_m_prev=("amount_usd_m", "sum"))
    h = a.join(b, how="outer").fillna(0)
    h["deal_growth_pct"] = 100 * (h.deals / h.deals_prev.replace(0, np.nan) - 1)
    h["usd_growth_pct"] = 100 * (h.usd_m / h.usd_m_prev.replace(0, np.nan) - 1)
    h["arventum_focus"] = h.index.isin(_focus())
    return h.sort_values("usd_m", ascending=False).round(1)


def top_investors(sector: str | None = None, months: int = 12, n: int = 15) -> pd.DataFrame:
    fd = funding_deals()
    fd = fd[fd.deal_date > fd.deal_date.max() - pd.DateOffset(months=months)]
    if sector:
        fd = fd[fd.sector == sector]
    inv = deal_investors()
    inv = inv[(inv.investor_type != "Individual") & inv.deal_id.isin(fd.deal_id)]
    x = inv.merge(fd[["deal_id", "amount_usd_m", "company"]], on="deal_id")
    g = x.groupby("investor").agg(deals=("deal_id", "nunique"), led=("is_lead", "sum"),
                                  hq=("hq_country", "first"), type=("ai_type", "first"),
                                  recent_companies=("company", lambda s: ", ".join(s.tolist()[-3:])))
    return g.sort_values(["deals", "led"], ascending=False).head(n).reset_index()


def stage_benchmarks(sector: str | None = None, years: int = 2) -> pd.DataFrame:
    """Typical round sizes by stage (median and inter-quartile range), last `years` years."""
    fd = funding_deals()
    fd = fd[(fd.deal_date > fd.deal_date.max() - pd.DateOffset(years=years)) & fd.amount_usd_m.notna()]
    if sector:
        fd = fd[fd.sector == sector]
    g = fd[fd.stage.isin(STAGE_ORDER)].groupby("stage").amount_usd_m
    out = pd.DataFrame({"deals": g.size(), "p25": g.quantile(0.25), "median": g.median(), "p75": g.quantile(0.75)})
    return out.reindex([s for s in STAGE_ORDER if s in out.index]).round(2)


def recent_deals(sector: str | None = None, n: int = 25) -> pd.DataFrame:
    d = deals()
    if sector:
        d = d[d.sector == sector]
    inv = deal_investors()
    leads = inv[inv.is_lead == 1].groupby("deal_id").investor.apply(lambda s: ", ".join(s))
    d = d.assign(lead_investors=d.deal_id.map(leads))
    return d.sort_values("deal_date", ascending=False).head(n)[
        ["deal_date", "company", "sector", "deal_type", "stage", "amount_usd_m", "lead_investors", "acquirer",
         "source_url"]]


def market_vs_reported() -> pd.DataFrame:
    """Our weekly totals next to the published weekly totals (transparency on coverage)."""
    w = weekly_totals()
    fd = funding_deals()
    rows = []
    for _, r in w.iterrows():
        m = fd[(fd.deal_date > r.week_end - pd.Timedelta(days=7)) & (fd.deal_date <= r.week_end)]
        rows.append({"week_end": r.week_end, "reported_deals": r.deal_count, "our_deals": len(m),
                     "reported_usd_m": r.total_usd_m, "our_usd_m": m.amount_usd_m.sum()})
    return pd.DataFrame(rows)


def sector_brief_facts(sector: str) -> dict:
    """Structured facts for a one-paragraph sector brief (the text itself can be written by an LLM)."""
    heat = sector_heat()
    row = heat.loc[sector] if sector in heat.index else None
    ti = top_investors(sector, n=5)
    rd = recent_deals(sector, n=5)
    return {
        "sector": sector,
        "deals_6m": None if row is None else int(row.deals),
        "usd_m_6m": None if row is None else float(row.usd_m),
        "deal_growth_pct": None if row is None else row.deal_growth_pct,
        "usd_growth_pct": None if row is None else row.usd_growth_pct,
        "top_investors": ti.investor.tolist(),
        "largest_recent": rd.sort_values("amount_usd_m", ascending=False).head(3)[["company", "amount_usd_m"]]
        .to_dict("records"),
    }
