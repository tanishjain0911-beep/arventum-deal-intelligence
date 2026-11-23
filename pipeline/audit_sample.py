"""Draw a reproducible random sample of extracted records + their source text for a manual audit.
Usage: python pipeline/audit_sample.py N SEED  -> data/processed/audit_sample.jsonl
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _records  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
n, seed = int(sys.argv[1]), int(sys.argv[2])
arts = {}
for f in (ROOT / "data" / "raw" / "articles").glob("*.json"):
    a = json.loads(f.read_text(encoding="utf-8"))
    arts[a["url"]] = a
recs = []
for f in sorted((ROOT / "data" / "extracted").glob("*/*.json")):
    for r in _records(f):
        if r.get("url") in arts:
            r["agent"] = f.parent.name
            recs.append(r)
random.Random(seed).shuffle(recs)
out = ROOT / "data" / "processed" / "audit_sample.jsonl"
with out.open("w", encoding="utf-8") as fh:
    for i, r in enumerate(recs[:n]):
        a = arts[r["url"]]
        keep = {k: r.get(k) for k in ("record_type", "company", "sector", "stage", "amount_value", "amount_currency",
                                      "amount_unit", "valuation_value", "lead_investors", "other_investors",
                                      "acquirer", "fiscal_year", "revenue_inr_cr", "profit_inr_cr", "agent")}
        fh.write(json.dumps({"i": i, "url": r["url"], "title": a.get("title"),
                             "text": " ".join(a.get("body") or [])[:1200], "extracted": keep},
                            ensure_ascii=False) + "\n")
print(f"sampled {min(n, len(recs))} of {len(recs)} records -> {out}")
