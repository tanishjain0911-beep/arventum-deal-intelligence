"""Regression tests for the deterministic headline amount parser (run: python tests/test_headline_parser.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from common import headline_amount_usd as h  # noqa: E402

FX = 86.6  # 2025 rate used by common.fx
CASES = {
    "Udaan valuation tanks to $1.7 Bn in Series E round": None,
    "Udaan raises $340 Mn in Series E round": 340,
    "PhonePe raises $350 Mn at over $12 Bn valuation": 350,
    "Zepto becomes first Indian unicorn of 2023, raises $200 Mn at $1.4 Bn valuation": 200,
    "Noise raises its maiden funding round from audio giant Bose": None,
    "Data Security Startup Matters.AI Nets ₹115 Cr From Tanglin": 115e7 / FX / 1e6,
    "Off Duty raises Rs 4 Cr from Velocity": 4e7 / FX / 1e6,
    "Fitness app All Is Well raises $250K from Bharat Founders Fund": 0.25,
    "Jewellery marketplace Amama raises $250,000 seed funding": 0.25,
    "Razorpay revenue approaches Rs 1,500 Cr in FY22": None,
    "Recur Club launches $10 Mn fund to back green startups": None,
    "Byju’s Aakash bags $168 Mn from Ranjan Pai": 168,
    "Investors pour Rs 50 Cr into X": 50e7 / FX / 1e6,
    "Moglix posts Rs 6,129 Cr revenue and Rs 160 Cr loss in FY26": None,
    "Lenskart bags $500 Mn from Abu Dhabi Investment Authority": 500,
    "Ola Electric raises $385 Mn from Temasek and State Bank of India": 385,
    "Antler India raises Rs 500 Cr for maiden fund": None,
    "Rebel Foods raises Rs 150 Cr debt from Alteria and InnoVen": 150e7 / FX / 1e6,
    "Hoola Health raises $5 Mn led by Peak XV's Surge": 5,
    "Unacademy’s valuation spikes over 70% to $3.44 Bn as it raises $440 Mn led by Temasek": 440,
}


def main():
    bad = 0
    for text, exp in CASES.items():
        got = h(text, 2025)
        ok = (got is None and exp is None) or (got is not None and exp is not None and abs(got - exp) <= 0.01 * max(exp, 1))
        bad += not ok
        print("OK " if ok else "BAD", None if got is None else round(got, 3), "|", text)
    print(f"{len(CASES) - bad}/{len(CASES)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
