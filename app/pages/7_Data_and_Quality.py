import sqlite3

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui
from lib import data

ui.page("Data & Quality", "🔍")
st.title("🔍 Data & Quality")
st.caption("How much to trust the numbers, measured four independent ways.")

build = ui.load_json("build_report.json")
val = ui.load_json("validation.json").get("checks", {})
cov = ui.load_json("coverage.json")
cc = ui.load_json("crosscheck.json")
me = ui.load_json("model_eval.json")

t = build.get("tables", {})
ui.tiles([
    (f"{t.get('deals', 0):,}", "deals", f"from {t.get('sources', 0):,} source articles"),
    (f"{build.get('multi_source_deals', 0):,}", "deals confirmed by 2+ articles", "cross-source de-duplication"),
    (f"{build.get('amount_disclosed_pct', '—')}%", "with a disclosed amount", ""),
    (f"{t.get('corrections', 0):,}", "automatic corrections", "every one logged"),
])

st.subheader("1 · Do two independent AI agents agree?")
nice = {"record_type": "Deal type", "company": "Company", "stage": "Stage", "amount": "Amount",
        "lead_investors": "Lead investors", "sector": "Sector"}
ag = {nice.get(k, k): v for k, v in cc.get("agreement_pct", {}).items()}
if ag:
    fig = go.Figure(go.Bar(x=list(ag.values()), y=list(ag.keys()), orientation="h", marker_color=ui.SERIES[0],
                           text=[f"{v}%" for v in ag.values()], textposition="outside",
                           textfont=dict(color=ui.INK2),
                           hovertemplate="%{y}: %{x}% agreement<extra></extra>"))
    fig.update_layout(height=280, xaxis=dict(range=[0, 105], title="% of articles where both agents agree"),
                      yaxis=dict(autorange="reversed"),
                      title=f"Codex vs OpenCode on the same {cc.get('articles_compared', 0)} articles")
    st.plotly_chart(fig, use_container_width=True)
st.markdown("**Every extraction method, with its measured accuracy against Codex** (the reference agent)")
rows = [{"extractor": "Codex (GPT-5.6, strict schema)", "role": "reference", "company": "—", "amount": "—",
         "lead investors": "—", "note": "audited manually: 40/40 type, company, investors"}]
if cc.get("agreement_pct"):
    a = cc["agreement_pct"]
    rows.append({"extractor": "OpenCode (GPT-5.6)", "role": "primary", "company": f"{a['company']}%",
                 "amount": f"{a['amount']}%", "lead investors": f"{a['lead_investors']}%",
                 "note": f"{cc.get('articles_compared')} articles read by both"})
for k, label in [("gemini", "Gemini Flash-Lite (free API)"), ("groq", "Groq gpt-oss-120b (free API)"),
                 ("deepseek", "DeepSeek (free)"), ("pickle", "Big Pickle (free)"), ("nemotron", "Nemotron (free)"),
                 ("mimo", "Mimo (free)")]:
    if k in me:
        rows.append({"extractor": label, "role": "fallback", "company": f"{me[k]['company']}%",
                     "amount": f"{me[k]['amount']}%", "lead investors": f"{me[k]['lead_investors']}%",
                     "note": f"{me[k]['articles']} articles compared"})
re_ = ui.load_json("rules_eval.json")
if re_:
    rows.append({"extractor": "Rule-based headline parser (no AI)", "role": "last resort", "company":
                 f"{re_['company_pct']}%", "amount": f"{re_['amount_pct']}%",
                 "lead investors": f"{re_['lead_precision_pct']}% precision",
                 "note": f"{re_['deals_compared']} deals compared; funding & financials only"})
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
st.caption("When several extractors read the same article, the merge prefers the more accurate one; lower-priority "
           "records are re-queued for the AI when it is available.")

st.subheader("2 · Rule-based checks (no AI involved)")
labels = {"headline_amount": "Amount matches the headline", "stage_size": "Round size plausible for its stage",
          "missing_core": "Core fields present", "company_in_title": "Company name found in the article"}
ui.tiles([(f"{v['pass_rate']}%", labels.get(k, k), f"{v['passed']:,} of {v['checked']:,}") for k, v in val.items()])

st.subheader("3 · Coverage: how much of the market do we capture?")
if cov:
    ui.tiles([
        (f"{cov['usd_recall_pct']}%", "of reported capital captured", f"{cov['weeks_compared']} weeks compared"),
        (f"{cov['deal_recall_pct']}%", "of reported deals captured", "small undisclosed rounds are the gap"),
    ])
    wf = ui.PROCESSED / "coverage_weekly.csv"
    if wf.exists():
        w = pd.read_csv(wf, parse_dates=["week_end"]).sort_values("week_end")
        fig = go.Figure()
        fig.add_scatter(x=w.week_end, y=w.reported_usd_m, name="published weekly total", mode="lines",
                        line=dict(color=ui.SERIES[1], width=2))
        fig.add_scatter(x=w.week_end, y=w.our_usd_m, name="captured in our database", mode="lines",
                        line=dict(color=ui.SERIES[0], width=2))
        fig.update_layout(title="Capital raised per week ($M): published vs captured", height=320,
                          hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    st.caption("Entrackr's weekly round-ups state how many deals happened and how much was raised. "
               "We parse those totals with rules and compare them with what our pipeline captured.")

st.subheader("4 · Independent manual audit")
st.markdown("""
A random sample of 40 extracted records was graded field by field against the source articles by a reviewer
that was **not** one of the extraction agents: deal type **40/40**, company **40/40**, investors **40/40**,
amount **39/40**, revenue **9/9**. The weakest field (profit/loss, 6/9) led to a pipeline fix.
""")

st.subheader("Audit trail")
con = sqlite3.connect(data.DB)
corr = pd.read_sql("SELECT rule, field, ai_value, corrected, url FROM corrections", con)
st.dataframe(corr, hide_index=True, use_container_width=True,
             column_config={"url": st.column_config.LinkColumn("source", display_text="article")})
by_src = pd.read_sql("SELECT site, COUNT(*) AS articles FROM sources GROUP BY site", con)
by_agent = pd.read_sql("SELECT agent, COUNT(*) AS deals FROM deals GROUP BY agent", con)
con.close()
c1, c2 = st.columns(2)
c1.markdown("**Articles by source**")
c1.dataframe(by_src, hide_index=True, use_container_width=True)
c2.markdown("**Deals by extracting agent**")
c2.dataframe(by_agent, hide_index=True, use_container_width=True)

st.subheader("Download the data")
d = pd.read_csv(ui.PROCESSED / "deals.csv")
st.download_button("Download all deals (CSV)", d.to_csv(index=False).encode(), "arventum_deals.csv", "text/csv")
ui.source_note()
