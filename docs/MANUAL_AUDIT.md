# Manual audit of AI extraction (independent reviewer)

**Method:** a reproducible random sample (`python pipeline/audit_sample.py 40 2026`) of 40 extracted records, drawn from 1,073 records available at audit time (Entrackr, 2023). Claude (not one of the two extraction agents) graded each record field by field against the source article text.

## Results

| Field | Correct | Notes |
|---|---|---|
| Record type | **40 / 40** | Correctly rejected "in talks to raise" stories (Oro Money, ZingBus), fund launches (Antler India, Recur Club) and market reports |
| Company name | **40 / 40** | Multi-company articles produce one record (see limitations) |
| Amount | **39 / 40** | One "closes Series D at $30 Mn" story recorded the round total rather than the $10M tranche (arguably correct) |
| Lead vs participating investors | **40 / 40** | Includes angels, family offices, DFIs (DEG, US DFC) |
| Valuation | 1 / 2 | One valuation (Rs 900 Cr) was captured without its currency, so it was dropped downstream |
| Stage | 38 / 40 | "Pre-Series B" mapped to Series B; one revenue-based-financing round not marked as debt |
| Revenue (financial stories) | **9 / 9** | Exact to the decimal (e.g. Razorpay Rs 1,481.2 Cr, Uniphore Rs 674.6 Cr) |
| Profit / loss | 6 / 9 | Three misses because the loss figure appears after the text cut-off |

## Actions taken
1. Financial stories now send 2,000 characters of text (was 1,000), so the profit/loss figure is included.
2. A deterministic headline parser now overrides AI amounts when they disagree ("headline-wins"). This catches unit slips such as "$500K" read as $50M, found by the rule-based validator.
3. A "thousand" unit was added to the extraction schema.

## Known limitations
- Articles comparing several companies (e.g. "Beardo, TMC and Ustraa…") yield one record, for the first company.
- "Annualised revenue" claims without a fiscal year are not stored as financials.
