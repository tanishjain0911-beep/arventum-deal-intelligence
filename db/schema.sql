-- Arventum Deal Intelligence: core schema (SQLite)

CREATE TABLE IF NOT EXISTS sources (
    source_id     INTEGER PRIMARY KEY,
    url           TEXT UNIQUE NOT NULL,
    site          TEXT NOT NULL,            -- e.g. entrackr
    kind          TEXT,                     -- deal / acquisition / financials / report
    published     DATE,
    title         TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    company_id    INTEGER PRIMARY KEY,
    name          TEXT UNIQUE NOT NULL,     -- canonical name
    sector        TEXT,                     -- one of sectors.yaml keys
    sub_sector    TEXT,
    city          TEXT,
    description   TEXT                      -- short "what they do"
);

CREATE TABLE IF NOT EXISTS investors (
    investor_id   INTEGER PRIMARY KEY,
    name          TEXT UNIQUE NOT NULL,     -- canonical name
    type          TEXT,                     -- VC / PE / CVC / Corporate / Angel / Debt / Govt / Family office / Other
    country       TEXT
);

CREATE TABLE IF NOT EXISTS investor_aliases (
    alias         TEXT PRIMARY KEY,         -- lower-cased raw spelling
    investor_id   INTEGER NOT NULL REFERENCES investors(investor_id)
);

CREATE TABLE IF NOT EXISTS deals (
    deal_id       INTEGER PRIMARY KEY,
    company_id    INTEGER NOT NULL REFERENCES companies(company_id),
    deal_date     DATE NOT NULL,
    deal_type     TEXT NOT NULL,            -- equity / debt / acquisition / secondary / ipo
    stage         TEXT,                     -- pre-seed, seed, pre-series-a, series-a ... growth, undisclosed
    amount_usd_m  REAL,                     -- NULL when undisclosed
    amount_inr_cr REAL,
    amount_raw    TEXT,                     -- as written in source, for audit
    valuation_usd_m REAL,                   -- post-money if disclosed
    acquirer_id   INTEGER REFERENCES investors(investor_id),  -- for acquisitions
    source_id     INTEGER REFERENCES sources(source_id),
    confidence    REAL                      -- extraction confidence 0..1
);

CREATE TABLE IF NOT EXISTS deal_investors (
    deal_id       INTEGER NOT NULL REFERENCES deals(deal_id),
    investor_id   INTEGER NOT NULL REFERENCES investors(investor_id),
    is_lead       INTEGER DEFAULT 0,
    PRIMARY KEY (deal_id, investor_id)
);

-- Company financials from public filings coverage (revenue / profit per fiscal year)
CREATE TABLE IF NOT EXISTS financials (
    company_id    INTEGER NOT NULL REFERENCES companies(company_id),
    fiscal_year   TEXT NOT NULL,            -- e.g. FY25
    revenue_inr_cr REAL,
    profit_inr_cr REAL,                     -- negative = loss
    source_id     INTEGER REFERENCES sources(source_id),
    PRIMARY KEY (company_id, fiscal_year)
);

-- Weekly market totals from the weekly funding reports (used for QA + dashboard)
CREATE TABLE IF NOT EXISTS weekly_totals (
    week_end      DATE PRIMARY KEY,
    deal_count    INTEGER,
    total_usd_m   REAL,
    source_id     INTEGER REFERENCES sources(source_id)
);

CREATE INDEX IF NOT EXISTS idx_deals_date ON deals(deal_date);
CREATE INDEX IF NOT EXISTS idx_deals_company ON deals(company_id);
CREATE INDEX IF NOT EXISTS idx_di_investor ON deal_investors(investor_id);
