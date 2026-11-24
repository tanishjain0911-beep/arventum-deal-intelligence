# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated: a static site (HTML/CSS/JS, no framework) that reads JSON exported by the existing Python pipeline (`pipeline/`, `app/lib/` engines). Interactive tools (Investor Matchmaker, Price Finder) compute in the browser from exported data; Radar, Buyer Mapping and Market Pulse are precomputed. Free static hosting (Vercel or GitHub Pages). Chosen for speed of build before a Wednesday-evening deadline, zero server maintenance, and full design control. The Streamlit app in `app/` remains as the reference implementation.

## Users

Both equally:
- **Arventum's founders (two managing directors of a tech-focused investment bank, Mumbai/Bengaluru)** first meet it in an internship candidate's live demo, then may explore it themselves. It must convince them fast and then hold up under clicking around.
- **Bankers doing pitch and deal preparation**: before meeting a founder, they need market context, likely investors and buyers, a valuation range, and a company's history, quickly and with sources.

## Product Purpose

An AI-native deal-intelligence system for Indian technology transactions, built only from public data. It turns thousands of public deal reports into a quality-checked database and five engines that map to steps of Arventum's own deal process: Market Pulse (industry intelligence), Origination Radar (who raises next), Investor Matchmaker (investor mapping), Buyer Mapping (acquirers), Price Finder (valuation benchmarking), plus Company Lookup. Success means the founders see it as credible, useful to their workflow, and clearly beyond what a single AI prompt could produce.

## Positioning

Its own sourced dataset plus measured accuracy. Every deal links to its source article. Every model is backtested on outcomes it never saw, and data quality is audited four ways (agent agreement, rule checks, coverage against published totals, manual audit). A chatbot can describe a market but cannot show dated, sourced, complete deal lists or prove its own accuracy.

## Operating Context

Used on a laptop during a live demo or meeting preparation. Viewers are senior bankers: numerate, skeptical, time-poor, used to research reports, pitch books and data terminals. Typical flow: open a sector or company, scan numbers, check the source, export or copy into a pitch.

## Capabilities and Constraints

- Data: ~5,350 deals, ~3,900 companies, ~5,600 investors, ~1,250 annual financial records (2021–2026), from Entrackr and Inc42; 92 listed comparables from Yahoo Finance. Exported from `db/deals.db` and `data/processed/`.
- Engines and their measured results live in `data/processed/*.json` (radar_backtest, matching_backtest, coverage, validation, crosscheck, model_eval).
- Coverage is partial and must be stated honestly: ~80% of reported startup capital, ~60% of deals by count.
- No server or API keys at runtime; everything ships as static files.
- Decision support for bankers, not investment advice.

## Brand Commitments

- Name: **Deal Intelligence** (neutral, standalone). Arventum may be named as the intended user, but the site must not use Arventum's logo or imitate its website.
- Voice: precise, factual and quietly confident; numbers first, no hype; every claim backed by a measured figure or a source link.

## Evidence on Hand

Real data only: deals, investors, companies, financials, backtests and quality metrics in `db/` and `data/processed/`; methodology, audit and engineering log in `docs/`. There are no testimonials, client logos, users or press. None may be invented.

## Product Principles

1. Every number is traceable: a source article or a stated method.
2. Show measured accuracy, including the modest parts.
3. Speed to answer: a banker should get the key fact for a sector or company within seconds.
4. Banker-grade restraint: credible over flashy.
5. Public data now, built so private data (CRM, paid databases) can plug in later.
