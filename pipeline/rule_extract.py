"""Deterministic (no-AI) extractor for formulaic deal headlines: a fallback when no AI agent is available.

Entrackr headlines are highly regular ("X raises $11 Mn in Series A round led by Y", "Y leads $5 Mn round in X",
"A acquires B") and each page names the company in its <meta keywords>. Rules recover company, amount, stage,
lead investor(s) and acquirer; sector is left empty (filled later from the company's other records or by an AI
pass). Records are written as agent "rules", the LOWEST merge priority, so any AI extraction supersedes them.

Usage:
  python pipeline/rule_extract.py LIST.csv TAG      # extract articles in LIST not yet covered by any agent
  python pipeline/rule_extract.py --eval            # accuracy vs Codex on articles both cover
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _records, headline_amount_usd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "extracted" / "rules"

NOT_DEAL = re.compile(r"\b(to raise|in talks|set to|plans? to|eyes|likely to|may raise|seeks?|looking to|"
                      r"launches .*fund|closes .*fund|fund of|layoffs?|ipo-bound|files? drhp|explained|decoding|"
                      r"report|weekly|this week|valuation tanks|in advanced talks|exclusive: .* to |"
                      r"for (?:its|their|a|maiden|new|first|second|third|fourth|fifth)\b.*\bfund\b|\bfund (?:i|ii|iii|iv|v|\d)\b|"
                      r"\bcorpus\b|\bsebi\b|\bipo\b|\bdrhp\b|raises stake|ups stake|increases stake|esop|"
                      r"secondary|buyback|block deal|stake sale|sells .* stake)", re.I)
ACQ = re.compile(r"^(?:exclusive:\s*)?(?P<acq>.+?)\s+(?:acquires|buys|to acquire|picks up majority stake in|"
                 r"takes over)\s+(?P<target>.+?)(?:\s+for\s+.*|\s+in\s+.*deal.*)?$", re.I)
RAISE = re.compile(r"\b(raises|raised|secures|bags|picks up|nets|gets|receives|mops up|closes|grabs|lands|"
                   r"scoops up|garners)\b", re.I)
LEADS = re.compile(r"^(?:exclusive:\s*)?(?P<lead>.+?)\s+(?:leads|co-leads)\s+.*?\b(?:round|funding)\s+in\s+"
                   r"(?:[a-z0-9\- ]*?\s)?(?P<company>[A-Z][\w.&'’\- ]+)$")
LED_BY = re.compile(r"\b(?:led by|from|backed by)\s+(?P<inv>.+?)(?:,? (?:and|with) (?:others|participation.*)|"
                    r"\s+to\s+.*|\s+for\s+.*|$)", re.I)
STAGE = [(r"pre[- ]?seed", "pre-seed"), (r"pre[- ]?series[- ]?a", "pre-series-a"), (r"\bseed\b", "seed"),
         (r"series[- ]?a\b", "series-a"), (r"series[- ]?b\b", "series-b"), (r"series[- ]?c\b", "series-c"),
         (r"series[- ]?d\b", "series-d"), (r"series[- ]?[e-h]\b", "series-e+"), (r"pre[- ]?ipo", "pre-ipo"),
         (r"\b(?:venture )?debt\b|\bncds?\b|\bloan\b", "debt"), (r"\bbridge\b", "bridge")]
FIN = re.compile(r"(revenue|income|topline|scale|loss|profit)", re.I)
FY = re.compile(r"\bFY\s?'?(\d{2})\b", re.I)
CR = re.compile(r"Rs\.?\s?([\d,]+(?:\.\d+)?)\s?(lakh\s)?Cr", re.I)


def split_investors(s: str) -> list:
    s = re.sub(r"\b(others|existing investors|angel investors|clutch of angels)\b", "", s, flags=re.I)
    parts = re.split(r",\s*|\s+and\s+|\s*&\s+", s)
    return [p.strip(" .") for p in parts if 2 < len(p.strip(" .")) < 60]


GENERIC_KW = re.compile(r"^(funding|valuation|debt funding|exclusive|acquisition|ipo|lead|series [a-z]|"
                        r"seed|startup|startups|fintech|edtech|healthtech|saas|d2c|ev|ai|hrtech|agritech)$", re.I)
DESCRIPTOR = re.compile(r"\b(startup|start-up|company|platform|firm|brand|maker|provider|marketplace|app|"
                        r"unicorn|player|operator|lender|nbfc|solution|solutions|venture|chain|label|service)s?$",
                        re.I)


def company_from(title: str, kws: list):
    """Company = a non-generic keyword that appears in the headline subject; else the name after descriptor words."""
    t = re.sub(r"^(exclusive|update|breaking)\s*:\s*", "", title, flags=re.I)
    parts = RAISE.split(t, maxsplit=1)
    subject = parts[0].strip() if len(parts) > 1 else ""
    for k in kws:
        k = k.strip()
        if k and not GENERIC_KW.match(k) and subject and re.search(re.escape(k), subject, re.I):
            return k
    if not subject:
        return None
    words = subject.split()
    cut = 0
    for i, w in enumerate(words):
        if DESCRIPTOR.search(w) or (w[:1].islower() and i < len(words) - 1):
            cut = i + 1
    name = " ".join(words[cut:]).strip(" ,'’s") or subject
    name = re.sub(r"[’']s$", "", name)
    return name if len(name) <= 60 else None


def stage_of(text: str):
    for pat, st in STAGE:
        if re.search(pat, text, re.I):
            return st
    return None


def extract(a: dict) -> dict:
    title = (a.get("title") or "").strip()
    desc = a.get("description") or ""
    kws = [k.strip() for k in (a.get("company_kw") or "").split(",") if k.strip()]
    kw = company_from(title, kws)
    rec = {"url": a["url"], "record_type": "not_a_deal", "company": kw, "company_description": None, "sector": None,
           "city": None, "stage": None, "amount_value": None, "amount_currency": None, "amount_unit": None,
           "valuation_value": None, "valuation_currency": None, "valuation_unit": None, "lead_investors": [],
           "other_investors": [], "acquirer": None, "fiscal_year": None, "revenue_inr_cr": None,
           "profit_inr_cr": None, "confidence": 0.55}
    if NOT_DEAL.search(title):
        return rec
    m = ACQ.match(title)
    if m:
        target = m.group("target").strip()
        tk = next((k for k in kws if not GENERIC_KW.match(k) and re.search(re.escape(k), target, re.I)), None)
        acq = re.sub(r"^(exclusive|update)\s*:\s*", "", m.group("acq").strip(), flags=re.I)
        rec.update(record_type="acquisition", acquirer=acq, stage="acquisition",
                   company=tk or target.split(" for ")[0].split()[-1])
        usd = headline_amount_usd(title)
        if usd:
            rec.update(amount_value=round(usd, 4), amount_currency="USD", amount_unit="mn")
        return rec
    fy = FY.search(title)
    if fy and FIN.search(title) and not RAISE.search(title):
        crs = CR.findall(title)
        if crs:
            vals = [float(v.replace(",", "")) * (0.01 if lakh else 1) for v, lakh in crs]
            rec.update(record_type="financials", fiscal_year=f"FY{fy.group(1)}", revenue_inr_cr=vals[0])
            if len(vals) > 1 and re.search(r"loss", title, re.I):
                rec["profit_inr_cr"] = -vals[1]
            elif len(vals) > 1 and re.search(r"profit", title, re.I):
                rec["profit_inr_cr"] = vals[1]
        return rec
    lm = LEADS.match(title)
    if lm or RAISE.search(title):
        rec["record_type"] = "funding"
        text = f"{title}. {desc}"
        rec["stage"] = stage_of(title) or stage_of(desc)
        usd = headline_amount_usd(title)
        if usd:
            rec.update(amount_value=round(usd, 4), amount_currency="USD", amount_unit="mn")
        if lm:
            rec["lead_investors"] = split_investors(lm.group("lead"))
            rec["company"] = kw or lm.group("company").strip()
        else:
            m2 = LED_BY.search(title) or LED_BY.search(desc)
            if m2:
                invs = split_investors(m2.group("inv"))
                key = "lead_investors" if re.search(r"led by", m2.group(0), re.I) or len(invs) == 1 else "other_investors"
                rec[key] = invs
        if rec["stage"] == "debt":
            rec["record_type"] = "funding"
        if not rec["company"]:
            rec["company"] = RAISE.split(title)[0].split()[-1] if RAISE.split(title)[0].split() else None
    return rec


def run(list_csv: str, tag: str):
    done = {r["url"] for f in (ROOT / "data" / "extracted").glob("*/*.json") for r in _records(f)}
    recs = []
    for row in csv.DictReader((ROOT / list_csv).open(encoding="utf-8")):
        if row["url"] in done:
            continue
        p = ROOT / "data" / "raw" / "articles" / (hashlib.md5(row["url"].encode()).hexdigest() + ".json")
        if not p.exists():
            continue
        a = json.loads(p.read_text(encoding="utf-8"))
        if a.get("error") or not a.get("title"):
            continue
        recs.append(extract(a))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{tag}.json").write_text(json.dumps({"records": recs}, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(len(recs), "rule-extracted", Counter(r["record_type"] for r in recs))


def evaluate():
    codex = {r["url"]: r for f in (ROOT / "data" / "extracted" / "codex").glob("*.json") for r in _records(f)}
    arts = {}
    for u in list(codex)[:3000]:
        p = ROOT / "data" / "raw" / "articles" / (hashlib.md5(u.encode()).hexdigest() + ".json")
        if p.exists():
            arts[u] = json.loads(p.read_text(encoding="utf-8"))
    from rapidfuzz import fuzz
    n = typ = comp = amt = lead = st = 0
    deal_n = 0
    for u, a in arts.items():
        if a.get("error"):
            continue
        r, c = extract(a), codex[u]
        n += 1
        typ += (r["record_type"] == c["record_type"]) or (r["record_type"] == "funding" and c["record_type"] == "secondary")
        if c["record_type"] in ("funding", "acquisition") and r["record_type"] == c["record_type"]:
            deal_n += 1
            comp += fuzz.token_set_ratio(r["company"] or "", c["company"] or "") >= 85
            from common import to_usd_m
            x, y = to_usd_m(r["amount_value"], r["amount_currency"], r["amount_unit"]), \
                to_usd_m(c["amount_value"], c["amount_currency"], c["amount_unit"])
            amt += (x is None and y is None) or bool(x and y and abs(x - y) <= 0.12 * max(x, y))
            lead += set(map(str.lower, r["lead_investors"])) <= set(map(str.lower, c["lead_investors"] +
                                                                      c["other_investors"])) or not r["lead_investors"]
            st += (r["stage"] or "undisclosed") == (c["stage"] or "undisclosed")
    res = {"articles": n, "record_type_pct": round(100 * typ / n, 1), "deals_compared": deal_n,
           "company_pct": round(100 * comp / deal_n, 1), "amount_pct": round(100 * amt / deal_n, 1),
           "lead_precision_pct": round(100 * lead / deal_n, 1), "stage_pct": round(100 * st / deal_n, 1)}
    (ROOT / "data" / "processed" / "rules_eval.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(res)


if __name__ == "__main__":
    if sys.argv[1] == "--eval":
        evaluate()
    else:
        run(sys.argv[1], sys.argv[2])
