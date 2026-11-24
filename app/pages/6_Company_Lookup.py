import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui
from lib import data, valuation

ui.page("Company Lookup", "🔎")
st.title("🔎 Company Lookup")
st.caption("Everything public about one company in one screen, for the meeting prep that usually takes an hour.")


@st.cache_data(ttl=3600)
def frames():
    d = data.deals()
    inv = data.deal_investors()
    fin = data.financials()
    sc = pd.read_csv(ui.PROCESSED / "radar_scores.csv") if (ui.PROCESSED / "radar_scores.csv").exists() \
        else pd.DataFrame()
    return d, inv, fin, sc


d, inv, fin, sc = frames()
names = sorted(set(d.company.dropna()) | set(fin.company.dropna()), key=str.lower)
top_pick = sc.sort_values("probability", ascending=False).company.iloc[0] if len(sc) else None
default = names.index(top_pick) if top_pick in names else 0  # open on the Radar's current top private company
company = st.selectbox("Company", names, index=default, help="Type to search")

cd = d[d.company == company].sort_values("deal_date", ascending=False)
cf = fin[fin.company == company].sort_values("fy")
prim = cd[cd.deal_type.isin(["equity", "debt"])]
sector = (cd.sector.dropna().tolist() + cf.sector.dropna().tolist() + ["Unclassified"])[0]
desc = next((x for x in cd.description.dropna().tolist() if x), None)

st.markdown(f"**{company}** · {sector}" + (f" · {desc}" if desc else ""))
score = sc[sc.company == company].probability.iloc[0] if len(sc) and company in set(sc.company) else None
last_val = cd.valuation_usd_m.dropna().iloc[0] if cd.valuation_usd_m.notna().any() else None
ui.tiles([
    (ui.usd(prim.amount_usd_m.sum()), "total raised (tracked)", f"{len(prim)} rounds"),
    (prim.deal_date.max().strftime("%b %Y") if len(prim) else "—", "last round",
     prim.stage.iloc[0] if len(prim) else ""),
    (ui.usd(last_val) if last_val else "—", "last disclosed valuation", ""),
    (f"{100 * score:.0f}%" if score is not None else "—", "Radar: likelihood of a round in 12m",
     "see Origination Radar"),
])
st.write("")

c1, c2 = st.columns([3, 2])
with c1:
    st.subheader("Deal history")
    leads = inv[inv.is_lead == 1].groupby("deal_id").investor.apply(lambda s: ", ".join(s))
    others = inv[inv.is_lead == 0].groupby("deal_id").investor.apply(lambda s: ", ".join(s))
    show = cd.assign(lead=cd.deal_id.map(leads).fillna(""), others=cd.deal_id.map(others).fillna(""),
                     acquirer=cd.acquirer.fillna(""))
    st.dataframe(show[["deal_date", "deal_type", "stage", "amount_usd_m", "lead", "others", "acquirer",
                       "source_url"]], hide_index=True, use_container_width=True, column_config={
        "deal_date": st.column_config.DateColumn("date", format="DD MMM YYYY"),
        "amount_usd_m": st.column_config.NumberColumn("amount ($M)", format="%.1f"),
        "source_url": st.column_config.LinkColumn("source", display_text="article")})
with c2:
    st.subheader("Backers")
    b = inv[inv.deal_id.isin(cd.deal_id)].groupby("investor").agg(rounds=("deal_id", "nunique"),
                                                                    led=("is_lead", "sum"),
                                                                    HQ=("hq_country", "first"))
    st.dataframe(b.sort_values(["rounds", "led"], ascending=False), use_container_width=True)

if len(cf):
    st.subheader("Reported financials (₹ crore)")
    c1, c2 = st.columns([3, 2])
    with c1:
        fig = go.Figure()
        fig.add_bar(x=cf.fiscal_year, y=cf.revenue_inr_cr, name="revenue", marker_color=ui.SERIES[0],
                    hovertemplate="%{x}: revenue ₹%{y:,.0f} Cr<extra></extra>")
        fig.update_layout(title="Revenue by fiscal year", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(cf[["fiscal_year", "revenue_inr_cr", "profit_inr_cr", "source_url"]], hide_index=True,
                     use_container_width=True, column_config={
                         "revenue_inr_cr": st.column_config.NumberColumn("revenue", format="%.0f"),
                         "profit_inr_cr": st.column_config.NumberColumn("profit / loss", format="%.0f"),
                         "source_url": st.column_config.LinkColumn("source", display_text="article")})

    latest = cf.dropna(subset=["revenue_inr_cr"]).iloc[-1]
    prev = cf.dropna(subset=["revenue_inr_cr"]).iloc[-2] if len(cf.dropna(subset=["revenue_inr_cr"])) > 1 else None
    growth = (latest.revenue_inr_cr / prev.revenue_inr_cr - 1) if prev is not None and prev.revenue_inr_cr > 0 \
        else 0.3
    margin = (latest.profit_inr_cr / latest.revenue_inr_cr) if pd.notna(latest.profit_inr_cr) and \
        latest.revenue_inr_cr > 0 else 0.0
    if sector in set(valuation.comparables().sector):
        v = valuation.value_company(sector, float(latest.revenue_inr_cr), float(np.clip(growth, -0.5, 2)),
                                    float(np.clip(margin, -1, 0.5)), "Both")
        bl = valuation.blended_range(v)
        if bl:
            st.info(f"**Indicative value from the Price Finder:** ₹{bl[0]:,.0f}–{bl[2]:,.0f} Cr "
                    f"(central ₹{bl[1]:,.0f} Cr), based on {latest.fiscal_year} revenue of "
                    f"₹{latest.revenue_inr_cr:,.0f} Cr, {growth:+.0%} growth and {margin:+.0%} net margin "
                    "(net margin used as a proxy for EBITDA margin).")
ui.source_note()
