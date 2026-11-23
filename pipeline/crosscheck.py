"""Quality check: field-level agreement between two independent AI extractors.

For every article extracted by BOTH Codex and OpenCode, compare the key fields.
High agreement = the extraction is reliable; disagreements are listed for review.
Output: data/processed/crosscheck.json
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _records  # noqa: E402

from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "data" / "extracted"


def load(agent):
    out = {}
    for f in (EX / agent).glob("*.json"):
        for r in _records(f):
            out[r["url"]] = r
    return out


def usd(r):
    v, c, u = r.get("amount_value"), r.get("amount_currency"), r.get("amount_unit")
    if v is None or c is None:
        return None
    if c == "USD":
        return v * {"mn": 1, "bn": 1000, "cr": 10, "lakh": 0.1}.get(u or "mn", 1)
    return v * {"cr": 1, "lakh": 0.01, "mn": 0.1, "bn": 100}.get(u or "cr", 1) * 1e7 / 85 / 1e6


def same_set(a, b):
    a = {x.lower().strip() for x in a}
    b = {x.lower().strip() for x in b}
    if not a and not b:
        return True
    hits = sum(any(fuzz.token_set_ratio(x, y) >= 85 for y in b) for x in a)
    return hits / max(len(a), len(b)) >= 0.8


def main():
    a, b = load("codex"), load("opencode")
    common = sorted(set(a) & set(b))
    fields = {
        "record_type": lambda x, y: x["record_type"] == y["record_type"],
        "company": lambda x, y: (not x.get("company") and not y.get("company"))
        or fuzz.token_set_ratio(x.get("company") or "", y.get("company") or "") >= 85,
        "stage": lambda x, y: (x.get("stage") or "") == (y.get("stage") or ""),
        "amount": lambda x, y: (usd(x) is None and usd(y) is None)
        or (usd(x) and usd(y) and abs(usd(x) - usd(y)) <= 0.05 * max(usd(x), usd(y))),
        "lead_investors": lambda x, y: same_set(x.get("lead_investors") or [], y.get("lead_investors") or []),
        "sector": lambda x, y: x.get("sector") == y.get("sector"),
    }
    agree = {k: 0 for k in fields}
    disagreements = []
    for u in common:
        for k, fn in fields.items():
            if fn(a[u], b[u]):
                agree[k] += 1
            else:
                disagreements.append({"url": u, "field": k,
                                      "codex": a[u].get(k if k != "amount" else "amount_value"),
                                      "opencode": b[u].get(k if k != "amount" else "amount_value")})
    n = len(common)
    result = {"articles_compared": n,
              "agreement_pct": {k: round(100 * v / n, 1) if n else None for k, v in agree.items()},
              "disagreements": disagreements}
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "processed" / "crosscheck.json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                                                 encoding="utf-8")
    print(f"compared {n} articles")
    for k, v in result["agreement_pct"].items():
        print(f"  {k:15s} {v}%")
    print(f"{len(disagreements)} field disagreements, first 12:")
    for d in disagreements[:12]:
        print("  ", d["field"], "|", d["codex"], "<>", d["opencode"], "|", d["url"].split("/")[-1][:60])


if __name__ == "__main__":
    main()
