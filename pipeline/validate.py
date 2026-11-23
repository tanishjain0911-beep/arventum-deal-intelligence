"""Rule-based validation of AI-extracted records (no AI involved).

Checks
  1. headline_amount : amount parsed by regex from the headline vs. the AI's amount
  2. stage_size      : round size implausible for its stage (e.g. $80M "seed")
  3. missing_core    : funding record without company or without any amount/investor
  4. company_in_title: extracted company name actually appears in headline/description
Writes data/processed/validation.json with pass rates and the flagged rows, and
data/processed/validation_flags.csv for manual review.
"""
import json
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _records, headline_amount_usd, to_usd_m  # noqa: E402

import pandas as pd
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]

STAGE_MAX_USD_M = {"pre-seed": 5, "seed": 15, "pre-series-a": 25, "series-a": 60, "series-b": 150}


def usd(r, year=2025):
    return to_usd_m(r.get("amount_value"), r.get("amount_currency"), r.get("amount_unit"), year)


def main():
    arts = {}
    for f in (ROOT / "data" / "raw" / "articles").glob("*.json"):
        a = json.loads(f.read_text(encoding="utf-8"))
        arts[a["url"]] = a
    recs = []
    for f in (ROOT / "data" / "extracted").glob("*/*.json"):
        for r in _records(f):
            if r["url"] in arts:
                r["agent"] = f.parent.name
                r["batch"] = f.stem
                recs.append(r)

    flags, stats = [], {"headline_amount": [0, 0], "stage_size": [0, 0], "missing_core": [0, 0],
                        "company_in_title": [0, 0]}
    for r in recs:
        a = arts[r["url"]]
        title = a.get("title") or ""
        if r["record_type"] in ("funding", "acquisition", "secondary", "ipo"):
            # 1. headline amount
            h = headline_amount_usd(title)
            x = usd(r)
            if h is not None and x is not None:
                ok = abs(h - x) <= 0.12 * max(h, x)  # 12% tolerance covers FX-rate differences
                stats["headline_amount"][0] += ok
                stats["headline_amount"][1] += 1
                if not ok:
                    flags.append({"check": "headline_amount", "url": r["url"], "title": title,
                                  "ai_usd_m": round(x, 2), "headline_usd_m": round(h, 2), "agent": r["agent"]})
            # 2. stage vs size
            cap = STAGE_MAX_USD_M.get(r.get("stage"))
            if cap and x is not None:
                ok = x <= cap
                stats["stage_size"][0] += ok
                stats["stage_size"][1] += 1
                if not ok:
                    flags.append({"check": "stage_size", "url": r["url"], "title": title,
                                  "ai_usd_m": round(x, 2), "stage": r.get("stage"), "agent": r["agent"]})
            # 3. missing core fields
            ok = bool(r.get("company")) and bool(x is not None or r.get("lead_investors")
                                                 or r.get("other_investors") or r.get("acquirer"))
            stats["missing_core"][0] += ok
            stats["missing_core"][1] += 1
            if not ok:
                flags.append({"check": "missing_core", "url": r["url"], "title": title, "agent": r["agent"]})
        # 4. company name grounded in the article
        if r.get("company"):
            hay = f"{title} {a.get('description') or ''} {' '.join((a.get('body') or [])[:2])}"
            ok = fuzz.partial_ratio(r["company"].lower(), hay.lower()) >= 85
            stats["company_in_title"][0] += ok
            stats["company_in_title"][1] += 1
            if not ok:
                flags.append({"check": "company_in_title", "url": r["url"], "title": title,
                              "company": r["company"], "agent": r["agent"]})

    summary = {k: {"passed": p, "checked": n, "pass_rate": round(100 * p / n, 1) if n else None}
               for k, (p, n) in stats.items()}
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    (out / "validation.json").write_text(json.dumps({"records": len(recs), "checks": summary}, indent=2),
                                         encoding="utf-8")
    pd.DataFrame(flags).to_csv(out / "validation_flags.csv", index=False)
    print(f"records checked: {len(recs)}")
    for k, v in summary.items():
        print(f"  {k:18s} {v['pass_rate']}%  ({v['passed']}/{v['checked']})")
    print(f"{len(flags)} flags -> data/processed/validation_flags.csv")
    for fl in flags[:10]:
        print("  ", {k: v for k, v in fl.items() if k not in ("url",)})


if __name__ == "__main__":
    main()
