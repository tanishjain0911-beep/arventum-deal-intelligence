"""Inspect the largest primary deals, to catch amount errors (used in QA)."""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "db" / "deals.db")
q = """SELECT d.deal_date, c.name, d.deal_type, d.stage, d.amount_usd_m, d.amount_raw, s.title
       FROM deals d JOIN companies c USING(company_id) JOIN sources s USING(source_id)
       WHERE d.deal_type IN ('equity','debt') {extra}
       ORDER BY d.amount_usd_m DESC LIMIT {n}"""
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 90)
print(pd.read_sql(q.format(extra="", n=15), con).to_string(index=False))
