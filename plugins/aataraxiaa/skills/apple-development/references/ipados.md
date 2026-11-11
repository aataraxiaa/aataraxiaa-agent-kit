# iPadOS

Read for iPad adaptation, window resizing, or keyboard/pointer interaction. This reference is self-contained; don't automatically load iOS as well.

Decision prompts:

- Does the hierarchy suit both narrow and wide windows? Choose tabs, sidebars, and split views from the information structure rather than replacing every tab bar with a sidebar.
- Is layout based on the available container rather than an assumed full-screen device size? Verify the windowing behavior supported by the target OS instead of relying on a fixed list of split ratios.
- Do selection, navigation, editing, and scroll context survive resizing and scene changes? Distinguish per-window state from shared data.
- Can people use relevant commands through touch, keyboard, and pointer? Inspect focus, selection, context menus, and drag/drop where the product supports them.

Sources: [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados), [Layout](https://developer.apple.com/design/human-interface-guidelines/layout), [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards). Consult their platform-specific sections before reporting a violation.
