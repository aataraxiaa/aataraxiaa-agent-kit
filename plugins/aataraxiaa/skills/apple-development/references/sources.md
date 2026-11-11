# Source access and freshness

Read when locating reference packs, exporting Apple skills, or maintaining this guidance. Routine tasks can follow the direct links in the topic files.

## Apple sources

Use current HIG for design recommendations and symbol documentation plus the installed SDK for API constraints. Documentation tools are optional: use an available Apple documentation search tool, the web, or local SDK interfaces. Apple documentation pages may expose a Markdown link when the HTML requires JavaScript. Keep the citation to the canonical Apple page.

Use [HIG Patterns](https://developer.apple.com/design/human-interface-guidelines/patterns) and [Components](https://developer.apple.com/design/human-interface-guidelines/components/) for task and control choices, [Apple Sample Code](https://developer.apple.com/documentation/samplecode) for runnable examples, and [Developer Updates](https://developer.apple.com/documentation/updates) or [Technotes](https://developer.apple.com/documentation/technotes) for version-specific behavior. Verify example APIs against the project targets. DuckDuckGo can help discover relevant pages when available. Verify guidance on the original Apple page.

Apple documents exportable SwiftUI skills in [this WWDC session](https://developer.apple.com/videos/play/wwdc2026/269/). Xcode 27.2 also exports `app-resizability`. Check `xcrun agent skills export --help` and export with `xcrun agent skills export --output-dir <destination>` on that version. Use an external artifact directory and open only the relevant reference. If export is unavailable, use current Apple documentation.

Inspect exported names and metadata before linking them; filenames are not assumed here. If export is unavailable, inspect the selected Xcode application's packaged resources for the relevant Apple skill or reference; discover paths instead of assuming another machine's layout. Do not silently install them or load the entire export. Record the Xcode build and export date alongside a retained export.

## Optional supplements

- [SwiftUI Expert](https://github.com/AvdLee/SwiftUI-Agent-Skill): specific SwiftUI topics and trace recording/analysis.
- [Swift Concurrency](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill) and [Swift Testing](https://github.com/AvdLee/Swift-Testing-Agent-Skill): use only for those concerns.
- [SwiftUI Pro](https://github.com/twostraws/SwiftUI-Agent-Skill): an alternative review reference, not another mandatory full read.
- [Axiom](https://github.com/CharlesWiltgen/Axiom): optional specialized diagnostics/tools; no dependency on its workflow or hooks.

Resolve repository paths from the current tree. Inspect scripts before executing them. Community rules remain secondary to verified Apple guidance and project requirements. If retaining upstream material, pin the revision and preserve attribution/license terms; Apple exportability is not a blanket redistribution license.

## Maintenance

Links and routing were reviewed on 2026-11-11; this date does not certify every linked page or API. After an SDK release or a demonstrated stale recommendation, review the affected topic, update its sources, and repeat its audit scenario. Record the source/version/date for version-dependent findings. Don't refresh every reference on every task or auto-rewrite guidance from a detected page change.

Review the index weekly and before a kit release using [Design What's New](https://developer.apple.com/design/whats-new/), Developer Updates, and Apple Sample Code. Update routes and examples when the change affects a decision. Fetch the relevant guidance live when using the skill.
