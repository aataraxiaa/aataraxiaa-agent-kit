---
name: visual-review
description: Offer concise interactive HTML explanations for meaningful plans, implementation results and code or PR reviews. Advisory by default; skip routine edits, read-only inspection, bot notices and empty diffs.
---

Help the user understand the work. For a meaningful plan, explain proposed behavior, decisions and verification before implementation. After substantial implementation, explain the actual diff, validation and limits. For code or PR reviews, explain actionable findings. Use a page when interaction or diagrams help; do not generate one for routine changes, bot notices, empty diffs or a task with nothing to decide.

The default mode is advisory. Never delay tools, demand approval, or continue a turn solely to produce a page. A Stop reminder is optional and appears at most once per declared task. The user can decline. Hard gates apply only when the user explicitly starts the host with `VISUAL_REVIEW_MODE=strict`; do not enable strict mode yourself.

Resolve `scripts/visual-review` relative to this plugin root. Pass `--cwd` and the exact host `--session` from the hook context. Run `status`, then explicitly declare meaningful work with `begin --kind implementation|plan|code-review|pr-review --scope "requested outcome"`. Reviews need `--base COMMIT --target COMMIT`, or `--pending` until discovery then `resolve`. An unresolved or empty review gets no Stop checkpoint. Use `begin --kind discussion --scope "..."` to dismiss a task that no longer needs a visual. Use `--new` for a different request.

The session owns one task, including edits in sibling worktrees. Edit hooks add source worktrees to the task without requiring another plan. Result receipts cover those worktrees, so later changes require a refreshed result when strict mode is enabled. If a worktree was changed through an unsupported tool, run the helper from that worktree and use `include --path WORKTREE` before recording the result. Separate host sessions remain independent. Delegated readers must not change the parent's task scope.

Read the bundled upstream [SKILL.md](../../vendor/visual-explainer/SKILL.md) only when producing a visual, then its selected references. Use the bundled dependency-free renderer; do not install upstream separately. Author `<stage>.src.html` under the path returned by `status`. Keep the explanation concise, with expandable detail. Do not substitute a receipt/status dashboard for an explanation of the work.

Run `render --stage plan|post|review --source /absolute/path/stage.src.html --present`. It uses upstream `kit/render.mjs` with `--no-check`, then the OS viewer. Inspect the page with host browser tools when available. `record --stage STAGE --html /absolute/path/page.html --present` records an already rendered page. Delivery means the viewer command succeeded, not that the user read or approved it.

In strict mode, supported project file edits need a plan and recognized PR creation needs a current result. Reads, shell redirections, scratch paths, host configuration and the entire artifact root are exempt. These are workflow conventions, not a security boundary. An explicit human prompt `visual-review override plan|post|review: reason` applies to the session's active task across its worktrees. Never fabricate that prompt. `check --publish` reports missing evidence in either mode; only strict hooks enforce it.
