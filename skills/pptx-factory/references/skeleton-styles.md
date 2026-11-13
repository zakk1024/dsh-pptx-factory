# Skeleton × style binding table (G2)

Two separate layers compose every page — **skeleton** (layout frame, chosen here) and **style** (visual language). Pick skeleton first, then bind a style code that the runtime actually has (see fake-mode rule in SKILL.md step 4).

## Skeleton library — 5 families × 4 variants = 20

| id | family | variant | frame | per-page budget |
|----|--------|---------|-------|------------------|
| cov-1 | cover | full-bleed visual + 2-line title over bottom-left safe box | ≤1 anim; elements ≤4 |
| cov-2 | cover | split: left title block, right hero image (≥55% width image) | ≤2 anim |
| cov-3 | cover | centred title + rule-line data row | ≤2 anim; one count-up max |
| cov-4 | cover | dark title bar + image strip below (strip height ≤42%) | ≤2 anim |
| sec-1 | section divider | full colour block + index number | ≤2 anim |
| sec-2 | section divider | half-height hero + title below image (title sits outside the image zone) | ≤2 anim; title ≤10 chars, body ≤7 lines |
| sec-3 | section divider | rule-line + centred title | ≤2 anim |
| sec-4 | section divider | dark background + single highlight word (≤12 chars, auto-fit off) | ≤2 anim |
| con-1 | concept | one statement + supporting chart to the right (chart band top ≈48%) | ≤2 anim (count-up OR bar-grow) |
| con-2 | concept | text block + supporting icon (icon sits inside the text box) | ≤2 anim |
| con-3 | concept | two-column compare (2 statements + 2 charts) | ≤2 anim |
| con-4 | concept | case study: left copy, right image (image caption sits outside the image) | ≤2 anim; text block area ≥25% |
| flo-1 | flow | numbered 3-step arrow chain | ≤2 anim (reveal per step OK as one group) |
| flo-2 | flow | central hub + 4 satellites (hub ≤40%) | ≤2 anim |
| flo-3 | flow | single chain on a dark ground (single accent colour only) | ≤2 anim |
| flo-4 | flow | circular flow (steps ≤4) | ≤2 anim |
| dat-1 | data | KPI top band (3–4 tiles) + table/list below | ≤2 anim; one count-up max |
| dat-2 | data | left panel chart (top band ≤48%) + right chart (4-col grid, 12px gutters) | ≤2 anim |
| dat-3 | data | full-chart hero + caption under the chart (caption outside frame) | ≤2 anim |
| dat-4 | data | comparison bar pair (2 bars + delta label) | ≤2 anim (bar-grow only) |
| qz-1 | quiz | question + options, answer revealed on click (reveal preset) | ≤2 anim |
| qz-2 | quiz | scenario + options (one stem ≤80 chars) | ≤2 anim |
| qz-3 | quiz | hint + options (hint above options, gap 16px) | ≤2 anim |
| qz-4 | quiz | answer recap: answer + explanation side by side | ≤2 anim |

Rules that bind the table:
- A quiz page is its own skeleton (qz-*), never appended to a content page's tail.
- One chart per page unless the skeleton explicitly carries two (dat-2, con-3).
- The animation budget column is the default; G5 reflow requests override per page, still capped by the global rule (see g4-gates.md).

## Style codes per runtime

- dsh-ppt themes (always available): `swiss` Swiss Pulse / `velvet` Velvet Standard / `data` Data Drift (charts-first, cool palette, colourblind set required) / `soft` Soft Signal / `bold` Maximalist Type (120/72/28 pt ladder).
- pptwise layers (if the skill is installed): `hero` hero-gradient + glow / `editorial` asymmetric editorial / `flat` flat technical (grid + colourblind-safe).
- deck-studio image styles (only when non-fake): BIZ/FYI/JPN/EDT/TEC/SKT/SWS/GRD/DSA — each pairs with dat-/cov- skeletons best; in fake mode they bind to nothing (placeholder panels).

## Routing (top-3 with confidence, never a hardcoded single pick)

Route = (audience, goal) → candidate list with confidence + reason; the top agent picks among the top 3.
- teaching + interaction-heavy → qz-1..4 skeleton family + quiz slots (bank ≤30, 1–3 per section).
- pitch / board / pricing → data family + `data` (or `flat`) style; single-pager → dat-2 one-pager variant.
- training manual → cover `sec-2` + qz-2 quiz family.
- kids / game feel → `velvet`/`bold` + per-page motion ≤2 with one bar-grow max.
