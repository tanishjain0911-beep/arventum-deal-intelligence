# Data report

_Generated from `db/deals.db` at 2026-11-24T06:04:13._

## Contents

| table | rows |
|---|---|
| sources | 2680 |
| companies | 1792 |
| investors | 3063 |
| deals | 1868 |
| deal_investors | 5913 |
| deal_sources | 1931 |
| financials | 577 |
| weekly_totals | 172 |
| corrections | 55 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 2454 |
| inc42 | 226 |

- Deal records before de-duplication: **1931**; duplicate reports merged: **63**; deals confirmed by 2+ articles: **60**
- Amount disclosed: **89.7%** of deals; at least one named investor: **87.9%**
- Automatic corrections applied: {'two-agent merge: filled gap': 22, 'headline-wins': 31, 'implausible amount dropped': 2}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2023 | 570 | 9,192.4 | 3.3 |
| 2024 | 878 | 12,390.8 | 4.0 |
| 2025 | 189 | 2,848.7 | 5.0 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| E-commerce & D2C | 293 | 5,890.7 |
| FinTech & Payments | 243 | 5,200.9 |
| EV & Auto | 93 | 1,639.0 |
| HealthTech | 140 | 1,368.4 |
| Consumer Internet | 56 | 1,302.2 |
| EdTech | 58 | 1,174.2 |
| Logistics & Mobility | 54 | 868.4 |
| Travel & Hospitality | 46 | 864.5 |
| Media & Gaming | 60 | 754.3 |
| SaaS | 69 | 593.5 |
| Artificial Intelligence | 76 | 592.9 |
| Industrial Tech | 47 | 580.7 |
| Enterprise Software | 25 | 492.5 |
| Digital Banking | 7 | 404.9 |
| AgriTech | 57 | 383.4 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Inflection Point Ventures | Institutional | Angel network / platform | India | 73 | 56 |
| Venture Catalysts | Institutional | Angel network / platform | India | 60 | 27 |
| Blume Ventures | Institutional | Venture Capital | India | 52 | 20 |
| Peak XV Partners | Institutional | Venture Capital | Singapore | 49 | 29 |
| Accel | Institutional | Venture Capital | United States | 40 | 24 |
| Lightspeed | Institutional | Venture Capital | United States | 36 | 20 |
| Z47 | Institutional | Venture Capital | India | 34 | 18 |
| Alteria Capital | Debt / Bank | Venture debt / NBFC / Bank | India | 34 | 7 |
| Elevation Capital | Institutional | Venture Capital | India | 33 | 17 |
| Trifecta Capital | Debt / Bank | Venture debt / NBFC / Bank | India | 25 | 8 |
| Stride Ventures | Debt / Bank | Venture debt / NBFC / Bank | India | 25 | 8 |
| Nexus Venture Partners | Institutional | Venture Capital | United States | 25 | 12 |
| Anicut Capital | Institutional | Private Equity / Growth | India | 25 | 10 |
| Rainmatter | Institutional | Corporate / CVC | India | 25 | 14 |
| LetsVenture | Angel network | Angel network / platform | India | 21 | 2 |
| Fireside Ventures | Institutional | Venture Capital | India | 21 | 14 |
| Chiratae Ventures | Institutional | Venture Capital | India | 21 | 5 |
| Omnivore | Institutional | Venture Capital | India | 21 | 10 |
| British International Investment | Institutional | Sovereign / Pension / DFI / Government | United Kingdom | 20 | 6 |
| Titan Capital | Institutional | Venture Capital | India | 19 | 6 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2025-03-26 | Solv India | Jumbotail |  |
| 2025-03-26 | Mobileware | Zaggle | 0.8 |
| 2025-03-25 | Big Charter | EaseMyTrip |  |
| 2025-03-24 | Oussum | Groyyo |  |
| 2025-03-21 | Shipway | Unicommerce |  |
| 2025-03-21 | Euler Motors | Hero MotoCorp | 60.6 |
| 2025-03-19 | Absolute Sports | Nazara Technologies | 8.0 |
| 2025-03-19 | 7-10 | WLDD |  |
| 2025-03-18 | Tata Play | Tata Sons |  |
| 2025-03-18 | Minimalist | Hindustan Unilever | 308.3 |
| 2025-03-17 | SpotKwik | Omnia |  |
| 2025-03-11 | CreditNirvana | Perfios |  |
| 2025-03-10 | Volt Money | DSP Group |  |
| 2025-03-04 | Digiledge | Mintoak |  |
| 2025-02-28 | ffreedom | Boss Wallah |  |

## Quality checks

**Coverage vs Entrackr weekly round-ups** (recall):

```json
{
  "weeks_compared": 109,
  "reported_deals_total": 2574,
  "our_deals_total": 1578,
  "deal_recall_pct": 61.3,
  "usd_recall_pct": 82.6,
  "median_weekly_deal_recall_pct": 62.5
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 1563,
    "checked": 1595,
    "pass_rate": 98.0
  },
  "stage_size": {
    "passed": 1096,
    "checked": 1129,
    "pass_rate": 97.1
  },
  "missing_core": {
    "passed": 2157,
    "checked": 2184,
    "pass_rate": 98.8
  },
  "company_in_title": {
    "passed": 3209,
    "checked": 3216,
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