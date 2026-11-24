---
version: 1
slug: "site-index-html"
primary_target: "site/index.html"
related_targets: []
---

## Scope
Whole static site `site/` (Home summary + Market, Origination Radar, Investor Matchmaker, Buyer Mapping, Price Finder, Company Lookup, Method & Quality). Mode: Operate (working tool) with a Home that must convince the Arventum founders in seconds.

## Audience, job, constraints
Arventum's two MDs in a live demo, then bankers preparing pitches. Job: get the market, the likely investors/buyers, a value range and a company's history fast, each with its source. Constraints: static files only, data from JSON exports, honest coverage (~80% of capital, ~60% of deals), no invented claims.

## Direction contract
THESIS: The product is a living pitch book: every view is a numbered exhibit with a title, its figure and a source line. It refuses the KPI-tile dashboard of identical cards.

OWN-WORLD: White page on a cool paper-grey ground; deep navy ink (#13233B) owns the shell (top bar and section spine); one teal (#1D7A74) carries selection and the primary data series; warm grey for secondary ink; red and amber only for meaning. Source Serif 4 sets exhibit titles and big figures; Source Sans 3 sets UI and tables with tabular figures. Hairline rules, no shadows on content, 4px radii.

STORY: The visitor sees in one screen that this is a sourced, measured deal book for Indian tech; opens a section by its tab; reads exhibits; checks any figure's source; leaves believing it is credible and useful.

FIRST VIEWPORT: Navy top bar: product name left, global search (company or investor) centre, "Method" right. Left spine: numbered section tabs 1–7. Main: Exhibit 1.1, one plain-sentence headline ("5,348 Indian tech deals since 2021, each traced to its source"), with a large chart of capital raised per quarter; right column: the measured results (Radar precision vs heuristic, Matchmaker hit rate, capital coverage) as an exhibit list with footnotes. Primary action: the search field, then "Open the Radar".

FORM: The Pitch Book; position 1 on the ordered list (IMPECCABLE’S PICK); seed:f538a3cc4b1ddb5f. Signature move: exhibit numbering plus a source/footnote line under every figure, with the footnote linking to the article or method.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved
Exact chart library (hand-built SVG preferred), deploy target (Vercel vs GitHub Pages).
