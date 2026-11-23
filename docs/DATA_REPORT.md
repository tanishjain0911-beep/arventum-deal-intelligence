# Data report

_Generated from `db/deals.db` at 2026-11-24T02:22:22._

## Contents

| table | rows |
|---|---|
| sources | 1514 |
| companies | 1145 |
| investors | 1982 |
| deals | 1013 |
| deal_investors | 3429 |
| deal_sources | 1028 |
| financials | 402 |
| weekly_totals | 84 |
| corrections | 25 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 1493 |
| inc42 | 21 |

- Deal records before de-duplication: **1028**; duplicate reports merged: **15**; deals confirmed by 2+ articles: **15**
- Amount disclosed: **91.7%** of deals; at least one named investor: **90.1%**
- Automatic corrections applied: {'headline-wins': 23, 'implausible amount dropped': 2}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2023 | 570 | 9,192.4 | 3.3 |
| 2024 | 323 | 3,300.7 | 4.0 |
| 2025 | 19 | 587.3 | 10.0 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| FinTech & Payments | 126 | 3,276.3 |
| E-commerce & D2C | 160 | 3,041.7 |
| EV & Auto | 56 | 1,072.6 |
| HealthTech | 82 | 958.2 |
| EdTech | 34 | 654.3 |
| Logistics & Mobility | 35 | 464.7 |
| Media & Gaming | 37 | 395.7 |
| SaaS | 49 | 376.3 |
| Enterprise Software | 14 | 347.6 |
| Travel & Hospitality | 29 | 313.2 |
| Industrial Tech | 22 | 232.3 |
| Artificial Intelligence | 31 | 216.8 |
| PropTech & Real Estate | 19 | 191.7 |
| Automation & Robotics | 14 | 187.0 |
| AgriTech | 36 | 172.6 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Inflection Point Ventures | Institutional |  |  | 47 | 37 |
| Venture Catalysts | Institutional |  |  | 31 | 15 |
| Blume Ventures | Institutional |  |  | 29 | 12 |
| Peak XV Partners | Institutional |  |  | 28 | 22 |
| Lightspeed | Institutional |  |  | 22 | 14 |
| Alteria Capital | Debt / Bank |  |  | 21 | 2 |
| Z47 | Institutional |  |  | 19 | 12 |
| Stride Ventures | Debt / Bank |  |  | 19 | 5 |
| Trifecta Capital | Debt / Bank |  |  | 17 | 6 |
| Anicut Capital | Institutional |  |  | 17 | 8 |
| Accel | Institutional |  |  | 16 | 9 |
| Titan Capital | Institutional |  |  | 16 | 5 |
| Elevation Capital | Institutional |  |  | 15 | 7 |
| Fireside Ventures | Institutional |  |  | 15 | 9 |
| LetsVenture | Angel network |  |  | 14 | 0 |
| 9Unicorns | Institutional |  |  | 14 | 1 |
| Nexus Venture Partners | Institutional |  |  | 13 | 7 |
| Mumbai Angels | Angel network |  |  | 13 | 2 |
| Omnivore | Institutional |  |  | 13 | 6 |
| Capital A | Institutional |  |  | 12 | 6 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2025-01-08 | CHEP India | LEAP India |  |
| 2024-05-14 | Duro Green | BizDateUp Technologies |  |
| 2024-05-03 | StreamO | Pravis |  |
| 2024-04-26 | Awign | Mynavi |  |
| 2024-04-19 | Arya.ai | Aurionpro Solutions | 16.5 |
| 2024-04-18 | Magzter | VerSe Innovation |  |
| 2024-04-09 | Shy Tiger Brands | Ghost Kitchens India |  |
| 2024-03-20 | Barcode | YKONE |  |
| 2024-03-12 | Calling Station and BatBall11 | OneVerse |  |
| 2024-02-29 | Captain Fresh | Captain Fresh |  |
| 2024-02-21 | Difenz | Signzy |  |
| 2024-02-07 | Qdigi Services | Onsitego | 9.6 |
| 2024-02-06 | Spartan Poker | OneVerse |  |
| 2024-02-06 | LotusPay | Juspay |  |
| 2024-02-06 | Kuvera | CRED |  |

## Quality checks

**Coverage vs Entrackr weekly round-ups** (recall):

```json
{
  "weeks_compared": 83,
  "reported_deals_total": 1935,
  "our_deals_total": 843,
  "deal_recall_pct": 43.6,
  "usd_recall_pct": 55.0,
  "median_weekly_deal_recall_pct": 55.0
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 729,
    "checked": 751,
    "pass_rate": 97.1
  },
  "stage_size": {
    "passed": 558,
    "checked": 582,
    "pass_rate": 95.9
  },
  "missing_core": {
    "passed": 1022,
    "checked": 1028,
    "pass_rate": 99.4
  },
  "company_in_title": {
    "passed": 1586,
    "checked": 1590,
    "pass_rate": 99.7
  }
}
```

**Two-agent agreement** (Codex vs OpenCode on the same articles):

```json
{
  "articles_compared": 0,
  "agreement_pct": {
    "record_type": null,
    "company": null,
    "stage": null,
    "amount": null,
    "lead_investors": null,
    "sector": null
  }
}
```

See also `docs/MANUAL_AUDIT.md` for the independent field-by-field audit.