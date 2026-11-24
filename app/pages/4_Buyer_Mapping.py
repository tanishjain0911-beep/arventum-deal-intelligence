import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import ui
from lib import acquirers

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from sectors import ALL_SECTORS  # noqa: E402

ui.page("Buyer Mapping", "🏢")
st.title("🏢 Buyer Mapping")
st.caption("Who acquires Indian tech companies like your client's? Ranked by sector relevance, appetite and recency.")

acq = acquirers.acquisitions()
if acq.empty:
    st.warning("No acquisitions in the database yet.")
    st.stop()

ms = acquirers.market_summary()
by_year = ms["acquisitions_by_year"]
ui.tiles([
    (f"{len(acq):,}", "acquisitions with a named buyer", f"{min(by_year)}–{max(by_year)}"),
    (f"{acq.acquirer.nunique():,}", "distinct acquirers", ""),
    (f"{int((acq.acquirer.value_counts() >= 2).sum())}", "serial acquirers (2+ deals)", ""),
    (f"{ms['disclosed_value_pct']}%", "with a disclosed price", "most Indian tech M&A is undisclosed"),
])
st.write("")

c1, c2 = st.columns([1, 2])
sectors = [s for s in ALL_SECTORS if s in set(acq.sector)]
sector = c1.selectbox("Target's sector", sectors,
                      index=sectors.index("FinTech & Payments") if "FinTech & Payments" in sectors else 0)
res = acquirers.rank_buyers(sector, top=30)
c1.markdown("**Acquisitions by sector**")
top_sec = acq[acq.sector != "Unclassified"].sector.value_counts().head(10).sort_values()
fig = go.Figure(go.Bar(y=top_sec.index, x=top_sec.values, orientation="h", marker_color=ui.SERIES[0],
                       hovertemplate="%{y}: %{x} acquisitions<extra></extra>"))
fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
c1.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown(f"**Most likely buyers for a {sector} company**")
    st.dataframe(res[["acquirer", "match_pct", "in_sector", "acquisitions_total", "last_24m", "months_since_last",
                      "targets"]], hide_index=True, use_container_width=True, column_config={
        "match_pct": st.column_config.ProgressColumn("match", format="%.0f", min_value=0, max_value=100),
        "in_sector": st.column_config.NumberColumn(f"{sector} buys"),
        "acquisitions_total": st.column_config.NumberColumn("total buys"),
        "last_24m": st.column_config.NumberColumn("buys, last 24m"),
        "months_since_last": st.column_config.NumberColumn("months since last", format="%.0f"),
        "targets": "recent targets"})

st.subheader("Recent acquisitions")
recent = acq.sort_values("deal_date", ascending=False).head(40)
st.dataframe(recent[["deal_date", "company", "sector", "acquirer", "amount_usd_m", "source_url"]], hide_index=True,
             use_container_width=True, column_config={
                 "deal_date": st.column_config.DateColumn("date", format="DD MMM YYYY"),
                 "company": "target", "amount_usd_m": st.column_config.NumberColumn("price ($M)", format="%.1f"),
                 "source_url": st.column_config.LinkColumn("source", display_text="article")})
ui.source_note()
