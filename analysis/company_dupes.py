"""Find likely-duplicate company names that the resolver did NOT merge."""
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "db" / "deals.db")
c = pd.read_sql("""SELECT c.company_id, c.name, c.sector, COUNT(d.deal_id) AS deals FROM companies c
                   LEFT JOIN deals d USING(company_id) GROUP BY c.company_id""", con)


def key(n):
    n = n.lower().replace("’", "'")
    n = re.sub(r"'s\b", "", n)
    n = re.sub(r"[^a-z0-9]", "", n)
    return n


groups = defaultdict(list)
for _, r in c.iterrows():
    groups[key(r["name"])].append(r["name"])
exact = {k: v for k, v in groups.items() if len(v) > 1}
print(f"{len(exact)} groups identical after removing case/punctuation/possessive:")
for k, v in list(exact.items())[:15]:
    print("  ", v)
names = c.sort_values("deals", ascending=False).name.tolist()[:1500]
pairs = []
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if a[0].lower() == b[0].lower() and fuzz.ratio(key(a), key(b)) >= 92 and key(a) != key(b):
            pairs.append((a, b))
print(f"{len(pairs)} near-duplicate pairs (ratio >= 92):", pairs[:20])
