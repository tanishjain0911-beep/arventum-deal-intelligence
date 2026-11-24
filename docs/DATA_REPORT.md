# Data report

_Generated from `db/deals.db` at 2026-11-24T07:22:09._

## Contents

| table | rows |
|---|---|
| sources | 7180 |
| companies | 3947 |
| investors | 6077 |
| deals | 5459 |
| deal_investors | 14771 |
| deal_sources | 5724 |
| financials | 1157 |
| weekly_totals | 299 |
| corrections | 153 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 6954 |
| inc42 | 226 |

- Deal records before de-duplication: **5724**; duplicate reports merged: **265**; deals confirmed by 2+ articles: **253**
- Amount disclosed: **89.4%** of deals; at least one named investor: **85.6%**
- Automatic corrections applied: {'two-agent merge: filled gap': 22, 'headline-wins': 127, 'implausible amount dropped': 4}

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
| Other | 658 | 10,332.0 |
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
| Inflection Point Ventures | Institutional | Angel network / platform | India | 169 | 140 |
| Peak XV Partners | Institutional | Venture Capital | Singapore | 154 | 93 |
| Accel | Institutional | Venture Capital | United States | 136 | 88 |
| Venture Catalysts | Institutional | Angel network / platform | India | 123 | 56 |
| Blume Ventures | Institutional | Venture Capital | India | 112 | 39 |
| Elevation Capital | Institutional | Venture Capital | India | 103 | 57 |
| Lightspeed | Institutional | Venture Capital | United States | 88 | 46 |
| Z47 | Institutional | Venture Capital | India | 87 | 42 |
| Info Edge Ventures | Institutional | Corporate / CVC | India | 73 | 41 |
| Alteria Capital | Debt / Bank | Venture debt / NBFC / Bank | India | 69 | 22 |
| Nexus Venture Partners | Institutional | Venture Capital | United States | 65 | 36 |
| Fireside Ventures | Institutional | Venture Capital | India | 64 | 41 |
| Titan Capital | Institutional | Venture Capital | India | 63 | 27 |
| Rainmatter | Institutional | Corporate / CVC | India | 62 | 37 |
| 3one4 Capital | Institutional | Venture Capital | India | 61 | 31 |
| LetsVenture | Angel network | Angel network / platform | India | 55 | 8 |
| Anicut Capital | Institutional | Private Equity / Growth | India | 53 | 19 |
| BEENEXT | Institutional | Venture Capital | Japan | 51 | 17 |
| Unicorn India Ventures | Institutional | Venture Capital | India | 51 | 43 |
| Chiratae Ventures | Institutional | Venture Capital | India | 51 | 21 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2026-11-12 | A2B | Bodhi Tree | 180.0 |
| 2026-11-06 | quick ride | MakeMyTrip |  |
| 2026-10-29 | platform | Freshworks |  |
| 2026-10-27 | Medsee | Practo co-founder Shashank ND’s startup Cent raises $15 Mn led by Blume | 15.0 |
| 2026-10-05 | Plix | Marico | 116.9 |
| 2026-09-21 | Calyx | Samara Capital |  |
| 2026-09-17 | Wheels | PB Fintech | 1.2 |
| 2026-09-08 | TrueFan AI | Bajaj Finance |  |
| 2026-09-07 | Swiggy | Udaan | 57.7 |
| 2026-09-01 | business | Niyo |  |
| 2026-08-27 | Longevous | Temple |  |
| 2026-08-20 | Pando.ai | Fleetx.ai |  |
| 2026-08-19 | BookMyShow | KKR |  |
| 2026-08-18 | platform | DSP Finance |  |
| 2026-08-11 | Diagnostics | Redcliffe Labs | 4.6 |

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
    "passed": 4435,
    "checked": 4503,
    "pass_rate": 98.5
  },
  "stage_size": {
    "passed": 2987,
    "checked": 3059,
    "pass_rate": 97.6
  },
  "missing_core": {
    "passed": 5884,
    "checked": 5978,
    "pass_rate": 98.4
  },
  "company_in_title": {
    "passed": 8287,
    "checked": 8300,
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