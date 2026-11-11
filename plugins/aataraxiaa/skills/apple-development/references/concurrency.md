# Swift concurrency

Read when async work, isolation, data races, or language migration is relevant. Don't load for a purely visual change.

Inspect the target's Swift language mode, strict-concurrency settings, default actor isolation, and enabled upcoming features before applying migration advice. SDK version alone doesn't establish these settings.

Trace who owns mutable state, where isolation changes, and whether work outlives its initiating task. Check cancellation and errors at those boundaries. An async declaration is not evidence that CPU-heavy work runs away from the main actor. Avoid blanket `@MainActor`, detached tasks, or unchecked sendability as diagnostic suppression.

Look up the applicable rule in [Apple's Swift 6 migration guidance](https://developer.apple.com/documentation/swift/adoptingswift6) and [Swift's migration guide](https://www.swift.org/migration/documentation/migrationguide/). Use [AvdLee's concurrency references](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill) for a specific unresolved diagnostic or pattern. Confirm advice against project compiler settings; don't initiate a language migration during an unrelated fix.
