# Engineering log: problems found and fixed while building the data pipeline

Real-world data is messy. Each entry below was **detected by a check built into the pipeline** (or by watching its throughput), diagnosed, and fixed at the root, with a regression test where possible.

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | 25% of article downloads failing | Site answered `429 Too Many Requests` to 4 parallel workers | Fewer workers; **adaptive (AIMD) rate limiter** shared by all threads: the gap widens ×1.6 on a 429 and narrows on success |
| 2 | 45 weekdays with "no articles" | Throttled sitemap responses had been **cached as empty days** | Never cache a non-200/404 response; deleted and re-collected the 45 days |
| 3 | Download stalled for ~30 minutes with no errors | **36 sitemap links pointed to the CMS host `entrackr-prod.publive.io`**, which doesn't resolve; each was retried for ~165 s | Rewrite the host to `entrackr.com` (same path, verified live); treat DNS failures as permanent (no retries) |
| 4 | Crawler could freeze for up to an hour | An uncapped `Retry-After` header was obeyed literally | Honour `Retry-After`, but cap it at 60 s |
| 5 | Second source (Inc42) returned empty article bodies | Page layout nesting was the opposite of what was first assumed | Fixed CSS selectors, verified on old and new layouts, purged the 84 bad cache files |
| 6 | Inc42 throughput ~4 articles/min | Aggressive throttling + fixed 20 s pauses | Same adaptive limiter; **priority ordering** (2025-26 deals first) so the most valuable data lands first |
| 7 | "$500K" recorded as $50M | Extraction schema had no "thousand" unit, forcing a wrong choice | Added the unit; **deterministic headline parser** overrides AI amounts that disagree ("headline-wins"), with an audit trail |
| 8 | Udaan's round recorded as $1.7B | The headline parser read the **valuation** ("valuation tanks to $1.7 Bn") as the round size | Parser skips amounts next to valuation, revenue, loss, fund, AUM and similar words; 19-case regression test |
| 9 | "Rs" matched inside ordinary words | Currency regex lacked word boundaries | Word-bounded currency tokens |
| 10 | 88 weekly round-ups sent to the AI as "acquisitions" | URL contains "funding-and-acquisitions" | Round-ups are excluded from AI extraction and parsed by rules instead (100% of reports parsed) |
| 11 | Weekly totals parsed for only 50% of reports | Many phrasings ("12 funding deals", "nine startups", "which scooped up") | Two-step parser (count, then the nearest $ total); 100% coverage |
| 12 | Investor rankings polluted by "angel investors", "existing investors" | The AI listed placeholders as investors | Placeholder filter + tests |
| 13 | Same fund under several names (IPV / Inflection Point Ventures; Sequoia India / Peak XV) | Spelling variants, acronyms, rebrands | Alias table + fuzzy matching + a duplicate-finder report for review; 29-case regression test; corrected "BII" to British International Investment |
| 14 | Financial records missing profit/loss | The loss figure sits later in the article than the 1,000-character window | Financial stories get a 2,000-character window (found by manual audit) |
| 15 | Radar crashed on periods with no financials | Histogram binning cannot handle an all-NaN feature | NaN-safe feature matrix; **synthetic end-to-end test** (planted 20-month cycles, which the model must recover: AUC 0.83 vs heuristic 0.76) |
| 16 | Matchmaker ranked one-deal investors at 100% "sector fit" | Small-sample proportions | **Empirical-Bayes shrinkage** toward the market average |
| 17 | Valuation regression weak (R² 0.15) | Missing driver | Leave-one-out CV across 6 specifications; adding gross margin doubled R² (0.30) and cut out-of-sample error ~10% |
| 18 | Schema file unreadable by Codex | PowerShell 5 wrote a UTF-8 BOM and mangled "₹" | Stripped the BOM, scanned all files for mojibake, moved edits to a safe path |

| 19 | History extraction "finished" with only 14 of ~80 batches | Fix #3 (treat DNS failure as permanent) was too broad: a brief network blip made **3,400 valid entrackr.com articles** look permanently dead | DNS failures are now retried with back-off and marked permanent only after 4 failures; poisoned cache entries purged and re-downloaded; a "remaining" list re-queues every downloaded-but-unextracted article |
| 20 | ChatGPT Plus quota exhausted overnight | ~100 batches per 5-hour window at full parallelism | Benchmarked 8 free OpenCode models against Codex; used only those scoring ~93% agreement; cut prompt size ~30%; each deal records which agent extracted it, and the merge prefers higher-accuracy agents |
| 21 | Investor Matchmaker no better than a "most active investors" list (top-10 hit 26% vs 29%) | Hand-set weights over-weighted sector fit | Weights tuned on a validation window and **tested on an untouched later window**: top-10 hit rate 38% vs 29% for the baseline (211 real rounds) |

| 22 | Radar weak on real data (AUC 0.55) despite AUC 0.83 on synthetic data | Gradient-boosted trees overfit noisy public-coverage labels; tested two other hypotheses first (equity-only labels: worse; denser training window: no change) | Compared model families on the same rolling backtest: **logistic regression** won (AUC 0.625); added "distance from usual fundraising cycle" and "inside 15-30 month window" features so a linear model can express the due-date peak, giving **AUC 0.63, top-100 precision 36% vs 12.5% for the banker heuristic (2.3× lift)**, and the synthetic test passes again |

| 23 | Free OpenCode models unresponsive (even one at a time) and ChatGPT quota exhausted again | External services down; no AI extractor available | Built a **deterministic headline extractor** measured against Codex on 3,000 articles (deal precision 97.5%, company 91%, amount 88%, stage 91%), stored as the lowest-priority agent so any later AI pass supersedes it; the "remaining" queue still re-sends those articles to the AI |
| 24 | Radar results looked unchanged after adding 1,250 history deals | The engine runner caught an exception and still reported success, so a stale result file stayed on screen | Engine failures are now collected and the runner exits non-zero, so `run_all.py` shows ERR; re-run gave the true figures (AUC 0.61, top-100 precision 30% vs 14% heuristic) |

| 25 | Buyer Mapping showed targets like "quick ride", "platform", and a wrong "Udaan acquired Swiggy" | The rule extractor's 97.5% figure measured deal *type*, not acquisition target names; headline target parsing is unreliable. Rule-only companies were also silently filed under sector "Other" | Rules now emit only funding rounds and financials (acquisitions wait for AI); companies with no extracted sector are labelled **"Unclassified"** and kept out of sector charts. Found by visual QA of the rendered page, a check no metric covered |
| 26 | Radar's top pick had already IPO'd | Listed companies aren't private-funding targets | Exclude companies with an IPO record, plus names matching the listed-comparables universe (catches listings before 2021, e.g. Nazara) |

| 27 | Some 2021–22 weeks showed *more* capital captured than the published market total | Unacademy recorded at $3.44B (its **valuation**: "valuation spikes over 70% to $3.44 Bn as it raises $440 Mn"), because digits between the keyword and the amount defeated the skip rule; "OfBusiness **closes** FY21 with…" read as a funding round | Valuation-context window now allows digits; "closes" counts as a raise only next to "round/funding/series/seed"; both added as regression tests (20/20 and 14/14). Found by reading the captured-vs-published chart, where capturing more than 100% of the market is impossible |

| 28 | Several weeks still captured 3–20× the published total | **Listed-company raises** (Zomato's ₹8,500 Cr QIP, Nazara's preferential issue, Swiggy's IPO anchor book) were counted as startup rounds; published startup totals exclude them | New `public_market` deal type for QIP, preferential issue, anchor book, rights issue, block deal and OFS (54 reclassified), kept out of private-funding analytics. Capital coverage fell from 84.8% to **79.6%**: lower, but now measured like-for-like |

**Takeaway:** every fix is enforced by a check that runs on each rebuild (`python pipeline/run_all.py`): validation, the coverage audit, two-agent agreement, and regression tests.
