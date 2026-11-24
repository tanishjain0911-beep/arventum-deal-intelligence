# Deal Intelligence: one-page summary

**Website:** https://deal-intelligence-kappa.vercel.app

**Problem.** Arventum's edge is knowing, before other banks do, *who* will raise, *who* will invest, *who* will buy and *at what price*. Today that knowledge sits in the founders' heads and in hours of manual research before every pitch.

**What I built.** A deal book of **6,655 Indian technology deals** (January 2021 to November 2026, 4,299 companies, 7,559 investors), each linked to its source article. It has five tools on top, at zero cost:

| Tool | Arventum process step | How it is validated |
|---|---|---|
| Market | Industry intelligence | Capital matches Entrackr's published weekly totals |
| Origination Radar | Market mapping, target identification | Walk-forward backtest: top-100 precision 43% vs 16% for a banker's rule of thumb (about 3× random) |
| Investor Matchmaker | Investor mapping | 333 real rounds: a real investor in the top 10 43% of the time vs 28% for a "most active" list |
| Buyer Mapping | Buyer mapping | 663 acquisitions, ranked by sector relevance, appetite and recency |
| Price Finder | Valuation benchmarking | Three methods; the regression was chosen by leave-one-out cross-validation |

**How.** A crawler downloaded about 10,400 articles from Entrackr and Inc42. AI agents (Codex and OpenCode on GPT-5.6, with measured free fallbacks) turned each one into a structured record. Rules then reconciled, de-duplicated and audited the records, logging 1,378 automatic corrections. Claude Code architected the system and coordinated the agents. The website was redesigned with Freebuff and reviewed with the Impeccable design tools.

**Trust.** Four independent checks:
- Two AI agents agree 99.4% on the company when reading the same articles.
- Rule checks with no AI pass 98–99%.
- Coverage is measured week by week against published totals.
- A 40-record manual audit scored 40/40 on deal type, company and investors.

**Engineering.** 36 real data problems were found and fixed, each logged with its cause, and each fix is enforced on every rebuild. Examples include corporate deals counted as startup rounds, duplicate company spellings, and IPO approvals mistaken for listings.

**Next, with Arventum's data.** The CRM and relationship network (to prefer warm introductions), a paid database for small rounds, and a weekly "top 10 companies to call" email.
