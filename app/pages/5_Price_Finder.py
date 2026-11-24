import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import ui
from lib import valuation

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from sectors import ALL_SECTORS  # noqa: E402

ui.page("Price Finder", "💰")
st.title("💰 Price Finder")
st.caption("What is the client worth? Three independent methods side by side: the banker's football field.")

comps = valuation.comparables()
sectors = [s for s in ALL_SECTORS if s in set(comps.sector)]
with st.form("val"):
    c1, c2, c3 = st.columns(3)
    sector = c1.selectbox("Sector", sectors, index=sectors.index("SaaS") if "SaaS" in sectors else 0)
    revenue = c2.number_input("Annual revenue (₹ crore)", min_value=1.0, value=150.0, step=10.0)
    growth = c3.slider("Revenue growth (YoY)", -20, 150, 50, format="%d%%") / 100
    c4, c5, c6 = st.columns(3)
    margin = c4.slider("EBITDA margin", -60, 50, 10, format="%d%%") / 100
    gm_known = c5.checkbox("I know the gross margin")
    gross = c5.slider("Gross margin", 0, 95, 65, format="%d%%", disabled=not gm_known) / 100
    scope = c6.radio("Listed peers", ["Both", "India", "Global"], horizontal=True)
    st.form_submit_button("Value it", type="primary")

v = valuation.value_company(sector, revenue, growth, margin, scope, gross if gm_known else None)
blend = valuation.blended_range(v)
if not blend:
    st.warning("Not enough comparables for this sector.")
    st.stop()

usd_per_cr = 1e7 / 88.0 / 1e6
ui.tiles([
    (f"₹{blend[0]:,.0f}–{blend[2]:,.0f} Cr", "indicative enterprise value range",
     f"≈ {ui.usd(blend[0] * usd_per_cr, 0)}–{ui.usd(blend[2] * usd_per_cr, 0)}"),
    (f"₹{blend[1]:,.0f} Cr", "central estimate", f"{blend[1] / revenue:.1f}× revenue"),
    (f"{len(v.peers)}", f"listed {sector} peers", scope.lower() if scope != "Both" else "India + global"),
    (f"{0 if v.private_comps is None else len(v.private_comps)}", "Indian private rounds with valuation & revenue",
     "precedents"),
])
st.write("")

# ---- football field: one horizontal range per method
rng = list(reversed(v.ranges))
fig = go.Figure()
fig.add_bar(y=[r["method"] for r in rng], x=[r["high"] - r["low"] for r in rng], base=[r["low"] for r in rng],
            orientation="h", marker_color=ui.SEQ[3], name="range",
            customdata=[[r["low"], r["high"], r["multiple"]] for r in rng],
            hovertemplate="%{y}<br>₹%{customdata[0]:,.0f} – ₹%{customdata[1]:,.0f} Cr<br>%{customdata[2]}"
                          "<extra></extra>")
fig.add_scatter(y=[r["method"] for r in rng], x=[r["mid"] for r in rng], mode="markers", name="midpoint",
                marker=dict(color=ui.NAVY, size=11, symbol="line-ns", line=dict(width=3, color=ui.NAVY)),
                hovertemplate="midpoint ₹%{x:,.0f} Cr<extra></extra>")
fig.add_vrect(x0=blend[0], x1=blend[2], fillcolor=ui.SERIES[2], opacity=0.10, line_width=0,
              annotation_text="indicative range", annotation_position="top left",
              annotation_font_color=ui.INK2)
fig.update_layout(title="Football field: enterprise value (₹ crore)", height=120 + 70 * len(rng),
                  showlegend=False, xaxis_title="₹ crore")
st.plotly_chart(fig, use_container_width=True)
for n in v.notes:
    st.caption(f"ℹ️ {n}")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Listed peers")
    p = v.peers[["name", "market", "ev_revenue", "revenue_growth", "gross_margin", "ebitda_margin"]].copy()
    st.dataframe(p, hide_index=True, use_container_width=True, column_config={
        "ev_revenue": st.column_config.NumberColumn("EV / revenue", format="%.1f×"),
        "revenue_growth": st.column_config.NumberColumn("growth", format="percent"),
        "gross_margin": st.column_config.NumberColumn("gross margin", format="percent"),
        "ebitda_margin": st.column_config.NumberColumn("EBITDA margin", format="percent")})
    st.caption(f"Live from Yahoo Finance (as of {comps.as_of.iloc[0]}). A 25% private-company discount is "
               "applied to listed multiples.")
with c2:
    st.subheader("Indian private rounds")
    if v.private_comps is not None and len(v.private_comps):
        st.dataframe(v.private_comps[["company", "deal_date", "stage", "valuation_inr_cr", "revenue_inr_cr",
                                      "ev_revenue", "source_url"]].head(25), hide_index=True,
                     use_container_width=True, column_config={
                         "valuation_inr_cr": st.column_config.NumberColumn("valuation ₹Cr", format="%.0f"),
                         "revenue_inr_cr": st.column_config.NumberColumn("revenue ₹Cr", format="%.0f"),
                         "ev_revenue": st.column_config.NumberColumn("× revenue", format="%.1f×"),
                         "source_url": st.column_config.LinkColumn("source", display_text="article")})
    else:
        st.info("Few Indian private rounds disclose both valuation and revenue.")

with st.expander("Model details"):
    r = v.regression
    st.markdown(f"""
**Regression on {r['n']} listed comparables:** log(EV/Revenue) = {r['intercept']:.2f} + {r['growth']:.2f}·growth
{r['margin']:+.2f}·EBITDA margin {r['gross']:+.2f}·gross margin {r['india']:+.2f}·India  (R² {r['r2']:.2f})

This specification was chosen by **leave-one-out cross-validation** across six candidates. Gross margin was the strongest
driver: high-gross-margin businesses command higher revenue multiples. The range shown is ±0.67 residual SD (the middle
50% of outcomes for companies like this one).
""")
ui.source_note()
