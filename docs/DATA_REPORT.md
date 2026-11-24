# Data report

_Generated from `db/deals.db` at 2026-11-24T07:31:57._

## Contents

| table | rows |
|---|---|
| sources | 7079 |
| companies | 3870 |
| investors | 5590 |
| deals | 5359 |
| deal_investors | 13819 |
| deal_sources | 5623 |
| financials | 1157 |
| weekly_totals | 299 |
| corrections | 151 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 6853 |
| inc42 | 226 |

- Deal records before de-duplication: **5623**; duplicate reports merged: **264**; deals confirmed by 2+ articles: **252**
- Amount disclosed: **90.7%** of deals; at least one named investor: **78.1%**
- Automatic corrections applied: {'two-agent merge: filled gap': 22, 'headline-wins': 125, 'implausible amount dropped': 4}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2021 | 457 | 25,319.7 | 8.0 |
| 2022 | 770 | 18,172.1 | 5.0 |
| 2023 | 622 | 9,632.6 | 3.4 |
| 2024 | 919 | 13,848.1 | 4.0 |
| 2025 | 1138 | 15,747.2 | 4.0 |
| 2026 | 872 | 12,315.9 | 4.2 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| E-commerce & D2C | 830 | 19,763.5 |
| FinTech & Payments | 610 | 15,552.1 |
| Unclassified | 605 | 10,010.6 |
| EdTech | 149 | 6,344.6 |
| EV & Auto | 210 | 5,088.6 |
| Consumer Internet | 130 | 5,011.9 |
| Logistics & Mobility | 144 | 4,710.9 |
| HealthTech | 357 | 4,480.6 |
| Media & Gaming | 133 | 2,685.4 |
| Industrial Tech | 126 | 2,368.0 |
| SaaS | 149 | 2,306.9 |
| Artificial Intelligence | 191 | 2,110.1 |
| AgriTech | 153 | 1,710.8 |
| Travel & Hospitality | 102 | 1,680.6 |
| Cloud Infrastructure | 21 | 1,440.8 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Inflection Point Ventures | Institutional | Angel network / platform | India | 158 | 129 |
| Peak XV Partners | Institutional | Venture Capital | Singapore | 145 | 86 |
| Accel | Institutional | Venture Capital | United States | 129 | 84 |
| Venture Catalysts | Institutional | Angel network / platform | India | 114 | 48 |
| Blume Ventures | Institutional | Venture Capital | India | 110 | 37 |
| Elevation Capital | Institutional | Venture Capital | India | 96 | 50 |
| Lightspeed | Institutional | Venture Capital | United States | 86 | 45 |
| Z47 | Institutional | Venture Capital | India | 84 | 39 |
| Info Edge Ventures | Institutional | Corporate / CVC | India | 69 | 38 |
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
  "our_deals_total": 4666,
  "deal_recall_pct": 59.8,
  "usd_recall_pct": 84.8,
  "median_weekly_deal_recall_pct": 64.5
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 4416,
    "checked": 4484,
    "pass_rate": 98.5
  },
  "stage_size": {
    "passed": 2987,
    "checked": 3059,
    "pass_rate": 97.6
  },
  "missing_core": {
    "passed": 5746,
    "checked": 5877,
    "pass_rate": 97.8
  },
  "company_in_title": {
    "passed": 8188,
    "checked": 8201,
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