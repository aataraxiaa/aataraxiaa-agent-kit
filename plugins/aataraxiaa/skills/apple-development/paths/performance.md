# Performance and Instruments

Use for a reported performance problem, a requested performance audit, or an existing trace. A general source audit should identify hypotheses without automatically recording.

## Choose evidence

For an existing `.trace`, inspect its contents before recording again. Otherwise identify the app/process, device, build configuration, repeatable interaction, and symptom. Infer these from project/session evidence; ask only for missing choices that affect capture. Use the active workflow's profiling/benchmark checks when present.

| Symptom | Candidate instrument |
| --- | --- |
| SwiftUI update churn, slow body calculations | SwiftUI, correlated with Time Profiler and hitches |
| CPU work or unresponsive interaction | Time Profiler / Hangs |
| Growing memory or retained objects | Allocations / Leaks, with object-lifetime investigation |
| Rendering, disk, network, or energy | Select the relevant available template after narrowing the symptom |

Discover installed devices and templates; do not assume a template exists or records all lanes on every target. Prefer a representative optimized build with matching symbols for performance conclusions. Label simulator results separately from device results. SwiftUI trace coverage can differ on simulator; absent events are not evidence of zero work.

## Capture and export

The built-in `xctrace` CLI can record and export without automating the Instruments UI. Inspect installed help:

```sh
xcrun xctrace list devices
xcrun xctrace list templates
xcrun xctrace help record
xcrun xctrace help export
```

Store traces outside the repository under the project's `review-artifacts/`. Select the actual device and process explicitly; don't default to profiling all processes. For example, after replacing the placeholders:

```sh
xcrun xctrace record --template 'Time Profiler' --device '<device>' \
  --attach '<pid>' --time-limit 30s --output '<artifact-dir>/baseline.trace'
xcrun xctrace export --input '<artifact-dir>/baseline.trace' --toc \
  --output '<artifact-dir>/toc.xml'
```

Use the table of contents to select export schemas with `--xpath`; don't guess schema names or paste full trace XML into context. Summarize the relevant interval, threads, symbols, counts, and durations. Preserve the raw trace. If the CLI cannot expose necessary data, use available Instruments UI tools or report that limitation. Don't install an analyzer merely to inspect a trace.

## Interpret

Connect samples or events to the reproduced interaction and the app's code. Inclusive sample weight is not exclusive time; a frequent system frame alone does not establish the root cause. Check symbolication and missing data before attributing work.

For a before/after claim, keep the device, build mode, workload, and capture method comparable, and repeat enough to assess noise. Report what changed, the observed metric, and limits. A clean trace for one interaction does not establish app-wide performance.

Sources: [Apple's SwiftUI performance analysis](https://developer.apple.com/documentation/Xcode/understanding-and-improving-swiftui-performance), [Optimize SwiftUI performance with Instruments](https://developer.apple.com/videos/play/wwdc2025/306/). For optional agent tooling, inspect the specific trace references in [SwiftUI Expert](https://github.com/AvdLee/SwiftUI-Agent-Skill/tree/main/skills/swiftui-expert-skill/references) or [Axiom](https://github.com/CharlesWiltgen/Axiom); keep the active workflow in control.
