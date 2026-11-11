# Layout, appearance, and accessibility

Read only for a relevant interface change or audit area. Choose the matching source below, not all of them.

| Question | Inspect | Apple source |
| --- | --- | --- |
| Adaptive layout and navigation | Inspect both size classes where available, usable container dimensions, and the conditions that change the view hierarchy. Check whether device or orientation branches stand in for available space. Compare how system containers adapt, and preserve selection, destination, and interaction state during reflow. | [Layout](https://developer.apple.com/design/human-interface-guidelines/layout#Size-classes) |
| Accessible interaction | Labels, values, traits, reading/focus order, text scaling, contrast, non-color cues, motion/transparency settings | [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) |
| Current platform appearance | Native control behavior, material placement, legibility, compatibility of custom styling | [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass) |

Choose dimensions and interaction targets from the applicable platform guidance; don't impose one universal point size. A custom control needs equivalent semantics and interaction behavior, not just a similar screenshot. Validate accessibility behavior with the actual accessibility tools when available.

For changes to resizing, orientation, or device idiom, consult the matching reference in Apple's exported `app-resizability` skill when available. See [source access](sources.md) for the export.

Do not apply decorative glass to every content surface or require an explicit migration merely to retain system-provided styling. Confirm current guidance and target availability before recommending appearance changes. Separate a visual preference from a demonstrable usability problem.
