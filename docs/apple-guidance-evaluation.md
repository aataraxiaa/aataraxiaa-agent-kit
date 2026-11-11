# Apple guidance evaluation

These are behavioral acceptance scenarios, not claims of completed app testing. Use the checkout's skill path explicitly until a release containing it is installed.

## First app audit

Choose an existing app and requested scope. Give the agent the app path and the Apple skill path; request an audit without edits. Preserve the report under the app's external `review-artifacts/` directory. Record:

- Skill revision, project revision, platforms, toolchain, and deployment targets.
- References actually loaded, with why each was needed. Count their text separately from retrieved documentation, source code, and tool output.
- Findings with source locations, applicable Apple citations, impact, and evidence type.
- Areas inspected and runtime checks that remain unverified.

Review whether the findings are accurate and useful before authorizing fixes. If a known defect is missed, identify whether routing, guidance, source access, or execution caused the miss. Correct that specific failure. Don't expand every task's mandatory reading.

## Routing scenarios

| Request | Expected behavior |
| --- | --- |
| Explain a Mac toolbar placement | Entry point, macOS reference, relevant Apple component page; no audit or profiling path |
| Fix an iPad sheet clipping large text | Change path, iPadOS and interface references; no Mac or trace material |
| Audit a SwiftUI Mac app | Audit path; Mac, SwiftUI, and relevant interface references as areas are reached; evidence-based findings, no automatic fixes |
| Analyze an existing scrolling trace | Performance path; inspect trace contents before deciding whether another capture is needed |
| Investigate a Swift actor-isolation diagnostic | Concurrency reference and project compiler settings; no HIG reading unless UI behavior is implicated |
| Audit an AppKit-only screen | Audit path and Mac/interface guidance; no SwiftUI-only checklist |
| Audit without permission to run a simulator | Continue source inspection, report runtime gaps, honor the restriction |
| Audit a phone app with supported rotation | Trace root-to-control sizing; exercise portrait, landscape, and return while in a flow; account for height as well as width |
| Apple exports or documentation unavailable | Use available local SDK evidence and report uncertainty; no invented requirement or unrelated Xcode repair |

For a whole-app request, verify that the report accounts for the full requested scope rather than presenting sampled screens as exhaustive coverage. For performance claims, verify that the trace supports the reported cause and that comparisons use comparable workloads.

## Acceptance criteria

A source-only review does not validate a full UI audit. Exercise rotation and resizing during active flows, record the affected controls and state, and keep runtime checks open when execution is blocked. Treat user-supplied defects as regression cases; use a separate, undisclosed case to evaluate independent discovery. Keep app-specific findings, revisions, screenshots, and machine diagnostics in external project artifacts rather than this public guidance.
