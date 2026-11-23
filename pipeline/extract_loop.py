"""Keep running extraction while the downloader works; final pass when everything is in.

Stops when every target article is downloaded and every batch has a result.
Safe to kill and restart at any time (all results are cached).
"""
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"deal", "acquisition", "financials", "report"}


def download_complete(urls_file="data/raw/entrackr_urls.csv"):
    cache = ROOT / "data" / "raw" / "articles"
    for row in csv.DictReader((ROOT / urls_file).open(encoding="utf-8")):
        if row["kind"] not in KINDS:
            continue
        p = cache / (hashlib.md5(row["url"].encode()).hexdigest() + ".json")
        if not p.exists():
            return False
        err = json.loads(p.read_text(encoding="utf-8")).get("error")
        if err and not re.match(r"http (40[0-4]|410|451)", err):
            return False
    return True


def main():
    extra = sys.argv[1:]
    urls_file = extra[extra.index("--urls") + 1] if "--urls" in extra else "data/raw/entrackr_urls.csv"
    while True:
        done = download_complete(urls_file)
        cmd = [sys.executable, str(ROOT / "pipeline" / "run_extraction.py")] + extra + (["--final"] if done else [])
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        tail = [l for l in p.stdout.splitlines() if "records" in l or "failed" in l or "done:" in l]
        print(time.strftime("%H:%M"), "download complete" if done else "downloading", "|",
              "; ".join(tail[-3:]), flush=True)
        if done and "0 failed" in p.stdout:
            print("ALL BATCHES EXTRACTED", flush=True)
            return
        time.sleep(90 if not done else 30)


if __name__ == "__main__":
    main()
