"""Find likely-duplicate investor names the resolver did NOT merge (for alias-table review)."""
import sqlite3
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "db" / "deals.db")
inv = pd.read_sql("""SELECT i.name, i.type, COUNT(*) AS n FROM investors i JOIN deal_investors di USING(investor_id)
                     GROUP BY i.investor_id HAVING n >= 2 ORDER BY n DESC""", con)
names = inv.name.tolist()
seen, pairs = set(), []
for i, a in enumerate(names[:600]):
    for b, score, _ in process.extract(a, names, scorer=fuzz.token_set_ratio, limit=4):
        if b == a or (b, a) in seen:
            continue
        if score >= 90 and fuzz.ratio(a.lower(), b.lower()) < 93:
            seen.add((a, b))
            pairs.append((a, b, score))
# acronym check: "Inflection Point Ventures" ~ "IPV"
acr = {"".join(w[0] for w in n.split() if w[0].isalpha()).upper(): n for n in names if len(n.split()) >= 2}
for n in names:
    if n.isupper() and 2 <= len(n) <= 5 and n in acr and acr[n] != n:
        pairs.append((n, acr[n], "acronym"))
for p in pairs[:80]:
    print(p)
print(len(pairs), "candidate pairs")
