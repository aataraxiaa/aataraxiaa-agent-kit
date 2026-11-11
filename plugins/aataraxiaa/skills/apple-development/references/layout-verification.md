# Layout verification

Read during UI audits or layout changes. Use the active workflow's native driver. Execute the checks yourself when tools permit; a list of checks for the user is not verification.

Build a small matrix from the app's supported configurations and flows:

- iPhone: portrait and both landscape directions, including a large phone's wide/short viewport. Rotate while reading, editing, and presenting a sheet, then rotate back.
- iPad/Mac: narrow and wide windows, plus short windows. Cross each layout breakpoint in both directions with an active selection, navigation destination, and editing state.
- At the tightest layouts: show the keyboard and increase text size. Check that primary and dismissal actions remain reachable.

Trace layout from the scene/root through the affected control, not just the leaf view. Inspect minimum frames, fixed dimensions, safe-area overrides, overlays, and conditions that replace view hierarchies. Width alone does not establish adequate height. Compare any minimum with the actual available viewport.

For each state, check that controls are visible, unobstructed, and usable; scrollable content does not make an off-screen fixed toolbar acceptable. Verify that rotation/resizing preserves the current destination, selection, and reading/editing context. Record the actual device, orientation/window size, flow, and evidence.

If execution fails, record the exact tool failure and continue source analysis. Label root-cause inferences separately from observed clipping; do not mark the matrix passed. A user-supplied defect is a targeted reproduction case, not an independently discovered finding.

Source: [Apple Layout HIG](https://developer.apple.com/design/human-interface-guidelines/layout). It calls for handling width and height size classes, orientations, text size, and safe areas while preserving functionality.
