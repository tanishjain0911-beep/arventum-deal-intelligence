# Data report

_Generated from `db/deals.db` at 2026-11-24T13:56:12._

## Contents

| table | rows |
|---|---|
| sources | 10366 |
| companies | 4480 |
| investors | 7879 |
| deals | 6655 |
| deal_investors | 21079 |
| deal_sources | 8591 |
| financials | 1476 |
| weekly_totals | 299 |
| corrections | 1378 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 7459 |
| inc42 | 2907 |

- Deal records before de-duplication: **8591**; duplicate reports merged: **1936**; deals confirmed by 2+ articles: **1833**
- Amount disclosed: **88.7%** of deals; at least one named investor: **84.4%**
- Automatic corrections applied: {'two-agent merge: filled gap': 136, 'public-market raise': 110, 'not an Indian company dropped': 1, 'headline-wins': 121, 'partial / unfinished fiscal year dropped': 851, 'self-acquisition dropped (role swap)': 20, 'before study period dropped': 28, 'multi-company record dropped': 13, 'valuation below round size': 8, 'implausible amount dropped': 5, 'corporate / listed-company deal': 8, 'company name variant merged': 77}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2021 | 594 | 34,178.0 | 8.3 |
| 2022 | 823 | 22,692.2 | 5.1 |
| 2023 | 803 | 12,243.0 | 3.6 |
| 2024 | 1051 | 14,447.9 | 4.0 |
| 2025 | 1218 | 17,488.9 | 4.0 |
| 2026 | 1004 | 14,578.7 | 4.1 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| E-commerce & D2C | 1085 | 26,075.3 |
| FinTech & Payments | 788 | 23,164.3 |
| EdTech | 223 | 8,406.4 |
| EV & Auto | 266 | 6,669.7 |
| Consumer Internet | 182 | 6,155.3 |
| Logistics & Mobility | 174 | 5,602.0 |
| HealthTech | 444 | 5,549.8 |
| Artificial Intelligence | 260 | 5,035.8 |
| Media & Gaming | 192 | 4,463.1 |
| SaaS | 230 | 3,586.2 |
| AgriTech | 199 | 2,301.4 |
| Industrial Tech | 140 | 2,042.7 |
| Travel & Hospitality | 131 | 1,978.6 |
| PropTech & Real Estate | 119 | 1,821.1 |
| Digital Banking | 39 | 1,336.9 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Peak XV Partners | Institutional | Venture Capital | Singapore | 236 | 117 |
| Accel | Institutional | Venture Capital | United States | 195 | 107 |
| Inflection Point Ventures | Institutional | Angel network / platform | India | 185 | 148 |
| Venture Catalysts | Institutional | Angel network / platform | India | 155 | 63 |
| Blume Ventures | Institutional | Venture Capital | India | 153 | 49 |
| Elevation Capital | Institutional | Venture Capital | India | 130 | 66 |
| Z47 | Institutional | Venture Capital | India | 123 | 50 |
| Lightspeed | Institutional | Venture Capital | United States | 119 | 53 |
| Alteria Capital | Debt / Bank | Venture debt / NBFC / Bank | India | 103 | 32 |
| Nexus Venture Partners | Institutional | Venture Capital | United States | 102 | 44 |
| Info Edge Ventures | Institutional | Corporate / CVC | India | 100 | 52 |
| 3one4 Capital | Institutional | Venture Capital | India | 99 | 41 |
| Titan Capital | Institutional | Venture Capital | India | 95 | 33 |
| Better Capital | Institutional | Venture Capital | India | 86 | 22 |
| LetsVenture | Angel network | Angel network / platform | India | 84 | 15 |
| Rainmatter | Institutional | Corporate / CVC | India | 79 | 42 |
| Fireside Ventures | Institutional | Venture Capital | India | 76 | 51 |
| 9Unicorns | Institutional | Accelerator / Incubator | India | 72 | 22 |
| BEENEXT | Institutional | Venture Capital | Japan | 70 | 22 |
| Stride Ventures | Debt / Bank | Venture debt / NBFC / Bank | India | 69 | 22 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2026-11-12 | A2B | Bodhi Tree Systems | 180.0 |
| 2026-11-06 | Quick Ride | MakeMyTrip |  |
| 2026-11-02 | Basilisk Industries | Provision Labs |  |
| 2026-10-29 | Robusta | Freshworks |  |
| 2026-10-27 | AIShield | Protectt.ai |  |
| 2026-10-14 | Zluri | Infotech |  |
| 2026-10-13 | Torii | Freshworks |  |
| 2026-10-05 | TravClan | Flipkart |  |
| 2026-10-05 | Plix | Marico | 115.0 |
| 2026-09-29 | Yoga Bar | ITC | 73.3 |
| 2026-09-17 | MyLoancare | PB Fintech | 1.1 |
| 2026-09-08 | TrueFan AI | Bajaj Finance |  |
| 2026-09-08 | Tazapay | Circle Internet Group |  |
| 2026-09-07 | Lynk Logistics | Udaan | 56.8 |
| 2026-09-02 | Rilo | Adobe |  |

## Quality checks

**Coverage vs Entrackr weekly round-ups** (recall):

```json
{
  "weeks_compared": 296,
  "reported_deals_total": 7808,
  "our_deals_total": 5341,
  "deal_recall_pct": 68.4,
  "usd_recall_pct": 100.5,
  "median_weekly_deal_recall_pct": 75.0
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 7409,
    "checked": 7538,
    "pass_rate": 98.3
  },
  "stage_size": {
    "passed": 4956,
    "checked": 5067,
    "pass_rate": 97.8
  },
  "missing_core": {
    "passed": 9991,
    "checked": 10166,
    "pass_rate": 98.3
  },
  "company_in_title": {
    "passed": 15794,
    "checked": 15895,
    "pass_rate": 99.4
  }
}
```

**Two-agent agreement** (Codex vs OpenCode on the same articles):

```json
{
  "articles_compared": 177,
  "agreement_pct": {
    "record_type": 98.9,
    "company": 99.4,
    "stage": 96.6,
    "amount": 94.4,
    "lead_investors": 96.6,
    "sector": 93.2
  }
}
```

See also `docs/MANUAL_AUDIT.md` for the independent field-by-field audit.