# Methodology: Arventum Deal Intelligence

This document explains how the data is collected, how AI is used, how quality is checked, and how each analytical engine works and is tested. Every number in the product can be traced to a public source article.

---

## 1. Data collection

| Source | What we take | How | Volume (2023 to present) |
|---|---|---|---|
| **Entrackr** (primary) | Funding rounds, acquisitions, company financials, weekly round-ups | Daily sitemaps list every article. A polite crawler downloads each relevant article. | ~6,600 relevant articles |
| **Inc42** (second source) | Funding rounds, acquisitions, financials | Post sitemaps, filtered by URL keywords | ~6,800 relevant articles |
| **Entrackr history** (2021-22) | The same, for longer company histories | Same crawler | in progress |
| **Yahoo Finance** | Listed comparable companies: EV, revenue, growth, margins | `yfinance` | 92 companies (India and global) |

**Politeness and compliance**
- Both sites' `robots.txt` allow crawling of article pages. Inc42 explicitly signals `ai-input=yes` (AI processing is allowed) and `ai-train=no`. We do no model training.
- YourStory was **excluded** because its content signals do not clearly allow AI processing.
- An **adaptive rate limiter** spaces requests, slows down automatically when a site answers `429 Too Many Requests`, and never caches a throttled response as data.
- Raw pages are cached, so nothing is downloaded twice.

## 2. Turning articles into structured data (multi-agent extraction)

Each article becomes one structured record: company, what it does, sector, city, deal type, stage, amount, currency, valuation, lead investors, other investors, acquirer, and (for financial stories) fiscal year, revenue and profit.

- **Two independent AI agents** do the reading, both running on GPT-5.6 through two different tools:
  - **Codex CLI**, with a **strict JSON schema**: the model cannot return malformed or out-of-vocabulary values.
  - **OpenCode**, with the same instructions, as a second, independent reader.
- Articles are processed in batches of 30, in parallel. A batch is assigned to one agent; every result is cached, so the run is resumable.
- The instructions forbid guessing ("use only facts stated in the article, null otherwise") and fix the vocabularies (32 sectors including Arventum's 20 focus sectors, and 16 stages).
- **Weekly and monthly round-ups are not sent to the AI.** They are parsed by deterministic rules (see QA).

## 3. Cleaning, reconciliation and de-duplication (`pipeline/build_db.py`)

| Step | Rule |
|---|---|
| Two-agent merge | When both agents read an article, the more confident record wins and its missing fields are filled from the other one. |
| **Headline-wins** | A deterministic parser reads the amount from the headline (`$11 Mn`, `Rs 70 Cr`, `₹115 Cr`, `$500K`). If the AI's amount differs by more than 12%, the headline amount is used. |
| Plausibility | Amounts outside $5k to $20bn are dropped (the deal is kept). Valuations below the round size are dropped. |
| Currency | INR is converted to USD at the average RBI reference rate of the deal's year. |
| Investor entity resolution | Manual alias table for known renames (e.g. Sequoia India → **Peak XV Partners**, SAIF → **Elevation Capital**, Matrix India → **Z47**), plus fuzzy matching on names stripped of generic words ("Capital", "Ventures", "Partners"…). |
| Company entity resolution | Fuzzy matching on names stripped of legal suffixes. |
| **Cross-source de-duplication** | Same company + same deal type + within 45 days + amount within 20% = one deal. Every confirming article is kept (`deal_sources`), so a deal reported by both Entrackr and Inc42 shows *2 sources*. |
| Investor typing | Rules classify investors as Institutional, Individual, Angel network, Accelerator, Debt / Bank, Family office or Corporate. |

Every automatic change is written to a **`corrections` audit table** (URL, field, AI value, corrected value, rule).

## 4. Quality assurance: three independent checks

1. **Agent agreement** (`pipeline/crosscheck.py`): a sample of batches is read by **both** agents, and agreement is measured field by field. Pilot (30 articles): deal type 100%, amount 96.7%, stage 96.7%, company 100%, lead investors 86.7%, sector 80% (sector is partly a judgement call).
2. **Rule-based validation** (`pipeline/validate.py`, no AI involved):
   - headline amount vs AI amount
   - round size plausible for its stage
   - core fields present
   - the extracted company name actually appears in the article (catches hallucinated names)
   Flagged rows are exported for manual review.
3. **Coverage / recall audit** (`pipeline/coverage.py`): Entrackr's weekly round-ups state how many deals happened each week ("43 startups raised $222.9M"). The parser reads 100% of the weekly reports downloaded so far, and we compare our captured deal count with the reported count, week by week. This measures how **complete** the database is, not just how accurate.

## 5. Database (`db/deals.db`, SQLite)

`companies`, `investors`, `investor_aliases`, `deals`, `deal_investors` (with a lead flag), `deal_sources`, `sources`, `financials` (revenue and profit per company per fiscal year, with the publication date), `weekly_totals`, `corrections`. CSV exports are in `data/processed/`.

## 6. Analytical engines (`app/lib/`)

### 6.1 Origination Radar (`radar.py`): who raises next?
- **Question:** which companies will announce a new primary round in the next 12 months?
- **Design:** a *panel* of monthly snapshots. At each cut-off date every company gets features computed **only from information published before that date**, so there is no look-ahead. The label is whether it raised within the following 12 months.
- **Features (16):** months since last round, stage and size of the last round, number of rounds, typical gap between rounds, total raised, number of backers, backed by a top-30 investor, named lead in the last round, last round was debt, sector momentum (deals in the last 6 months vs the prior 6), sector volume, and public-financials signals (revenue, revenue growth, profitability), used only after their publication date.
- **Model:** gradient-boosted trees (scikit-learn `HistGradientBoostingClassifier`), which handle missing values natively.
- **Backtest:** walk-forward. Train only on cut-offs whose 12-month outcome window closed **before** the test date, then test on an unseen later cut-off. Reported: AUC, base rate, precision in the top 50 and top 100, lift over random, and hit rate by decile.
- **Explainability:** permutation importance (drop in AUC when a feature is shuffled) plus plain-English signals for each company.

### 6.2 Investor Matchmaker (`matching.py`): who will invest?
- Each investor's taste profile comes from its deals, recency-weighted with a 1-year half-life.
- **Score** = weighted geometric blend of sector fit, stage fit (same or adjacent stage), cheque-size fit, recent activity (18 months) and, optionally, lead propensity.
- **Empirical-Bayes shrinkage:** an investor with 1 deal cannot "prove" a 100% sector focus. Shares are pulled toward the market average until there is enough evidence.
- **Backtest:** for every round in 2026, investors are ranked using only data before that month. We check whether a real participant appears in the top 10, 20 or 50. The baseline is "most active investors overall", the list a banker might use today.

### 6.3 Price Finder (`valuation.py`): what is it worth?
Three independent methods, shown together as a banker's **football-field chart**:
1. **Listed sector peers:** the 25th to 75th percentile of EV/Revenue for listed comparables in the sector, after a **25% private-company (illiquidity) discount**.
2. **Regression-adjusted:** log(EV/Revenue) regressed on revenue growth, EBITDA margin, gross margin and an India dummy. The specification was **chosen by leave-one-out cross-validation** among 6 candidates (`analysis/valuation_model_selection.py`). Gross margin was the strongest addition (in-sample R² from 0.15 to 0.30, out-of-sample error down about 10%).
3. **Indian private rounds:** valuation ÷ latest reported revenue for private rounds in our database where both are public.

## 7. Known limitations (stated openly)
- Public news covers most disclosed rounds, but not every private transaction. The coverage audit quantifies this.
- Private valuations and revenues are disclosed for only a minority of companies, so private-market multiples rest on a smaller sample.
- The Radar sees companies' fundraising history only from the start of our data window. Earlier rounds are invisible, which is why the history back-fill (2021-22) matters.
- Investor "fit" is inferred from public deal participation, not from fund mandates or dry powder.
- With access to a paid database (Tracxn, Venture Intelligence, PitchBook) or Arventum's own CRM, every engine would improve without code changes.
