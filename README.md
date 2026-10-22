# aataraxiaa agent kit

<img src="plugins/aataraxiaa/assets/icon.png" alt="A deadpan yellow toolbox with a lowercase a" width="180">

Personal development skills for Claude Code and Codex. The first skill, `aataraxiaa:visual-review`, helps you understand agent-written work through concise interactive HTML explanations.

**Advisory by default.** It offers visuals for meaningful plans, results and reviews. It does not block edits or force another turn. Routine inspection, bot notices and empty diffs need no page.

## Install

Requires Python 3.9+, Git, Node.js and an OS HTML opener.

### Claude Code

```sh
claude plugin marketplace add aataraxiaa/aataraxiaa-agent-kit
claude plugin install aataraxiaa@aataraxiaa-tools
```

### Codex

```sh
codex plugin marketplace add https://github.com/aataraxiaa/aataraxiaa-agent-kit.git --ref v0.2.1
codex plugin add aataraxiaa@aataraxiaa-tools
```

Start a fresh session. Review native hook trust prompts; Codex uses `/hooks`. Hook changes may require renewed trust. Check the installation with `claude plugin list` or `codex plugin list`. Installation alone does not prove live hook behavior.

If the marketplace was previously registered from a local checkout, remove that registration first:

```sh
# Run the command for your host, then use its install commands above.
claude plugin marketplace remove aataraxiaa-tools
codex plugin marketplace remove aataraxiaa-tools
```

### Update

For Claude Code:

```sh
claude plugin marketplace update aataraxiaa-tools
claude plugin update aataraxiaa@aataraxiaa-tools
```

For a Codex installation pinned to an older tag, remove the marketplace registration and re-add it with the new release tag, then run `codex plugin add aataraxiaa@aataraxiaa-tools`. Restart the host after updates. Do not hand-edit plugin caches.

## How it works

The agent explicitly declares meaningful work and offers a visual when it helps. A declared task can receive one optional reminder at Stop; it never forces a continuation in advisory mode. Merely editing a file does not create a task in this mode.

One host session owns one active request across worktrees. Its plan is shared; its result includes the source state of every worktree registered by supported edit hooks. New requests get new task IDs and separate HTML directories. Human overrides apply to that same session task, regardless of the working folder.

The CLI path and session ID appear in hook context. All commands accept `--cwd PATH --session HOST_SESSION_ID` before the operation:

```sh
python3 /plugin/scripts/visual-review --session SESSION begin --kind implementation --scope "Add empty-state behavior"
python3 /plugin/scripts/visual-review --session SESSION status
python3 /plugin/scripts/visual-review --session SESSION render --stage plan --source /artifacts/plan.src.html --present
```

Use `post` after implementation, or `review` for code/PR review. Reviews declare explicit `--base` and `--target` commits. Empty diffs and unresolved targets do not trigger a Stop checkpoint. Use `include --path WORKTREE` for worktrees changed through tools that hooks cannot recognize. `begin --kind discussion --scope "No visual needed"` dismisses an active task.

Receipts bind source and HTML hashes. A successful OS viewer command is delivery evidence, never human approval. The renderer runs without optional browser checks; the agent should inspect layout when browser tooling is available.

## Optional strict mode

Explicitly opt in when starting your host:

```sh
VISUAL_REVIEW_MODE=strict claude
# Or:
VISUAL_REVIEW_MODE=strict codex
```

Strict mode requires a plan before supported source-file edits and a current result before recognized PR creation. It may request one continuation at Stop. Unset the variable to restore advisory behavior. Agents must not opt in on your behalf.

Even in strict mode, reads, shell redirects, host configuration, ignored files, scratch directories (`tmp`, `temp`, `scratch`, `work`), and the plugin's full artifact root are exempt. Git operations alone do not require a page. Opaque scripts, interactive terminal input and unsupported tools are outside coverage. This is not a security boundary.

The human can send `visual-review override plan|post|review: reason` for a source-bound exception on the active session task. The agent must not manufacture user input.

## Storage and compatibility

HTML and task journals live outside application checkouts under the directory provided by `~/.agents/bin/agent-task-dir`, with `AGENT_ARTIFACTS_DIR` and `AGENT_PROJECT_DIR` support. A small routing database under `~/.agents-work/visual-review-sessions/` connects session IDs to their initial artifact root, allowing sibling worktrees to share a task.

Version 0.2.0 starts a fresh session-task table. Old worktree-scoped receipts remain on disk but do not carry old blocking state into the new workflow. No vendor files are modified.

## Upstream updates

Visual Explainer 0.14.0 is bundled unchanged from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) at `5f378868e0ea745a6284b51e710c390f0c76f72c`. Its license and checksums are in `plugins/aataraxiaa/vendor/`.

Follow the [upstream maintenance plan](docs/upstream-maintenance.md): check weekly and before releases, review upstream changes, update the explicit pin in a branch, test, then release. Upstream changes are never automatically installed. The weekly check is a maintainer procedure; no scheduled job is configured yet.

## Verification

```sh
python3 scripts/sync-upstream.py --check
python3 -m unittest discover -s tests -v
claude plugin validate plugins/aataraxiaa
```

Tests exercise advisory and strict behavior, session/worktree sharing, artifacts, overrides and source freshness. Native host end-to-end testing and browser layout inspection must be verified separately; passing these tests does not establish either.
