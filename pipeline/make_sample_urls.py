"""Build a small URL list from already-cached sitemaps (for smoke tests)."""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_sitemaps import CACHE, classify  # noqa: E402

out = Path(sys.argv[1])
rows = []
for f in sorted(CACHE.glob("*.xml"))[-12:]:
    for u in re.findall(r"<loc>(.*?)</loc>", f.read_text(encoding="utf-8")):
        rows.append({"date": f.stem, "url": u, "slug": u.rstrip("/").split("/")[-1], "kind": classify(u)})
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["date", "url", "slug", "kind"])
    w.writeheader()
    w.writerows(rows)
print(len(rows), "sample urls")
