# Implement or change

Use this alongside the active implementation or bug-fix workflow.

- Read the affected view and its callers before choosing references. For UI behavior, select the target platform reference. For state or identity changes, select SwiftUI. Add interface guidance for layout, appearance, or accessibility changes.
- Look up the specific control, modifier, or behavior in current Apple documentation. Check SDK and runtime availability separately. Do not raise deployment targets or modernize unrelated code as a side effect.
- Use platform-native navigation, controls, commands, and presentation when they satisfy the requirement. Share data and behavior across platforms without assuming identical navigation or window structure.
- Keep existing project architecture unless the requested change requires revisiting it. A community skill's style preference is not an Apple requirement.
- Feed relevant checks into the existing verification step: changed interaction, affected sizes, text expansion, input methods, and accessibility settings. Use the project's driver and permitted devices; don't introduce a competing verification system.

Return the implementation and evidence through the active workflow. If execution is unavailable, identify which behavior remains unverified. A successful build establishes compilation, not layout quality or accessibility.
