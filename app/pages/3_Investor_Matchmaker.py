import sys
from pathlib import Path

import pandas as pd
import streamlit as st

import ui
from lib import data, matching

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from sectors import ALL_SECTORS  # noqa: E402

ui.page("Investor Matchmaker", "🤝")
st.title("🤝 Investor Matchmaker")
st.caption("Describe the client. Get a ranked list of investors most likely to back it, with the evidence.")

with st.form("profile"):
    c1, c2, c3 = st.columns(3)
    sector = c1.selectbox("Sector", ALL_SECTORS, index=ALL_SECTORS.index("Cybersecurity"))
    stage = c2.selectbox("Round", [s for s in data.STAGE_ORDER if s != "pre-ipo"], index=3)
    amount = c3.number_input("Target raise ($M)", min_value=0.1, max_value=2000.0, value=10.0, step=1.0)
    c4, c5, c6 = st.columns(3)
    need_lead = c4.checkbox("Client needs a lead investor", value=True)
    foreign = c5.checkbox("Foreign investors only (HQ outside India)")
    top = c6.selectbox("Show top", [20, 30, 50], index=1)
    go_btn = st.form_submit_button("Find investors", type="primary")


@st.cache_data(ttl=3600, show_spinner="Scoring investors…")
def run(sector, stage, amount, need_lead, foreign, top):
    return matching.rank(sector, stage, amount, need_lead=need_lead, top=top, foreign_only=foreign)


res = run(sector, stage, amount, need_lead, foreign, top)
if res.empty:
    st.warning("No investors match these filters yet.")
    st.stop()

inv = data.deal_investors()
meta = inv.drop_duplicates("investor_id").set_index("investor_id")[["hq_country", "ai_type"]]
res = res.join(meta, on="investor_id")
st.dataframe(
    res[["investor", "ai_type", "hq_country", "match_pct", "deals_in_sector", "activity_18m", "median_round_usd_m",
         "lead_rate"]],
    hide_index=True, use_container_width=True,
    column_config={
        "match_pct": st.column_config.ProgressColumn("match", format="%.0f", min_value=0, max_value=100),
        "ai_type": "type (AI-classified)", "hq_country": "HQ",
        "deals_in_sector": st.column_config.NumberColumn(f"{sector} deals"),
        "activity_18m": st.column_config.NumberColumn("deals, last 18m"),
        "median_round_usd_m": st.column_config.NumberColumn("typical round ($M)", format="%.1f"),
        "lead_rate": st.column_config.NumberColumn("leads", format="%.0f%%",
                                                   help="share of its deals where it led the round"),
    })
st.caption("Match blends sector fit, stage fit, cheque-size fit, recent activity and (optionally) lead appetite. "
           "Small samples are shrunk toward the market average, so one lucky deal can't make a 'specialist'.")

st.subheader("Evidence for an investor")
who = st.selectbox("Investor", res.investor.tolist())
h = matching._history(data.funding_deals().deal_date.max() + pd.Timedelta(days=1))
row = res[res.investor == who].iloc[0]
summary, ex = matching.reasons(row, sector, h)
st.markdown(f"**{who}**: {summary}")
allx = h[h.investor_id == row.investor_id].sort_values("deal_date", ascending=False)
deals_df = data.deals()[["deal_id", "source_url"]]
allx = allx.merge(deals_df, on="deal_id", how="left")
st.dataframe(allx[["deal_date", "company", "sector", "stage", "amount_usd_m", "is_lead", "source_url"]].head(25),
             hide_index=True, use_container_width=True, column_config={
                 "deal_date": st.column_config.DateColumn("date", format="DD MMM YYYY"),
                 "amount_usd_m": st.column_config.NumberColumn("round ($M)", format="%.1f"),
                 "is_lead": st.column_config.CheckboxColumn("led"),
                 "source_url": st.column_config.LinkColumn("source", display_text="article")})

bt = ui.load_json("matching_backtest.json")
if bt.get("test_deals"):
    with st.expander("Does it work? Out-of-sample test"):
        m, b = bt["model_hit_rate"], bt["baseline_hit_rate"]
        st.markdown(f"For **{bt['test_deals']} real rounds since {bt['period_start']}**, investors were ranked using "
                    "only data from before each round. How often was a real participant in the list?")
        ui.tiles([(f"{100 * m[k]:.0f}%", f"in the top {k}", f"vs {100 * b[k]:.0f}% for 'most active investors'")
                  for k in m])
ui.source_note()
