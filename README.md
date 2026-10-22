# Aataraxiaa Agent Kit

A personal plugin for Claude Code and Codex. The first skill, `aataraxiaa:visual-review`, makes substantive plans, implementation results, code reviews and PR reviews reviewable as interactive HTML.

The companion keeps task receipts outside application checkouts. Hooks require a presented plan before known edits and a current result visual before known PR creation commands. Read-only reviews need an explicit base and target and a visual before final delivery. Receipts record delivery evidence. They never record or imply human approval.

## Install

Register this repository as a local marketplace in each host, install `aataraxiaa` from `aataraxiaa-tools`, then review and trust its hooks through the host's normal workflow. The marketplace is `.claude-plugin/marketplace.json`; both host manifests are bundled under `plugins/aataraxiaa/`. Do not install the vendored upstream plugin separately for this workflow.

For Claude Code, from a checkout of this repository:

```sh
claude plugin marketplace add .
claude plugin install aataraxiaa@aataraxiaa-tools
```

For a temporary Claude development session:

```sh
claude --plugin-dir /absolute/path/to/aataraxiaa-agent-kit/plugins/aataraxiaa
```

For Codex, add this local marketplace through the plugin interface, install `aataraxiaa`, then use `/hooks` to review and trust the exact definitions. Hook changes need renewed trust. Do not bypass native hook trust. Installation, native registration and event coverage must be verified separately on each host before describing the workflow as active.

Requires Python 3.9+, Git, Node.js and an OS HTML opener. The companion uses Python's standard library, SQLite and upstream's dependency-free renderer. It starts no MCP server and makes no model calls from hooks.

## Workflow

The SessionStart hook gives the exact CLI path. Every command accepts `--cwd PATH --session HOST_SESSION_ID` before its operation. Use the session id from the hook, rather than an invented value. A task is bound to its canonical worktree and host session. Some Codex subagents report their parent's session id. Delegated readers must not call `begin` or change the parent's scope.

```sh
python3 /plugin/scripts/visual-review --session SESSION begin --kind implementation --scope "Add empty-state behavior"
python3 /plugin/scripts/visual-review --session SESSION status
```

Write `plan.src.html` in the artifact directory printed by `status`, using the bundled upstream visual-explainer instructions. Present it before editing:

```sh
python3 /plugin/scripts/visual-review --session SESSION render --stage plan --source /artifacts/plan.src.html --present
```

After implementation, inspect the actual diff, author and present `post.src.html` with `--stage post`. Before creating a PR:

```sh
python3 /plugin/scripts/visual-review --session SESSION check --publish
```

For a read-only code or PR review, use `begin --kind code-review|pr-review --scope "..." --base COMMIT --target COMMIT`. Use `--pending` if the target first needs discovery, then `resolve --base COMMIT --target COMMIT`. Present the review with `--stage review`. Plan-only tasks use `--kind plan` and `--stage plan`. Discussion and ordinary inspection need no visual. Switching an incomplete substantive task to discussion is refused.

`begin` is idempotent for the same declaration. A changed scope or `--new` starts a new task and requires new checkpoints. Ordinary prompt followups preserve the active task and its valid plan. A new explicit task can use the prefix `New task:`; the skill must declare changed scope when intent is less obvious. Prompt detection deliberately does not treat every mention of "review" or every `git diff` as a new review.

The renderer uses actual upstream `kit/render.mjs`, with `--no-check` to avoid optional browser checking dependencies. Inspect rendered pages with host browser tools where available. `record --stage STAGE --html /artifacts/page.html --present` can register an already rendered page. Both operations run the native viewer command and record only on success. They require interactive HTML with a script. This structural check cannot judge whether the content is a useful plan or review; the skill supplies that obligation. An opener returning success does not prove the human viewed the page.

Only the human may send `visual-review override plan|post|review: reason`. The user prompt hook journals that exact exception against the current source fingerprint. There is no agent-facing override command. An agent must never synthesize a human prompt or invoke a hook with invented input. Local hooks are a workflow convention, not an adversarial security system.

## State and enforcement

The shared project SQLite journal lives in `review-artifacts/visual-review/`; each task has its own `tasks/TASK_ID/` artifact directory printed by `status`. State lives under the path returned by `~/.agents/bin/agent-task-dir`. Its `AGENT_PROJECT_DIR` and `AGENT_ARTIFACTS_DIR` overrides remain supported. Without that helper, the CLI uses `AGENT_ARTIFACTS_DIR` or a deterministic directory under `~/.agents-work/`. It refuses artifact directories inside the application worktree.

SQLite `BEGIN IMMEDIATE` transactions isolate task changes. Receipts bind stage, task, session, canonical worktree, scope, source fingerprint, pinned generator revision and HTML SHA-256. Fingerprints include HEAD, index entries, changed/deleted tracked worktree content, untracked source and review base/target commit identities. Git-ignored files are outside this contract. Clean `.env` files bind through their index entries without reading content; dirty or untracked `.env` files prevent certification. Symlink contents bind as link targets, rather than reading outside the checkout. Dirty submodules recursively bind their HEAD, index and changed content. Unchanged tracked files bind through Git object identities without reading their bytes.

A plan receipt survives changes within its declared implementation scope. A post or review receipt requires the current source fingerprint. Missing, deleted or altered HTML invalidates any stage. The final Stop hook requests one continuation per unresolved stage/source fingerprint, then emits a visible `INCOMPLETE` message. It does not falsely mark the task complete or loop forever.

`PreToolUse` denies known edits without a plan, including Claude `Write`/`Edit`, Codex `apply_patch` through `tool_input.command`, supported file-write MCP tools and recognized shell mutations. Writes confined to the current task artifact directory are exempt. Hooks resolve explicit shell workdirs, direct `cd`, `git -C`, absolute edit paths and each structured patch path before choosing that target worktree’s journal. Read-only commands remain available. Chained direct `gh pr create` and known GitHub MCP PR creation tools require a current plan and post visual, even when no task was previously declared. PR creation from a plan or review task starts an implementation scope and requires its checkpoints. Publication requires a clean committed tree, local origin, and current branch. Explicit `gh --repo`/`-R` and `--head`/`-H` must match that origin and branch; MCP calls must supply both repository and head. This proves local identity only: hooks do not fetch or certify the remote branch revision. Commit changes and refresh the post visual before opening a PR.

Codex code mode applies hooks to actual nested tool events; the companion handles those events. It does not parse JavaScript inside `functions.exec`. Opaque scripts, interpreter code, shell aliases/functions, commands hidden behind another shell, custom HTTP clients, interactive terminal input, unsupported file-edit tools and disabled or untrusted hooks remain coverage gaps. The shell recognizer intentionally recognizes supported direct commands rather than implementing a security sandbox. Unresolvable supported mutation targets are refused; use structured edits or explicit workdirs. In-place sed/perl edits, shell patch input and Git target options other than `-C` need a structured edit or a simpler direct command. Read-only `git stash list` and `git stash show` preserve review state. A command mentioning the helper does not gain a blanket exemption. Future unrelated skills do not automatically inherit this skill's task states.

## Upstream and verification

`plugins/aataraxiaa/vendor/visual-explainer` contains unchanged tracked files from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer), version 0.14.0, revision `5f378868e0ea745a6284b51e710c390f0c76f72c`. Its license and per-file checksums are in `vendor/LICENSE` and `vendor/provenance.json`. No `node_modules` or untracked upstream files are copied. The upstream skill is read lazily and is not exposed as another globally installed skill.

Reproduce or verify the vendor copy:

```sh
python3 scripts/sync-upstream.py /local/upstream/git/checkout
python3 scripts/sync-upstream.py --check
python3 -m unittest discover -s tests -v
claude plugin validate plugins/aataraxiaa
```

Behavior tests cover source and HTML freshness, task scope, read-only review targets, session and worktree isolation, edit and PR gates, failed presentation, artifact confinement, human exception journaling and bounded Stop recovery. These checks do not establish live native host coverage or actual browser presentation. Verify those separately after trusted installation.
