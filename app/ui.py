"""Shared look & feel: palette (validated reference palette), Plotly template, page chrome, helpers."""
import json
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

# Validated categorical palette (fixed order, never cycled) and chrome, light mode
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
NAVY = "#0d1b2a"

pio.templates["arventum"] = go.layout.Template(layout=go.Layout(
    font=dict(family='system-ui, -apple-system, "Segoe UI", sans-serif', color=INK2, size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=SURFACE, colorway=SERIES,
    xaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED)),
    yaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED)),
    hoverlabel=dict(bgcolor="white", font=dict(color=INK)),
    margin=dict(l=10, r=10, t=64, b=10), bargap=0.25,
    title=dict(x=0, xanchor="left", y=0.98, yanchor="top", font=dict(color=INK, size=15)),
    legend=dict(orientation="h", y=1.0, yanchor="bottom", x=1, xanchor="right", font=dict(color=INK2)),
))
pio.templates.default = "arventum"

CSS = f"""
<style>
  .block-container {{ padding-top: 1.6rem; max-width: 1250px; }}
  h1, h2, h3 {{ color: {NAVY}; letter-spacing: -0.01em; }}
  .hero {{ background: {NAVY}; color: #f0efec; border-radius: 14px; padding: 28px 32px; margin-bottom: 18px; }}
  .hero h1 {{ color: #ffffff; margin: 0 0 6px 0; font-size: 2.0rem; }}
  .hero p {{ color: #c3c2b7; margin: 0; font-size: 1.02rem; }}
  .tile {{ background: #ffffff; border: 1px solid rgba(11,11,11,0.10); border-radius: 12px; padding: 14px 16px; }}
  .tile .v {{ font-size: 1.7rem; font-weight: 650; color: {INK}; line-height: 1.15; }}
  .tile .l {{ font-size: 0.82rem; color: {INK2}; margin-top: 2px; }}
  .tile .s {{ font-size: 0.76rem; color: {MUTED}; margin-top: 4px; }}
  .card {{ background: #ffffff; border: 1px solid rgba(11,11,11,0.10); border-radius: 12px; padding: 16px 18px;
           height: 100%; }}
  .card h4 {{ margin: 0 0 6px 0; color: {NAVY}; }}
  .card p {{ margin: 0; color: {INK2}; font-size: 0.9rem; }}
  .pill {{ display:inline-block; background:#eef4fc; color:#1c5cab; border-radius: 999px; padding: 2px 10px;
           font-size: 0.75rem; margin: 2px 4px 2px 0; }}
  .note {{ color: {MUTED}; font-size: 0.82rem; }}
  .signal {{ margin: 2px 0; color: {INK2}; }}
</style>
"""


def page(title: str, icon: str = "📈"):
    st.set_page_config(page_title=f"{title} · Arventum Deal Intelligence", page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def tiles(items):
    """items: list of (value, label, sub) -> a row of stat tiles."""
    cols = st.columns(len(items))
    for c, (v, l, s) in zip(cols, items):
        c.markdown(f'<div class="tile"><div class="v">{v}</div><div class="l">{l}</div>'
                   f'<div class="s">{s or "&nbsp;"}</div></div>', unsafe_allow_html=True)


def usd(x, digits=1):
    if x is None or x != x:
        return "—"
    if abs(x) >= 1000:
        return f"${x / 1000:,.{digits}f}B"
    if abs(x) >= 1:
        return f"${x:,.{digits}f}M"
    return f"${x * 1000:,.0f}K"


def load_json(name: str) -> dict:
    f = PROCESSED / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def source_note():
    st.markdown('<p class="note">Built only from public sources (Entrackr, Inc42, Yahoo Finance). Every deal links '
                'to the article it came from. Decision support for bankers, not investment advice.</p>',
                unsafe_allow_html=True)
