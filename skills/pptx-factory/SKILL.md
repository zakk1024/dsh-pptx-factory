---
name: pptx-factory
description: "Bundled PPTX/web-deck factory (bundle dsh-pptx-factory; successor of the old global pptx-pipeline skill — this is the single source of truth). Zero-touch line: G1 research → G2 skeleton & style → G3 generate (dsh-ppt or pptwise deep pages) → G4 scan gates → G5 one-page review + PPTX/HTML export. Tool roster in fixed order: course_assistant.analyze → course_assistant.ask → dsh_ppt_preview → (dsh_ppt_propose | pptwise) → quiz_factory --check + scan_pptx gates → dsh_ppt_review; human has exactly 2 eye-gates (G2 skeleton confirm, G5 one-page review). Use when user says 跑流水线 / 做课件 / 做 deck / 用 factory, or asks for a quiz/animated/teaching-power deck, or a course_assistant report exists and a deck should follow."
---

# PPTX factory — G1–G5, zero-touch (bundle-baked)

The human touches exactly **2 pages**: the skeleton-confirm page (G2) and the one-page review (G5). Everything else runs silently. Never pause mid-pipeline to ask "should I continue" — degrade + flag instead (see Rules).

## Where the assets are

`scripts/` and `references/` below are relative to this skill dir. On this machine that is one of (check in order, use the first that exists):

1. `~/.dsh/profiles/desktop/node_modules/dsh-pptx-factory/skills/pptx-factory/` (installed bundle)
2. `<project>/dsh-pptx-factory/skills/pptx-factory/` (workspace source copy)
3. `~/.agents/skills/pptx-pipeline/` (legacy global copy — read-only fallback, do not edit)

The two scripts are pure stdlib + python-pptx. Run them with the harness python that already has `pptx` (probe: `~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3`, verified `pptx 1.0.2`); system `/usr/bin/python3` does NOT have pptx here.

## Tool roster (fixed order, never skip a stage)

G1 `course_assistant.analyze(reportLevel=max)` → G1 `course_assistant.ask` (page-cited facts) → G2 `dsh_ppt_preview` → G3 `dsh_ppt_propose` (or pptwise deep-route) → G4 quiz bank gate `quiz_factory.py --check` + scan gate `scan_pptx.py` → G5 `dsh_ppt_review` / answer-me one-page + export.
If any tool is absent or errors, take the file-path fallback written into that step — do not silently skip the stage. `dsh_ppt_preview/propose/review` live in bundle **dsh-ppt-flashmade** (0.7.1); check its install.json before calling.

## Environment probe (run first, ~4 shell probes)

1. Tool presence: check whether `course_assistant`, `dsh_ppt_preview/propose/review`, `ppt_check/edit/render/data`, `ppt_themes/ppt_templates` exist in the tool registry. Missing → take the file-path fallback written into the step that needs it.
2. Interpreter with python-pptx: try `~/.dsh/dsh-runtimes/*/dependencies/python/bin/python3` first — system `/usr/bin/python3` on this machine has no `pptx` module (verified env fact, do not re-derive). Same interpreter for every script call.
3. `soffice` on PATH? This machine: no → never plan a per-page-PNG render gate here; static scan scripts ARE the visual path.
4. Image-gen endpoint (only if deck-studio/Deckline present): look for `render-settings.json` with an `/v1/images/generations` base URL inside its data root (`~/.dsh/deckline`, `~/.dsh/deck-studio`, `~/.dsh/plugin-data/dsh-plugin-deck-studio`, `~/.dsh/profiles/<p>/data/dsh-plugin-deck-studio`). None found = **fake mode**: deck-studio would emit placeholder panels → route styles through dsh-ppt themes + pptwise layers instead. Do not run scripts against `/tmp` (volatile here) — seed files live in the project folder or `testbed/`.

## G1 · Research (agent, silent)

- If `course_assistant` exists: `analyze(reportLevel=max)` for K/E/Q + per-chapter quiz bank; when max is unavailable, analyze at normal and note it. Then `ask` per knowledge point to pull page-cited facts (target ≤30 facts/deck, ≥1/3 with page numbers). `coverage` against the old outline when one exists.
- No course_assistant → grep/read the source files directly and hand-write `facts.md`.
- Emit `scratch/<deck>/facts.md`: one bullet per fact, `file:page` source tag per bullet, plus a quiz-bank JSON `bank.json` (`{"stem","opts":[...],"answer":0-based,"explain","section"}` per row, ≤30 rows).
- Done when: every fact bullet carries a source tag and the bank parses with `scripts/quiz_factory.py --check <bank.json>` (violations listed, never crashes; if >30 rows, auto-degrade to one-per-section and write that choice in G5 — never stop to ask).

## G2 · Skeleton & style (agent → **human eye ①** = skeleton-confirm page)

- Pick skeleton × style from `references/skeleton-styles.md` (5×4 skeletons × styles: dsh-ppt 5 themes / pptwise 3 layers / deck-studio 9 styles when non-fake).
- Reserve quiz slots from bank.json (1–3 per section, max 30); apply the animation budget table on the same page (≤2 anim + ≤4 elements per page; quiz pages default to click-reveal).
- Produce ONE skeleton-confirm page: `dsh_ppt_preview` if present, else hand-write `scratch/<deck>/skeleton_confirm.md` — per page: skeleton id + style code + anim budget + quiz slot count; hand it to the human, accept edits/rename/swap, then re-print once.
- Done when: page exists and the human answered (or approved implicitly by saying run/继续).

## G3 · Generate (agent, silent)

- Tool path: `dsh_ppt_propose` (draft, review card) → follow its per-page author flow; dsh-ppt markdown route for `ppt_edit` patches; never reorder pages outside a tool's power.
- File path: `scripts/quiz_factory.py --bank bank.json --format both` injects quiz pages (md) + click-reveal fragments (html); animation names only from the 8-preset list (count-up, bar-grow, flip, reveal, zoom, pan, fade, slide) and ≤2/page; if live charts keep the dual-track rule (live in HTML main page; frozen static copy on the PPTX side — dsh_ppt_edit rebuild or python-pptx rebuild, never a renderer).
- Done when: deck HTML + PPTX both exist on disk; scan script runs without crash.

## G4 · Scan gates (agent, silent — self-gate, never ask)

- `scripts/scan_pptx.py --deck <pptx> [--html <html>] [--font-floor 12] [--allow-caption] --out scan.json` → JSON verdict: oversize_chart_area (>70% slide area), font_floor (<12pt body; 9–11.5pt caption pass with --allow-caption), contrast_poor (dark <4.5:1 / light >7:1 inverted), colorblind_check (outside the 6-colour set #2563EB #DC2626 #059669 #D97706 #7C3AED #0F172A), anim_over_budget (>2 preset seeds/slide), anim_preset_unknown, size_warn (HTML >2 MB).
- Any gate red → auto-reflow ≤2 rounds (re-run from the failing gate only — scan/reflow ≠ regenerate), then **degrade + flag + continue** (never stop-and-ask). Red-line items needing human taste (e.g. "5×4 chart too decorative") go to the G5 page, not a prompt.
- Done when: scan JSON exists and every remaining red is listed as a degrade-flag on the G5 page.

## G5 · Deliver (human eye ② = one-page review, the ONLY input point)

- Build the one-page answer-me review (skill `answer-me-with-html`: pipe draft to am.mjs `render - --no-open`; new page = no `--replace`). Panel content: pipeline trace (which gates degraded), quiz answer-reveal + coverage table, font/area self-check verdict, cost & duration.
- PPTX export side: charts frozen to PNG (no live engine here); quiz reveal and live charts live only in the HTML main page (dual-track).
- Citation discipline: every self-check claim cites `file:page`; cites=0 → the claim is a guess → do not write it.
- Human comments → auto-reflow ≤1 round, re-entering only the failed gates.

## Rules (hard)

1. 2-eyes rule: exactly the two pages above are shown; anything else runs silently.
2. No mid-pipeline prompts; on block → degrade, flag on G5 page, continue.
3. Citation discipline: G5 claims must cite `file:page` from facts.md; "引用数 0" = the claim is unverifiable → do not write it.
4. Token discipline: reflow ≠ regenerate — rerun only the failed stage/scan.
5. This machine has no LibreOffice: PPTX visual truth comes from scan scripts + (with image-capable model) `dsh_ppt_review`; do not fabricate render receipts, and never plan the `ppt_render`/`office_render` chain here.
6. Roster = law: the G1→G5 order above is what the pipeline IS; if a tool in the roster is missing, that is an environment fact to flag (probe #1), not a license to reorder stages.

## Disclosed reference (load on demand)

- `references/g4-gates.md` — full scan rule set + self-check verdict template (load at G4/G5).
- `references/skeleton-styles.md` — skeleton×style binding table (load at G2).
- `scripts/scan_pptx.py`, `scripts/quiz_factory.py` — run, don't read, unless editing the scripts.
