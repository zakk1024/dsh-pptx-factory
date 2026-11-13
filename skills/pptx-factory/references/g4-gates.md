# G4 scan gates + self-check template

Load this when running the G4/G5 steps of `pptx-pipeline`, or when editing `scripts/scan_pptx.py`.

## Scan rules (what a red flag means, and the reflow that fixes it)

| Flag (scan_pptx.py key) | Rule | Reflow (≤2 rounds, then degrade+flag) |
|---|---|---|
| oversize_chart_area | one chart/image shape bbox > 70% of slide area | shrink the frame into the top band (top ~48%) and move supporting copy under it, OR delete the shape's redundant frame |
| sparse_text_block | text-block area < 25% and a chart/image occupies > 70% (decorative emptiness) | add a caption block or merge the neighbouring text shape into the same frame |
| font_floor | any body run < 12 pt (captions allowed down to 9 pt if `--allow-caption`) | raise to floor or cut text volume |
| contrast_poor | fg/bg pair with WCAG ratio < 4.5:1 (dark mode) / < 7:1 (light mode) against white or black panel | swap to the colourblind-safe set: #2563EB blue / #DC2626 red / #059669 green / #D97706 amber / #7C3AED violet / #0F172A ink |
| anim_over_budget | timing seeds on a slide > 2, or one element carrying > 2 entrance behaviours | keep ≤2 per page; drop one element's animation |
| anim_preset_unknown | motion preset name outside the 8-preset list | replace by nearest allowed preset |
| size_warn (html) | single-file deck HTML > 2 MB | drop inlined data/blob; keep chart as reference |

**8 motion presets (closed list):** count-up, bar-grow, flip, reveal, zoom, pan, fade, slide.
**Animation budget (per page):** ≤2 entrance animations, ≤4 visible elements, ≤2 text blocks; one count-up OR one bar-grow per page (never both).

## Self-check verdict template (G5 page, one table)

| id | claim (quote ≤20 chars) | source `file:page` | coverage vs old outline | verdict | cites |
|----|--------------------------|--------------------|--------------------------|---------|-------|

- `coverage` = covered / drifted / not_covered — measured against the previous outline or the G1 facts table, never asserted.
- `verdict` keeps one of: ok / degraded (name the degraded gate) / pending (human must look).
- A claim whose `source` is blank or whose `cites` count is 0 fails the citation rule → replace it with one that has traceable pages (a claim with zero citations is unverifiable by definition — e.g. course_assistant `ask` answers with no cited page must not be presented as fact).
- The table doubles as the G5 handoff: "degraded" rows are exactly what stays red on the one-page review.

## Scan-fallback (no LibreOffice / no Keynote)

This machine has no per-page renderer, so the scan scripts are the only visual path — their output is legitimate "evidence", a screenshot never exists here. If an image-capable model + attachment service exist, `dsh_ppt_review` may run with `findings` to record page-level notes; otherwise rely on `scan_pptx.py` JSON plus the scan rule set above.
