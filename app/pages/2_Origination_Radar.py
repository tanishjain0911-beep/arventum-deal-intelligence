import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui
from lib import data, radar

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from sectors import ARVENTUM_FOCUS  # noqa: E402

ui.page("Origination Radar", "🎯")
st.title("🎯 Origination Radar")
st.caption("Which companies are likely to announce their next round within 12 months? "
           "Call them before another bank does.")

scores_f = ui.PROCESSED / "radar_scores.csv"
bt = ui.load_json("radar_backtest.json")
if not scores_f.exists():
    st.warning("Radar scores have not been computed yet. Run `python analysis/run_engines.py radar`.")
    st.stop()


@st.cache_data(ttl=3600)
def load_scores():
    s = pd.read_csv(scores_f, parse_dates=["last_date"])
    imp = pd.read_csv(ui.PROCESSED / "radar_importance.csv", index_col=0).iloc[:, 0] \
        if (ui.PROCESSED / "radar_importance.csv").exists() else pd.Series(dtype=float)
    return s, imp


scores, importance = load_scores()

# ---- proof first: the backtest
summ = bt.get("summary", {})
if summ:
    st.subheader("Does it work? Backtest on deals the model never saw")
    ui.tiles([
        (f"{summ['mean_auc']:.2f}", "ranking accuracy (AUC)", f"vs {summ['mean_auc_heuristic']:.2f} for the "
                                                               "'raised 18-24 months ago' rule"),
        (f"{100 * summ['mean_precision_top100']:.0f}%", "of the top-100 picks raised within 12 months",
         f"vs {100 * summ['mean_precision_top100_heuristic']:.0f}% for the rule"),
        (f"{summ['mean_lift_top100']:.1f}×", "better than picking at random",
         f"base rate {100 * summ['mean_base_rate']:.0f}%"),
        (f"{len(bt.get('folds', []))}", "separate test quarters", "walk-forward, no look-ahead"),
    ])
    folds = bt.get("folds", [])
    if folds and folds[-1].get("deciles"):
        dec = folds[-1]["deciles"]
        fig = go.Figure(go.Bar(x=[f"D{i}" for i in range(1, len(dec) + 1)], y=[100 * v for v in dec],
                               marker_color=ui.SERIES[0],
                               hovertemplate="%{x}: %{y:.0f}% actually raised<extra></extra>"))
        fig.add_hline(y=100 * folds[-1]["base_rate"], line_dash="dot", line_color=ui.MUTED,
                      annotation_text="average company", annotation_font_color=ui.INK2)
        fig.update_layout(title=f"Share that actually raised, by model score decile (test date "
                                f"{folds[-1]['test_cutoff']}; D1 = highest scores)", height=300,
                          yaxis_title="% raised within 12 months")
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("How the backtest works"):
        st.markdown("""
For each test date the model is trained **only on snapshots whose 12-month outcome was already known before that
date**, then scores every company as of the test date. We then check who actually raised in the following 12 months.
Features use only information published before each snapshot (no look-ahead). The benchmark is the rule a banker
would use by hand: companies whose last round was ~18-24 months ago are "due".
""")
        st.dataframe(pd.DataFrame(folds).drop(columns=["deciles"], errors="ignore"), hide_index=True,
                     use_container_width=True)
else:
    st.info("Backtest not available yet. It needs more than 21 months of history in the database.")

# ---- the list
st.subheader("Companies most likely to raise next")
c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
sector_opt = c1.selectbox("Sector", ["Arventum focus sectors", "All sectors"] + sorted(scores.sector.dropna().unique()))
stages = ["any"] + [s for s in data.STAGE_ORDER if s in set(scores.last_stage)]
stage_opt = c2.selectbox("Last round stage", stages)
min_raise = c3.select_slider("Last round at least", options=[0, 1, 5, 10, 25, 50], value=1,
                             format_func=lambda v: "any" if v == 0 else f"${v}M")
top_n = c4.selectbox("Show", [25, 50, 100], index=0)

s = scores.copy()
if sector_opt == "Arventum focus sectors":
    s = s[s.sector.isin(ARVENTUM_FOCUS)]
elif sector_opt != "All sectors":
    s = s[s.sector == sector_opt]
if stage_opt != "any":
    s = s[s.last_stage == stage_opt]
s["last_round_usd_m"] = np.expm1(s.log_last_amount)
if min_raise:
    s = s[s.last_round_usd_m.fillna(0) >= min_raise]
s = s.sort_values("probability", ascending=False).head(top_n)
s["likelihood_pct"] = 100 * s.probability
st.dataframe(
    s[["company", "sector", "last_stage", "last_date", "months_since_last", "last_round_usd_m", "n_prior_rounds",
       "likelihood_pct"]],
    hide_index=True, use_container_width=True,
    column_config={
        "likelihood_pct": st.column_config.ProgressColumn("likelihood (12m)", format="%.0f%%", min_value=0,
                                                          max_value=100),
        "last_date": st.column_config.DateColumn("last round", format="MMM YYYY"),
        "months_since_last": st.column_config.NumberColumn("months since", format="%.0f"),
        "last_round_usd_m": st.column_config.NumberColumn("last round ($M)", format="%.1f"),
        "n_prior_rounds": st.column_config.NumberColumn("rounds since 2023"),
        "last_stage": "stage",
    })
st.caption("Likelihood = the model's estimated probability of a new primary round within 12 months.")

# ---- drill-down
st.subheader("Why is a company on the list?")
pick = st.selectbox("Company", s.company.tolist())
if pick:
    row = s[s.company == pick].iloc[0]
    c1, c2 = st.columns([1, 2])
    with c1:
        ui.tiles([(f"{100 * row.probability:.0f}%", "likelihood of a round in 12 months", row.sector)])
    with c2:
        for sig in radar.explain_row(row):
            st.markdown(f'<p class="signal">• {sig}</p>', unsafe_allow_html=True)
    hist = data.deals()
    hist = hist[hist.company == pick].sort_values("deal_date", ascending=False)
    st.dataframe(hist[["deal_date", "deal_type", "stage", "amount_usd_m", "source_url"]], hide_index=True,
                 use_container_width=True, column_config={
                     "deal_date": st.column_config.DateColumn("date", format="DD MMM YYYY"),
                     "amount_usd_m": st.column_config.NumberColumn("amount ($M)", format="%.1f"),
                     "source_url": st.column_config.LinkColumn("source", display_text="article")})

if len(importance):
    with st.expander("What drives the model (permutation importance)"):
        imp = importance.sort_values()
        fig = go.Figure(go.Bar(y=imp.index, x=imp.values, orientation="h", marker_color=ui.SERIES[0],
                               hovertemplate="%{y}: AUC drops %{x:.3f} when shuffled<extra></extra>"))
        fig.update_layout(height=420, title="Drop in AUC when the feature is shuffled")
        st.plotly_chart(fig, use_container_width=True)
ui.source_note()
