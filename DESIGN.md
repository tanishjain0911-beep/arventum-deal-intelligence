---
name: Deal Intelligence
description: A sourced deal book for Indian technology transactions, set as a printed research note.
colors:
  paper: "#F1F1EE"
  surface: "#FBFBF9"
  wash: "#E7E7E2"
  ink: "#1A1A16"
  ink-secondary: "#45443B"
  ink-tertiary: "#6B665A"
  hairline: "#D8D8D1"
  hairline-strong: "#B0B0A6"
  claret: "#8A2B2B"
  claret-deep: "#6B1E1E"
  claret-wash: "#F4E8E2"
  chart-ink: "#23241D"
  stone: "#948B7A"
  tan: "#C6AC97"
  gold: "#8A6520"
  gold-wash: "#F6EDD8"
  band-text: "#DADAD2"
  white: "#FFFFFF"
typography:
  display:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "clamp(40px, 7.4vw, 92px)"
    fontWeight: 500
    lineHeight: 0.97
    letterSpacing: "-0.038em"
  band-headline:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "clamp(32px, 4.6vw, 62px)"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.035em"
  section-title:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "clamp(30px, 3.4vw, 44px)"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.028em"
  figure-large:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "clamp(34px, 4.2vw, 52px)"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.035em"
    fontFeature: "\"tnum\", \"lnum\""
  lede:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "clamp(22px, 2.4vw, 29px)"
    fontWeight: 500
    lineHeight: 1.22
    letterSpacing: "-0.02em"
  figure:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "26px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
    fontFeature: "\"tnum\", \"lnum\""
  item-title:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "25px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  exhibit-title:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.012em"
  body:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  table:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    fontFeature: "\"tnum\", \"lnum\""
  label:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    letterSpacing: "0.1em"
  exhibit-number:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    letterSpacing: "0.14em"
  note:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  none: "0px"
  hairline: "1px"
  sm: "2px"
spacing:
  s1: "4px"
  s2: "8px"
  s3: "12px"
  s4: "16px"
  s5: "24px"
  s6: "32px"
  s7: "48px"
  s8: "64px"
  page-gutter: "clamp(20px, 5vw, 64px)"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0 16px"
    height: "36px"
  button-primary-hover:
    backgroundColor: "{colors.claret}"
    textColor: "{colors.white}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0 16px"
    height: "36px"
  button-ghost-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  cta:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "15px 26px"
  cta-hover:
    backgroundColor: "{colors.claret}"
    textColor: "{colors.white}"
  cta-light:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "15px 26px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0 12px"
    height: "36px"
  input-focus:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
  segmented-on:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    height: "36px"
  exhibit:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "24px"
  tag:
    backgroundColor: "{colors.wash}"
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.hairline}"
    padding: "2px 6px"
  tag-claret:
    backgroundColor: "{colors.claret-wash}"
    textColor: "{colors.claret-deep}"
    rounded: "{rounded.hairline}"
    padding: "2px 6px"
  tag-gold:
    backgroundColor: "{colors.gold-wash}"
    textColor: "{colors.gold}"
    rounded: "{rounded.hairline}"
    padding: "2px 6px"
  tooltip:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    padding: "6px 9px"
---

# Design System: Deal Intelligence

## Overview

**Creative North Star: "The Research Note"**

Deal Intelligence is set like a sell-side research note: neutral off-white paper, near-black ink, one claret accent, and rules doing the work that boxes and shadows do elsewhere. Serif carries the voice (the landing headline, section titles, exhibit titles, every headline figure); a humanist sans carries the machinery (controls, tables, labels, source lines). The reader is a numerate, skeptical banker, so the page earns trust the way a printed note does: numbered exhibits, a "Source:" line under every chart and table, figures read from the data rather than typed, and claims sized to what the data supports.

Density is report-like rather than dashboard-like. The app is a sticky ruled topbar, a numbered section spine, and a 12-column grid of exhibits on paper. The landing page is a single printed broadsheet: masthead over a heavy rule, a very large serif headline, a four-figure band with its own source line, a five-item numbered tool list, a dark closing band, and a quiet footer. Nothing glows, nothing floats, corners are square or nearly so. Motion is a short transform-only settle that never hides content.

The system was built by the Freebuff coding agent from a brief, then corrected after review. The corrections are part of the system: neutral paper, not cream; no kicker or eyebrow labels above headings; a 12px text floor; exhibit numbers and source lines everywhere; figures always live from `data/summary.json`; no decorative side stripes; transform-only motion; and a phone layout with no sideways scroll.

**Key Characteristics:**
- Neutral off-white paper with a lighter surface for plates and bands; near-black ink.
- One accent, claret, used for links, numerals, selection and hover, never as a fill for large areas.
- Heavy ink rules (2–3px) open a region; hairlines (1px) divide within it; dotted hairlines set off source lines.
- Source Serif 4 for voice and figures, Source Sans 3 for controls and data, nothing smaller than 12px.
- Every exhibit is numbered (section.item) and closes with a "Source:" line.
- Square to near-square corners (0–2px); no ambient shadows.

## Colors

A warm-neutral greyscale with a single oxblood voice and a stone second data tone.

### Primary
- **Claret** (claret): the only accent. Links, the section numeral superscript, exhibit numbers, tool-list numerals, sort arrows, focus outlines, the active spine numeral, chart-bar hover, and the hover fill of every ink button.
- **Deep Claret** (claret-deep): link hover, text on claret-wash tags.
- **Claret Wash** (claret-wash): selected table row and the claret tag background. A tint, never a panel colour for whole regions.

### Secondary
- **Stone** (stone): the second data tone. "Other" bars beside ink "focus" bars, the "other sector" legend key.
- **Tan** (tan): the range bars of range and football-field charts, behind an ink median tick.
- **Gold** (gold) with **Gold Wash** (gold-wash): a cautionary tag, and the "published total" reference line set against the book's own line. Rare.

### Neutral
- **Paper** (paper): page background in both landing and app; also the text colour on ink.
- **Surface** (surface): exhibits, the masthead, topbar, figures band, inputs, table header cells. One step lighter than paper; the only "lift" the system has.
- **Wash** (wash): row hover, active spine tab, default tag, callouts, search-result hover.
- **Ink** (ink): body text, headings, heavy rules, primary buttons, the closing band, tooltip.
- **Chart Ink** (chart-ink): default bar fill, a hair lighter than ink so bars read as data rather than type.
- **Ink Secondary** (ink-secondary): supporting prose, ledes under section titles, table labels.
- **Ink Tertiary** (ink-tertiary): metadata, axis text, uppercase labels, source lines, placeholders.
- **Hairline** (hairline): row dividers, exhibit frames, figure-band column rules.
- **Hairline Strong** (hairline-strong): the rule under a section head, ghost-button and input borders, link underlines at rest, dotted source rules.
- **Band Text** (band-text): body copy on the dark closing band.
- **White** (white): focused input fields and text on claret hover fills only.

### Named Rules
**The One Voice Rule.** Claret is the only chromatic accent in the interface. It marks what is clickable, current or numbered; it never fills a hero, a band or a card.

**The Neutral Paper Rule.** Paper is a neutral off-white (paper), not cream or bone-yellow. A warmer page reads as nostalgic; this one reads as a printed note.

**The Ink-and-Stone Data Rule.** Charts are ink with stone for the comparison series and tan for ranges; claret appears in a chart only on hover. A chart never introduces a new hue.

## Typography

**Display Font:** Source Serif 4 (with Georgia, Times New Roman, serif)
**Body Font:** Source Sans 3 (with Segoe UI, system-ui, sans-serif)

**Character:** a research house's serif for anything the reader should remember, a plain humanist sans for anything the reader operates. Both self-hosted as variable woff2 (weights 200–900), preloaded.

### Hierarchy
- **Display** (500, clamp 40–92px, 0.97, -0.038em, max 16ch, balanced): the landing headline only.
- **Band Headline** (500, clamp 32–62px, 1.0): the closing band's statement. Landing band titles such as "Five tools, one book" sit between this and the section title (500, clamp 30–46px, 1.02, -0.03em).
- **Section Title** (500, clamp 30–44px, 1.0, -0.028em; 30px on phones): the app section heading, preceded by its section numeral as a small claret superscript (serif 400, 0.46em, raised 0.75em).
- **Figure Large** (600, clamp 34–52px, tabular lining numerals; 40px on phones): the four landing figures.
- **Lede** (500, clamp 22–29px, 1.22, max 30ch; 23px on phones): one sentence that states the finding at the top of an exhibit.
- **Figure** (600, 25–26px, tabular lining): fact strips and measured-result lists.
- **Item Title** (600, 25px): landing tool names.
- **Exhibit Title** (600, 19px; 17.5px on phones): every exhibit heading, preceded by its exhibit number.
- **Body** (400, 15px app / 16px landing, 1.55; hero sub 17px at 1.6, max 62ch): prose, max 62–68ch.
- **Table** (400, 13.5px, tabular): data tables; headers are labels.
- **Label** (700, 12px, 0.07–0.14em, uppercase): buttons, nav links, table headers, field labels, figure captions, tags.
- **Exhibit Number** (sans 700, 12px, 0.14em, claret): "1.1", "2.3" ahead of the exhibit title, inline, never on its own line.
- **Note** (400, 12–13px, 1.5, ink-tertiary): source lines, sub-captions, chart axis text.

### Named Rules
**The Twelve Pixel Floor.** No text renders below 12px, including chart axis labels, tags, source lines and the spine footer. SVG charts are drawn at the exhibit's real pixel width so their 12px text stays 12px.

**The Numbered Exhibit Rule.** Section numbers are claret superscripts on the section title; exhibit numbers are claret letterspaced micro-labels inline with the exhibit title. Numbers sit in the heading, never as a separate label above it.

**The Tabular Figures Rule.** Every number in a table, figure or chart uses tabular lining numerals and is right-aligned in tables.

## Layout

**Landing.** A full-width masthead (surface, 20px vertical padding, heavy 2px ink rule below) holds the serif wordmark and two uppercase links, the second in claret. The hero sits in a 1320px column: the display headline, then a hairline-topped two-column row with the subline (live deal count in bold ink) and the actions. The figures band runs full bleed on surface between a 2px ink rule and a hairline: an uppercase caption with the live date range at right, four figures in columns divided by hairlines, then a dotted-ruled "Source:" line. The tools section is a 1320px column: title and sentence in two columns over a 2px ink rule, then five rows on hairlines (numeral 64px, name 200px, description, arrow). The closing band is full-bleed ink. The footer is a hairline-topped row of two 12px lines. Side gutter everywhere is `page-gutter`.

**App.** A grid shell: 236px spine plus fluid main, under a 60px sticky topbar (surface, heavy ink rule below) holding wordmark, search (max 520px) and two uppercase links. The spine is paper with a hairline right edge and a footer of live totals. Main content has 32/48/64px padding and a 1240px max view. Each section opens with a section head; exhibits sit in a 12-column grid with 24px gaps, spans of 12, 8/4, 7/5 or 6/6.

**Spacing rhythm.** A 4px-based scale (s1–s8: 4, 8, 12, 16, 24, 32, 48, 64). Landing vertical rhythm uses clamps (hero 48–116px top, tools 56–104px).

**Responsive.** Landing: at 1000px the hero row and tool head stack and tool rows reflow to numeral + text; at 820px figures go 2×2; at 560px figures go single column with top hairlines and the masthead wraps. App: at 1100px every exhibit spans 12 and the settle animation stops; at 780px the shell becomes one column, the spine becomes a horizontally scrolling tab row with a claret bottom marker, search drops to its own row, controls go full width, fact strips go 2×2, and secondary table columns (`wide-only`) are hidden.

### Named Rules
**The No Sideways Scroll Rule.** At 390px nothing scrolls horizontally except the spine tab row, which is a deliberate scroller. Tables lose secondary columns instead of overflowing.

**The Twelve Rows Rule.** On phones (under 780px) every table shows at most 12 rows, followed by a full-width ghost "Show all N" button.

## Elevation & Depth

The system is flat. Depth is tonal and ruled: paper is the ground, surface is the plate, wash is the pressed or hovered state, and ink rules separate regions. The masthead, topbar, figures band and section heads all announce themselves with a heavy ink rule rather than a shadow. The search results list and tooltip are the only floating layers, and they float on a 1px ink border, not a shadow.

### Shadow Vocabulary
- **Plate lip** (`box-shadow: 0 1px 0 rgba(26, 26, 22, .04)`): a near-invisible 1px lip on exhibits. The only shadow in the system.
- **Focus underline** (`box-shadow: inset 0 -2px 0 #8A2B2B`): focused selects and inputs, a claret underline drawn inside the field.

### Named Rules
**The Rules Not Shadows Rule.** Heavy rule (2px ink; 3px on the section head) opens a region, hairline (1px) divides inside it, dotted hairline sets off a source line. If a boundary needs more emphasis, use a heavier rule, never a shadow.

## Shapes

Square and near-square. Landing CTAs and the closing band have 0 radius; app buttons, inputs, segmented controls, exhibits and the tooltip use 2px; tags use 1px; chart bars use 2px. Bars in in-table meters and callouts are square. Lines are the main form element: horizontal rules, column hairlines in fact strips and the figure band, and the dotted rule above every source line.

## Components

### Buttons
- **Shape:** near-square (2px app, 0 landing), 36px tall in the app, 15px × 26px padding on the landing.
- **Primary:** ink fill, paper text, uppercase 12px label at 0.1–0.12em.
- **Hover / Focus:** fill and border turn claret, text white, in 0.16–0.18s; active presses down 1px. Focus is a 2px claret outline at 3px offset.
- **Ghost:** transparent with a hairline-strong border and ink text; hover inverts to ink fill and paper text.
- **Light CTA:** paper fill on the dark closing band; hover goes claret with white text.
- **Text link CTA:** uppercase 12px ink-tertiary label with a hairline-strong underline border that darkens to ink on hover.

### Segmented Control
- Hairline-strong frame on surface, 13px sentence-case options divided by hairlines; the selected option is ink with paper text; hover is wash.

### Cards / Containers (Exhibits)
- **Corner Style:** 2px.
- **Background:** surface on paper.
- **Shadow Strategy:** the plate lip only (see Elevation & Depth).
- **Border:** 1px hairline.
- **Internal Padding:** 24px (16px on phones).
- **Anatomy:** numbered title, optional 13px ink-tertiary sub-caption, body (scrolls horizontally inside the plate if it must), and a dotted-ruled 12px source line beginning with a bold "Source:" and ending in a link to Method.

### Inputs / Fields
- **Style:** 36px, hairline-strong border, surface fill, 14px text, 2px radius. Labels above are uppercase 12px ink-tertiary.
- **Hover:** border darkens to ink-tertiary.
- **Focus:** border goes ink, fill goes white, claret underline inside. Search uses paper fill at rest and a leading 16px stroked icon.
- **Checkbox:** claret accent colour, 15px.

### Tables
- Ink top rule, sticky surface header of uppercase 12px labels over a hairline-strong rule, 13.5px rows on hairlines, numbers right-aligned and tabular. Sortable headers darken on hover and show a claret arrow. Row hover is wash; the selected row is claret wash. Company and article names are claret links.

### Navigation
- **Landing masthead:** serif wordmark (21px, 600) left; uppercase 12px links right, ink-tertiary with an underline border on hover, the "Open the book" link in claret.
- **App topbar:** serif wordmark with an uppercase "India tech" sub-label behind a hairline divider; uppercase links whose hover underline is claret.
- **Spine:** eight numbered entries (serif numeral, 15px name, 12px one-line description). Hover is wash; active is wash, ink text at 600 and a claret numeral. On phones it becomes a single scrolling row with a 2px claret bottom marker on the active tab.

### Section Head
A 3px ink bar above, a hairline-strong rule below, the section title with its claret superscript numeral, one ink-secondary sentence (max 62ch), and the section's controls aligned bottom-right.

### Figures Band and Fact Strip
Ruled rows of figures: uppercase 12px caption, a large serif tabular figure, a 12–13px ink-tertiary qualifier underneath, columns divided by hairlines. On the landing the band ends with its own "Source:" line and every value is filled from `data/summary.json` at load; placeholders are an em dash until then.

### Measured-Results List
Rows on hairlines: what was measured (13.5px), the figure at right (serif 25px), and the comparison baseline underneath in 12px. Accuracy is always shown against a baseline.

### Charts
Hand-built SVG, drawn at the exhibit's pixel width. Ink bars (chart-ink) with stone for the comparison series, tan range bars with an ink median tick, 1.75px polylines, hairline gridlines, an ink baseline, 12px ink-tertiary axis text. Bars turn claret on hover and show an ink tooltip with tabular figures. Legends use 11 × 3px swatches.

### Tool List (landing)
Five rows on hairlines: claret serif numeral ("01"), serif name, a 15px description, and an arrow. Hover shifts the row 12px right on a surface fill and turns the arrow claret, nudging it 3px.

### Closing Band (landing)
Full-bleed ink, band headline in paper, one band-text sentence, a light CTA. Every link on the band turns white on hover or focus.

## Do's and Don'ts

### Do:
- **Do** number every exhibit (section.item) and close every chart and table with a "Source:" line linking to Method.
- **Do** read every headline figure from the data at load time; show an em dash until it arrives.
- **Do** size claims to the data ("each traced to its source", not "every round").
- **Do** open regions with a heavy ink rule and divide them with hairlines.
- **Do** keep claret for links, numerals, current state, focus and hover.
- **Do** keep all text at 12px or larger, including chart text.
- **Do** animate with transform only (a 7px settle in the app, a 16px rise on landing bands, ease cubic-bezier(0.22, 1, 0.36, 1)) and switch all motion off under prefers-reduced-motion.
- **Do** hide secondary table columns and cap lists at 12 rows with "Show all" on phones.
- **Do** make every link on the dark closing band turn white on hover and focus.

### Don't:
- **Don't** put kicker or eyebrow labels above headings; numbers live inside the heading.
- **Don't** use cream or yellowed paper; the ground is neutral (paper).
- **Don't** use a coloured side stripe as a decorative accent on panels, callouts or cards.
- **Don't** add ambient or drop shadows, glows, gradients or rounded cards.
- **Don't** introduce a second accent hue or colour charts outside ink, stone, tan (and gold for a reference series).
- **Don't** type figures into markup; they come from `data/summary.json`.
- **Don't** fade content in from invisible; a section that has not animated yet is still fully legible.
- **Don't** let any page scroll sideways at 390px.
