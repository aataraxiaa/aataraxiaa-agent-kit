---
name: apple-development
description: Apple-specific reference routing for iOS, iPadOS, and macOS implementation, design questions, audits, and Instruments performance investigation. Supplements the active development workflow with relevant HIG and framework guidance.
---

# Apple development guidance

Supply domain guidance inside the active workflow, including AStack or Peakstack. Let that workflow own planning, delegation, implementation, testing, and delivery. This skill adds no lifecycle hooks or approval stages.

## Select a path

Establish the affected platform, UI framework, deployment target, and SDK/Swift settings from the project. Reuse known session facts. Ask only when a missing fact changes the answer.

| Request | Read first |
| --- | --- |
| Implement, fix, or adapt an interface | [Change guidance](paths/change.md) |
| Audit an app, screen, or diff | [Audit guidance](paths/audit.md) |
| Investigate slowness, memory growth, or an Instruments trace | [Performance guidance](paths/performance.md) |
| Answer a focused design/API question | Only the matching topic below |

Load references on demand, never this directory recursively. For a narrow task, start with one path and one relevant reference. Add another only when the code or question crosses that boundary. For a whole-app audit, cover topics in scoped passes. Do not reopen unchanged references already read this session.

## Select knowledge

| Concern | Reference |
| --- | --- |
| iPhone navigation, touch, presentation | [iOS](references/ios.md) |
| iPad resizing, navigation adaptation, input | [iPadOS](references/ipados.md) |
| Mac windows, menus, commands, focus | [macOS](references/macos.md) |
| Layout, safe areas, typography, materials, accessibility | [Interface](references/interface.md) |
| SwiftUI state, identity, tasks, API choice | [SwiftUI](references/swiftui.md) |
| Swift isolation, actors, async work | [Concurrency](references/concurrency.md) |
| Finding/exporting Apple skills, optional community references, refreshing sources | [Source access](references/sources.md) |

## Evidence rules

The references are decision prompts, not a complete or frozen copy of Apple's guidance. Read the linked Apple page for the decision being made. Verify changing API claims against current documentation and the installed SDK; preserve deployment targets. Separate API requirements, HIG recommendations, and project preferences. Prefer native controls where they fit; justify custom behavior by the product need.

Use available documentation tools or web access. If a source is unavailable, state the uncertainty and use local SDK evidence where possible. Do not invent an Apple requirement or claim runtime verification from code inspection.
