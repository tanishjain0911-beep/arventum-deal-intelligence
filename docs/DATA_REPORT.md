# Data report

_Generated from `db/deals.db` at 2026-11-24T08:24:59._

## Contents

| table | rows |
|---|---|
| sources | 7161 |
| companies | 3887 |
| investors | 5587 |
| deals | 5348 |
| deal_investors | 13823 |
| deal_sources | 5610 |
| financials | 1252 |
| weekly_totals | 299 |
| corrections | 551 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 6937 |
| inc42 | 224 |

- Deal records before de-duplication: **5610**; duplicate reports merged: **262**; deals confirmed by 2+ articles: **251**
- Amount disclosed: **90.9%** of deals; at least one named investor: **78.3%**
- Automatic corrections applied: {'two-agent merge: filled gap': 22, 'headline-wins': 124, 'partial / unfinished fiscal year dropped': 338, 'self-acquisition dropped (role swap)': 9, 'public-market raise': 54, 'implausible amount dropped': 4}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2021 | 451 | 22,255.2 | 8.0 |
| 2022 | 769 | 18,172.1 | 5.0 |
| 2023 | 622 | 9,632.6 | 3.4 |
| 2024 | 916 | 12,132.5 | 4.0 |
| 2025 | 1136 | 15,389.4 | 3.9 |
| 2026 | 866 | 11,645.6 | 4.1 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| E-commerce & D2C | 862 | 20,180.0 |
| FinTech & Payments | 632 | 15,710.3 |
| Unclassified | 400 | 6,071.1 |
| EV & Auto | 215 | 5,015.9 |
| EdTech | 170 | 4,918.5 |
| HealthTech | 371 | 4,519.8 |
| Logistics & Mobility | 143 | 4,474.4 |
| Consumer Internet | 129 | 3,375.1 |
| Media & Gaming | 147 | 2,829.9 |
| SaaS | 176 | 2,541.2 |
| Artificial Intelligence | 206 | 2,347.3 |
| Industrial Tech | 126 | 2,041.2 |
| AgriTech | 162 | 1,793.2 |
| Travel & Hospitality | 106 | 1,650.3 |
| Cloud Infrastructure | 24 | 1,511.4 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Inflection Point Ventures | Institutional | Angel network / platform | India | 156 | 127 |
| Peak XV Partners | Institutional | Venture Capital | Singapore | 145 | 86 |
| Accel | Institutional | Venture Capital | United States | 129 | 84 |
| Venture Catalysts | Institutional | Angel network / platform | India | 114 | 48 |
| Blume Ventures | Institutional | Venture Capital | India | 110 | 37 |
| Elevation Capital | Institutional | Venture Capital | India | 95 | 50 |
| Lightspeed | Institutional | Venture Capital | United States | 86 | 45 |
| Z47 | Institutional | Venture Capital | India | 83 | 39 |
| Info Edge Ventures | Institutional | Corporate / CVC | India | 68 | 37 |
| Alteria Capital | Debt / Bank | Venture debt / NBFC / Bank | India | 67 | 20 |
| Fireside Ventures | Institutional | Venture Capital | India | 64 | 41 |
| Nexus Venture Partners | Institutional | Venture Capital | United States | 62 | 34 |
| Rainmatter | Institutional | Corporate / CVC | India | 62 | 37 |
| Titan Capital | Institutional | Venture Capital | India | 59 | 24 |
| Anicut Capital | Institutional | Private Equity / Growth | India | 53 | 19 |
| IvyCap Ventures | Institutional | Venture Capital | India | 51 | 31 |
| Stride Ventures | Debt / Bank | Venture debt / NBFC / Bank | India | 50 | 16 |
| 3one4 Capital | Institutional | Venture Capital | India | 50 | 20 |
| LetsVenture | Angel network | Angel network / platform | India | 48 | 4 |
| BEENEXT | Institutional | Venture Capital | Japan | 47 | 16 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2026-06-12 | Kirana Club | Meesho | 23.0 |
| 2026-06-08 | iKeva | Incuspaze |  |
| 2026-06-05 | Brevistay | ixigo | 7.5 |
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

## Quality checks

**Coverage vs Entrackr weekly round-ups** (recall):

```json
{
  "weeks_compared": 296,
  "reported_deals_total": 7808,
  "our_deals_total": 4648,
  "deal_recall_pct": 59.5,
  "usd_recall_pct": 79.6,
  "median_weekly_deal_recall_pct": 64.5
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 4413,
    "checked": 4480,
    "pass_rate": 98.5
  },
  "stage_size": {
    "passed": 2987,
    "checked": 3059,
    "pass_rate": 97.6
  },
  "missing_core": {
    "passed": 5743,
    "checked": 5873,
    "pass_rate": 97.8
  },
  "company_in_title": {
    "passed": 9211,
    "checked": 9274,
    "pass_rate": 99.3
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