"""Compare extraction agents against a reference agent (default: codex) on the same articles.
Usage: python analysis/model_eval.py [reference]
Output: data/processed/model_eval.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from common import _records  # noqa: E402
from crosscheck import load  # noqa: E402

from rapidfuzz import fuzz  # noqa: E402

import crosscheck as cc  # noqa: E402

ref_name = sys.argv[1] if len(sys.argv) > 1 else "codex"
ref = load(ref_name)
results = {}
for d in sorted((ROOT / "data" / "extracted").glob("*")):
    if d.name == ref_name:
        continue
    other = load(d.name)
    common = sorted(set(ref) & set(other))
    if not common:
        continue
    fields = {
        "record_type": lambda x, y: x["record_type"] == y["record_type"],
        "company": lambda x, y: (not x.get("company") and not y.get("company"))
        or fuzz.token_set_ratio(x.get("company") or "", y.get("company") or "") >= 85,
        "stage": lambda x, y: (x.get("stage") or "") == (y.get("stage") or ""),
        "amount": lambda x, y: (cc.usd(x) is None and cc.usd(y) is None)
        or bool(cc.usd(x) and cc.usd(y) and abs(cc.usd(x) - cc.usd(y)) <= 0.05 * max(cc.usd(x), cc.usd(y))),
        "lead_investors": lambda x, y: cc.same_set(x.get("lead_investors") or [], y.get("lead_investors") or []),
        "sector": lambda x, y: x.get("sector") == y.get("sector"),
    }
    agree = {k: round(100 * sum(fn(ref[u], other[u]) for u in common) / len(common), 1) for k, fn in fields.items()}
    agree["mean"] = round(sum(agree.values()) / len(fields), 1)
    results[d.name] = {"articles": len(common), **agree}
(ROOT / "data" / "processed" / "model_eval.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"agreement with {ref_name} (%):")
for k, v in sorted(results.items(), key=lambda kv: -kv[1]["mean"]):
    print(f"  {k:10s} n={v['articles']:4d}  type {v['record_type']:5}  company {v['company']:5}  amount {v['amount']:5}  "
          f"leads {v['lead_investors']:5}  stage {v['stage']:5}  sector {v['sector']:5}  MEAN {v['mean']}")
