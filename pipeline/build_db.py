"""Steps 4-5: clean, normalise, de-duplicate and load into SQLite.

Inputs : data/raw/articles.jsonl, data/extracted/<agent>/*.json
Output : db/deals.db  (+ CSV exports in data/processed/)
"""
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db" / "deals.db"
PROCESSED = ROOT / "data" / "processed"

# Average INR per USD by calendar year (RBI reference rate, rounded)
INR_PER_USD = {2023: 82.6, 2024: 83.7, 2025: 86.6, 2026: 88.0}

DEAL_TYPES = {"funding": "equity", "acquisition": "acquisition", "secondary": "secondary", "ipo": "ipo"}

# Known renames / spellings that fuzzy matching alone won't catch
MANUAL_ALIASES = {
    "sequoia india": "Peak XV Partners",
    "sequoia capital india": "Peak XV Partners",
    "sequoia capital india and sea": "Peak XV Partners",
    "peak xv": "Peak XV Partners",
    "surge": "Peak XV Partners",
    "peak xv's surge": "Peak XV Partners",
    "matrix partners india": "Z47",
    "matrix partners": "Z47",
    "sidbi": "SIDBI",
    "small industries development bank of india": "SIDBI",
    "y combinator": "Y Combinator",
    "yc": "Y Combinator",
}
GENERIC = re.compile(
    r"\b(partners?|ventures?|capital|fund|funds|vc|llp|ltd|limited|pvt|private|advisors?|"
    r"management|investments?|asset|holdings?|group|inc|the|india|co)\b"
)
DEBT_FUNDS = re.compile(r"alteria|stride|innoven|trifecta|blacksoil|northern arc|recur club|klub|"
                        r"getvantage|velocity|grip|bank|sidbi|nabard|lending|credit|debt", re.I)
ACCEL_WORDS = re.compile(r"accelerator|incubator|cohort|program|y combinator|techstars|antler", re.I)
FUND_WORDS = re.compile(r"capital|ventures?|partners|fund|vc|investments?|holdings|advisors|"
                        r"management|equity|angels?|network|syndicate|llp|ltd|limited|inc|group|"
                        r"bank|labs|securities|family office", re.I)


def norm_key(name: str) -> str:
    k = name.lower().replace("&", " and ")
    k = re.sub(r"[^a-z0-9 ]", " ", k)
    return re.sub(r"\s+", " ", k).strip()


def match_key(name: str) -> str:
    k = GENERIC.sub(" ", norm_key(name))
    return re.sub(r"\s+", " ", k).strip() or norm_key(name)


def investor_type(name: str) -> str:
    if DEBT_FUNDS.search(name):
        return "Debt / Bank"
    if ACCEL_WORDS.search(name):
        return "Accelerator"
    if re.search(r"angel|network|syndicate|lets venture|letsventure", name, re.I):
        return "Angel network"
    words = name.split()
    if not FUND_WORDS.search(name) and 2 <= len(words) <= 4 and all(w[:1].isupper() for w in words):
        return "Individual"
    return "Institutional"


def to_usd_m(value, currency, unit, year):
    if value is None or currency is None:
        return None
    fx = INR_PER_USD.get(year, 86.0)
    if currency == "USD":
        return value * {"mn": 1, "bn": 1000, "cr": 10, "lakh": 0.1}.get(unit or "mn", 1)
    inr_cr = value * {"cr": 1, "lakh": 0.01, "mn": 0.1, "bn": 100}.get(unit or "cr", 1)
    return inr_cr * 1e7 / fx / 1e6


def load_records():
    arts = {}
    for line in (ROOT / "data" / "raw" / "articles.jsonl").open(encoding="utf-8"):
        a = json.loads(line)
        arts[a["url"]] = a
    recs = {}
    for agent_dir in sorted((ROOT / "data" / "extracted").glob("*")):
        for f in sorted(agent_dir.glob("*.json")):
            for r in json.loads(f.read_text(encoding="utf-8"))["records"]:
                if r.get("url") not in arts:
                    continue
                r["agent"] = agent_dir.name
                prev = recs.get(r["url"])
                if prev is None or (r.get("confidence") or 0) > (prev.get("confidence") or 0):
                    recs[r["url"]] = r
    return arts, list(recs.values())


class Resolver:
    """Groups spelling variants of the same entity under one canonical name."""

    def __init__(self, manual=None):
        self.manual = manual or {}
        self.groups = {}       # match_key -> Counter of raw spellings
        self.alias_to_key = {}

    def add(self, raw: str) -> str:
        raw = raw.strip().strip(".")
        nk = norm_key(raw)
        if nk in self.manual:
            raw = self.manual[nk]
        mk = match_key(raw)
        if mk not in self.groups:
            for other in self.groups:   # fuzzy fold into an existing group
                if other[:3] == mk[:3] and fuzz.ratio(mk, other) >= 93:
                    mk = other
                    break
        self.groups.setdefault(mk, Counter())[raw] += 1
        self.alias_to_key[nk] = mk
        return mk

    def canonical(self, mk: str) -> str:
        for name in self.manual.values():
            if match_key(name) == mk:
                return name
        return self.groups[mk].most_common(1)[0][0]


def weekly_totals(arts):
    rows = []
    pat = re.compile(r"(\d+)\s+Indian startups (?:collectively )?raised (?:around |about |over |nearly )?"
                     r"\$\s?([\d.,]+)\s*(million|billion|mn|bn)", re.I)
    for a in arts.values():
        if a.get("kind") != "report" or "weekly" not in a["url"]:
            continue
        text = " ".join([a.get("description") or ""] + (a.get("body") or []))
        m = pat.search(text)
        if m:
            amt = float(m.group(2).replace(",", ""))
            if m.group(3).lower() in ("billion", "bn"):
                amt *= 1000
            rows.append({"week_end": a["date"], "deal_count": int(m.group(1)), "total_usd_m": amt, "url": a["url"]})
    return rows


def main():
    arts, recs = load_records()
    print(f"articles: {len(arts)}, extracted records: {len(recs)}")
    print("record types:", Counter(r["record_type"] for r in recs))

    companies, investors = Resolver(), Resolver(MANUAL_ALIASES)
    deal_rows, fin_rows = [], []
    for r in recs:
        if not r.get("company"):
            continue
        a = arts[r["url"]]
        d = date.fromisoformat(a["date"])
        ck = companies.add(r["company"])
        if r["record_type"] in DEAL_TYPES:
            usd = to_usd_m(r.get("amount_value"), r.get("amount_currency"), r.get("amount_unit"), d.year)
            if usd is not None and not (0.005 <= usd <= 20000):
                usd = None  # implausible extraction, keep deal but drop amount
            val = to_usd_m(r.get("valuation_value"), r.get("valuation_currency"), r.get("valuation_unit"), d.year)
            stage = r.get("stage")
            dtype = DEAL_TYPES[r["record_type"]]
            if dtype == "equity" and stage == "debt":
                dtype = "debt"
            deal_rows.append({
                "company_key": ck, "deal_date": d.isoformat(), "deal_type": dtype,
                "stage": stage or ("acquisition" if dtype == "acquisition" else "undisclosed"),
                "amount_usd_m": round(usd, 3) if usd else None,
                "amount_inr_cr": round(usd * INR_PER_USD.get(d.year, 86) / 10, 2) if usd else None,
                "amount_raw": f"{r.get('amount_value')} {r.get('amount_currency')} {r.get('amount_unit')}" if r.get("amount_value") else None,
                "valuation_usd_m": round(val, 2) if val else None,
                "acquirer_key": investors.add(r["acquirer"]) if r.get("acquirer") else None,
                "leads": [investors.add(x) for x in r.get("lead_investors") or [] if x.strip()],
                "others": [investors.add(x) for x in r.get("other_investors") or [] if x.strip()],
                "url": r["url"], "title": a.get("title"), "kind": a.get("kind"),
                "confidence": r.get("confidence"), "agent": r["agent"],
                "sector": r.get("sector"), "city": r.get("city"), "desc": r.get("company_description"),
            })
        elif r["record_type"] == "financials" and (r.get("revenue_inr_cr") is not None):
            fin_rows.append({"company_key": ck, "fiscal_year": (r.get("fiscal_year") or "").upper(),
                             "revenue_inr_cr": r.get("revenue_inr_cr"), "profit_inr_cr": r.get("profit_inr_cr"),
                             "url": r["url"], "title": a.get("title"), "kind": a.get("kind"),
                             "sector": r.get("sector"), "city": r.get("city"), "desc": r.get("company_description")})

    # ---- de-duplicate deals: same company + type, within 45 days, similar amount
    deal_rows.sort(key=lambda x: (x["company_key"], x["deal_date"]))
    kept, dropped = [], 0
    for row in deal_rows:
        dup = None
        for k in reversed(kept[-5:]):
            if k["company_key"] != row["company_key"] or k["deal_type"] != row["deal_type"]:
                continue
            gap = (date.fromisoformat(row["deal_date"]) - date.fromisoformat(k["deal_date"])).days
            a1, a2 = k["amount_usd_m"], row["amount_usd_m"]
            same_amt = a1 is None or a2 is None or abs(a1 - a2) <= 0.2 * max(a1, a2)
            if gap <= 45 and same_amt:
                dup = k
                break
        if dup:
            dropped += 1
            if (row["confidence"] or 0) > (dup["confidence"] or 0):
                kept[kept.index(dup)] = {**row, "leads": list(set(row["leads"] + dup["leads"])),
                                         "others": list(set(row["others"] + dup["others"]))}
            else:
                dup["leads"] = list(set(dup["leads"] + row["leads"]))
                dup["others"] = list(set(dup["others"] + row["others"]))
        else:
            kept.append(row)
    print(f"deals: {len(deal_rows)} extracted, {dropped} duplicates merged, {len(kept)} kept")

    # ---- company attributes: most common sector / city across its records
    attrs = defaultdict(lambda: {"sector": Counter(), "city": Counter(), "desc": None})
    for row in kept + fin_rows:
        at = attrs[row["company_key"]]
        if row.get("sector"):
            at["sector"][row["sector"]] += 1
        if row.get("city"):
            at["city"][row["city"]] += 1
        at["desc"] = at["desc"] or row.get("desc")

    # ---- write SQLite
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))
    cur = con.cursor()

    src_ids = {}
    for row in kept + fin_rows:
        if row["url"] not in src_ids:
            cur.execute("INSERT INTO sources(url, site, kind, published, title) VALUES (?,?,?,?,?)",
                        (row["url"], "entrackr", row.get("kind"), row.get("deal_date"), row.get("title")))
            src_ids[row["url"]] = cur.lastrowid

    comp_ids = {}
    for ck in {r["company_key"] for r in kept + fin_rows}:
        at = attrs[ck]
        cur.execute("INSERT OR IGNORE INTO companies(name, sector, city, description) VALUES (?,?,?,?)",
                    (companies.canonical(ck), at["sector"].most_common(1)[0][0] if at["sector"] else None,
                     at["city"].most_common(1)[0][0] if at["city"] else None, at["desc"]))
        comp_ids[ck] = cur.execute("SELECT company_id FROM companies WHERE name=?",
                                   (companies.canonical(ck),)).fetchone()[0]

    inv_ids = {}
    for mk in investors.groups:
        name = investors.canonical(mk)
        cur.execute("INSERT OR IGNORE INTO investors(name, type) VALUES (?,?)", (name, investor_type(name)))
        inv_ids[mk] = cur.execute("SELECT investor_id FROM investors WHERE name=?", (name,)).fetchone()[0]
    for nk, mk in investors.alias_to_key.items():
        cur.execute("INSERT OR IGNORE INTO investor_aliases VALUES (?,?)", (nk, inv_ids[mk]))

    for row in kept:
        cur.execute("""INSERT INTO deals(company_id, deal_date, deal_type, stage, amount_usd_m, amount_inr_cr,
                       amount_raw, valuation_usd_m, acquirer_id, source_id, confidence)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (comp_ids[row["company_key"]], row["deal_date"], row["deal_type"], row["stage"],
                     row["amount_usd_m"], row["amount_inr_cr"], row["amount_raw"], row["valuation_usd_m"],
                     inv_ids.get(row["acquirer_key"]), src_ids[row["url"]], row["confidence"]))
        did = cur.lastrowid
        for mk in set(row["leads"]):
            cur.execute("INSERT OR IGNORE INTO deal_investors VALUES (?,?,1)", (did, inv_ids[mk]))
        for mk in set(row["others"]) - set(row["leads"]):
            cur.execute("INSERT OR IGNORE INTO deal_investors VALUES (?,?,0)", (did, inv_ids[mk]))

    for row in fin_rows:
        if row["fiscal_year"]:
            cur.execute("INSERT OR REPLACE INTO financials VALUES (?,?,?,?,?)",
                        (comp_ids[row["company_key"]], row["fiscal_year"], row["revenue_inr_cr"],
                         row["profit_inr_cr"], src_ids[row["url"]]))

    for w in weekly_totals(arts):
        cur.execute("INSERT OR REPLACE INTO weekly_totals(week_end, deal_count, total_usd_m) VALUES (?,?,?)",
                    (w["week_end"], w["deal_count"], w["total_usd_m"]))
    con.commit()

    # ---- exports + summary
    PROCESSED.mkdir(parents=True, exist_ok=True)
    flat = pd.read_sql("""
        SELECT d.deal_id, d.deal_date, c.name AS company, c.sector, c.city, d.deal_type, d.stage,
               d.amount_usd_m, d.amount_inr_cr, d.valuation_usd_m,
               (SELECT group_concat(i.name, '; ') FROM deal_investors di JOIN investors i USING(investor_id)
                 WHERE di.deal_id = d.deal_id AND di.is_lead = 1) AS lead_investors,
               (SELECT group_concat(i.name, '; ') FROM deal_investors di JOIN investors i USING(investor_id)
                 WHERE di.deal_id = d.deal_id AND di.is_lead = 0) AS other_investors,
               a.name AS acquirer, s.url AS source_url
        FROM deals d JOIN companies c USING(company_id) JOIN sources s USING(source_id)
        LEFT JOIN investors a ON a.investor_id = d.acquirer_id
        ORDER BY d.deal_date DESC""", con)
    flat.to_csv(PROCESSED / "deals.csv", index=False)
    pd.read_sql("SELECT * FROM investors", con).to_csv(PROCESSED / "investors.csv", index=False)
    pd.read_sql("SELECT c.name, f.* FROM financials f JOIN companies c USING(company_id)", con).to_csv(
        PROCESSED / "financials.csv", index=False)
    for t in ["companies", "investors", "deals", "deal_investors", "financials", "weekly_totals"]:
        print(f"{t:15s} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]}")
    con.close()


if __name__ == "__main__":
    main()
