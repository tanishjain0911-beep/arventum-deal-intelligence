"""Build a list of every downloaded target article that no extraction output covers yet.

Used to catch articles skipped by earlier runs (e.g. ones temporarily marked as failed), without
disturbing existing batch boundaries. Output: data/raw/remaining_urls.csv (newest first).
Usage: python pipeline/make_remaining.py
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _records  # noqa: E402
from run_extraction import is_roundup  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"deal", "acquisition", "financials"}
done = {r["url"] for f in (ROOT / "data" / "extracted").glob("*/*.json") for r in _records(f)}
lists = ["entrackr_urls.csv", "entrackr_urls_extra.csv"]
rows, seen = [], set()
for name in lists:
    for r in csv.DictReader((ROOT / "data" / "raw" / name).open(encoding="utf-8")):
        if r["kind"] not in KINDS or r["url"] in done or r["url"] in seen or is_roundup(r["url"]):
            continue
        p = ROOT / "data" / "raw" / "articles" / (hashlib.md5(r["url"].encode()).hexdigest() + ".json")
        if p.exists() and not json.loads(p.read_text(encoding="utf-8")).get("error"):
            seen.add(r["url"])
            rows.append({"date": r["date"], "url": r["url"], "slug": r["slug"], "kind": r["kind"]})
rows.sort(key=lambda r: r["date"], reverse=True)
with (ROOT / "data" / "raw" / "remaining_urls.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["date", "url", "slug", "kind"])
    w.writeheader()
    w.writerows(rows)
print(len(rows), "downloaded but not yet extracted")
