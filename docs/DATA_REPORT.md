# Data report

_Generated from `db/deals.db` at 2026-11-24T06:55:55._

## Contents

| table | rows |
|---|---|
| sources | 5911 |
| companies | 3280 |
| investors | 5486 |
| deals | 4204 |
| deal_investors | 13156 |
| deal_sources | 4460 |
| financials | 1155 |
| weekly_totals | 296 |
| corrections | 95 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 5685 |
| inc42 | 226 |

- Deal records before de-duplication: **4460**; duplicate reports merged: **256**; deals confirmed by 2+ articles: **244**
- Amount disclosed: **90.8%** of deals; at least one named investor: **87.2%**
- Automatic corrections applied: {'two-agent merge: filled gap': 22, 'headline-wins': 70, 'implausible amount dropped': 3}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2021 | 58 | 8,033.7 | 13.7 |
| 2022 | 432 | 7,150.2 | 4.0 |
| 2023 | 622 | 9,632.6 | 3.4 |
| 2024 | 917 | 13,232.1 | 4.0 |
| 2025 | 1136 | 15,744.8 | 4.0 |
| 2026 | 462 | 6,334.5 | 3.4 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| E-commerce & D2C | 708 | 15,526.1 |
| FinTech & Payments | 509 | 11,323.2 |
| Consumer Internet | 112 | 3,519.9 |
| EV & Auto | 182 | 3,273.9 |
| HealthTech | 312 | 3,252.0 |
| Logistics & Mobility | 121 | 2,991.8 |
| EdTech | 119 | 2,056.5 |
| SaaS | 135 | 1,966.6 |
| Artificial Intelligence | 178 | 1,534.9 |
| Industrial Tech | 113 | 1,485.5 |
| Cloud Infrastructure | 21 | 1,440.8 |
| Media & Gaming | 112 | 1,426.0 |
| Travel & Hospitality | 92 | 1,329.4 |
| AgriTech | 123 | 1,120.1 |
| HR & Workforce | 55 | 984.8 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Inflection Point Ventures | Institutional | Angel network / platform | India | 135 | 106 |
| Peak XV Partners | Institutional | Venture Capital | Singapore | 135 | 77 |
| Accel | Institutional | Venture Capital | United States | 113 | 72 |
| Venture Catalysts | Institutional | Angel network / platform | India | 109 | 43 |
| Blume Ventures | Institutional | Venture Capital | India | 108 | 36 |
| Elevation Capital | Institutional | Venture Capital | India | 84 | 39 |
| Z47 | Institutional | Venture Capital | India | 81 | 36 |
| Lightspeed | Institutional | Venture Capital | United States | 80 | 40 |
| Alteria Capital | Debt / Bank | Venture debt / NBFC / Bank | India | 64 | 18 |
| Fireside Ventures | Institutional | Venture Capital | India | 59 | 36 |
| Info Edge Ventures | Institutional | Corporate / CVC | India | 58 | 29 |
| Titan Capital | Institutional | Venture Capital | India | 56 | 22 |
| Nexus Venture Partners | Institutional | Venture Capital | United States | 54 | 29 |
| Rainmatter | Institutional | Corporate / CVC | India | 53 | 30 |
| Anicut Capital | Institutional | Private Equity / Growth | India | 52 | 18 |
| Stride Ventures | Debt / Bank | Venture debt / NBFC / Bank | India | 49 | 16 |
| 3one4 Capital | Institutional | Venture Capital | India | 49 | 20 |
| LetsVenture | Angel network | Angel network / platform | India | 48 | 4 |
| BEENEXT | Institutional | Venture Capital | Japan | 46 | 15 |
| IvyCap Ventures | Institutional | Venture Capital | India | 45 | 25 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2026-06-12 | Kirana Club | Meesho | 23.0 |
| 2026-06-01 | Bluechip Capital | Scripbox |  |
| 2026-05-25 | HelloTravel | Ziptrrip |  |
| 2026-05-19 | GoldenPi | Oxyzo |  |
| 2026-05-13 | GreenLife | Raise Financial Services |  |
| 2026-05-12 | S Cube Capital | InCred Capital |  |
| 2026-05-07 | MobileAction | InMobi |  |
| 2026-05-07 | IndiaLends | Freo |  |
| 2026-05-07 | IncNut Digital | Emami | 36.5 |
| 2026-05-05 | Moove Connected Mobility | Netradyne |  |
| 2026-04-25 | Shopflo | Pine Labs | 10.0 |
| 2026-04-22 | Lanstitut | Emversity | 4.2 |
| 2026-04-21 | Stratzy | Raise Financial Services |  |
| 2026-04-13 | GiantDot | Shortgun Games |  |
| 2026-04-07 | Qckin | Fashinza |  |

## Quality checks

**Coverage vs Entrackr weekly round-ups** (recall):

```json
{
  "weeks_compared": 250,
  "reported_deals_total": 6732,
  "our_deals_total": 3536,
  "deal_recall_pct": 52.5,
  "usd_recall_pct": 62.8,
  "median_weekly_deal_recall_pct": 64.5
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 3369,
    "checked": 3436,
    "pass_rate": 98.1
  },
  "stage_size": {
    "passed": 2379,
    "checked": 2441,
    "pass_rate": 97.5
  },
  "missing_core": {
    "passed": 4650,
    "checked": 4714,
    "pass_rate": 98.6
  },
  "company_in_title": {
    "passed": 6968,
    "checked": 6981,
    "pass_rate": 99.8
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