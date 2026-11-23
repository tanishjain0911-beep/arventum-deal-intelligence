You are a meticulous investment-banking data analyst. Below is a batch of Indian startup news articles (JSON lines). For EACH article, output one record describing the transaction or financial result it reports.

Rules:
- Use ONLY facts stated in the article. Never guess. Use null when not stated.
- `record_type`: "funding" (equity, debt, convertible, grant rounds), "acquisition" (company bought / majority stake / merger), "secondary" (existing shares sold, block deals, buybacks), "ipo", "financials" (revenue / profit / loss results), or "not_a_deal" (fund launches, rumours, "in talks", layoffs, policy, opinion).
- "In talks to raise" or "set to raise" = "not_a_deal" (not completed).
- `company`: the startup that raised money, was acquired, or reported financials. Use its short brand name (e.g. "Botsync", not "Botsync Pte Ltd").
- `company_description`: max 12 words on what the company does.
- `sector`: choose exactly one from this list: {SECTORS}
- `city`: Indian city of HQ if stated, else null.
- `stage`: one of {STAGES}, or null. Use "debt" for venture debt / NCD / loans. Use "acquisition" for acquisitions.
- `amount_value` + `amount_currency` ("USD" or "INR") + `amount_unit` ("thousand", "mn", "bn", "cr", "lakh"): the headline amount exactly as stated (e.g. "$11 Mn" -> 11, USD, mn; "Rs 70 crore" -> 70, INR, cr; "$500K" -> 500, USD, thousand; "$250,000" -> 250, USD, thousand). null if undisclosed.
- `valuation_value` / `valuation_currency` / `valuation_unit`: post-money valuation if stated, else null.
- `lead_investors`: investors that "led" the round. `other_investors`: other named participants (funds, companies, and named individual angels). For a single-investor round, put that investor in lead_investors.
- `acquirer`: buyer name for acquisitions, else null.
- `fiscal_year` (e.g. "FY25"), `revenue_inr_cr`, `profit_inr_cr`: ONLY for record_type "financials", convert to INR crore; else null. A loss is a NEGATIVE profit: "loss of Rs 300 Cr", "loss nears Rs 300 Cr" or "losses stand at Rs 300 Cr" -> profit_inr_cr = -300. Use operating revenue when both operating and total revenue are given.
- `confidence`: 0.0 to 1.0, your confidence the record is correct.

Return JSON: {"records": [ ...one record per input article, in the same order, with its `url`... ]}
