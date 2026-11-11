# Audit

An audit reports findings. It does not authorize fixes or broad modernization. Use the existing review workflow and output conventions.

## Scope and coverage

Identify whether the request covers a diff, screen, flow, or whole app. For a whole app, inventory targets, navigation/window entry points, shared components, and primary user flows. Keep a compact coverage list: area, source inspected, runtime inspected, and outstanding checks. Start with shared components and high-use flows, then cover the remaining requested areas. A sample is not a whole-app audit.

For a whole-app audit, read [coverage and execution](../references/audit-coverage.md). Build the coverage record before reviewing; use it to find omissions before reporting. Treat iPhone and iPad as separate interaction environments even when they share an iOS target.

Load each affected platform reference and relevant topic only when its area is reached. Start with the UI framework actually used; don't load SwiftUI guidance for an AppKit-only view. Read-only tooling, builds, and permitted interaction can supply evidence; honor project execution restrictions. If runtime access is unavailable, continue source review and mark the runtime gap.

## Judge the interface

For a UI or whole-app audit, make design judgment a primary deliverable. Inspect the interface as a user would encounter it, even when the controls work. Follow primary tasks on each platform and capture representative screens before judging visual composition. Use source to explain component choice and distinguish intentional project design from accidental behavior.

- **Component fit.** Name the job and the control that performs it. Check whether its placement, appearance, and semantics communicate that job. Compare with the appropriate native pattern when there is a meaningful difference. Review navigation, search, toolbars, menus, lists, forms, sheets, and settings wherever they carry a primary task.
- **Hierarchy and discoverability.** Check what people notice first, which actions are visible or hidden, how selection and scope are communicated, and whether competing controls interrupt the task. Inspect typography, spacing, density, and accessibility where they affect the experience.
- **Platform adaptation.** Compare the same task across the requested platforms. Judge whether a shared design fits the available space and input. For example, a global search field and a list filter may be clear on successive iPhone screens yet hard to distinguish when both sit side by side in an iPad or Mac window.

A working control can warrant a finding. Explain the consequence before recommending a different component. A native API or newer visual style alone does not make a design better. When a custom component fits the task, assess what it preserves or improves.

For primary flows, record the expected native pattern and its Apple source before judging the observed UI. Compare the same task across relevant width, height, and input conditions using [interface guidance](../references/interface.md). Give the design choice and the functional outcome separate verdicts. A successful transition can still expose a layout or navigation mismatch. Report previously known cases separately from new findings.

## Findings

For each actionable finding, record:

- Location and affected user interaction, including conditions that expose it.
- Evidence: source inspection, observed runtime behavior, or measurement. Keep a hypothesis separate from a confirmed defect.
- Applicable Apple source and SDK/OS context. Distinguish an API requirement, a HIG recommendation, and a product design judgment.
- User impact, proposed correction, and how to verify it.

For a UI or whole-app audit, lead with the design verdict and the most consequential component and platform findings. Include supporting screenshots or links. Put functional regressions and test results after the design findings, and give data loss or a blocked primary task clear visibility. If the request is explicitly a correctness review, lead with defects. Distinguish supported-but-older APIs from actual deprecations. Do not invent findings or assign a compliance score from a checklist.

## Runtime and performance boundary

For UI coverage, load [layout verification](../references/layout-verification.md). Inspect transitions as well as static screens using the active workflow's tools. Screenshots support visual findings; they don't establish VoiceOver behavior, focus order, or performance.

Flag plausible performance hotspots as unmeasured until demonstrated. Open [performance guidance](performance.md) when performance investigation is requested or needed to resolve a specific finding; don't record a trace merely because this is a whole-app audit.

End with scope covered, prioritized findings, and remaining evidence gaps. Store bulky screenshots, logs, and traces in the project's external artifact directory, and link them rather than inserting raw output.
