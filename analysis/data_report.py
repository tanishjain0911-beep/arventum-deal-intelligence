"""Generate docs/DATA_REPORT.md: a factual snapshot of the database and its quality checks."""
import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"


def load(name):
    f = P / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def md_table(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,.1f}" if isinstance(v, float) else str(v))
                                       for v in r.values) + " |")
    return "\n".join(lines)


def main():
    con = sqlite3.connect(ROOT / "db" / "deals.db")
    q = lambda s: pd.read_sql(s, con)  # noqa: E731
    build, cov, val, cc = load("build_report.json"), load("coverage.json"), load("validation.json"), load("crosscheck.json")

    deals = q("""SELECT d.*, c.name AS company, c.sector FROM deals d JOIN companies c USING(company_id)""")
    deals["year"] = deals.deal_date.str[:4]
    prim = deals[deals.deal_type.isin(["equity", "debt"])]
    by_year = prim.groupby("year").agg(deals=("deal_id", "count"), usd_m=("amount_usd_m", "sum"),
                                       median_usd_m=("amount_usd_m", "median")).reset_index()
    by_sector = prim.groupby("sector").agg(deals=("deal_id", "count"), usd_m=("amount_usd_m", "sum")) \
        .sort_values("usd_m", ascending=False).head(15).reset_index()
    top_inv = q("""SELECT i.name, i.type, i.ai_type, i.hq_country, COUNT(*) AS deals, SUM(di.is_lead) AS led
                   FROM investors i JOIN deal_investors di USING(investor_id)
                   WHERE i.type != 'Individual' GROUP BY i.investor_id ORDER BY deals DESC LIMIT 20""")
    acq = q("""SELECT d.deal_date, c.name AS target, a.name AS acquirer, d.amount_usd_m
               FROM deals d JOIN companies c USING(company_id) LEFT JOIN investors a ON a.investor_id=d.acquirer_id
               WHERE d.deal_type='acquisition' ORDER BY d.deal_date DESC LIMIT 15""")
    src = q("SELECT site, COUNT(*) AS articles FROM sources GROUP BY site")

    out = ["# Data report", "",
           f"_Generated from `db/deals.db` at {build.get('built', 'n/a')}._", "",
           "## Contents", "", md_table(pd.DataFrame([build.get("tables", {})]).T.reset_index()
                                         .rename(columns={"index": "table", 0: "rows"})), "",
           "Articles used, by source:", "", md_table(src), "",
           f"- Deal records before de-duplication: **{build.get('deal_records_before_dedupe')}**; duplicate reports "
           f"merged: **{build.get('duplicate_reports_merged')}**; deals confirmed by 2+ articles: "
           f"**{build.get('multi_source_deals')}**",
           f"- Amount disclosed: **{build.get('amount_disclosed_pct')}%** of deals; at least one named investor: "
           f"**{build.get('with_named_investor_pct')}%**",
           f"- Automatic corrections applied: {build.get('corrections_by_rule')}", "",
           "## Primary rounds by year", "", md_table(by_year), "",
           "## Top sectors by capital raised", "", md_table(by_sector), "",
           "## Most active institutional investors", "", md_table(top_inv), "",
           "## Latest acquisitions", "", md_table(acq), "",
           "## Quality checks", "",
           "**Coverage vs Entrackr weekly round-ups** (recall):", "",
           "```json", json.dumps(cov, indent=2), "```", "",
           "**Rule-based validation** (no AI):", "", "```json", json.dumps(val.get("checks", {}), indent=2), "```", "",
           "**Two-agent agreement** (Codex vs OpenCode on the same articles):", "",
           "```json", json.dumps({k: cc.get(k) for k in ("articles_compared", "agreement_pct")}, indent=2), "```", "",
           "See also `docs/MANUAL_AUDIT.md` for the independent field-by-field audit."]
    (ROOT / "docs" / "DATA_REPORT.md").write_text("\n".join(out), encoding="utf-8")
    print("wrote docs/DATA_REPORT.md")


if __name__ == "__main__":
    main()
