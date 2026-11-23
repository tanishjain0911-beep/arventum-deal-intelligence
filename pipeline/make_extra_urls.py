"""URLs found by a later sitemap pass that are not in the main list (history years + recovered gap days).
Usage: python pipeline/make_extra_urls.py data/raw/entrackr_urls_2021on.csv data/raw/entrackr_urls_extra.csv
Rows are ordered newest-first so the most useful history (2022) is downloaded and extracted first.
"""
import sys

import pandas as pd

new = pd.read_csv(sys.argv[1])
main = pd.read_csv("data/raw/entrackr_urls.csv")
extra = new[~new.url.isin(main.url)].copy()
extra = extra.sort_values("date", ascending=False)
extra.to_csv(sys.argv[2], index=False)
extra["y"] = extra.date.str[:4]
print(len(extra), "extra urls")
print(extra.groupby(["y", "kind"]).size().unstack(fill_value=0))
