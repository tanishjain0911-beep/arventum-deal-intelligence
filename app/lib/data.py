"""Data access layer: loads the SQLite deal database into pandas frames."""
import sqlite3
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "db" / "deals.db"
PROCESSED = ROOT / "data" / "processed"


def _con():
    return sqlite3.connect(DB)


@lru_cache(maxsize=1)
def deals() -> pd.DataFrame:
    """One row per deal, with company attributes and investor lists."""
    with _con() as con:
        df = pd.read_sql("""
            SELECT d.deal_id, d.deal_date, d.deal_type, d.stage, d.amount_usd_m, d.amount_inr_cr,
                   d.valuation_usd_m, d.confidence, d.agent, c.company_id, c.name AS company, c.sector, c.city,
                   c.description, a.name AS acquirer, s.url AS source_url, s.title AS source_title
            FROM deals d JOIN companies c USING(company_id)
            LEFT JOIN investors a ON a.investor_id = d.acquirer_id
            LEFT JOIN sources s USING(source_id)""", con, parse_dates=["deal_date"])
    return df


@lru_cache(maxsize=1)
def deal_investors() -> pd.DataFrame:
    """Long table: one row per (deal, investor)."""
    with _con() as con:
        df = pd.read_sql("""
            SELECT di.deal_id, di.is_lead, i.investor_id, i.name AS investor, i.type AS investor_type,
                   i.ai_type, i.hq_country, i.is_foreign
            FROM deal_investors di JOIN investors i USING(investor_id)""", con)
    return df


@lru_cache(maxsize=1)
def financials() -> pd.DataFrame:
    with _con() as con:
        df = pd.read_sql("""
            SELECT c.company_id, c.name AS company, c.sector, f.fiscal_year, f.revenue_inr_cr, f.profit_inr_cr,
                   s.url AS source_url, s.published
            FROM financials f JOIN companies c USING(company_id) LEFT JOIN sources s USING(source_id)""", con,
                         parse_dates=["published"])
    df["fy"] = pd.to_numeric(df.fiscal_year.str.extract(r"(\d{2})")[0], errors="coerce") + 2000
    return df


@lru_cache(maxsize=1)
def weekly_totals() -> pd.DataFrame:
    with _con() as con:
        return pd.read_sql("SELECT * FROM weekly_totals ORDER BY week_end", con, parse_dates=["week_end"])


@lru_cache(maxsize=1)
def comparables() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "comparables.csv")


def funding_deals() -> pd.DataFrame:
    """Primary capital raises only (equity + debt), the basis for most analytics."""
    d = deals()
    return d[d.deal_type.isin(["equity", "debt"])].copy()


STAGE_ORDER = ["pre-seed", "seed", "pre-series-a", "series-a", "series-b", "series-c",
               "series-d", "series-e+", "growth", "pre-ipo"]
STAGE_RANK = {s: i for i, s in enumerate(STAGE_ORDER)}
