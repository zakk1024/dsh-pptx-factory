# dsh-pptx-factory

把「PPTX/web-deck 流水线」打包成一个 plugin bundle：`skills/` 目录整包随插件安装（不复制进 ~/.agents/skills），内含流水线 skill `pptx-factory`、其 references（G4 扫描门规则 + 骨架×风格绑定表）与 scripts（scan_pptx.py / quiz_factory.py，纯 stdlib + python-pptx）。

## 内容物

- `skills/pptx-factory/SKILL.md` — G1–G5 零接触流水线 + **工具 roster**（course_assistant.analyze → ask → dsh_ppt_preview → dsh_ppt_propose/pptwise → quiz_factory --check + scan_pptx → dsh_ppt_review）+ 2 眼闸门（G2 skeleton-confirm、G5 one-page review）
- `skills/pptx-factory/references/` — `g4-gates.md`（扫描 flag 表 + 自查判定模板）、`skeleton-styles.md`（20 skeletons × 风格绑定）
- `skills/pptx-factory/scripts/` — `scan_pptx.py`（静态扫描门：chart>70% / font<12pt / contrast / colorblind / anim presets / size）、`quiz_factory.py`（--check bank.json ≤30 题 + --format both 注入题目页/点击揭示）
- `cordis.patch.yml` — 两層结构：① `insert` 把 `./skills` 注册成专属 skill 根（provider `dsh-skill-filesystem`，bundledSkillDir 从安装 identity 解析——与 dsh-answer-me-with-html 同款结构）；② **0.2.0 新增 `preset-pptx-factory` session mode**：进入该模式自动挂工具 roster（course-assistant → ppt → ppt-fusion → factory → deck-studio 选修）+ 缺件明示纪律（agent 第一则回复必须列 [env-probe] MISSING 清单，G5 审查页带缺件红榜）

## 新机器缺件安装（自查，0.2.0 新增）

- 必配同装：`dsh-course-assistant`、`dsh-ppt`、`dsh-ppt-flashmade`（选修 `dsh-plugin-deck-studio`；无 images endpoint 时默认 fake mode 会照跑）— factory 只装流程与 scripts，生成器/审阅器本来就不在里面
- 缺件通知两表面：① 进入 `preset-pptx-factory` session mode → 工具清单里缺件显为空槽（roster 缺口可见，不需记忆）② 不进 mode → agent 跑流水线的第一句回答必须含 `[env-probe]` MISSING 清单（SKILL.md 硬性规则，静默=违规）
- package.json `dsh.market.dependencies`（required/optional + missingPolicy）→ market detail 页可见需装清单，缺件不会静默略过

## 这台机器上的安装/验证事实（2026-11-13）

- 无 LibreOffice / PowerPoint → 视觉 ground truth = 静态扫描 scripts（不是 screenshots）
- python-pptx 1.0.2 只在 `~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3`（系统 python3 没有）
- roster 引用的 4 个插件都在 profiles/desktop/node_modules：`dsh-course-assistant`(course_assistant v1.15.0 含 analyze/ask/coverage/export)、`dsh-ppt-flashmade`(0.7.1 = dsh_ppt_preview/propose/review + pptwise/ppt-master)、`dsh-ppt`(20.5)、`dsh-plugin-deck-studio`(= Deckline，默认 fake mode：无 images/generations endpoint 数据)
- `/tmp` 每 session 清空 → testbed 资料放 workspace（见 `testbed/`），不要依赖 /tmp

## 用法

安装本 bundle 后，对 agent 说「跑流水线 / 做课件 / 做 deck」即触发 `pptx-factory` skill；agent 依 roster 顺序自动操作全部工具，人类只在 2 个眼闸门介入（骨架确认页 + 单页审查页）。
