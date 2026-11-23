"""Enrich the most active investors with type and headquarters country (AI-classified, labelled as such).

Why: Arventum positions itself on *global* capital. Knowing which investors are foreign (US, Japan,
Gulf, Singapore...) and what kind they are (VC, PE, corporate, family office, sovereign/DFI,
venture debt) lets the Matchmaker filter by investor type and geography.

Method: Codex (strict JSON schema), batches of 60 names, each with the sectors and deals the
investor appears in (context to avoid confusing similarly-named entities). Output is cached in
data/processed/investor_enrichment.json and merged into the `investors` table by build_db.py
(columns ai_type, hq_country, is_foreign, ai_confidence).
Usage: python pipeline/enrich_investors.py [TOP_N]
"""
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "investor_enrichment.json"
SCHEMA = ROOT / "pipeline" / "investor_schema.json"
TYPES = ["Venture Capital", "Private Equity / Growth", "Corporate / CVC", "Angel investor (individual)",
         "Angel network / platform", "Accelerator / Incubator", "Venture debt / NBFC / Bank",
         "Family office", "Sovereign / Pension / DFI / Government", "Hedge fund / Crossover / Asset manager",
         "Other"]

PROMPT = f"""You are a private-markets analyst. For each investor below (active in Indian startup deals),
classify it using your knowledge of the investment industry, using the context (sectors and sample
portfolio companies) to disambiguate. If you do not recognise an entity, infer conservatively from its
name and context and lower your confidence.

Fields:
- name: exactly as given
- investor_type: one of {TYPES}
- hq_country: country of headquarters of the investing entity (e.g. "India", "United States", "Japan",
  "Singapore", "United Arab Emirates"). For individuals use their country of residence if known, else "India".
- is_foreign: true if hq_country is not India
- confidence: 0.0-1.0

Return JSON: {{"investors": [ ... one object per input investor, same order ... ]}}
"""

SCHEMA_OBJ = {
    "type": "object", "additionalProperties": False, "required": ["investors"],
    "properties": {"investors": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["name", "investor_type", "hq_country", "is_foreign", "confidence"],
        "properties": {"name": {"type": "string"}, "investor_type": {"type": "string", "enum": TYPES},
                       "hq_country": {"type": "string"}, "is_foreign": {"type": "boolean"},
                       "confidence": {"type": "number"}}}}}}


def top_investors(n):
    con = sqlite3.connect(ROOT / "db" / "deals.db")
    rows = con.execute("""
        SELECT i.name, COUNT(*) AS n,
               group_concat(DISTINCT c.sector) AS sectors,
               group_concat(DISTINCT c.name) AS companies
        FROM investors i JOIN deal_investors di USING(investor_id)
        JOIN deals d USING(deal_id) JOIN companies c USING(company_id)
        GROUP BY i.investor_id ORDER BY n DESC LIMIT ?""", (n,)).fetchall()
    con.close()
    return [{"name": r[0], "deals": r[1], "sectors": (r[2] or "")[:120],
             "sample_companies": ",".join((r[3] or "").split(",")[:5])} for r in rows]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 800
    SCHEMA.write_text(json.dumps(SCHEMA_OBJ), encoding="utf-8")
    done = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    todo = [x for x in top_investors(n) if x["name"] not in done]
    print(f"{len(todo)} investors to classify ({len(done)} cached)")
    for i in range(0, len(todo), 60):
        chunk = todo[i:i + 60]
        prompt = PROMPT + "\nINVESTORS:\n" + "\n".join(json.dumps(x, ensure_ascii=False) for x in chunk)
        tmp = ROOT / "data" / "processed" / "_inv_out.json"
        cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "-m", "gpt-5.6-terra",
               "-c", 'model_reasoning_effort="low"', "--output-schema", str(SCHEMA), "-o", str(tmp), "-"]
        subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=900, shell=True)
        try:
            res = json.loads(tmp.read_text(encoding="utf-8"))["investors"]
        except Exception as e:  # noqa: BLE001
            print("batch failed:", e)
            continue
        for r in res:
            done[r["name"]] = r
        OUT.write_text(json.dumps(done, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  classified {len(done)}")
    tmp = ROOT / "data" / "processed" / "_inv_out.json"
    if tmp.exists():
        tmp.unlink()


if __name__ == "__main__":
    main()
