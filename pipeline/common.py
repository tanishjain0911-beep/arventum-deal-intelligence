"""Shared helpers for pipeline scripts: safe file reading and money conversion."""
import json
import re
from pathlib import Path

# Average INR per USD by calendar year (RBI reference rate, rounded)
INR_PER_USD = {2017: 65.1, 2018: 68.4, 2019: 70.4, 2020: 74.1, 2021: 73.9, 2022: 78.6,
               2023: 82.6, 2024: 83.7, 2025: 86.6, 2026: 88.0}

USD_UNIT_TO_MN = {"thousand": 0.001, "mn": 1, "bn": 1000, "cr": 10, "lakh": 0.1}
INR_UNIT_TO_CR = {"thousand": 1e-4, "lakh": 0.01, "mn": 0.1, "cr": 1, "bn": 100}


def _records(f: Path) -> list:
    """Records from one extraction output file; [] if the file is empty or still being written."""
    try:
        return json.loads(f.read_text(encoding="utf-8"))["records"]
    except (json.JSONDecodeError, KeyError, OSError):
        return []


def fx(year: int) -> float:
    return INR_PER_USD.get(year, 86.0)


def to_usd_m(value, currency, unit, year: int = 2025):
    """Convert an (amount, currency, unit) triple to USD millions."""
    if value is None or currency is None:
        return None
    if currency == "USD":
        return value * USD_UNIT_TO_MN.get(unit or "mn", 1)
    inr_cr = value * INR_UNIT_TO_CR.get(unit or "cr", 1)
    return inr_cr * 1e7 / fx(year) / 1e6


AMT = re.compile(
    r"(?P<cur>\$|usd|rs\.?|inr|₹)\s?(?P<num>\d+(?:[.,]\d+)*)\s?"
    r"(?P<unit>mn|million|m\b|bn|billion|b\b|cr|crore|lakh|lakhs|k\b|thousand)?",
    re.I)


def headline_amount_usd(text: str, year: int = 2025):
    """Deterministic amount parser for headlines like '$11 Mn', 'Rs 70 Cr', '₹115 Cr', '$250,000', '$500K'.
    Returns USD millions or None when no confident match."""
    m = AMT.search(text or "")
    if not m:
        return None
    raw = m.group("num")
    num = float(raw.replace(",", ""))
    cur = m.group("cur").lower()
    unit = (m.group("unit") or "").lower()
    if cur in ("$", "usd"):
        if unit in ("k", "thousand"):
            return num / 1000
        if unit in ("bn", "billion", "b"):
            return num * 1000
        if unit in ("mn", "million", "m"):
            return num
        return num / 1e6 if num >= 1000 else None   # bare "$250,000"; bare "$5" is ambiguous
    if unit in ("", "k", "thousand") and num < 1000:
        return None  # "Rs 50" without unit is ambiguous
    cr = num * {"lakh": 0.01, "lakhs": 0.01, "mn": 0.1, "million": 0.1, "bn": 100, "billion": 100,
                "cr": 1, "crore": 1}.get(unit, 1e-7)
    return cr * 1e7 / fx(year) / 1e6
