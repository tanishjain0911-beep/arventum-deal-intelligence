# Arventum Deal Intelligence

**AI-native deal intelligence for technology investment banking, built entirely from public data.**

Arventum advises Indian technology companies on fundraising and M&A. This project turns thousands of public deal reports into a structured, quality-checked deal database, and runs four analytical engines on it. Each engine maps to a step in Arventum's own deal process.

| Engine | Arventum process step | Question it answers | How it is validated |
|---|---|---|---|
| **Origination Radar** | Market Mapping, Target Identification | Which companies are likely to raise or transact in the next 12 months? | Walk-forward backtest: AUC, precision@50/100, lift over random |
| **Investor Matchmaker** | Investor Mapping | Which funds are most likely to back this company, and why? | 2026 out-of-sample hit rate vs a "most active investors" baseline |
| **Buyer Mapping** | Buyer Mapping | Who acquires companies like this one? | Recency- and sector-weighted acquirer appetite |
| **Price Finder** | Valuation Benchmarking | What is it worth? | Listed peers, CV-selected regression, Indian private rounds (football field) |
| **Market Pulse** | Industry Intelligence | What is happening in each of Arventum's 20 sectors? | Coverage audited against published weekly totals |

## How it works

```
 Entrackr + Inc42 sitemaps ──► polite crawler (adaptive rate limit, robots.txt-compliant)
                                   │  ~13,000 deal / acquisition / financials articles (2023 to present, history back-fill)
                                   ▼
            Multi-agent extraction:  Codex CLI (strict JSON schema)  ║  OpenCode   (GPT-5.6, in parallel)
                                   │
                                   ▼
   Reconciliation: two-agent merge · headline-wins amount check · plausibility rules · entity resolution
                   · cross-source de-duplication · full audit trail of every correction
                                   │
                                   ▼
          SQLite deal database  ──►  QA: agent agreement · rule-based validation · coverage vs weekly totals
                                   │      · independent manual audit · regression tests
                                   ▼
             Origination Radar · Investor Matchmaker · Buyer Mapping · Price Finder · Market Pulse
```

## Built with an AI team
- **Claude Code**: architect and lead engineer. Designed the system, wrote the pipeline and models, orchestrated the other agents, and audited their output.
- **Codex CLI** and **OpenCode** (ChatGPT Plus / GPT-5.6): parallel bulk extraction of thousands of articles; a sample is read by both to measure agreement.
- **GitHub**: version control and the scheduled refresh.

## Reproduce
```bash
pip install -r requirements.txt
python pipeline/collect_sitemaps.py          # article URLs (Entrackr daily sitemaps)
python pipeline/fetch_articles.py            # polite download, cached
python pipeline/extract_loop.py              # multi-agent extraction (needs codex / opencode logged in)
python pipeline/fetch_comparables.py         # listed comparables (Yahoo Finance)
python pipeline/run_all.py                   # build DB + all QA + engines + data report
```

## Documentation
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md): collection, extraction, cleaning, QA and every model, with limitations stated openly
- [`docs/DATA_REPORT.md`](docs/DATA_REPORT.md): current database contents and quality metrics (auto-generated)
- [`docs/MANUAL_AUDIT.md`](docs/MANUAL_AUDIT.md): independent field-by-field audit of AI extraction

## Repository layout
```
pipeline/   collection, extraction, reconciliation, QA (build_db.py, validate.py, coverage.py, ...)
app/lib/    analytics engines (radar.py, matching.py, acquirers.py, valuation.py, data.py)
analysis/   engine runs, model selection, reports
tests/      regression tests (headline parser, entity resolution)
db/         schema.sql and deals.db
data/       raw URL lists, AI extraction outputs, processed CSV exports
docs/       methodology, data report, audit
```

_All data comes from public sources. Articles are used for information extraction only. Each record links to its source._
