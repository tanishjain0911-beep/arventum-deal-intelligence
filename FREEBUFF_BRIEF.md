# Brief: redesign the Deal Intelligence website

Paste this whole file into Freebuff as your first message.

## What this is

`site/` is a static website (plain HTML, CSS and JavaScript modules, no framework, no build step) about Indian technology funding deals. It is for an investment bank: founders will see it in a demo, and bankers will use it to prepare pitches. It reads all its numbers from JSON files in `site/data/`, which a Python pipeline generates.

Files:
- `site/index.html`: the page shell (top bar, left section list, main area).
- `site/css/app.css`: all styling.
- `site/js/kit.js`: helpers: data loading, number formatting, tables, and hand-drawn SVG charts (`barChart`, `hbarChart`, `rangeChart`, `lineChart`).
- `site/js/app.js`: the 8 sections (Summary, Market, Origination, Investors, Buyers, Valuation, Company, Method), the search, and the hash router (`#/market` and so on).
- `site/assets/fonts/`: self-hosted Source Serif 4 and Source Sans 3.

## The job, in two parts

### 1. A new visual look for the app (same content)
Give the 8 sections a fresh, distinctive, premium visual style: colours, typography, layout, chart styling and motion. It should feel like a top investment bank's research product, not a generic dashboard template. Every section, exhibit, table, chart, number, control and tool must still be there and still work.

### 2. A landing page
Add a landing page that introduces the project before someone opens the tool:
- Put it at `site/index.html`, and move the current app to `site/app.html` (update every link; the app keeps its `#/section` routes, so `app.html#/radar` opens the Origination section).
- It should say in one clear headline what this is, show 3 or 4 real headline figures, explain the five tools in a sentence each, and end with a clear button to open the app.
- Real figures only: read them from `site/data/summary.json` at load time (for example `tables.deals`, `companies`, `investors`, `radar.summary.mean_precision_top100`, `matching.model_hit_rate["10"]`). Never type a number into the HTML.

## Hard rules (do not break these)

1. **Do not edit anything in `site/data/`.** It is generated.
2. **Do not change the maths.** In `app.js` these functions must stay exactly as they are: `rankInvestors`, `valueCompany`, `downloadBrief`. In `kit.js`, keep `quantile`, `median` and the formatting functions (`usd`, `inr`, `pct`, `date`, `month`). Restyling the charts is fine; changing what they compute is not.
3. **No invented content.** No testimonials, client logos, user counts, awards or claims that are not in the data. Do not use Arventum's logo or imitate its brand; the product is called "Deal Intelligence".
4. **Keep a source line under every chart and table** (the small "Source: …" text). It is how readers know where a figure comes from.
5. **Static only.** No React, no npm packages, no build step, no CDN links: the site is deployed as plain files. If you want an animation library, don't; use CSS transitions and `IntersectionObserver`.
6. **Avoid the "AI-made" look:** no purple/blue gradients, no gradient text, no glowing or coloured shadows, no glassmorphism, no emoji or icon fonts used as decoration, no rows of identical stat cards, no "eyebrow" labels above every heading, no stock phrases like "Unlock insights" or "Supercharge".
7. **Must work on a phone (390px wide)** with no sideways scrolling, and with readable chart text.
8. **Accessible:** text contrast at least 4.5:1, visible keyboard focus, and respect `prefers-reduced-motion`.

## How to check your work

From the project folder:

```
python analysis/serve_site.py
```

Then open http://localhost:8600 (landing) and http://localhost:8600/app.html#/summary (app). Click through all 8 sections, try the Investors and Valuation inputs, and the search box.

Screenshot every section at desktop and phone widths (prints `overflow=True` if a page scrolls sideways):

```
python analysis/screenshot_site.py .impeccable/review/freebuff
```

Note: `screenshot_site.py` opens `http://localhost:8600/?r=…#/<section>`. After moving the app to `app.html`, change that URL in the script to `http://localhost:8600/app.html?r=…#/<section>`.

## When you are done

Commit on the current branch (`freebuff-redesign`) with a clear message. Do not push and do not touch the `main` branch.
