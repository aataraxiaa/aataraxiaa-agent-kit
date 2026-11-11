# Whole-app coverage and execution

Inventory reachable screens and flows from scene roots, navigation destinations, sheets, menus, settings, extensions, and feature flags. Exclude disabled or retired features explicitly. Trace shared wrappers before reviewing individual screens; a root constraint or shared state owner can affect every screen.

Keep one external coverage table with these columns: platform, flow/state, source locations, runtime configuration, action, expected result, evidence, result. Record component fit and platform conventions for the primary flows even where behavior passes. Use `observed pass`, `design finding`, `observed defect`, `source finding`, `blocked`, or `not checked`. A build or an accessibility identifier's existence cannot establish visibility or usability. Record the checkout revision and build provenance separately.

Cover each requested platform independently:

- iPhone: primary flows in portrait and both landscape directions, small and large supported viewports, and transitions back while a destination or sheet is active.
- iPad: full-size and narrow/short windows, resizing across layout branches, selection and reading/editing state, keyboard and pointer paths, and independent scenes where supported.
- macOS: minimum and expanded windows, window lifecycle and independent windows, menu/toolbar commands, keyboard focus and shortcuts, settings, sheets, and state restoration.

Within each platform, include navigation, content actions, import/share, settings, and supported loading/empty/error/offline states. Exercise larger text, keyboard obstruction, accessible names/actions, and appearance where relevant. Select representative combinations by risk; list omitted combinations rather than implying the entire cross-product was tested. Use synthetic data in an isolated test library when available.

For layout checks, read [layout verification](layout-verification.md). Check the control's visible bounds against the usable viewport and then activate it. Verify outcomes and preservation of state, not just screenshot appearance. For source findings, follow the event through its handler and persistence/state update before attributing impact.

Discover the project's required driver and current tools. If unavailable, use a supported fallback. Distinguish sandbox denial, missing SDK/runtime, inaccessible project, and application build errors. Try a justified alternative or permitted host access; do not repeatedly issue an unchanged failing call. Keep diagnostics and any successful build/test logs as evidence. Never use a previously installed app as proof about the audited revision without establishing provenance.

Before finishing, reconcile every inventory item with the coverage table. Consolidate duplicate root causes across platforms while retaining platform-specific impacts. Review source findings for active reachability and counterevidence. Keep performance hypotheses unmeasured unless traces support them. A blocked runtime pass leaves the full audit incomplete, even when source review is finished.

For a rerun, preserve the prior report and label known defects as regression cases. Re-read current code and validate findings instead of copying the previous list. Record which skill changes affected coverage and which omissions remain. Do not claim independent discovery when the reviewer already knows the defect.
