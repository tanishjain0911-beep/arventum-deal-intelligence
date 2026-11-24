# Demo script (about 8 minutes)

The story to tell: **"Your website says Arventum is AI-native. I built what that looks like: a deal-intelligence system that does Market Mapping, Investor Mapping, Buyer Mapping and Valuation Benchmarking from public data, and proves its own accuracy."**

---

## 0 · Opening (30 s), on the Home page
- "In 2 days, using only public data and a team of AI agents I orchestrated, I built a database of **[N] Indian tech deals**, **[N] investors** and **[N] companies**, with five engines on top. Each engine maps to a step in Arventum's own 16-step process."
- Point at the four quality tiles: "Before showing what it does, here's why you can trust it."

## 1 · Market Pulse (1 min): "Industry Intelligence"
- Pick **Arventum's 20 focus sectors**. Show capital per month and the stage benchmarks.
- Say: "Before a pitch, a banker needs the market in one screen: who's investing, what a Series A looks like right now (median **$7M**), which sectors are heating up."
- Click a source link: "Every number traces back to the article it came from."

## 2 · Origination Radar (1.5 min): "Target Identification"
- "This finds clients **before** they call another bank."
- Show the backtest tiles: "Trained only on the past, tested on outcomes it never saw, and compared with the rule a banker uses by hand: 'they raised 18–24 months ago, so they're due.'"
- Filter to a focus sector, pick a company, show the plain-English reasons and its funding history.

## 3 · Investor Matchmaker (1.5 min): "Investor Mapping"
- Enter a realistic client: *Cybersecurity, Series A, $10M, needs a lead*. Then tick **foreign investors only**: "Arventum sells global capital."
- Open the evidence: "Not a guess. These are the deals this fund actually did."
- Open "Does it work?": "On **314 real rounds**, an actual investor in the round was in our top 10 **47%** of the time, vs **27%** for a 'most active investors' list. Weights were tuned on an earlier period and tested on a later one."

## 4 · Buyer Mapping (45 s): "Buyer Mapping"
- Pick FinTech: "Serial acquirers, ranked by sector relevance and appetite. CRED → Kuvera, Juspay → LotusPay."

## 5 · Price Finder (1 min): "Valuation Benchmarking"
- *SaaS, ₹150 Cr revenue, 50% growth, 10% EBITDA.* Show the football field: "Three independent methods: listed peers, a regression chosen by cross-validation, and 57 Indian private rounds."
- "Gross margin turned out to be the strongest driver of revenue multiples. I tested six model specifications out-of-sample to find that."

## 6 · Data & Quality (1 min): the "not a prompt" proof
- Agreement chart: "Two different AI agents read the same 177 articles independently and agree 99% on the company and deal type."
- Weekly chart: "Our captured capital tracks the published weekly totals. That's how we measure coverage."
- Audit trail: "Every automatic correction is logged."

## 7 · How it was built (45 s)
- Diagram: "Claude Code was the architect. It orchestrated Codex and OpenCode from the terminal, and when the ChatGPT quota ran out overnight it benchmarked eight free models and used only the ones that scored about 93%."
- Engineering log: "Real data is messy. Here are 24 problems the pipeline caught and how each was fixed."

## Close (30 s)
- "With your CRM and the founders' 700+ relationships plugged in, the Matchmaker can weight warm relationships, and a network view could suggest warm introductions. That's the next step if I join."

---

### Questions to expect
| Question | Answer |
|---|---|
| Is the data complete? | ~85% of reported capital, ~60% of deals by count. The gap is small undisclosed rounds. A paid database would close it. |
| What if the AI is wrong? | Four independent checks (agent agreement, rule checks, coverage, manual audit), headline-wins correction, and every record links to its source. |
| Why not just ask ChatGPT? | It can't give dated, sourced, complete deal lists, and it can't backtest itself. This system has its own data and measured accuracy. |
| How current is it? | One command refreshes: collect → extract → check → load. |
| What did it cost? | ₹0. Public data, free tooling, an existing ChatGPT Plus subscription, and free models as fallback. |
