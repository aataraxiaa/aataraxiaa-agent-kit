# Layout, appearance, and accessibility

Read only for a relevant interface change or audit area. Choose the matching source below, not all of them.

| Question | Inspect | Apple source |
| --- | --- | --- |
| Resizing or clipped content | Available container, safe areas, intrinsic sizing, long/localized text, keyboard obstruction; preserve interaction state during reflow | [Layout](https://developer.apple.com/design/human-interface-guidelines/layout) |
| Accessible interaction | Labels, values, traits, reading/focus order, text scaling, contrast, non-color cues, motion/transparency settings | [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) |
| Current platform appearance | Native control behavior, material placement, legibility, compatibility of custom styling | [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass) |

Choose dimensions and interaction targets from the applicable platform guidance; don't impose one universal point size. A custom control needs equivalent semantics and interaction behavior, not just a similar screenshot. Validate accessibility behavior with the actual accessibility tools when available.

Do not apply decorative glass to every content surface or require an explicit migration merely to retain system-provided styling. Confirm current guidance and target availability before recommending appearance changes. Separate a visual preference from a demonstrable usability problem.
