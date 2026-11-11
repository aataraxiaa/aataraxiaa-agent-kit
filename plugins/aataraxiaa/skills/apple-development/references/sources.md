# Source access and freshness

Read when locating reference packs, exporting Apple skills, or maintaining this guidance. Routine tasks can follow the direct links in the topic files.

## Apple sources

Use current HIG for design recommendations and symbol documentation plus the installed SDK for API constraints. Documentation tools are optional: use an available Apple documentation search tool, the web, or local SDK interfaces. Apple documentation pages may expose a Markdown link when the HTML requires JavaScript. Keep the citation to the canonical Apple page.

Apple documents exportable SwiftUI Specialist and What's New in SwiftUI skills in [this WWDC session](https://developer.apple.com/videos/play/wwdc2026/269/). On a compatible Xcode installation, `xcrun agent skills export <destination>` exports Markdown. Inspect local command support first. Use a fresh external artifact directory, not the application repository or a global skill directory. Export may launch Xcode; honor session execution constraints. If it fails, use live documentation and report the unavailable source; don't repair Xcode as a side effect.

Inspect exported names and metadata before linking them; filenames are not assumed here. If export is unavailable, inspect the selected Xcode application's packaged resources for the relevant Apple skill or reference; discover paths instead of assuming another machine's layout. Do not silently install them or load the entire export. Record the Xcode build and export date alongside a retained export.

## Optional supplements

- [SwiftUI Expert](https://github.com/AvdLee/SwiftUI-Agent-Skill): specific SwiftUI topics and trace recording/analysis.
- [Swift Concurrency](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill) and [Swift Testing](https://github.com/AvdLee/Swift-Testing-Agent-Skill): use only for those concerns.
- [SwiftUI Pro](https://github.com/twostraws/SwiftUI-Agent-Skill): an alternative review reference, not another mandatory full read.
- [Axiom](https://github.com/CharlesWiltgen/Axiom): optional specialized diagnostics/tools; no dependency on its workflow or hooks.

Resolve repository paths from the current tree. Inspect scripts before executing them. Community rules remain secondary to verified Apple guidance and project requirements. If retaining upstream material, pin the revision and preserve attribution/license terms; Apple exportability is not a blanket redistribution license.

## Maintenance

Links and routing were reviewed on 2026-11-11; this date does not certify every linked page or API. After an SDK release or a demonstrated stale recommendation, review the affected topic, update its sources, and repeat its audit scenario. Record the source/version/date for version-dependent findings. Don't refresh every reference on every task or auto-rewrite guidance from a detected page change.
