# Arventum Deal Intelligence

AI-powered deal intelligence for technology investment banking, built only on public data.

## Modules
1. **Deal Database:** Indian tech funding rounds and M&A, collected from public sources, extracted by AI agents, then cleaned and quality-checked.
2. **Market Pulse:** a sector dashboard showing deal momentum, active investors, round-size benchmarks and sector heat.
3. **Origination Radar:** a backtested model that predicts which companies are likely to raise or transact next.
4. **Price Finder:** valuation benchmarking from listed comparables and precedent deals, with a football-field chart.

## Built with a multi-agent workflow
- Claude Code: architect and lead engineer
- Codex CLI and OpenCode (GPT models): parallel bulk extraction and cross-checking
- GitHub: version control and scheduled data refresh

## Structure
```
data/raw/        source files as collected (not edited)
data/processed/  cleaned tables
db/              SQLite database
pipeline/        collection, extraction, cleaning scripts
app/             web application
```
