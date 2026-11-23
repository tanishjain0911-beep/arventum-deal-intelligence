"""Step 2a: collect every Entrackr article URL from the daily sitemaps.

Politeness: max 3 parallel requests, short pause per request, cached so a day
is never fetched twice. Output: data/raw/entrackr_urls.csv (date, url, slug, kind)
"""
import csv
import datetime as dt
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "sitemaps"
OUT = ROOT / "data" / "raw" / "entrackr_urls.csv"
UA = {"User-Agent": "Mozilla/5.0 (research project; polite crawler)"}
START = dt.date(2023, 1, 1)

DEAL_WORDS = re.compile(
    r"raises?|raised|secures?|bags?|leads?-|led-by|funding|round|invests?|backs?|"
    r"picks-up|acquires?|acquisition|buys|merger|stake|ipo|series-|seed|pre-series|debt"
)


def classify(slug: str) -> str:
    if "fintrackr" in slug or re.search(r"revenue|loss|profit|fy2\d", slug):
        return "financials"
    if re.search(r"weekly-funding-report|monthly-funding-report", slug):
        return "report"
    if re.search(r"acquires?|acquisition|buys-|merger|merges", slug):
        return "acquisition"
    if DEAL_WORDS.search(slug):
        return "deal"
    return "other"


def fetch_day(day: dt.date):
    path = CACHE / f"{day}.xml"
    if not path.exists():
        for attempt in range(8):
            try:
                r = requests.get(f"https://entrackr.com/sitemap_{day}.xml", headers=UA, timeout=30)
                if r.status_code == 200:
                    path.write_text(r.text, encoding="utf-8")
                    break
                if r.status_code == 404:
                    path.write_text("", encoding="utf-8")  # genuinely no sitemap that day
                    break
                time.sleep(20 * (attempt + 1))  # 429 / 5xx: back off, never cache
            except requests.RequestException:
                time.sleep(5 * (attempt + 1))
        time.sleep(1.0)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    # some sitemaps leak the CMS host (entrackr-prod.publive.io); the same path is live on entrackr.com
    return [(str(day), u.replace("://entrackr-prod.publive.io/", "://entrackr.com/"))
            for u in re.findall(r"<loc>(.*?)</loc>", text)]


def main():
    """Usage: collect_sitemaps.py [START END OUTFILE]   e.g. 2019-01-01 2022-12-31 data/raw/entrackr_urls_hist.csv"""
    import sys
    global OUT
    CACHE.mkdir(parents=True, exist_ok=True)
    start, end = START, dt.date.today()
    if len(sys.argv) == 4:
        start, end = dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2])
        OUT = ROOT / sys.argv[3]
    days = [start + dt.timedelta(d) for d in range((end - start).days + 1)]
    rows = []
    with ThreadPoolExecutor(max_workers=1) as ex:
        for i, res in enumerate(ex.map(fetch_day, days)):
            rows.extend(res)
            if i % 100 == 0:
                print(f"{i}/{len(days)} days, {len(rows)} urls", flush=True)
    seen, out = set(), []
    for day, url in rows:
        if url in seen:
            continue
        seen.add(url)
        slug = url.rstrip("/").split("/")[-1]
        out.append({"date": day, "url": url, "slug": slug, "kind": classify(url)})
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "url", "slug", "kind"])
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print("total", len(out), Counter(r["kind"] for r in out))


if __name__ == "__main__":
    main()
