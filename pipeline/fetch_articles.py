"""Step 2b: download deal / acquisition / financials / report articles.

Keeps only what extraction needs: title, description, company keyword,
published date and the first body paragraphs. Cached per article, so the
script can be stopped and re-run safely.
Output: data/raw/articles.jsonl
"""
import csv
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
URLS = ROOT / "data" / "raw" / "entrackr_urls.csv"
CACHE = ROOT / "data" / "raw" / "articles"
OUT = ROOT / "data" / "raw" / "articles.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (research project; polite crawler)"}
KINDS = {"deal", "acquisition", "financials", "report"}
STOP_MARKERS = ("Disclaimer", "Entrackr is a new age media platform")
NOISE = ("By clicking the button", "Don’t have an account", "Follow Us")


def meta(soup, key):
    tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
    return (tag.get("content") or "").strip() if tag else ""


def parse(html: str):
    soup = BeautifulSoup(html, "lxml")
    paras = []
    for p in soup.find_all("p"):
        txt = p.get_text(" ", strip=True)
        if not txt or txt == "0" or any(n in txt for n in NOISE):
            continue
        if any(txt.startswith(s) for s in STOP_MARKERS):
            break
        if p.parent and p.parent.get("class"):
            continue
        paras.append(txt)
    return {
        "title": meta(soup, "og:title"),
        "description": meta(soup, "og:description"),
        "company_kw": meta(soup, "keywords"),
        "published": meta(soup, "article:published_time"),
        "body": paras[:8],
    }


def fetch(row):
    key = hashlib.md5(row["url"].encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    rec = {"url": row["url"], "date": row["date"], "kind": row["kind"], "error": None}
    for attempt in range(3):
        try:
            r = requests.get(row["url"], headers=UA, timeout=30)
            if r.status_code == 200:
                rec.update(parse(r.text))
            else:
                rec["error"] = f"http {r.status_code}"
            break
        except requests.RequestException as e:
            rec["error"] = str(e)[:120]
            time.sleep(3 * (attempt + 1))
    path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.5)
    return rec


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    urls_file = Path(sys.argv[2]) if len(sys.argv) > 2 else URLS
    rows = [r for r in csv.DictReader(urls_file.open(encoding="utf-8")) if r["kind"] in KINDS]
    if len(sys.argv) > 1 and int(sys.argv[1]) > 0:
        rows = rows[: int(sys.argv[1])]
    print("articles to fetch:", len(rows), flush=True)
    done, errors = [], 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, rec in enumerate(ex.map(fetch, rows)):
            done.append(rec)
            errors += bool(rec.get("error"))
            if i % 250 == 0:
                print(f"{i}/{len(rows)} fetched, {errors} errors", flush=True)
    with OUT.open("w", encoding="utf-8") as f:
        for rec in done:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("done", len(done), "errors", errors)


if __name__ == "__main__":
    main()
