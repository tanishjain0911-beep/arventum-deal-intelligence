# Demo script (about 8 minutes)

Website: https://deal-intelligence-kappa.vercel.app

The story to tell: **"Arventum calls itself AI-native. I built what that looks like: a deal book of 6,655 Indian tech deals from public sources, with tools for origination, investor mapping, buyer mapping and valuation. And it measures its own accuracy."**

---

## 0 · Opening (30 s): the landing page
- Point at the headline and the four figures: deals, companies, the Radar's 43%, investors. "Every figure here is read live from the data, and every deal links to the article it came from."
- Click **Open the deal book**.

## 1 · Summary (30 s)
- Exhibit 1.1: capital raised per quarter since 2021. The 2021 boom and the slowdown after are visible at a glance.
- Exhibit 1.2, "Measured, not claimed": "Before I show what it does, here's why you can trust it. Every model is tested on outcomes it never saw."

## 2 · Market (1 min)
- Keep **Arventum's 20 focus sectors** selected. Show 2.3, where money went in the last six months (hover a bar for the change versus the prior six months), and 2.4, what a round at each stage looks like now.
- Click **Article** on any row of 2.6: "Every number traces back to its source."

## 3 · Origination (1.5 min)
- "This finds clients before they call another bank."
- Exhibit 3.1: "Its top 100 picks raised within a year 43% of the time, against 16% for the rule bankers use by hand ('raised 18 to 24 months ago') and 14% at random. That's about three times better than chance."
- Click a company in 3.3 to show the plain-English reasons, then **Download this week's brief**.

## 4 · Investors (1.5 min)
- Enter a realistic client: *FinTech & Payments, Series A, $10M, needs a lead*. Then tick **Headquartered outside India**: "Arventum sells access to global capital."
- Click an investor: "Not a guess. These are the deals this fund actually did."
- Exhibit 4.3: "On 333 real rounds, a real investor was in its top 10 43% of the time, against 28% for a 'most active investors' list. The weights were tuned on an earlier period and tested on a later one."

## 5 · Buyers (45 s)
- Pick a sector: "Acquirers ranked by how many similar companies they've bought, how many in total, and how recently."

## 6 · Valuation (1 min)
- *SaaS, ₹150 crore revenue, 50% growth, 10% EBITDA margin.* Show the football field: "Three independent methods: listed peers, a growth-and-margin regression chosen by cross-validation, and 131 Indian private rounds with a disclosed valuation."
- Be upfront: "The regression explains about 30% of the variation, which is why it shows a range from three methods, not one number."

## 7 · Company (30 s)
- Search **Zepto** in the top bar. Show its deal history, backers and Radar score.
- Point out the IPO rows say "board approval" and "SEBI approval", not a completed IPO: "When I spotted the AI calling every IPO headline an IPO, I fixed the pipeline so each step is labelled correctly."

## 8 · Method (1 min): the "not just a prompt" proof
- 8.2: "Two different AI agents read the same 177 articles independently and agree 99% on the company."
- 8.4: rule checks with no AI involved pass about 98%. 8.5: the book tracks the published weekly totals.
- "36 real data problems were found and fixed, each logged in the engineering log on GitHub."

## Close (30 s)
- "It cost nothing to build. With Arventum's CRM and the founders' relationships plugged in, the Matchmaker could prefer warm introductions. That's the next step if I join."

---

### Questions to expect
| Question | Answer |
|---|---|
| Is the data complete? | About 68% of deals by count against Entrackr's published weekly counts, and the capital matches their totals. The gap is mostly small, undisclosed rounds. A paid database would close it. |
| What if the AI is wrong? | Four independent checks (two-agent agreement, rule checks, coverage, a manual audit), automatic corrections with a full log, and every record links to its source. |
| Why not just ask ChatGPT? | ChatGPT can't produce a dated, sourced, complete deal list, and it can't test itself on past outcomes. This system has its own data and measured accuracy. |
| 43% doesn't sound high. | Only 14% of companies raise in a given year, so 43% is about three times random, and nearly three times the rule bankers use today. It turns 4,000 companies into a call list. |
| How accurate is the valuation? | It's a starting range. That's why it shows three methods side by side instead of one number. |
| How current is it? | Data runs to 23 November 2026. One command collects, extracts, checks and reloads the latest deals; another republishes the site. |
| What did it cost? | ₹0: public data, free hosting, an existing ChatGPT subscription, and free models as backup. |
