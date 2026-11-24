import pandas as pd
import streamlit as st

import ui
from lib import data

ui.page("Home", "🏛️")
ui.hero("Arventum Deal Intelligence",
        "AI-native origination, investor & buyer mapping, and valuation benchmarking for Indian technology deals, "
        "built from thousands of public deal reports by a team of AI agents.")


@st.cache_data(ttl=3600)
def headline():
    d = data.deals()
    fd = data.funding_deals()
    inv = data.deal_investors()
    fin = data.financials()
    return {
        "deals": len(d), "usd": fd.amount_usd_m.sum(), "companies": d.company_id.nunique(),
        "investors": inv.investor_id.nunique(), "financials": len(fin),
        "acq": int((d.deal_type == "acquisition").sum()),
        "first": d.deal_date.min(), "last": d.deal_date.max(),
    }


h = headline()
ui.tiles([
    (f"{h['deals']:,}", "deals tracked", f"{h['first']:%b %Y} – {h['last']:%b %Y}"),
    (ui.usd(h["usd"], 1), "capital raised in tracked rounds", "equity + venture debt"),
    (f"{h['investors']:,}", "investors profiled", "funds, angels, corporates, DFIs"),
    (f"{h['companies']:,}", "companies", f"{h['financials']:,} with reported revenue"),
    (f"{h['acq']:,}", "acquisitions mapped", "strategic & financial buyers"),
])
st.write("")

st.subheader("Five engines, one per step of Arventum's deal process")
cards = [
    ("pages/1_Market_Pulse.py", "📊 Market Pulse", "Industry Intelligence",
     "Deal momentum, typical round sizes, most active investors and recent deals across Arventum's 20 sectors."),
    ("pages/2_Origination_Radar.py", "🎯 Origination Radar", "Market Mapping · Target Identification",
     "Which companies are likely to raise in the next 12 months, scored by a backtested model, with reasons."),
    ("pages/3_Investor_Matchmaker.py", "🤝 Investor Matchmaker", "Investor Mapping",
     "Rank funds for a client by sector, stage, cheque size and recent activity, with their comparable deals."),
    ("pages/4_Buyer_Mapping.py", "🏢 Buyer Mapping", "Buyer Mapping",
     "Serial acquirers of Indian tech companies by sector, appetite and recency."),
    ("pages/5_Price_Finder.py", "💰 Price Finder", "Valuation Benchmarking",
     "Football-field valuation from listed peers, a cross-validated regression and Indian private rounds."),
]
cols = st.columns(len(cards))
for c, (path, title, step, desc) in zip(cols, cards):
    with c:
        st.markdown(f'<div class="card"><h4>{title}</h4><span class="pill">{step}</span><p>{desc}</p></div>',
                    unsafe_allow_html=True)
        st.page_link(path, label="Open →")

st.write("")
left, right = st.columns([3, 2])
with left:
    st.subheader("Why this isn't a ChatGPT prompt")
    st.markdown("""
- **Its own data.** Every deal is extracted from a public article and linked back to it. A prompt guesses from memory.
- **Measured, not claimed.** Each model is backtested on deals it never saw, and data quality is audited four independent ways.
- **Built to stay current.** One command (`run_all.py --refresh`) collects, extracts, checks and loads the latest deals.
- **Explainable.** Every score comes with the signals and comparable deals behind it.
""")
with right:
    q = ui.load_json("validation.json").get("checks", {})
    cov = ui.load_json("coverage.json")
    cc = ui.load_json("crosscheck.json").get("agreement_pct", {})
    st.subheader("Data quality at a glance")
    ui.tiles([
        (f"{cc.get('company', '—')}%", "AI agents agree on company", "Codex vs OpenCode, same articles"),
        (f"{q.get('headline_amount', {}).get('pass_rate', '—')}%", "amounts match the headline", "deterministic check"),
    ])
    st.write("")
    ui.tiles([
        (f"{cov.get('usd_recall_pct', '—')}%", "of reported $ captured", "vs published weekly totals"),
        (f"{q.get('company_in_title', {}).get('pass_rate', '—')}%", "company names grounded", "found in the source text"),
    ])
    st.page_link("pages/7_Data_and_Quality.py", label="See the full data-quality report →")

st.divider()
ui.source_note()
