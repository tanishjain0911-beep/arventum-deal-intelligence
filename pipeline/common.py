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
    r"(?P<cur>\$|₹|\b(?:usd|rs\.?|inr)(?=\s?\d))\s?(?P<num>\d+(?:[.,]\d+)*)\s?"
    r"(?P<unit>mn\b|million\b|m\b|bn\b|billion\b|b\b|cr\b|crore\b|lakh\b|lakhs\b|k\b|thousand\b)?",
    re.I)
# an amount next to these words is not the round size
NOT_ROUND_BEFORE = re.compile(r"(valuation|valued|valuing|worth|revenue|loss|losses|profit|gmv|arr|turnover|"
                              r"income|sales|fund\s+of|corpus|aum|ebitda|tanks\s+to|drops\s+to|jumps\s+to)"
                              r"[^$₹]{0,30}$", re.I)  # digits allowed between ("valuation spikes 70% to $3.4 Bn")
NOT_ROUND_AFTER = re.compile(r"^\s*(?:mn|million|bn|billion|cr|crore)?\s*(?:for\s+(?:its\s+)?(?:\w+\s+){0,2})?"
                             r"(valuation|revenue|loss|profit|gmv|arr|turnover|fund\b|corpus|aum)", re.I)


def all_headline_amounts(text: str, year: int = 2025) -> list:
    """Every amount mentioned in a headline (USD millions), regardless of context."""
    out = []
    for m in AMT.finditer(text or ""):
        v = headline_amount_usd(m.group(0), year)
        if v is not None:
            out.append(v)
    return out


def headline_amount_usd(text: str, year: int = 2025):
    """Deterministic amount parser for headlines like '$11 Mn', 'Rs 70 Cr', '₹115 Cr', '$250,000', '$500K'.
    Skips amounts that describe a valuation, revenue, loss, fund size etc.
    Returns USD millions or None when no confident match."""
    text = text or ""
    m = None
    for cand in AMT.finditer(text):
        before, after = text[:cand.start()], text[cand.end():cand.end() + 20]
        if NOT_ROUND_BEFORE.search(before) or NOT_ROUND_AFTER.search(after):
            continue
        m = cand
        break
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
