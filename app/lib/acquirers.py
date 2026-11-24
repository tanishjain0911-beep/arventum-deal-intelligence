"""Buyer Mapping: who acquires Indian tech companies? (supports Arventum's sell-side M&A work)

For a target profile (sector), rank acquirers by:
  sector relevance : acquisitions in the same sector (shrunk toward the market share, as in matching.py)
  appetite         : number of acquisitions in the last 24 months (serial acquirers rank higher)
  recency          : months since the most recent acquisition
Also summarises the M&A market: acquisitions per year, by sector, and the share of foreign acquirers.
"""
import numpy as np
import pandas as pd

from .data import deals

KEYS = ["acquirer"]


def acquisitions() -> pd.DataFrame:
    d = deals()
    a = d[(d.deal_type == "acquisition") & d.acquirer.notna()].sort_values("deal_date").copy()
    # Announcement, completion and regulator approval of one acquisition arrive as separate articles:
    # count each buyer-target pair once, dated at announcement, with any disclosed price.
    a["amount_usd_m"] = a.groupby(["company_id", "acquirer"]).amount_usd_m.transform("max")
    return a.drop_duplicates(["company_id", "acquirer"], keep="first")


def rank_buyers(sector: str, asof: pd.Timestamp | None = None, top: int = 30) -> pd.DataFrame:
    a = acquisitions()
    asof = asof or a.deal_date.max() + pd.Timedelta(days=1)
    a = a[a.deal_date < asof]
    if a.empty:
        return pd.DataFrame()
    M = 2.0
    market = (a.sector == sector).mean()
    g = a.groupby("acquirer")
    n = g.size()
    in_sector = a[a.sector == sector].groupby("acquirer").size().reindex(n.index).fillna(0)
    sector_fit = (in_sector + M * market) / (n + M)
    recent = a[a.deal_date >= asof - pd.DateOffset(months=24)].groupby("acquirer").size().reindex(n.index).fillna(0)
    months_since = (asof - g.deal_date.max()).dt.days / 30.44
    appetite = np.log1p(recent) / np.log1p(max(recent.max(), 1))
    recency = np.exp(-months_since / 18)
    score = (sector_fit + 0.02) ** 0.45 * (appetite + 0.02) ** 0.35 * (recency + 0.02) ** 0.20
    out = pd.DataFrame({"score": score, "acquisitions_total": n, "in_sector": in_sector,
                        "last_24m": recent, "months_since_last": months_since.round(1),
                        "targets": g.company.apply(lambda s: ", ".join(s.tolist()[-4:]))}).reset_index()
    out = out.sort_values("score", ascending=False).head(top)
    out["match_pct"] = (100 * out.score / out.score.max()).round(0)
    return out


def market_summary() -> dict:
    a = deals()
    a = a[a.deal_type == "acquisition"].copy()
    a["year"] = a.deal_date.dt.year
    return {
        "acquisitions_by_year": a.groupby("year").size().to_dict(),
        "top_sectors": a.sector.value_counts().head(10).to_dict(),
        "serial_acquirers": a.acquirer.value_counts().head(15).to_dict(),
        "disclosed_value_pct": round(100 * a.amount_usd_m.notna().mean(), 1),
    }
