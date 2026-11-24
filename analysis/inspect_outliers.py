"""Inspect the largest primary deals (optionally in a date range) to catch amount errors (QA).
Usage: python analysis/inspect_outliers.py [START END N]
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
start, end, n = (sys.argv[1:4] + ["2000-01-01", "2100-01-01", "20"])[:3] if len(sys.argv) > 1 else \
    ("2000-01-01", "2100-01-01", "20")
con = sqlite3.connect(ROOT / "db" / "deals.db")
q = f"""SELECT d.deal_date, c.name, d.deal_type, d.stage, d.amount_usd_m, d.amount_raw, d.agent, s.title
        FROM deals d JOIN companies c USING(company_id) JOIN sources s USING(source_id)
        WHERE d.deal_type IN ('equity','debt') AND d.deal_date BETWEEN '{start}' AND '{end}'
        ORDER BY d.amount_usd_m DESC LIMIT {int(n)}"""
pd.set_option("display.width", 260)
pd.set_option("display.max_colwidth", 80)
print(pd.read_sql(q, con).to_string(index=False))
