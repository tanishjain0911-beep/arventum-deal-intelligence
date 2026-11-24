"""QA: acquisitions where the recorded target may actually be the buyer (role swap)."""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "db" / "deals.db")
a = pd.read_sql("""SELECT d.deal_id, c.name AS target, i.name AS acquirer, s.title, d.agent
                   FROM deals d JOIN companies c USING(company_id) LEFT JOIN investors i ON i.investor_id=d.acquirer_id
                   JOIN sources s USING(source_id) WHERE d.deal_type='acquisition'""", con)


def swapped(r):
    t = (r.title or "").lower()
    m = re.search(r"^(?:exclusive:\s*)?(.+?)\s+(acquires|buys|to acquire|picks up|takes over)\b", t)
    return bool(m and r.target and r.target.lower().split()[0] in m.group(1))


a["suspect"] = a.apply(swapped, axis=1)
print(f"{len(a)} acquisitions, {a.suspect.sum()} where the 'target' is the subject of 'X acquires ...'")
pd.set_option("display.width", 220)
print(a[a.suspect][["target", "acquirer", "agent", "title"]].head(15).to_string(index=False))
