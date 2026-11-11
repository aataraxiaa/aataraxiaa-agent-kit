# Audit

An audit reports findings. It does not authorize fixes or broad modernization. Use the existing review workflow and output conventions.

## Scope and coverage

Identify whether the request covers a diff, screen, flow, or whole app. For a whole app, inventory targets, navigation/window entry points, shared components, and primary user flows. Keep a compact coverage list: area, source inspected, runtime inspected, and outstanding checks. Start with shared components and high-use flows, then cover the remaining requested areas. A sample is not a whole-app audit.

For a whole-app audit, read [coverage and execution](../references/audit-coverage.md). Build the coverage record before reviewing; use it to find omissions before reporting. Treat iPhone and iPad as separate interaction environments even when they share an iOS target.

Load each affected platform reference and relevant topic only when its area is reached. Start with the UI framework actually used; don't load SwiftUI guidance for an AppKit-only view. Read-only tooling, builds, and permitted interaction can supply evidence; honor project execution restrictions. If runtime access is unavailable, continue source review and mark the runtime gap.

## Findings

For each actionable finding, record:

- Location and affected user interaction, including conditions that expose it.
- Evidence: source inspection, observed runtime behavior, or measurement. Keep a hypothesis separate from a confirmed defect.
- Applicable Apple source and SDK/OS context. Label project conventions and community advice explicitly.
- User impact, proposed correction, and how to verify it.

Prioritize broken interactions, inaccessible controls, lost state, and unusable layouts over cosmetic preferences. Distinguish supported-but-older APIs from actual deprecations and correctness defects. Do not invent findings to fill categories or assign a compliance score from a checklist.

## Runtime and performance boundary

For UI coverage, load [layout verification](../references/layout-verification.md). Inspect transitions as well as static screens using the active workflow's tools. Screenshots support visual findings; they don't establish VoiceOver behavior, focus order, or performance.

Flag plausible performance hotspots as unmeasured until demonstrated. Open [performance guidance](performance.md) when performance investigation is requested or needed to resolve a specific finding; don't record a trace merely because this is a whole-app audit.

End with scope covered, prioritized findings, and remaining evidence gaps. Store bulky screenshots, logs, and traces in the project's external artifact directory, and link them rather than inserting raw output.
