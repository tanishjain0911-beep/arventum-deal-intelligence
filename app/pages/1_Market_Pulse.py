import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui
from lib import data, market

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from sectors import ARVENTUM_FOCUS, ALL_SECTORS  # noqa: E402

ui.page("Market Pulse", "📊")
st.title("📊 Market Pulse")
st.caption("Industry intelligence across Indian tech funding, refreshed from public deal reports.")

ALL, FOCUS = "All sectors", "Arventum's 20 focus sectors"
c1, c2 = st.columns([2, 1])
choice = c1.selectbox("Sector", [ALL, FOCUS] + ALL_SECTORS, index=1)
months = c2.select_slider("Look-back for tables", options=[3, 6, 12, 24], value=12, format_func=lambda m: f"{m} months")


@st.cache_data(ttl=3600)
def frames():
    return data.funding_deals(), data.deals(), data.deal_investors()


fd_all, d_all, inv_all = frames()


def pick(df):
    if choice == ALL:
        return df
    if choice == FOCUS:
        return df[df.sector.isin(ARVENTUM_FOCUS)]
    return df[df.sector == choice]


fd = pick(fd_all)
end = fd_all.deal_date.max()
recent = fd[fd.deal_date > end - pd.DateOffset(months=months)]
prev = fd[(fd.deal_date <= end - pd.DateOffset(months=months)) & (fd.deal_date > end - pd.DateOffset(months=2 * months))]


def delta(a, b):
    return f"{100 * (a / b - 1):+.0f}% vs prior {months}m" if b else "no prior period"


ui.tiles([
    (f"{len(recent):,}", f"rounds in last {months} months", delta(len(recent), len(prev))),
    (ui.usd(recent.amount_usd_m.sum()), "capital raised", delta(recent.amount_usd_m.sum(), prev.amount_usd_m.sum())),
    (ui.usd(recent.amount_usd_m.median(), 1), "median round size", "disclosed rounds"),
    (f"{recent.company_id.nunique():,}", "companies funded", ""),
])
st.write("")

# ---- monthly trend: two separate charts (never a dual axis)
m = fd.assign(month=fd.deal_date.dt.to_period("M").dt.to_timestamp()).groupby("month") \
    .agg(deals=("deal_id", "count"), usd_m=("amount_usd_m", "sum")).asfreq("MS", fill_value=0).reset_index()
left, right = st.columns(2)
with left:
    fig = go.Figure(go.Bar(x=m.month, y=m.usd_m, marker_color=ui.SERIES[0],
                           hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}M raised<extra></extra>"))
    fig.update_layout(title="Capital raised per month ($M)", height=320)
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = go.Figure(go.Bar(x=m.month, y=m.deals, marker_color=ui.SERIES[0],
                           hovertemplate="%{x|%b %Y}<br>%{y} rounds<extra></extra>"))
    fig.update_layout(title="Number of rounds per month", height=320)
    st.plotly_chart(fig, use_container_width=True)
st.caption("The most recent month may be incomplete while new articles are being processed.")

# ---- sector heat
st.subheader("Where the money is moving")
h = market.sector_heat(window_m=6).reset_index().rename(columns={"index": "sector"})
h = h[(h.deals + h.deals_prev >= 3) & (h.sector != "Unclassified")]
h["group"] = h.arventum_focus.map({True: "Arventum focus sector", False: "Other sector"})
h = h.sort_values("usd_m")
fig = go.Figure()
for i, (g, sub) in enumerate(h.groupby("group", sort=False)):
    fig.add_bar(y=sub.sector, x=sub.usd_m, orientation="h", name=g, marker_color=ui.SERIES[i],
                customdata=sub[["deals", "deal_growth_pct", "usd_growth_pct"]].values,
                hovertemplate="<b>%{y}</b><br>$%{x:,.0f}M in last 6 months · %{customdata[0]:.0f} rounds"
                              "<br>rounds %{customdata[1]:+.0f}% · capital %{customdata[2]:+.0f}% vs prior 6m"
                              "<extra></extra>")
fig.update_layout(title="Capital raised by sector, last 6 months ($M)", height=max(360, 22 * len(h)),
                  barmode="overlay", yaxis=dict(categoryorder="array", categoryarray=h.sector.tolist()))
st.plotly_chart(fig, use_container_width=True)

# ---- stage benchmarks
st.subheader("What rounds look like right now")
sb_src = fd[fd.deal_date > end - pd.DateOffset(years=2)]
sb = sb_src[sb_src.stage.isin(data.STAGE_ORDER) & sb_src.amount_usd_m.notna()].groupby("stage").amount_usd_m \
    .describe(percentiles=[0.25, 0.5, 0.75]).reindex([s for s in data.STAGE_ORDER])
sb = sb[sb["count"] >= 3]
c1, c2 = st.columns([3, 2])
with c1:
    fig = go.Figure()
    fig.add_bar(y=sb.index, x=sb["75%"] - sb["25%"], base=sb["25%"], orientation="h", marker_color=ui.SEQ[2],
                name="middle 50% of rounds", hovertemplate="%{y}: $%{base:.1f}M – $%{x:.1f}M wide<extra></extra>")
    fig.add_scatter(y=sb.index, x=sb["50%"], mode="markers", name="median", marker=dict(color=ui.NAVY, size=10),
                    hovertemplate="%{y} median: $%{x:.1f}M<extra></extra>")
    ticks = [0.1, 0.3, 1, 3, 10, 30, 100, 300]
    fig.update_layout(title="Round size by stage, last 2 years ($M, log scale)", height=400,
                      xaxis=dict(type="log", tickvals=ticks, ticktext=[f"${t:g}M" for t in ticks]),
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    t = sb[["count", "25%", "50%", "75%"]].rename(columns={"count": "rounds", "25%": "p25 $M", "50%": "median $M",
                                                           "75%": "p75 $M"}).round(1)
    t["rounds"] = t.rounds.astype(int)
    st.dataframe(t, use_container_width=True)

# ---- investors and deals
c1, c2 = st.columns([2, 3])
with c1:
    st.subheader("Most active investors")
    ids = recent.deal_id
    inv = inv_all[inv_all.deal_id.isin(ids) & (inv_all.investor_type != "Individual")]
    top = inv.groupby("investor").agg(rounds=("deal_id", "nunique"), led=("is_lead", "sum"),
                                       HQ=("hq_country", "first")).sort_values(["rounds", "led"], ascending=False)
    st.dataframe(top.head(15), use_container_width=True)
with c2:
    st.subheader("Latest deals")
    dd = pick(d_all).sort_values("deal_date", ascending=False).head(40)
    leads = inv_all[inv_all.is_lead == 1].groupby("deal_id").investor.apply(lambda s: ", ".join(s))
    dd = dd.assign(lead=dd.deal_id.map(leads).fillna(""), acquirer=dd.acquirer.fillna(""))
    show = dd[["deal_date", "company", "sector", "stage", "amount_usd_m", "lead", "acquirer", "source_url"]]
    st.dataframe(show, use_container_width=True, hide_index=True, column_config={
        "deal_date": st.column_config.DateColumn("date", format="DD MMM YYYY"),
        "amount_usd_m": st.column_config.NumberColumn("amount ($M)", format="%.1f"),
        "source_url": st.column_config.LinkColumn("source", display_text="article"),
    })
ui.source_note()
