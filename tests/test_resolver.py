"""Regression tests for entity resolution and placeholder filtering (run: python tests/test_resolver.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from build_db import COMPANY_SUFFIX, MANUAL_ALIASES, PLACEHOLDER, Resolver, investor_type  # noqa: E402

failures = 0


def check(cond, msg):
    global failures
    failures += not cond
    print("OK " if cond else "BAD", msg)


inv = Resolver(MANUAL_ALIASES)
same = [("Sequoia India", "Peak XV Partners"), ("Peak XV's Surge", "Peak XV Partners"),
        ("IPV", "Inflection Point Ventures"), ("Accel Partners", "Accel"), ("Lightspeed India Partners", "Lightspeed"),
        ("Capillary", "Capillary Technologies"), ("Blume Ventures", "Blume"), ("SAIF Partners", "Elevation Capital"),
        ("Matrix Partners India", "Z47")]
for a, b in same:
    check(inv.add(a) == inv.add(b), f"merge: {a} == {b}")
different = [("B Capital", "Big Capital"), ("Leo Capital", "Lok Capital"), ("Pi Ventures", "8i Ventures"),
             ("Nexus Venture Partners", "M Venture Partners"), ("SIDBI Venture Capital", "SIG Venture Capital")]
for a, b in different:
    check(inv.add(a) != inv.add(b), f"keep apart: {a} != {b}")
check(inv.canonical(inv.add("sequoia capital india")) == "Peak XV Partners", "canonical name is the alias target")

comp = Resolver(generic=COMPANY_SUFFIX, threshold=95, squash=True)
check(comp.add("Botsync Pte Ltd") == comp.add("Botsync"), "company suffix stripped")
for a, b in [("Money View", "Moneyview"), ("Byju's", "Byju"), ("Sid’s Farm", "Sid's Farm"),
             ("RENÉE Cosmetics", "RENEE Cosmetics"), ("TheMathCompany", "The Math Company"), ("Fresh Bus", "FreshBus")]:
    check(comp.add(a) == comp.add(b), f"company variants merged: {a} == {b}")
check(comp.add("Zepto") != comp.add("Zetwerk"), "distinct companies kept apart")

for p in ["angel investors", "Other angel investors", "existing investors", "HNIs", "family offices"]:
    check(bool(PLACEHOLDER.match(p)), f"placeholder rejected: {p}")
for p in ["Mumbai Angels", "Indian Angel Network", "Kunal Shah"]:
    check(not PLACEHOLDER.match(p), f"real entity kept: {p}")

check(investor_type("Kunal Shah") == "Individual", "type: individual")
check(investor_type("Alteria Capital") == "Debt / Bank", "type: venture debt")
check(investor_type("Y Combinator") == "Accelerator", "type: accelerator")
check(investor_type("Mumbai Angels") == "Angel network", "type: angel network")
print("failures:", failures)
sys.exit(1 if failures else 0)
