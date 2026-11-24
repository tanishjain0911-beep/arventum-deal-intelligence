---
name: Deal Intelligence
description: A sourced, measured deal book for Indian technology transactions, set as a living pitch book.
colors:
  navy: "#13233B"
  navy-raised: "#1C3050"
  navy-rule: "#2A4166"
  navy-ink: "#C9D3E2"
  navy-mute: "#8C9BB3"
  ground: "#E9ECF0"
  page: "#FFFFFF"
  ink: "#13233B"
  ink-secondary: "#3B4658"
  ink-tertiary: "#5A6475"
  rule: "#DDE1E7"
  rule-strong: "#C4CAD3"
  wash: "#F5F7F9"
  teal: "#1D7A74"
  teal-deep: "#155C57"
  teal-wash: "#E2F0EE"
  teal-soft: "#9CCBC6"
  series-other: "#A8B3C4"
  amber: "#A86412"
  amber-wash: "#FBF0DF"
  red: "#B42318"
  red-wash: "#FBE9E7"
typography:
  section-title:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "34px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  lede:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "30px"
    fontWeight: 500
    lineHeight: 1.22
    letterSpacing: "-0.02em"
  exhibit-title:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  figure:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "22px"
    fontWeight: 600
    lineHeight: 1.1
    fontFeature: "\"tnum\", \"lnum\""
  body:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  table:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "\"tnum\", \"lnum\""
  label:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    lineHeight: 1.45
  chart-text:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "11.5px"
    fontWeight: 400
rounded:
  tag: "3px"
  r: "4px"
spacing:
  s1: "4px"
  s2: "8px"
  s3: "12px"
  s4: "16px"
  s5: "24px"
  s6: "32px"
  s7: "48px"
  s8: "64px"
components:
  button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.page}"
    rounded: "{rounded.r}"
    padding: "0 16px"
    height: "36px"
  button-primary-hover:
    backgroundColor: "{colors.navy-rule}"
    textColor: "{colors.page}"
  button-ghost:
    backgroundColor: "{colors.page}"
    textColor: "{colors.navy}"
    rounded: "{rounded.r}"
    padding: "0 16px"
    height: "36px"
  input-field:
    backgroundColor: "{colors.page}"
    textColor: "{colors.ink}"
    rounded: "{rounded.r}"
    padding: "0 12px"
    height: "36px"
  search-field:
    backgroundColor: "{colors.navy-raised}"
    textColor: "{colors.page}"
    rounded: "{rounded.r}"
    height: "36px"
  segmented-on:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.page}"
    height: "36px"
  section-tab:
    textColor: "{colors.navy-ink}"
    rounded: "{rounded.r}"
    padding: "10px 24px"
  section-tab-active:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.navy}"
  exhibit:
    backgroundColor: "{colors.page}"
    textColor: "{colors.ink}"
    rounded: "{rounded.r}"
    padding: "24px"
  detail-panel:
    backgroundColor: "{colors.teal-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.r}"
    padding: "16px 24px"
  tag:
    backgroundColor: "{colors.wash}"
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.tag}"
    padding: "1px 7px"
  tag-teal:
    backgroundColor: "{colors.teal-wash}"
    textColor: "{colors.teal-deep}"
    rounded: "{rounded.tag}"
    padding: "1px 7px"
  tooltip:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.page}"
    rounded: "{rounded.r}"
    padding: "6px 9px"
---

# Design System: Deal Intelligence

## Overview

**Creative North Star: "The Pitch Book"**

The product is a living pitch book. Every view is a numbered section of a bound deal book, and every unit of content inside it is a numbered exhibit: a serif title with its number, the figure (chart, table, or ruled figure row), and a source line beneath it that names where the number came from and links to the article or the method. The reader is a senior banker who already knows what a pitch book looks like; the system borrows that document's discipline (numbering, hairline rules, sourced figures, a single navy ink) rather than the visual vocabulary of a SaaS dashboard.

Density is high but ordered. White exhibit pages sit on a cool paper-grey ground, framed by a deep navy shell (top bar and a left spine of numbered section tabs). Depth is conveyed by ground against page and by hairlines, never by shadow on content. Colour is spent on meaning: navy for ink and structure, one teal for numbering, links, selection and the primary data series, warm amber and red only when a value needs a warning. Motion is minimal: one short fade-and-rise as a view enters, and quick state transitions on controls.

The world refuses the KPI-tile dashboard of identical floating cards. Summary figures are themselves numbered exhibits (2.0, 6.0, 7.0) with a ruled figure row and a source line.

**Key Characteristics:**
- Numbered exhibits (section.exhibit, e.g. 2.4) with a serif title and a source line under every figure.
- Navy shell (top bar plus numbered spine) around white pages on a cool grey ground.
- Serif (Source Serif 4) for titles and big figures; sans (Source Sans 3) for UI and tables, with tabular lining figures everywhere numbers align.
- Hairline rules, 4px corners, no shadows on content.
- Hand-built SVG charts sized to their container, text at fixed CSS sizes.

## Colors

A restrained banker's palette: one navy ink, one teal accent, cool neutrals, and two warning hues held in reserve.

### Primary
- **Deep Ledger Navy** (navy): the ink of the whole system. Top bar and spine background, section and exhibit titles, the lede, big figures, primary buttons, the active segmented option, the median tick on range charts, the 2px rule under each section head, the tooltip.
- **Raised Navy** (navy-raised) and **Navy Rule** (navy-rule): the search field and tab hover inside the shell; borders and dividers inside the shell, and the primary button's hover.
- **Shell Ink** (navy-ink) and **Shell Mute** (navy-mute): tab labels and secondary text on navy; placeholder text and tab numerals at rest.

### Secondary
- **Exhibit Teal** (teal): exhibit and section numbers, links, focus rings, the active tab's numeral, selected-row and sort-arrow marks, and the primary data series in every chart. **Teal Deep** (teal-deep) is its hover/pressed state and the text of teal tags. **Teal Wash** (teal-wash) fills selected rows, search-result hover, detail panels and the input focus halo. **Teal Soft** (teal-soft) is the interquartile bar on range charts, the detail-panel border, the text selection and the brand subline.
- **Comparison Slate** (series-other): the secondary series in bar charts ("other sector") and its legend swatch.

### Tertiary
- **Ochre Warning** (amber, amber-wash): meaning only. Amber tags and the "published weekly total" comparison line on the coverage chart.
- **Signal Red** (red, red-wash): meaning only; reserved for errors and negative signals.

### Neutral
- **Paper Ground** (ground): the page behind exhibits, and the active tab, which appears cut from the ground into the spine.
- **Page White** (page): exhibit surfaces, table headers, inputs.
- **Ink** (ink), **Secondary Ink** (ink-secondary), **Tertiary Ink** (ink-tertiary): body text; prose and labels; captions, source lines, axis text, muted columns.
- **Hairline** (rule) and **Strong Hairline** (rule-strong): exhibit borders, table row rules, source-line rules; table header rule, input and ghost-button borders.
- **Wash** (wash): row hover, neutral tags, callouts.

### Named Rules
**The One Ink Rule.** Navy is the only ink for titles, ledes and figures. The lede is navy, never teal.

**The Teal Is Earned Rule.** Teal marks numbering, links, selection and the primary data series. It never fills a surface larger than a selected row or a detail panel wash.

**The Meaning-Only Rule.** Amber and red appear only when a value carries a warning or a contrasting published figure; never as decoration or category colour.

## Typography

**Display Font:** Source Serif 4 (with Georgia, serif), self-hosted variable woff2.
**Body Font:** Source Sans 3 (with Segoe UI, system-ui, sans-serif), self-hosted variable woff2.

**Character:** A research-report pairing: a sturdy transitional serif carries titles and the numbers that matter, a quiet humanist sans carries every control, table and caption.

### Hierarchy
- **Section title** (600, 34px, 1.1, -0.02em; 28px under 780px): the view's h1, prefixed by its teal section number.
- **Lede** (500, 30px, 1.22, -0.02em, max 30ch; 24px under 780px): one plain-sentence headline inside the lead exhibit, navy.
- **Exhibit title** (600, 19px, 1.25, -0.01em): every exhibit h2, prefixed by its teal exhibit number.
- **Figure** (600, 22px in figure rows, 24px in results lists; tabular lining): the numbers a banker would quote.
- **Body** (400, 15px, 1.5): running text; prose capped at 68–70ch.
- **Table** (400, 14px; headers 600, 12.5px, tertiary ink): all lists and tables, tabular figures, numbers right-aligned.
- **Label** (600, 12.5px): field labels; source lines and captions use the same 12.5px at 400 in tertiary ink with a bold lead word ("Source:").
- **Chart text** (400, 11.5px axes; 12.5px category labels; 12px values): fixed CSS sizes regardless of chart width.

### Named Rules
**The Serif Means Quote It Rule.** Serif is for titles and quotable figures only; controls, tables and captions stay in sans.

**The Tabular Figures Rule.** Any number that sits in a column or beside another number uses tabular lining figures.

## Layout

A fixed shell: a 56px navy top bar (brand, centred search up to 560px, "Method & quality" link) over a two-column grid with a 232px navy spine of numbered section tabs and a scrolling main column. Main pads 32px/48px and centres views at a 1240px maximum.

Each view opens with a section head (title and one-line description left, controls right, closed by a 2px navy rule), followed by a 12-column grid with a 24px gap. Exhibits span 12, 8, 7, 6, 5 or 4 columns; grid items align to start, so exhibits keep their natural height instead of stretching to match neighbours.

Spacing steps on a 4px base: 4, 8, 12, 16, 24, 32, 48, 64. Exhibits pad 24px; source lines sit 16px below the figure behind a hairline with 12px above the text.

Responsive behaviour:
- **Under 1100px:** every exhibit spans the full 12 columns; main pads 24px.
- **Under 780px:** the shell stacks; the top bar becomes static with search full-width; the spine becomes a horizontal scrolling row of numbered tabs without descriptions; figure rows go to two columns; secondary table columns (marked wide) are hidden; tables and lists cap at 12 rows with a full-width "Show all N" ghost button; inline bar graphics drop to numbers; controls fill the width.
- **Print:** shell hidden, exhibits avoid page breaks.

Charts are rendered at the exhibit's measured width (charts take a width option) so their text keeps its CSS size. Horizontal-bar and range-chart label gutters size from the longest label (capped at 55% of the width); axis thinning on range and log axes always keeps both end ticks.

## Elevation & Depth

Flat. Depth comes from two surfaces (white page on cool grey ground) and hairline borders; content never casts a shadow. Shadows exist only on things that float above the page and disappear when dismissed.

### Shadow Vocabulary
- **Popover** (`box-shadow: 0 12px 32px rgba(0, 0, 0, .14)`): the search results dropdown.
- **Tooltip** (`box-shadow: 0 6px 18px rgba(0, 0, 0, .2)`): the navy chart tooltip.
- **Focus halo** (`box-shadow: 0 0 0 3px` teal-wash): input and select focus, paired with a teal border.

### Named Rules
**The Paper Not Glass Rule.** Exhibits, panels, tables and callouts are flat paper with a hairline. Only transient overlays may lift.

## Shapes

Quietly squared. One radius (4px) for exhibits, inputs, buttons, segmented controls, detail panels, callouts, the dropdown and tooltip; 3px for tags; 2px on chart bars and legend swatches. The active spine tab rounds only its left corners, so it reads as a tab cut from the ground into the navy. Borders are 1px hairlines; the only heavy line is the 2px navy rule under each section head.

## Components

### Buttons
Compact and firm.
- **Shape:** 4px radius, 36px tall, 16px side padding, 14px 600 sans.
- **Primary:** navy fill, white text; hover lifts to navy-rule; press scales to 0.97.
- **Ghost:** white fill, navy text, strong-hairline border; hover borders in navy. Also used for "Show all N".
- **Segmented control:** 36px bordered group, white options, the active one navy with white text.

### Exhibit (signature component)
The unit of the whole system.
- **Structure:** a number and serif title (`1.2 Measured, not claimed`), an optional tertiary-ink sub line, the body (chart, table, figure row, list or prose, horizontally scrollable if needed), then a source line.
- **Surface:** page white, 1px hairline, 4px radius, 24px padding, no shadow.
- **Source line:** 12.5px tertiary ink above a hairline, led by a bold "Source:", ending in a link to the article or Method. Every exhibit carries one.

### Figure row
The replacement for KPI tiles: a definition list inside a numbered exhibit, four columns between a strong hairline above and a hairline below, separated by vertical hairlines. Each cell has a 12.5px tertiary label and a 22px serif navy figure, with an optional small sans qualifier beneath. Two columns under 780px.

### Results list
A ruled list of measured claims: description left in secondary ink, a 24px serif figure right, and a 12.5px comparison line ("vs 14% for the … rule") spanning beneath.

### Tables
- 14px sans, sticky white header (12.5px 600 tertiary ink) over a strong hairline, hairline row rules, 8px/10px cell padding.
- Numbers right-aligned, tabular, no wrap. Sortable headers show a teal arrow.
- Row hover in wash; selected row in teal wash; clickable rows show a pointer.
- Up to 560px tall with internal scroll on desktop; under 780px, wide columns hide and rows cap at 12 behind "Show all N".

### Inputs / Fields
- **Style:** 36px, white, strong-hairline border, 4px radius, 14px text; labels stacked above in 12.5px 600 tertiary ink.
- **Hover:** border darkens to tertiary ink.
- **Focus:** teal border plus a 3px teal-wash halo.
- **Checkbox:** teal accent colour.

### Navigation
- **Top bar:** navy, serif brand ("Deal Intelligence" in white 19px 600 with a teal-soft subline), raised-navy search field that turns white on focus, quiet shell-ink links.
- **Spine tabs:** a serif numeral (shell mute, teal when active) and a label with a 12.5px description. Hover raises to navy-raised; the active tab takes the ground colour and navy text, indented 12px and rounded on the left only. Under 780px: a horizontal scrolling row, numerals and labels only.

### Charts
Hand-built SVG: teal bars (slate for the comparison series), 2px bar corners, hairline gridlines, a strong-hairline baseline, tertiary-ink axis text. Range charts draw the interquartile band in teal soft with a 3px navy median tick. Line charts use 1.75px strokes. Hover shows the navy tooltip; bars deepen to teal-deep.

### Tags, detail panel, callout
- **Tag:** 12px, 3px radius, wash fill with hairline; teal and amber variants on their washes without a border.
- **Detail panel:** teal-wash fill, teal-soft border, serif 18px heading; shows the selected row's reasoning.
- **Callout:** wash fill, hairline, 14px secondary ink, for a single explanatory sentence.

## Do's and Don'ts

### Do:
- **Do** number every exhibit (section.index) and give it a serif title and a source line that links to the article or the Method view.
- **Do** present summary figures as a numbered exhibit with a ruled figure row (as in 2.0, 6.0, 7.0), not as tiles.
- **Do** render charts at the container's measured width with fixed CSS text sizes, and size horizontal label gutters from the longest label.
- **Do** keep both end ticks when thinning a range or log axis.
- **Do** align grid items to start so exhibits keep their natural height.
- **Do** mark secondary table columns as wide so they hide under 780px, and cap mobile lists at 12 rows with a "Show all N" button.
- **Do** set every aligned number in tabular lining figures, right-aligned.
- **Do** keep the lede and all titles in navy; spend teal only on numbering, links, selection and the primary series.

### Don't:
- **Don't** build strips of identical KPI tile cards.
- **Don't** put a shadow on an exhibit, panel, table or callout; shadows belong only to the dropdown and tooltip.
- **Don't** use amber or red for anything but a warning or a contrasting published figure.
- **Don't** set a figure, chart or table without a source line.
- **Don't** stretch grid items to equal heights.
- **Don't** scale chart text with the SVG viewBox; charts take an explicit width instead.
- **Don't** use a radius other than 4px (3px tags, 2px chart marks), or a thicker line than the 2px section rule.

## Open opportunities (not yet part of the system)

Raised in the finish review and deliberately left unadopted; record here so they are not mistaken for rules:
- The word "Exhibit" before each number, with a running page head and folio.
- Footnote markers tied to individual figures, rather than one source line per exhibit.
- A bound-tab treatment for the spine.
- Chart annotations (labelled events or callouts on the figure).
- One authored motion moment beyond the view-enter fade.
