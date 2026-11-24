# Arventum Deal Intelligence: one-page summary

**Problem.** Arventum's edge is knowing, faster than other banks, *who* will raise, *who* will invest, *who* will buy and *at what price*. Today that knowledge sits in two founders' heads and in hours of manual research before every pitch.

**What I built.** An AI-native deal-intelligence system, using only public data, with no ongoing cost:

| Engine | Arventum process step | Validated how |
|---|---|---|
| Market Pulse | Industry Intelligence | Captured capital tracks published weekly totals |
| Origination Radar | Market Mapping, Target Identification | Walk-forward backtest: top-100 precision 30% vs 14% for a banker's rule of thumb |
| Investor Matchmaker | Investor Mapping | 314 real rounds: top-10 hit rate 47% vs 27% baseline |
| Buyer Mapping | Buyer Mapping | Sector- and recency-weighted acquirer appetite |
| Price Finder | Valuation Benchmarking | Model chosen by leave-one-out CV; listed peers + Indian private rounds |

**How.** A crawler downloaded ~11,000 deal, acquisition and financials articles (Entrackr 2021–2026, Inc42). Two AI agents (Codex and OpenCode, GPT-5.6) extracted them into a structured database under a strict schema. When the ChatGPT quota ran out, benchmarked free models and then a measured rule-based extractor (97.5% deal precision) filled in, each labelled so a later AI pass supersedes it. Rules then reconciled, de-duplicated and audited the records. Claude Code architected the system and orchestrated the agents. The result is **5,459 deals, 3,947 companies and 5,645 investors** across 2021–2026.

**Trust.** Four independent quality checks: AI agents agree 99% on company and deal type; 98% of amounts match the headline; company names are grounded in the source 99.8% of the time; an independent manual audit scored 40/40 on type, company and investors. Every record links to its source article, and every automatic correction is logged.

**Engineering.** 24 real data problems found and fixed (throttling, leaked CMS links, DNS blips, valuation figures mistaken for round sizes, quota exhaustion, …), with regression tests for each.

**Next with Arventum's data.** Plug in the CRM and relationship network (warm-introduction paths), a paid database for small rounds, and a weekly "top 10 companies to call" email.
