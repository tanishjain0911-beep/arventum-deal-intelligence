import streamlit as st

import ui

ui.page("How It Was Built", "🛠️")
st.title("🛠️ How it was built")
st.caption("One AI agent orchestrating a team of AI agents, with every step measured.")

st.graphviz_chart("""
digraph G {
  rankdir=LR; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#ffffff", color="#c3c2b7", fontname="Segoe UI", fontsize=11];
  edge [color="#898781"];
  src  [label="Public sources\\nEntrackr · Inc42 · Yahoo Finance", fillcolor="#eef4fc"];
  crawl[label="Polite crawler\\nsitemaps · adaptive rate limit\\nrobots.txt-compliant"];
  ext  [label="Multi-agent extraction\\nCodex (strict JSON schema)\\nOpenCode · free fallback models", fillcolor="#fff4e8"];
  rec  [label="Reconciliation\\nheadline-wins · plausibility\\nentity resolution · de-dup"];
  db   [label="SQLite deal database\\ndeals · investors · financials\\nsources · audit trail", fillcolor="#eef4fc"];
  qa   [label="Quality assurance\\nagent agreement · rule checks\\ncoverage audit · manual audit · tests"];
  eng  [label="Engines\\nRadar · Matchmaker · Buyers\\nPrice Finder · Market Pulse", fillcolor="#e9f7f1"];
  src -> crawl -> ext -> rec -> db -> eng; db -> qa; qa -> rec [style=dashed, label=" fixes"];
}
""")

st.subheader("The AI team")
c = st.columns(3)
team = [
    ("Claude Code · architect & lead engineer",
     "Designed the system, wrote the pipeline and models, orchestrated the other agents from the terminal, "
     "audited their output, and diagnosed every failure."),
    ("Codex CLI & OpenCode · extraction team",
     "Read thousands of deal articles in parallel and returned schema-validated records. A sample is read by both, "
     "to measure agreement."),
    ("Free models · fallback",
     "When the ChatGPT quota ran out overnight, free models (DeepSeek, Big Pickle) were benchmarked against Codex "
     "and used only after scoring ~93% agreement."),
]
for col, (h, p) in zip(c, team):
    col.markdown(f'<div class="card"><h4>{h}</h4><p>{p}</p></div>', unsafe_allow_html=True)

st.subheader("Engineering log: real problems found and fixed")
log = (ui.ROOT / "docs" / "ENGINEERING_LOG.md")
if log.exists():
    st.markdown(log.read_text(encoding="utf-8").split("\n", 2)[2])

st.subheader("What would make it stronger")
st.markdown("""
- **Arventum's own relationship data** (CRM, the founders' 700+ investor relationships): the Matchmaker would weight
  warm relationships, and a network view could suggest warm introductions.
- **A paid database** (Tracxn / Venture Intelligence / PitchBook): fuller coverage of small rounds and private valuations.
- **Weekly refresh** via a scheduled job: collect, extract, check, load, then email the Radar's top-10 to the team.
""")
ui.source_note()
