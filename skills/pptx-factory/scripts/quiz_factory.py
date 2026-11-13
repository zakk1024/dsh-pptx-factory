#!/usr/bin/env python3
"""Quiz factory for the pptx-pipeline (G1 bank -> G3 quiz pages).

Input  : bank.json — list of {"stem","opts":[...],"answer":0-based,"explain","section"}
Modes  : --check              validate the bank only (exit 1 on any violation)
         --format md          append-ready quiz slides as dsh-ppt markdown
         --format html        single-file <details> click-reveal fragment
         --format both        write md + html into --outdir
Quiz page rule: one question = its own slide(s) (qz-* skeleton family),
answer and explanation revealed by click; quiz count must stay <=30.
Letter-numbered answers are rendered with a trailing period ("A." / "B.").
"""
import argparse, json, os, sys

LETTERS = "ABCDEFGH"
MAX_QUIZ = 30


def check_bank(bank):
    errs = []
    if not isinstance(bank, list):
        return ["bank must be a JSON array"]
    if len(bank) > MAX_QUIZ:
        errs.append(f"quiz count {len(bank)} > {MAX_QUIZ}")
    for i, q in enumerate(bank):
        if not isinstance(q, dict):
            errs.append(f"[{i}] not an object")
            continue
        if not q.get("stem"):
            errs.append(f"[{i}] missing stem")
        if len(q.get("stem", "")) > 80:
            errs.append(f"[{i}] stem longer than 80 chars")
        opts = q.get("opts") or []
        if not (2 <= len(opts) <= 8):
            errs.append(f"[{i}] opts need 2-8 items, got {len(opts)}")
        a = q.get("answer")
        if not isinstance(a, int) or not (0 <= a < len(opts)):
            errs.append(f"[{i}] answer must be a 0-based index inside opts")
        if not q.get("explain"):
            errs.append(f"[{i}] missing explain (click-reveal payload)")
        if not q.get("section"):
            errs.append(f"[{i}] missing section (quiz pages bind to sections)")
    return errs


def to_md(bank):
    out = ["", "## 測驗 · 随堂題庫", ""]
    by_sec = {}
    for q in bank:
        by_sec.setdefault(q.get("section", "未分節"), []).append(q)
    for sec, qs in by_sec.items():
        out.append(f"## 測驗 · {sec}")
        out.append("")
        for n, q in enumerate(qs, 1):
            ans = q.get("answer", 0)
            opts = q.get("opts", [])
            out.append(f"### 第 {n} 題 · {q.get('stem','')}")
            out.append("")
            for i, o in enumerate(opts):
                mark = " ✅" if i == ans else ""
                out.append(f"- {LETTERS[i]}. {o}{mark}")
            letter = LETTERS[ans] if ans < len(LETTERS) else "?"
            out.append(f"- 點擊揭示 → 答案 {letter}.；{q.get('explain','')}")
            out.append("")
    return "\n".join(out) + "\n"


HTML_TMPL = """<!-- quiz fragment (pptx-pipeline quiz factory) — {n} questions, click-reveal + count-up -->
<style>
.quiz details{{border:1px solid rgba(128,128,128,.35);border-radius:14px;padding:14px 18px;margin:14px 0}}
.quiz summary{{cursor:pointer;font-weight:600;list-style:none}}
.quiz summary::-webkit-details-marker{{display:none}}
.quiz .opts{{margin:10px 0 0;padding-left:0;list-style:none}}
.quiz .opts li{{margin:4px 0}}
.quiz .answer{{margin-top:12px;padding:10px 14px;border-radius:10px;background:rgba(37,99,235,.10)}}
.quiz .sec{{font-size:.8em;opacity:.65;letter-spacing:.08em;text-transform:uppercase}}
</style>
<section class="slide quiz" data-sec="quiz">
{sections}</section>
<script>
document.querySelectorAll('.quiz details').forEach(function(d){{
  d.addEventListener('toggle',function(){{ if(d.open && window.__quizPing) window.__quizPing(d); }});
}});
window.__quizPing = window.__quizPing || function(){{}};
</script>
"""

SEC_TMPL = """<h3 class="sec">{sec} · 測驗 {count} 題</h3>
{items}"""

ITEM_TMPL = """<details class="quiz-q">
<summary>Q{no}. {stem}
<ul class="opts">{opts}</ul>
<div class="answer"><strong>答案 {letter}.</strong> {explain}</div>
</details>"""


def to_html(bank):
    by_sec = {}
    for q in bank:
        by_sec.setdefault(q.get("section", "未分節"), []).append(q)
    secs, no = [], 0
    for sec, qs in by_sec.items():
        items = []
        for q in qs:
            no += 1
            opts = q.get("opts", [])
            opts_html = "".join(f"<li>{LETTERS[i]}. {o}</li>" for i, o in enumerate(opts))
            ans = q.get("answer", 0)
            items.append(ITEM_TMPL.format(no=no, stem=q.get("stem", ""), opts=opts_html,
                                          letter=LETTERS[ans] if ans < len(LETTERS) else "?",
                                          explain=q.get("explain", "")))
        secs.append(SEC_TMPL.format(sec=sec, count=len(qs), items="\n".join(items)))
    return HTML_TMPL.format(n=len(bank), sections="\n".join(secs))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", required=True, help="bank.json path")
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--format", choices=["md", "html", "both"], default=None)
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()
    bank = json.load(open(a.bank, encoding="utf-8"))
    errs = check_bank(bank)
    if a.check:
        if errs:
            print("BANK INVALID:")
            for e in errs:
                print(" -", e)
            sys.exit(1)
        print(f"BANK OK: {len(bank)} questions")
        return
    if errs:
        print("WARNING: bank has violations, fixing them first is cheaper:")
        for e in errs:
            print(" -", e)
    os.makedirs(a.outdir, exist_ok=True)
    if a.format in ("md", "both"):
        p = os.path.join(a.outdir, "quiz_pages.md")
        open(p, "w", encoding="utf-8").write(to_md(bank))
        print("written:", p)
    if a.format in ("html", "both"):
        p = os.path.join(a.outdir, "quiz_fragment.html")
        open(p, "w", encoding="utf-8").write(to_html(bank))
        print("written:", p)


if __name__ == "__main__":
    main()
