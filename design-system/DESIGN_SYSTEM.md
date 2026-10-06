# Evidence Folio 2.0

The design system of the DLMP AI Policy Explorer. It was extracted from the
standalone page (`source/DLMP_AI_Policy_Explorer.original.html`) and the
`AI_Policy_Workflow` film, then refined into a quiet, scholarly system for an
offline faculty research tool.

- Tokens: [`tokens.json`](tokens.json) (W3C design-token format)
- Stylesheet: [`explorer.css`](explorer.css), inlined into the page by `tools/apply_design.py`
- Presentation script: [`explorer-enhancements.js`](explorer-enhancements.js)
- Checks for this pass: [`design-pass-checks.json`](design-pass-checks.json), produced by `tools/verify_design.cjs`

## What was extracted

| Source | Carried forward |
| --- | --- |
| Page stylesheet | UW Purple `#4b2e83`, UW Gold `#b7a57a`, ink `#23202b`, muted `#57515f`, paper `#faf8f4`, line `#d3ccdc`, soft `#f0ebf6`, control border `#776d83`; Georgia display face; 44 px targets; 4/6/8 px radii; the ink-outline-plus-gold-halo focus ring; 1000 and 650 px breakpoints |
| Workflow film | Numbered eyebrows ("01 · Public source collection"); serif headlines over a gold hairline; old-style numerals; concentric-ring ornament; large faint watermark words; solid purple callout blocks; the three modes *Independent competence*, *Supported work* and *Critical oversight* with their one-line descriptions |

## Principles

1. **Evidence first.** Quotations are set in the book face with a hanging mark; locators and dates are set in mono as records. Everything else steps back.
2. **Say who is speaking.** Four layer marks keep institutional evidence, international context, analyst interpretation and draft proposals visually distinct.
3. **Shape before color.** Stance is carried by glyph shape, so nothing depends on hue alone and no mark implies a score or ranking.
4. **Quiet chrome.** Hairlines instead of boxes, little shadow, gold used as an accent rather than a fill.
5. **Offline by construction.** System fonts only; every icon is inline CSS or a data URI permitted by the page's content security policy.

## Color

UW Purple and UW Gold stay exactly as the chair specified. Ramps share their
OKLCH hue (295 and 88), so tints read as one family.

| Token | Hex | Role |
| --- | --- | --- |
| purple-950 | `#1b0d35` | Footer field |
| purple-900 | `#2a164f` | Deep band; UW Gold text is AA here |
| purple-800 | `#392068` | Hover, pressed |
| **purple-700** | `#4b2e83` | **UW Purple** |
| purple-600 | `#6246a0` | Secondary marks |
| purple-300 | `#b9b0da` | Captions on dark purple |
| purple-200 | `#d8d4ec` | Selection; text on purple-900 |
| purple-100 | `#f0ebf6` | Tags, chip hover, agenda panel |
| purple-50 | `#f7f6fc` | Filter rail, date rails, selected tiles |
| gold-900 | `#534627` | Text on the draft hatch |
| gold-800 | `#685933` | Gold labels on light grounds |
| gold-700 | `#847348` | Large numerals, quotation marks |
| **gold-500** | `#b7a57a` | **UW Gold** |
| gold-300 | `#dbcdab` | Small gold text on UW Purple |
| gold-200 / 100 | `#e9dfc7` / `#f6f0e1` | Hatch stripe / interpretation wash |
| ink, ink-2, muted, subtle | `#23202b` `#3a3542` `#57515f` `#6c6676` | Text, strongest to quietest |
| border, line, hairline | `#776d83` `#d3ccdc` `#e5e1eb` | Controls, dividers, card rings |
| paper, white | `#faf8f4` `#ffffff` | Ground, cards |

### Measured contrast

| Pair | Ratio | Use |
| --- | --- | --- |
| Ink on paper | 15.08 | Body |
| Muted on paper | 7.21 | Secondary text |
| Subtle on paper | 5.21 | Floor for captions |
| UW Purple on paper | 9.81 | Links, labels |
| Gold 800 on paper | 6.46 | Gold labels |
| White on UW Purple | 10.41 | Hero, buttons, table header |
| Gold 300 on UW Purple | 6.61 | Small gold text in the hero |
| UW Gold on Purple 900 | 6.54 | Gold text in deep bands |
| UW Gold on UW Purple | 4.30 | 24 px and larger only (the italic *together*) |
| UW Gold on white | 2.42 | Rules and ornament only, never text |
| Border on white | 4.88 | Control outlines (3:1 required) |

## Type

| Role | Face | Size / line | Notes |
| --- | --- | --- | --- |
| Display XL | Display | clamp(46–94) / 0.98 | −2% tracking; the hero question |
| Display L | Display | clamp(34–52) / 1.06 | Section headlines, max 22ch |
| Display M | Display | 30 / 1.2 | Synthesis findings, agenda title |
| Title | Display | 25 / 1.24 | Source, scenario titles |
| Quote | Display | 17 / 1.6 | Evidence, hanging gold-700 mark |
| Lead | UI | 19 / 1.58 | Section introductions |
| Body | UI | 16 / 1.625 | |
| Small, caption | UI | 14, 13 | Muted, subtle |
| Eyebrow | UI | 12, 700, +14% caps | Section kickers |
| Record | Mono | 12.5 | Dates, locators, versions |
| Figure | Display | 64, old-style | Hero statistics, gauges |

Display stack: Iowan Old Style → Palatino Linotype → Palatino → Book Antiqua → Georgia.
Interface stack: system UI (SF Pro, Segoe UI). Mono stack: SF Mono, Cascadia Mono, Menlo, Consolas.

## Components

**Stance marks** (`.st .st-{stance}`). Circles describe latitude of use, squares a firm rule, dashed outlines what is unresolved. Each mark describes one passage, for its stated actor, activity and conditions, and always appears next to the word or inside a link whose text or hidden label gives it.

| Mark | Stance |
| --- | --- |
| filled circle | encouraged |
| open circle | permitted |
| half-filled circle | conditional |
| circle with bar | discouraged |
| filled square | required |
| crossed square | prohibited |
| dashed circle | unclear |
| short dash | not coded (no selected passage; not silence, permission or disagreement) |

**Layer marks.** *Public position* (solid purple), *External context* (purple outline), *Analyst interpretation* (gold wash with a diamond), *Draft proposal* (gold hatch).

**Citation chip** (`.evlink`). White chip, hairline ring, stance mark, institution, gold-700 arrow. Hover: purple-100 fill with a purple ring. Inside the matrix the chip drops its ring and reads as a token.

**Coverage instrument.** Two rows of 17 ticks: filled for analyzed public positions, dashed for the chair's original collection. The opening label states coverage in words, and supplements never fill a tick.

**Source ledger card.** Meta column (institution, date chip, authority) beside title, summary and tags. Unknown dates use a dashed chip. The disclosure line carries the card's passage stances as a strip. Opened, it shows scope, a date rail (every stated date in order, retrieval last, unknown dates listed in words) and passages in a two-up grid.

**Evidence passage.** Theme, status badge and stance; source line; quotation; mono locator; an *Interpretation* panel in the gold wash; conditions; outbound link. A focused or targeted passage gets a purple ring with a gold halo.

**Tension callout.** Two quotations side by side with a gold ≠ divider, used only where the ledger records a genuine difference. The authority warning sits beside it on Purple 900.

**Competency lanes.** Three columns, *i–iii*, one per mode, each headed by its label, title and description; draft proposals stack beneath. An empty lane says so.

**Scenario tiles.** Radio choices as 48 px tiles; the checked tile gets a 2 px purple ring on purple-50. The rationale panel uses a gold top rule; before a choice it is a quiet italic prompt.

**Agenda sheet.** Ruled 26 px lines in a white sheet on the purple-100 panel.

**Ledgers.** Verification rows with a status mark (filled check, half, dashed) and a value; never summarized as one green badge.

## Layout, motion, print

- Container 1280 px; gutter clamp(20–40 px); sections 120 px apart (72 px on phones).
- Sticky section nav with numbered links; the link for the section in view gets `aria-current="location"`.
- Filter rail sticks beside the list on wide, tall screens and stacks above it elsewhere.
- Hover 160 ms ease-out; disclosure 240 ms; both off under reduced motion.
- Print opens every disclosure (and restores them afterwards), drops navigation and ornament, keeps stance marks and ticks, and lets long cards break between passages.

## Accessibility

- Focus: 3 px ink outline at 4 px offset with a 6 px gold halo (white outline on purple grounds). Focused elements are never hidden under the sticky nav (`scroll-padding-top: 76px`, `scroll-margin-top` on passages).
- Targets of 44 px or more for buttons, fields, nav links and summaries; 32 px citation chips sit inside text blocks.
- Decorative rings and watermark words are `aria-hidden`; quotation marks are generated with empty alternative text.
- Disclosures stay native `<details>`; filters keep native `<select>` and `<input>`.
- What was checked for this pass is listed in `design-pass-checks.json` and in the page's methods section. Screen readers, Safari, Firefox and physical devices were not tested.

## Rebuilding

```sh
python3 tools/apply_design.py                                  # source/…original.html → DLMP_AI_Policy_Explorer.html
NODE_PATH="$(npm root -g)" node tools/verify_design.cjs        # needs Playwright + Chromium
```

The transform asserts every anchor it relies on and refuses to write if the
embedded page data or the page's main script would change by a single byte.

## Content left untouched

The visual pass did not edit analysis text. Some analyst-written strings in the
EU card are missing spaces in the source data ("Article113", "AnnexIII",
"December2 2027"); they appear exactly as they do in the original page.
