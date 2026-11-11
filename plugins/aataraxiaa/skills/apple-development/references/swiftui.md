# SwiftUI correctness

Use for SwiftUI implementation or source review. Start with the affected concern, not an exhaustive modernization pass.

- State and observation: identify ownership, lifetime, and readers. Choose wrappers based on those facts and supported OS versions. Keep per-window state separate from shared app data.
- Identity and navigation: inspect stable item identity, selection and path ownership, presentation state, and what survives view reconstruction. Avoid fixing a lifecycle problem by adding arbitrary identities.
- Async effects: check task lifetime, cancellation, repeated loading, and actor isolation. Read [concurrency guidance](concurrency.md) when execution or isolation is in question.
- Updates and layout: keep work attributable to the view that needs it. Treat expensive body calculations or broad dependencies as investigation candidates; don't claim a measured slowdown from their presence alone.
- API choice: distinguish hard deprecation, newer alternatives, and preference. Check the actual declaration and availability before recommending replacements.

Use the relevant symbol documentation in [Apple's SwiftUI reference](https://developer.apple.com/documentation/swiftui). If accessible, load the relevant reference from Apple's exported SwiftUI Specialist skill. For targeted supplementary explanations, use [AvdLee's SwiftUI Expert](https://github.com/AvdLee/SwiftUI-Agent-Skill/tree/main/skills/swiftui-expert-skill). Do not load multiple complete SwiftUI skills for the same question. For discovery or unavailable exports, read [source access](sources.md).

These checks don't prescribe MVVM, a folder structure, or one type per file. Preserve project conventions unless they cause a demonstrated problem.
