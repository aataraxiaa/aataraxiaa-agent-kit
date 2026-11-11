# macOS

Read for native Mac or Catalyst interface decisions. Identify which is being built before applying API advice.

Decision prompts:

- Do windows have useful sizing, titles, lifecycle, and restoration for the app's purpose? Does state belong to the correct window or document?
- Are commands discoverable through appropriate menus and toolbars, with enabled state tied to the current selection/focus? Preserve standard shortcuts; add custom shortcuts for useful frequent actions rather than every command.
- Do keyboard navigation, selection, editing, undo, and context menus behave appropriately for the content?
- Are settings, inspectors, sheets, and alerts using suitable Mac conventions? Does a resizable layout use the extra room meaningfully?

Use [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos) and [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards) to locate relevant component guidance. Consult [SwiftUI](https://developer.apple.com/documentation/swiftui) or [AppKit](https://developer.apple.com/documentation/appkit) for implementation. SwiftUI-first does not forbid an AppKit bridge when a required native behavior needs it.
