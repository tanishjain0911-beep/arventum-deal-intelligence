"""Steps 4-5: clean, normalise, reconcile, de-duplicate and load into SQLite.

Inputs : data/raw/articles/*.json         (downloaded articles, all sources)
         data/extracted/<agent>/*.json    (AI extraction output, Codex + OpenCode)
Output : db/deals.db, data/processed/*.csv, data/processed/build_report.json

Robustness rules (each logged in the `corrections` table):
  * two-agent merge   : when both AIs read an article, take the more confident record and
                        fill its missing fields from the other one
  * headline-wins     : when a regex can read the amount from the headline and the AI disagrees
                        by >12%, the headline amount is used
  * implausible amount: amounts outside $5k..$20bn are dropped (deal kept)
  * entity resolution : investor / company spellings are folded (manual aliases + fuzzy match)
  * cross-source dedupe: same company + type within 45 days + similar amount = one deal,
                         with every confirming article kept in `deal_sources`
"""
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _records, fx, headline_amount_usd, to_usd_m  # noqa: E402
from sectors import ALL_SECTORS, STAGES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db" / "deals.db"
PROCESSED = ROOT / "data" / "processed"

DEAL_TYPES = {"funding": "equity", "acquisition": "acquisition", "secondary": "secondary", "ipo": "ipo"}
ROUNDUP = re.compile(r"this-week|weekly-funding|monthly-funding|funding-galore")

# Known renames / spellings that fuzzy matching alone won't catch
MANUAL_ALIASES = {
    "sequoia india": "Peak XV Partners", "sequoia capital india": "Peak XV Partners",
    "sequoia capital india and sea": "Peak XV Partners", "sequoia capital": "Peak XV Partners",
    "peak xv": "Peak XV Partners", "peak xv partners": "Peak XV Partners",
    "surge": "Peak XV Partners", "peak xv s surge": "Peak XV Partners", "sequoia surge": "Peak XV Partners",
    "matrix partners india": "Z47", "matrix partners": "Z47", "z47": "Z47",
    "sidbi": "SIDBI", "small industries development bank of india": "SIDBI",
    "sidbi venture capital": "SIDBI Venture Capital",
    "y combinator": "Y Combinator", "yc": "Y Combinator",
    "lightspeed": "Lightspeed", "lightspeed india": "Lightspeed", "lightspeed venture partners": "Lightspeed",
    "lightspeed india partners": "Lightspeed",
    "accel": "Accel", "accel india": "Accel", "accel partners": "Accel",
    "elevation": "Elevation Capital", "saif partners": "Elevation Capital",
    "blume": "Blume Ventures", "kalaari": "Kalaari Capital",
    "nexus": "Nexus Venture Partners", "nexus vp": "Nexus Venture Partners",
    "chiratae": "Chiratae Ventures", "idg ventures india": "Chiratae Ventures",
    "temasek holdings": "Temasek", "softbank vision fund": "SoftBank", "softbank vision fund 2": "SoftBank",
    "tiger global management": "Tiger Global", "general atlantic": "General Atlantic",
    "letsventure": "LetsVenture", "lets venture": "LetsVenture",
    "indian angel network": "Indian Angel Network", "ian": "Indian Angel Network",
    "ian group": "Indian Angel Network", "ian fund": "IAN Alpha Fund",
    "venture catalysts": "Venture Catalysts", "vcats": "Venture Catalysts",
    "info edge": "Info Edge Ventures", "info edge ventures": "Info Edge Ventures",
    "alteria": "Alteria Capital", "stride ventures": "Stride Ventures",
    "innoven": "InnoVen Capital", "innoven capital": "InnoVen Capital",
    "trifecta": "Trifecta Capital", "blacksoil": "BlackSoil",
    "ipv": "Inflection Point Ventures", "inflection point": "Inflection Point Ventures",
    "wfc": "We Founder Circle", "we founder circle": "We Founder Circle",
    "mumbai angels network": "Mumbai Angels", "mumbai angels": "Mumbai Angels",
    "peak xv partners surge": "Peak XV Partners", "surge by peak xv": "Peak XV Partners",
    "piper serica angel fund": "Piper Serica", "piper serica": "Piper Serica",
    "vertex ventures southeast asia and india": "Vertex Ventures SEA & India",
    "vertex ventures sea and india": "Vertex Ventures SEA & India",
    "rainmatter health": "Rainmatter", "rainmatter by zerodha": "Rainmatter",
    "100x vc": "100X.VC", "100xvc": "100X.VC",
    "dsp": "DSP Investment Managers", "iifl": "IIFL", "iifl fintech fund": "IIFL Fintech Fund",
    "9unicorns": "9Unicorns", "9 unicorns": "9Unicorns",
    "titan capital": "Titan Capital", "better capital": "Better Capital",
    "devc": "DeVC", "devc india": "DeVC",
    "vertex ventures": "Vertex Ventures SEA & India", "alpha wave": "Alpha Wave Global",
    "alpha wave global": "Alpha Wave Global", "alpha wave ventures": "Alpha Wave Global",
    "singularity growth opportunities fund i": "Singularity Growth", "singularity growth": "Singularity Growth",
    "advantedge": "AdvantEdge Founders", "advantedge founders": "AdvantEdge Founders",
    "general catalyst partners": "General Catalyst", "a91 partners": "A91 Partners",
    "a91 emerging fund": "A91 Partners", "multiples alternate asset management": "Multiples PE",
    "multiples": "Multiples PE", "chryscapital": "ChrysCapital", "chrys capital": "ChrysCapital",
    "goldman sachs asset management": "Goldman Sachs", "jungle ventures": "Jungle Ventures",
    "bertelsmann india investments": "Bertelsmann India Investments",
    "bii": "British International Investment", "cdc group": "British International Investment",
    "3one4": "3one4 Capital", "3one4 capital": "3one4 Capital",
}
# phrases the AI sometimes lists as investors that are not entities
PLACEHOLDER = re.compile(
    r"^(other |existing |several |some |a clutch of |a group of |prominent |marquee |strategic |new |few )?"
    r"(angel investors?|angels|investors?|backers|hnis?|high net worth individuals|family offices?|"
    r"founders?|undisclosed( investors?)?|others|existing shareholders|clients|employees|"
    r"angel investors? and family offices|individual investors?)$", re.I)
GENERIC = re.compile(
    r"\b(partners?|ventures?|capital|fund|funds|vc|llp|ltd|limited|pvt|private|advisors?|"
    r"management|investments?|asset|holdings?|group|inc|the|india|co|and|technologies|technology|"
    r"pte|corp|corporation)\b")
COMPANY_SUFFIX = re.compile(r"\b(pvt|private|ltd|limited|inc|pte|llp|llc|corp|corporation|gmbh|"
                            r"technologies|technology|tech|labs|solutions|india|software|services|the)\b\.?", re.I)
DEBT_FUNDS = re.compile(r"alteria|stride|innoven|trifecta|blacksoil|northern arc|recur club|klub|"
                        r"getvantage|velocity|grip invest|\bbank\b|sidbi|nabard|lending|credit|debt", re.I)
ACCEL_WORDS = re.compile(r"accelerator|incubator|cohort|program|y combinator|techstars|antler|"
                         r"100x\.vc|iit|iim|startup india|t-hub", re.I)
CORP_WORDS = re.compile(r"\b(ltd|limited|corporation|corp|industries|motors|group|enterprises)\b", re.I)
FUND_WORDS = re.compile(r"capital|ventures?|partners|fund|vc|investments?|holdings|advisors|"
                        r"management|equity|angels?|network|syndicate|llp|ltd|limited|inc|group|"
                        r"bank|labs|securities|family office|trust|foundation|corp", re.I)


def norm_key(name: str) -> str:
    k = name.lower().replace("&", " and ").replace("’", "'")
    k = re.sub(r"[^a-z0-9 ]", " ", k)
    return re.sub(r"\s+", " ", k).strip()


def match_key(name: str, generic=GENERIC) -> str:
    k = generic.sub(" ", norm_key(name))
    return re.sub(r"\s+", " ", k).strip() or norm_key(name)


def investor_type(name: str) -> str:
    if DEBT_FUNDS.search(name):
        return "Debt / Bank"
    if ACCEL_WORDS.search(name):
        return "Accelerator"
    if re.search(r"angel|network|syndicate|letsventure", name, re.I):
        return "Angel network"
    if re.search(r"family office|family trust|'s family", name, re.I):
        return "Family office"
    words = name.split()
    if not FUND_WORDS.search(name) and 2 <= len(words) <= 4 and all(w[:1].isupper() for w in words):
        return "Individual"
    if CORP_WORDS.search(name) and not re.search(r"capital|ventures|fund", name, re.I):
        return "Corporate"
    return "Institutional"


class Resolver:
    """Groups spelling variants of one entity under a canonical name."""

    def __init__(self, manual=None, generic=GENERIC, threshold=93):
        self.manual, self.generic, self.threshold = manual or {}, generic, threshold
        self.groups, self.alias_to_key, self.by_prefix = {}, {}, defaultdict(list)

    def add(self, raw: str) -> str:
        raw = re.sub(r"\s+", " ", raw.strip().strip(".,;"))
        nk = norm_key(raw)
        if nk in self.manual:
            raw = self.manual[nk]
        mk = match_key(raw, self.generic)
        if mk not in self.groups:
            for other in self.by_prefix[mk[:3]]:
                if fuzz.ratio(mk, other) >= self.threshold:
                    mk = other
                    break
            else:
                self.by_prefix[mk[:3]].append(mk)
        self.groups.setdefault(mk, Counter())[raw] += 1
        self.alias_to_key[nk] = mk
        return mk

    def canonical(self, mk: str) -> str:
        names = self.groups[mk]
        for name in set(self.manual.values()):
            if name in names:
                return name
        return names.most_common(1)[0][0]


def load_articles():
    arts = {}
    for f in (ROOT / "data" / "raw" / "articles").glob("*.json"):
        a = json.loads(f.read_text(encoding="utf-8"))
        if not a.get("error") and a.get("title"):
            arts[a["url"]] = a
    return arts


def load_records(arts, corrections):
    """One merged record per article URL (two-agent merge)."""
    by_url = defaultdict(list)
    for agent_dir in sorted((ROOT / "data" / "extracted").glob("*")):
        for f in sorted(agent_dir.glob("*.json")):
            for r in _records(f):
                if r.get("url") in arts and not ROUNDUP.search(r["url"]):
                    r["agent"] = agent_dir.name
                    by_url[r["url"]].append(r)
    merged = []
    # agents ranked by measured agreement with the reference (analysis/model_eval.py); confidence breaks ties
    priority = {"codex": 0, "opencode": 0, "deepseek": 1, "pickle": 1, "nemotron": 2, "mimo": 3,
                "beam": 3, "hy4": 3, "flint": 3, "lightning": 3}
    for url, rs in by_url.items():
        rs = sorted(rs, key=lambda r: (priority.get(r["agent"], 5), -(r.get("confidence") or 0)))
        best = dict(rs[0])
        for other in rs[1:]:
            if other["record_type"] != best["record_type"]:
                continue
            for k, v in other.items():
                if best.get(k) in (None, [], "") and v not in (None, [], ""):
                    best[k] = v
                    corrections.append((url, k, None, json.dumps(v)[:200], "two-agent merge: filled gap"))
        best["n_agents"] = len(rs)
        merged.append(best)
    return merged


def main():
    corrections = []
    arts = load_articles()
    recs = load_records(arts, corrections)
    print(f"articles: {len(arts)}, records: {len(recs)}  types: {dict(Counter(r['record_type'] for r in recs))}")

    companies = Resolver(generic=COMPANY_SUFFIX, threshold=95)
    investors = Resolver(MANUAL_ALIASES)
    deal_rows, fin_rows = [], []
    for r in recs:
        if not r.get("company"):
            continue
        a = arts[r["url"]]
        d = date.fromisoformat(a["date"][:10])
        ck = companies.add(r["company"])
        sector = r.get("sector") if r.get("sector") in ALL_SECTORS else None
        if r["record_type"] in DEAL_TYPES:
            usd = to_usd_m(r.get("amount_value"), r.get("amount_currency"), r.get("amount_unit"), d.year)
            head = headline_amount_usd(a.get("title"), d.year)
            if head is not None and (usd is None or abs(head - usd) > 0.12 * max(head, usd)):
                corrections.append((r["url"], "amount_usd_m", usd, head, "headline-wins"))
                usd = head
            if usd is not None and not (0.005 <= usd <= 20000):
                corrections.append((r["url"], "amount_usd_m", usd, None, "implausible amount dropped"))
                usd = None
            val = to_usd_m(r.get("valuation_value"), r.get("valuation_currency"), r.get("valuation_unit"), d.year)
            if val is not None and usd is not None and val < usd:
                corrections.append((r["url"], "valuation_usd_m", val, None, "valuation below round size"))
                val = None
            stage = r.get("stage") if r.get("stage") in STAGES else None
            dtype = DEAL_TYPES[r["record_type"]]
            if dtype == "equity" and stage == "debt":
                dtype = "debt"
            deal_rows.append({
                "company_key": ck, "deal_date": d.isoformat(), "deal_type": dtype,
                "stage": stage or ("acquisition" if dtype == "acquisition" else "undisclosed"),
                "amount_usd_m": round(usd, 4) if usd else None,
                "amount_inr_cr": round(usd * fx(d.year) / 10, 2) if usd else None,
                "amount_raw": (f"{r.get('amount_value')} {r.get('amount_currency')} {r.get('amount_unit')}"
                               if r.get("amount_value") is not None else None),
                "valuation_usd_m": round(val, 2) if val else None,
                "acquirer_key": investors.add(r["acquirer"]) if r.get("acquirer") else None,
                "leads": [investors.add(x) for x in r.get("lead_investors") or []
                          if x and x.strip() and not PLACEHOLDER.match(x.strip())],
                "others": [investors.add(x) for x in r.get("other_investors") or []
                           if x and x.strip() and not PLACEHOLDER.match(x.strip())],
                "urls": [r["url"]], "title": a.get("title"), "kind": a.get("kind"),
                "confidence": r.get("confidence"), "n_agents": r["n_agents"], "agent": r["agent"],
                "sector": sector, "city": r.get("city"), "desc": r.get("company_description"),
            })
        elif r["record_type"] == "financials" and r.get("revenue_inr_cr") is not None:
            fin_rows.append({"company_key": ck, "published": d.isoformat(),
                             "fiscal_year": re.sub(r"\s", "", (r.get("fiscal_year") or "")).upper(),
                             "revenue_inr_cr": r.get("revenue_inr_cr"), "profit_inr_cr": r.get("profit_inr_cr"),
                             "url": r["url"], "title": a.get("title"), "kind": a.get("kind"),
                             "sector": sector, "city": r.get("city"), "desc": r.get("company_description")})

    # ---- cross-source de-duplication
    deal_rows.sort(key=lambda x: (x["company_key"], x["deal_date"]))
    kept, merged_n = [], 0
    for row in deal_rows:
        dup = None
        for k in reversed(kept[-6:]):
            if k["company_key"] != row["company_key"] or k["deal_type"] != row["deal_type"]:
                continue
            gap = (date.fromisoformat(row["deal_date"]) - date.fromisoformat(k["deal_date"])).days
            a1, a2 = k["amount_usd_m"], row["amount_usd_m"]
            same_amt = a1 is None or a2 is None or abs(a1 - a2) <= 0.3 * max(a1, a2)
            if gap <= 45 and same_amt:
                dup = k
                break
        if dup is None:
            kept.append(row)
            continue
        merged_n += 1
        dup["urls"] = dup["urls"] + row["urls"]
        dup["leads"] = list(dict.fromkeys(dup["leads"] + row["leads"]))
        dup["others"] = list(dict.fromkeys(dup["others"] + row["others"]))
        for f in ("amount_usd_m", "amount_inr_cr", "amount_raw", "valuation_usd_m", "acquirer_key", "sector", "city"):
            if dup.get(f) is None and row.get(f) is not None:
                dup[f] = row[f]
        if dup["stage"] == "undisclosed" and row["stage"] != "undisclosed":
            dup["stage"] = row["stage"]
    print(f"deals: {len(deal_rows)} records -> {len(kept)} unique deals ({merged_n} duplicate reports merged)")

    # ---- financials: one row per company + fiscal year (latest article wins)
    fin_best = {}
    for row in sorted(fin_rows, key=lambda x: x["published"]):
        if row["fiscal_year"] and re.fullmatch(r"FY\d{2}", row["fiscal_year"]):
            fin_best[(row["company_key"], row["fiscal_year"])] = row

    # ---- company attributes: majority vote across all records
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

    def source_id(url):
        if url not in src_ids:
            a = arts[url]
            cur.execute("INSERT INTO sources(url, site, kind, published, title) VALUES (?,?,?,?,?)",
                        (url, "inc42" if "inc42.com" in url else "entrackr", a.get("kind"),
                         a["date"][:10], a.get("title")))
            src_ids[url] = cur.lastrowid
        return src_ids[url]

    comp_ids = {}
    used_companies = {r["company_key"] for r in kept} | {k[0] for k in fin_best}
    for ck in used_companies:
        at = attrs[ck]
        name = companies.canonical(ck)
        cur.execute("INSERT OR IGNORE INTO companies(name, sector, city, description) VALUES (?,?,?,?)",
                    (name, at["sector"].most_common(1)[0][0] if at["sector"] else "Other",
                     at["city"].most_common(1)[0][0] if at["city"] else None, at["desc"]))
        comp_ids[ck] = cur.execute("SELECT company_id FROM companies WHERE name=?", (name,)).fetchone()[0]

    inv_ids = {}
    for mk in investors.groups:
        name = investors.canonical(mk)
        cur.execute("INSERT OR IGNORE INTO investors(name, type) VALUES (?,?)", (name, investor_type(name)))
        inv_ids[mk] = cur.execute("SELECT investor_id FROM investors WHERE name=?", (name,)).fetchone()[0]
    for nk, mk in investors.alias_to_key.items():
        cur.execute("INSERT OR IGNORE INTO investor_aliases VALUES (?,?)", (nk, inv_ids[mk]))
    enr_path = PROCESSED / "investor_enrichment.json"
    if enr_path.exists():
        enr = json.loads(enr_path.read_text(encoding="utf-8"))
        for name, e in enr.items():
            cur.execute("UPDATE investors SET ai_type=?, hq_country=?, is_foreign=?, ai_confidence=? WHERE name=?",
                        (e["investor_type"], e["hq_country"], int(e["is_foreign"]), e["confidence"], name))

    for row in kept:
        cur.execute("""INSERT INTO deals(company_id, deal_date, deal_type, stage, amount_usd_m, amount_inr_cr,
                       amount_raw, valuation_usd_m, acquirer_id, source_id, confidence, agent)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (comp_ids[row["company_key"]], row["deal_date"], row["deal_type"], row["stage"],
                     row["amount_usd_m"], row["amount_inr_cr"], row["amount_raw"], row["valuation_usd_m"],
                     inv_ids.get(row["acquirer_key"]), source_id(row["urls"][0]), row["confidence"],
                     row.get("agent")))
        did = cur.lastrowid
        for u in dict.fromkeys(row["urls"]):
            cur.execute("INSERT OR IGNORE INTO deal_sources VALUES (?,?)", (did, source_id(u)))
        for mk in set(row["leads"]):
            cur.execute("INSERT OR IGNORE INTO deal_investors VALUES (?,?,1)", (did, inv_ids[mk]))
        for mk in set(row["others"]) - set(row["leads"]):
            cur.execute("INSERT OR IGNORE INTO deal_investors VALUES (?,?,0)", (did, inv_ids[mk]))

    for (ck, fy), row in fin_best.items():
        cur.execute("INSERT OR REPLACE INTO financials VALUES (?,?,?,?,?)",
                    (comp_ids[ck], fy, row["revenue_inr_cr"], row["profit_inr_cr"], source_id(row["url"])))

    for w in weekly_totals(arts):
        cur.execute("INSERT OR REPLACE INTO weekly_totals(week_end, deal_count, total_usd_m, source_id) "
                    "VALUES (?,?,?,?)", (w["week_end"], w["deal_count"], w["total_usd_m"], source_id(w["url"])))

    cur.executemany("INSERT INTO corrections VALUES (?,?,?,?,?)",
                    [(u, f, None if a is None else str(a), None if b is None else str(b), rule)
                     for u, f, a, b, rule in corrections])
    con.commit()
    export(con, corrections, len(deal_rows), merged_n)
    con.close()


def weekly_totals(arts):
    """Two-step parse of Entrackr weekly round-ups: deal count, then the first $ total that follows it."""
    rows = []
    words = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve "
                                        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
                                        .split())}
    num = r"(\d+|" + "|".join(words) + r")"
    count_pat = re.compile(
        num + r"\s+(?:Indian\s+)?(?:startups?\s+)?(?:(?:which|that)\s+)?(?:have\s+)?"
              r"(?:collectively\s+|cumulatively\s+)?"
              r"(?:raised|secured|raked\s+in|garnered|mopped\s+up|bagged|scooped\s+up|funding\s+deals)", re.I)
    amt_pat = re.compile(r"\$\s?([\d.,]+)\s*(million|billion|mn|bn)", re.I)
    for a in arts.values():
        if "entrackr.com" not in a["url"] or "this-week" not in a["url"]:
            continue
        for text in [" ".join((a.get("body") or [])[:2]), a.get("description") or ""]:
            c = count_pat.search(text)
            if not c:
                continue
            m = amt_pat.search(text, c.end(), c.end() + 220)
            if not m:
                continue
            amt = float(m.group(1).replace(",", ""))
            if m.group(2).lower() in ("billion", "bn"):
                amt *= 1000
            n = c.group(1).lower()
            rows.append({"week_end": a["date"][:10], "deal_count": int(n) if n.isdigit() else words[n],
                         "total_usd_m": amt, "url": a["url"]})
            break
    return rows


def export(con, corrections, n_records, merged_n):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    flat = pd.read_sql("""
        SELECT d.deal_id, d.deal_date, c.name AS company, c.sector, c.city, d.deal_type, d.stage,
               d.amount_usd_m, d.amount_inr_cr, d.valuation_usd_m,
               (SELECT group_concat(i.name, '; ') FROM deal_investors di JOIN investors i USING(investor_id)
                 WHERE di.deal_id = d.deal_id AND di.is_lead = 1) AS lead_investors,
               (SELECT group_concat(i.name, '; ') FROM deal_investors di JOIN investors i USING(investor_id)
                 WHERE di.deal_id = d.deal_id AND di.is_lead = 0) AS other_investors,
               a.name AS acquirer,
               (SELECT COUNT(*) FROM deal_sources ds WHERE ds.deal_id = d.deal_id) AS n_sources,
               s.url AS source_url
        FROM deals d JOIN companies c USING(company_id) JOIN sources s USING(source_id)
        LEFT JOIN investors a ON a.investor_id = d.acquirer_id
        ORDER BY d.deal_date DESC""", con)
    flat.to_csv(PROCESSED / "deals.csv", index=False)
    inv = pd.read_sql("""SELECT i.*, COUNT(di.deal_id) AS n_deals, SUM(di.is_lead) AS n_led
                         FROM investors i LEFT JOIN deal_investors di USING(investor_id)
                         GROUP BY i.investor_id ORDER BY n_deals DESC""", con)
    inv.to_csv(PROCESSED / "investors.csv", index=False)
    pd.read_sql("SELECT c.name, c.sector, f.* FROM financials f JOIN companies c USING(company_id)", con) \
        .to_csv(PROCESSED / "financials.csv", index=False)
    pd.read_sql("SELECT * FROM companies", con).to_csv(PROCESSED / "companies.csv", index=False)

    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ["sources", "companies", "investors", "deals", "deal_investors", "deal_sources",
                        "financials", "weekly_totals", "corrections"]}
    report = {
        "built": pd.Timestamp.now().isoformat(timespec="seconds"),
        "tables": counts,
        "deal_records_before_dedupe": n_records,
        "duplicate_reports_merged": merged_n,
        "corrections_by_rule": dict(Counter(c[4] for c in corrections)),
        "deals_by_type": dict(flat.deal_type.value_counts()),
        "deals_by_year": {str(k): int(v) for k, v in flat.deal_date.str[:4].value_counts().sort_index().items()},
        "amount_disclosed_pct": round(100 * flat.amount_usd_m.notna().mean(), 1),
        "with_named_investor_pct": round(100 * (flat.lead_investors.notna() | flat.other_investors.notna()).mean(), 1),
        "multi_source_deals": int((flat.n_sources > 1).sum()),
        "top_investors": inv.head(15)[["name", "type", "n_deals", "n_led"]].to_dict("records"),
    }
    (PROCESSED / "build_report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    for t, n in counts.items():
        print(f"  {t:15s} {n}")
    print("corrections:", report["corrections_by_rule"])


if __name__ == "__main__":
    main()
