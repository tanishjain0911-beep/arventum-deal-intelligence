# Data report

_Generated from `db/deals.db` at 2026-11-24T02:18:39._

## Contents

| table | rows |
|---|---|
| sources | 1234 |
| companies | 954 |
| investors | 1684 |
| deals | 797 |
| deal_investors | 2757 |
| deal_sources | 810 |
| financials | 340 |
| weekly_totals | 84 |
| corrections | 21 |

Articles used, by source:

| site | articles |
|---|---|
| entrackr | 1234 |

- Deal records before de-duplication: **810**; duplicate reports merged: **13**; deals confirmed by 2+ articles: **13**
- Amount disclosed: **92.1%** of deals; at least one named investor: **90.1%**
- Automatic corrections applied: {'headline-wins': 19, 'implausible amount dropped': 2}

## Primary rounds by year

| year | deals | usd_m | median_usd_m |
|---|---|---|---|
| 2023 | 570 | 9,192.4 | 3.3 |
| 2024 | 148 | 1,489.1 | 4.2 |

## Top sectors by capital raised

| sector | deals | usd_m |
|---|---|---|
| FinTech & Payments | 97 | 2,872.9 |
| E-commerce & D2C | 134 | 2,851.3 |
| EV & Auto | 44 | 969.6 |
| EdTech | 31 | 624.7 |
| Logistics & Mobility | 29 | 425.4 |
| HealthTech | 60 | 331.1 |
| SaaS | 41 | 311.5 |
| Enterprise Software | 9 | 304.3 |
| Media & Gaming | 29 | 268.9 |
| Travel & Hospitality | 20 | 237.6 |
| Industrial Tech | 17 | 195.2 |
| Artificial Intelligence | 24 | 177.5 |
| Automation & Robotics | 9 | 152.7 |
| Consumer Internet | 27 | 148.5 |
| SpaceTech | 8 | 114.9 |

## Most active institutional investors

| name | type | ai_type | hq_country | deals | led |
|---|---|---|---|---|---|
| Inflection Point Ventures | Institutional |  |  | 37 | 30 |
| Venture Catalysts | Institutional |  |  | 23 | 9 |
| Peak XV Partners | Institutional |  |  | 23 | 18 |
| Blume Ventures | Institutional |  |  | 20 | 7 |
| Lightspeed | Institutional |  |  | 18 | 11 |
| Alteria Capital | Debt / Bank |  |  | 17 | 2 |
| Stride Ventures | Debt / Bank |  |  | 16 | 5 |
| Trifecta Capital | Debt / Bank |  |  | 14 | 4 |
| Z47 | Institutional |  |  | 14 | 11 |
| Fireside Ventures | Institutional |  |  | 14 | 9 |
| Titan Capital | Institutional |  |  | 14 | 3 |
| Elevation Capital | Institutional |  |  | 13 | 7 |
| LetsVenture | Angel network |  |  | 13 | 0 |
| Accel | Institutional |  |  | 12 | 6 |
| Anicut Capital | Institutional |  |  | 12 | 6 |
| Y Combinator | Accelerator |  |  | 11 | 6 |
| Better Capital | Institutional |  |  | 10 | 4 |
| Capital A | Institutional |  |  | 10 | 6 |
| Nexus Venture Partners | Institutional |  |  | 10 | 5 |
| British International Investment | Institutional |  |  | 10 | 3 |

## Latest acquisitions

| deal_date | target | acquirer | amount_usd_m |
|---|---|---|---|
| 2024-02-29 | Captain Fresh | Captain Fresh |  |
| 2024-02-21 | Difenz | Signzy |  |
| 2024-02-07 | Qdigi Services | Onsitego | 9.6 |
| 2024-02-06 | LotusPay | Juspay |  |
| 2024-01-24 | Comic Con India | NODWIN Gaming | 6.6 |
| 2024-01-17 | ZestMoney | DMI Group |  |
| 2024-01-06 | PingSafe | SentinelOne |  |
| 2023-12-14 | Pirimid Fintech | Infibeam Avenues | 3.0 |
| 2023-12-04 | Doubtnut | Allen Career Institute |  |
| 2023-11-21 | FactoryPlus | Bizongo |  |
| 2023-11-14 | DeHaat | DeHaat |  |
| 2023-10-30 | Yumlane | Curefoods |  |
| 2023-10-30 | TangoEye | Lenskart |  |
| 2023-10-19 | Freight Tiger | Tata Motors | 18.2 |
| 2023-09-28 | Pocket Aces | Saregama | 21.1 |

## Quality checks

**Coverage vs Entrackr weekly round-ups** (recall):

```json
{
  "weeks_compared": 49,
  "reported_deals_total": 989,
  "our_deals_total": 591,
  "deal_recall_pct": 59.8,
  "usd_recall_pct": 88.6,
  "median_weekly_deal_recall_pct": 60.9
}
```

**Rule-based validation** (no AI):

```json
{
  "headline_amount": {
    "passed": 553,
    "checked": 571,
    "pass_rate": 96.8
  },
  "stage_size": {
    "passed": 438,
    "checked": 457,
    "pass_rate": 95.8
  },
  "missing_core": {
    "passed": 784,
    "checked": 788,
    "pass_rate": 99.5
  },
  "company_in_title": {
    "passed": 1247,
    "checked": 1251,
    "pass_rate": 99.7
  }
}
```

**Two-agent agreement** (Codex vs OpenCode on the same articles):

```json
{
  "articles_compared": null,
  "agreement_pct": null
}
```

See also `docs/MANUAL_AUDIT.md` for the independent field-by-field audit.