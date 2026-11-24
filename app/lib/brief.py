"""Weekly origination brief: the 'top companies to call this week' email, generated from the engines."""
import pandas as pd

from . import market, radar


def weekly_brief(scores: pd.DataFrame, focus: list, n: int = 10) -> str:
    today = pd.Timestamp.today().strftime("%d %b %Y")
    top = scores[scores.sector.isin(focus)].sort_values("probability", ascending=False).head(n)
    heat = market.sector_heat(window_m=3)
    heat = heat[(heat.deals >= 3) & heat.arventum_focus].sort_values("deal_growth_pct", ascending=False)
    asof = pd.to_datetime(scores.last_date).max().strftime("%d %b %Y")
    lines = [f"# Arventum Origination Brief - week of {today}", "", f"_Deal data as of {asof}._", "",
             f"## Top {n} companies to call (Arventum focus sectors)", ""]
    for i, (_, r) in enumerate(top.iterrows(), 1):
        last = pd.to_datetime(r.last_date).strftime("%b %Y")
        lines.append(f"**{i}. {r.company}** ({r.sector}): **{100 * r.probability:.0f}%** likelihood of a round "
                     f"in 12 months · last round {r.last_stage}, {last}")
        for s in radar.explain_row(r)[:3]:
            lines.append(f"   - {s}")
        lines.append("")
    lines += ["## Sectors heating up (last 3 months vs prior 3)", ""]
    for sector, r in heat.head(5).iterrows():
        g = "n/a" if pd.isna(r.deal_growth_pct) else f"{r.deal_growth_pct:+.0f}%"
        lines.append(f"- **{sector}**: {int(r.deals)} rounds, ${r.usd_m:,.0f}M raised (rounds {g})")
    ti = market.top_investors(months=3, n=8)
    lines += ["", "## Most active investors (last 3 months)", ""]
    lines += [f"- {r.investor}: {int(r.deals)} rounds ({int(r.led)} led)" for _, r in ti.iterrows()]
    lines += ["", "_Generated automatically by Arventum Deal Intelligence from public deal reports. "
                  "Likelihoods come from a backtested model; decision support, not investment advice._"]
    return "\n".join(lines)
