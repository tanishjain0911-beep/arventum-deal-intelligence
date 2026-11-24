"""Regression tests for the deterministic headline extractor (run: python tests/test_rule_extract.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from rule_extract import extract  # noqa: E402

CASES = [
    # (title, keywords, expected record_type, expected company, expected stage, lead investor that must appear)
    ("Fintech startup BankSathi raises $4 Mn in pre-series A", "funding, BankSathi", "funding", "BankSathi",
     "pre-series-a", None),
    ("Exclusive: Darwinbox raises $5 Mn fresh funds from SBI", "funding, SBI, Darwinbox, HRtech", "funding",
     "Darwinbox", None, "SBI"),
    ("Peepul Tree raises $6 Mn in seed round led by Elevar Equity", "funding, Peepul Tree", "funding", "Peepul Tree",
     "seed", "Elevar Equity"),
    ("IvyCap Ventures leads $11 Mn Series B round in robotics company Botsync", "Botsync", "funding", "Botsync",
     "series-b", "IvyCap Ventures"),
    ("Slice raises Rs 75 Cr debt from Stride Ventures", "Slice", "funding", "Slice", "debt", "Stride Ventures"),
    # must NOT be deals
    ("Exclusive: Gold loan platform Oro Money to raise $12-15 Mn in a new round", "Oro Money", "not_a_deal", None,
     None, None),
    ("3one4 Capital raises $200 Mn for its fourth early-stage fund", "3one4", "not_a_deal", None, None, None),
    ("MamaEarth’s parent receives nod from SEBI for IPO", "MamaEarth", "not_a_deal", None, None, None),
    ("PhysicsWallah raises stake in Utkarsh Classes to 75.5%", "PhysicsWallah", "not_a_deal", None, None, None),
    ("Lenskart raises $200 Mn in secondary round", "Lenskart", "not_a_deal", None, None, None),
    # acquisitions are deliberately left to the AI (target names are unreliable from headlines)
    ("MakeMyTrip acquires quick ride platform", "MakeMyTrip", "not_a_deal", None, None, None),
    # financials
    ("Razorpay’s revenue approaches Rs 1,500 Cr in FY22", "Razorpay", "financials", "Razorpay", None, None),
    ("OfBusiness closes FY21 with 2X jump in revenue and Rs 56 Cr profit", "OfBusiness", "financials", "OfBusiness",
     None, None),
    ("Swiggy closes $1.25 Bn round led by SoftBank and Prosus", "Swiggy", "funding", "Swiggy", None, "SoftBank"),
]

bad = 0
for title, kw, typ, company, stage, lead in CASES:
    r = extract({"url": "u", "title": title, "description": "", "company_kw": kw})
    ok = r["record_type"] == typ
    if ok and company:
        ok = (r["company"] or "").lower() == company.lower()
    if ok and stage:
        ok = r["stage"] == stage
    if ok and lead:
        ok = lead in r["lead_investors"] + r["other_investors"]
    if ok and typ == "funding":  # investor names must never be sentence fragments
        ok = all(len(i.split()) <= 5 for i in r["lead_investors"] + r["other_investors"])
    bad += not ok
    print("OK " if ok else "BAD", r["record_type"], "|", r["company"], "|", r["stage"], "|", r["lead_investors"], "|",
          title[:60])
print(f"{len(CASES) - bad}/{len(CASES)} passed")
sys.exit(1 if bad else 0)
