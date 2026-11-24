"""One command to rebuild everything after new articles are extracted.

  python pipeline/run_all.py            # build DB + all quality checks + engines + report
  python pipeline/run_all.py --refresh  # first collect new URLs/articles of the last 14 days and extract them

Steps: [refresh] -> build_db -> validate -> crosscheck -> coverage -> tests -> engines -> data report
Each step's success/failure is printed; a failing step does not stop the later independent ones.
"""
import datetime as dt
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def step(name, args):
    t = time.time()
    p = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    ok = p.returncode == 0
    tail = (p.stdout.strip().splitlines() or [""])[-1][:110]
    print(f"[{'OK ' if ok else 'ERR'}] {name:28s} {time.time() - t:6.1f}s  {tail}", flush=True)
    if not ok:
        print("      ", (p.stderr.strip().splitlines() or [""])[-1][:200])
    return ok


def main():
    if "--refresh" in sys.argv:
        start = (dt.date.today() - dt.timedelta(days=14)).isoformat()
        end = dt.date.today().isoformat()
        step("collect new sitemaps", ["pipeline/collect_sitemaps.py", start, end, "data/raw/entrackr_urls_recent.csv"])
        step("download new articles", ["pipeline/fetch_articles.py", "0", "data/raw/entrackr_urls_recent.csv", "2"])
        step("extract new articles", ["pipeline/run_extraction.py", "--urls", "data/raw/entrackr_urls_recent.csv",
                                      "--tag", f"recent{end.replace('-', '')}", "--final"])
    step("build database", ["pipeline/build_db.py"])
    step("rule-based validation", ["pipeline/validate.py"])
    step("two-agent agreement", ["pipeline/crosscheck.py"])
    step("coverage audit", ["pipeline/coverage.py"])
    step("tests: headline parser", ["tests/test_headline_parser.py"])
    step("tests: entity resolution", ["tests/test_resolver.py"])
    step("tests: rule extractor", ["tests/test_rule_extract.py"])
    step("analytics engines", ["analysis/run_engines.py"])
    step("data report", ["analysis/data_report.py"])


if __name__ == "__main__":
    main()
