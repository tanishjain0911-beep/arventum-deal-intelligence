"""Second source: Inc42 article URLs (for coverage and cross-source validation).

Respects robots.txt (no query strings, no /page/ paths). Polite: 1 request at a time.
Output: data/raw/inc42_urls.csv (url, lastmod, slug, kind)
"""
import csv
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "sitemaps_inc42"
OUT = ROOT / "data" / "raw" / "inc42_urls.csv"
UA = {"User-Agent": "Mozilla/5.0 (research project; polite crawler)"}

FUNDING = re.compile(r"(raises?|raised|nets|bags|secures?|grabs|gets|lands|closes|funding|round|"
                     r"series-[a-f]|pre-series|seed|invests?|backs|led-by|debt-funding)")
ACQ = re.compile(r"(acquires?|acquisition|acquired|buys|merger|merges|takeover)")
FIN = re.compile(r"(revenue|loss|profit|fy2\d|financials)")
EXCLUDE = re.compile(r"(funding-galore|weekly-funding|this-week|tracker|report-|-report|ipo-|explained|why-|how-)")


def classify(slug):
    if EXCLUDE.search(slug):
        return "other"
    if ACQ.search(slug):
        return "acquisition"
    if FIN.search(slug) and not FUNDING.search(slug):
        return "financials"
    if FUNDING.search(slug):
        return "deal"
    return "other"


def get(url, path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=60)
        if r.status_code == 200:
            path.write_text(r.text, encoding="utf-8")
            time.sleep(1.5)
            return r.text
        time.sleep(15 * (attempt + 1))
    return ""


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    idx = get("https://inc42.com/sitemap_index.xml", CACHE / "index.xml")
    sms = [u for u in re.findall(r"<loc>(.*?)</loc>", idx) if "post-sitemap" in u]
    rows = []
    for sm in sms:
        text = get(sm, CACHE / sm.rsplit("/", 1)[-1])
        for block in re.findall(r"<url>(.*?)</url>", text, re.S):
            loc = re.search(r"<loc>(.*?)</loc>", block)
            mod = re.search(r"<lastmod>(.*?)</lastmod>", block)
            if not loc:
                continue
            u = loc.group(1).strip()
            if "?" in u or "/page/" in u:
                continue
            slug = u.rstrip("/").split("/")[-1]
            rows.append({"url": u, "lastmod": mod.group(1)[:10] if mod else "", "slug": slug, "kind": classify(slug)})
        print(sm.rsplit("/", 1)[-1], len(rows), flush=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "lastmod", "slug", "kind"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print("total", len(rows), Counter(r["kind"] for r in rows))


if __name__ == "__main__":
    main()
