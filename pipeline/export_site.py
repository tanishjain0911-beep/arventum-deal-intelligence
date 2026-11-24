"""Export everything the static site needs as JSON into site/data/.

Run after `pipeline/run_all.py`. The site is static: no server, no keys. Interactive tools
(Matchmaker, Price Finder) re-implement the Python formulas in the browser from these files.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "pipeline"))
from lib import acquirers, data, matching, valuation  # noqa: E402
from sectors import ARVENTUM_FOCUS, ALL_SECTORS  # noqa: E402

OUT = ROOT / "site" / "data"
P = ROOT / "data" / "processed"


def load(name):
    f = P / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def clean(o):
    """Make numpy/pandas values JSON-safe and round floats."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if (math.isnan(o) or math.isinf(o)) else round(float(o), 4)
    if isinstance(o, (pd.Timestamp, __import__("datetime").date)):
        return o.strftime("%Y-%m-%d")
    return o


def write(name, obj):
    (OUT / name).write_text(json.dumps(clean(obj), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  {name:24s} {(OUT / name).stat().st_size / 1024:8.1f} KB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = data.deals()
    fd = data.funding_deals()
    inv = data.deal_investors()
    fin = data.financials()
    leads = inv[inv.is_lead == 1].groupby("deal_id").investor.apply(list)
    others = inv[inv.is_lead == 0].groupby("deal_id").investor.apply(list)

    # ---- summary + quality
    build = load("build_report.json")
    write("summary.json", {
        "built": build.get("built"), "tables": build.get("tables"),
        "first": d.deal_date.min(), "last": d.deal_date.max(),
        "capital_usd_m": fd.amount_usd_m.sum(), "companies": int(d.company_id.nunique()),
        "investors": int(inv.investor_id.nunique()),
        "acquisitions": int((d.deal_type == "acquisition").sum()),
        "radar": load("radar_backtest.json"), "matching": load("matching_backtest.json"),
        "coverage": load("coverage.json"), "validation": load("validation.json").get("checks", {}),
        "crosscheck": load("crosscheck.json").get("agreement_pct", {}),
        "crosscheck_n": load("crosscheck.json").get("articles_compared"),
        "model_eval": load("model_eval.json"), "rules_eval": load("rules_eval.json"),
        "corrections": build.get("corrections_by_rule"), "multi_source": build.get("multi_source_deals"),
        "amount_disclosed_pct": build.get("amount_disclosed_pct"),
        "focus_sectors": ARVENTUM_FOCUS, "all_sectors": ALL_SECTORS,
    })

    # ---- deals (slim)
    rows = []
    for r in d.sort_values("deal_date", ascending=False).itertuples():
        rows.append([r.deal_id, r.deal_date.strftime("%Y-%m-%d"), r.company, r.sector, r.deal_type, r.stage,
                     None if pd.isna(r.amount_usd_m) else round(float(r.amount_usd_m), 3),
                     leads.get(r.deal_id, []), others.get(r.deal_id, [])[:6],
                     None if pd.isna(r.acquirer) else r.acquirer, r.source_url, r.company_id])
    write("deals.json", {"cols": ["id", "date", "company", "sector", "type", "stage", "usd_m", "leads", "others",
                                  "acquirer", "url", "cid"], "rows": rows})

    # ---- weekly coverage
    wf = P / "coverage_weekly.csv"
    if wf.exists():
        w = pd.read_csv(wf)
        write("coverage_weekly.json", w[["week_end", "reported_deals", "our_deals", "reported_usd_m",
                                         "our_usd_m"]].to_dict("records"))

    # ---- radar
    rs = pd.read_csv(P / "radar_scores.csv", parse_dates=["last_date"]).sort_values("probability", ascending=False)
    from lib import radar
    top = []
    for _, r in rs.head(400).iterrows():
        top.append({"cid": r.company_id, "company": r.company, "sector": r.sector, "stage": r.last_stage,
                    "last": r.last_date.strftime("%Y-%m-%d"), "months": r.months_since_last,
                    "last_usd_m": float(np.expm1(r.log_last_amount)) if pd.notna(r.log_last_amount) else None,
                    "rounds": r.n_prior_rounds, "p": r.probability, "why": radar.explain_row(r)})
    imp = pd.read_csv(P / "radar_importance.csv", index_col=0).iloc[:, 0] if (P / "radar_importance.csv").exists() \
        else pd.Series(dtype=float)
    write("radar.json", {"top": top, "importance": imp.sort_values(ascending=False).head(10).to_dict()})

    # ---- investor profiles for the in-browser Matchmaker
    asof = fd.deal_date.max() + pd.Timedelta(days=1)
    h = matching._history(asof)
    keys = ["investor_id", "investor", "investor_type"]
    profiles = []
    meta = inv.drop_duplicates("investor_id").set_index("investor_id")[["hq_country", "ai_type"]]
    recent_cut = asof - pd.Timedelta(days=548)
    for (iid, name, itype), g in h.groupby(keys):
        recent = int((g.deal_date >= recent_cut).sum())
        if recent == 0:
            continue
        sec = g.groupby("sector").w.sum().round(3).to_dict()
        stg = g.groupby("stage_rank").w.sum().round(3)
        examples = g.sort_values("deal_date", ascending=False).head(12)
        profiles.append({
            "id": int(iid), "name": name, "type": itype,
            "ai_type": meta.ai_type.get(iid) if iid in meta.index else None,
            "hq": meta.hq_country.get(iid) if iid in meta.index else None,
            "w": round(float(g.w.sum()), 3), "sec": sec, "stg": {str(int(k)): v for k, v in stg.items()},
            "med": None if g.amount_usd_m.dropna().empty else float(g.amount_usd_m.median()),
            "recent": recent, "lead": float(g.is_lead.mean()), "n": int(len(g)),
            "ex": [[e.deal_date.strftime("%Y-%m-%d"), e.company, e.sector, e.stage,
                    None if pd.isna(e.amount_usd_m) else round(float(e.amount_usd_m), 2), int(e.is_lead)]
                   for e in examples.itertuples()],
        })
    write("investors.json", {"weights": matching.W, "market_sector": (h.groupby("sector").size() / len(h)).to_dict(),
                             "stage_order": data.STAGE_ORDER, "profiles": profiles,
                             "market_stage_rank": h.stage_rank.value_counts(normalize=True).sort_index().to_dict()})

    # ---- buyers per sector (precomputed)
    acq = acquirers.acquisitions()
    buyers = {}
    for s in sorted(acq.sector.dropna().unique()):
        if s == "Unclassified":
            continue
        rb = acquirers.rank_buyers(s, top=15)
        buyers[s] = rb[["acquirer", "match_pct", "in_sector", "acquisitions_total", "last_24m", "months_since_last",
                        "targets"]].to_dict("records")
    recent_acq = acq.sort_values("deal_date", ascending=False).head(60)
    write("buyers.json", {"by_sector": buyers, "summary": acquirers.market_summary(),
                          "recent": [[r.deal_date.strftime("%Y-%m-%d"), r.company, r.sector, r.acquirer,
                                      None if pd.isna(r.amount_usd_m) else r.amount_usd_m, r.source_url]
                                     for r in recent_acq.itertuples()]})

    # ---- valuation inputs
    comps = valuation._clean_comps(valuation.comparables())
    reg = valuation.growth_regression(comps)
    pm = valuation._private_multiples_all()
    write("valuation.json", {
        "comps": comps[["ticker", "name", "sector", "market", "ev_revenue", "revenue_growth", "gross_margin",
                        "ebitda_margin"]].to_dict("records"),
        "as_of": str(valuation.comparables().as_of.iloc[0]), "regression": reg,
        "private": pm[["company", "sector", "deal_date", "stage", "valuation_inr_cr", "revenue_inr_cr", "ev_revenue",
                       "source_url"]].to_dict("records") if len(pm) else [],
        "discount": valuation.PRIVATE_DISCOUNT, "usd_inr": valuation.USD_INR,
        "sector_gross": {s: valuation.sector_gross_margin(s) for s in comps.sector.unique()},
    })

    # ---- companies (lookup index + financials)
    fin_by = fin.sort_values("fy").groupby("company_id")
    comp = d.groupby("company_id").agg(name=("company", "first"), sector=("sector", "first"),
                                       desc=("description", "first")).reset_index()
    write("companies.json", {
        "list": comp.values.tolist(),
        "fin": {int(cid): g[["fiscal_year", "revenue_inr_cr", "profit_inr_cr", "source_url"]].values.tolist()
                for cid, g in fin_by},
        "radar": {int(r.company_id): round(float(r.probability), 3) for r in rs.itertuples()},
    })
    print("exported to", OUT)


if __name__ == "__main__":
    main()
