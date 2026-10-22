# Upstream maintenance

Owner: repository maintainer. Cadence: weekly, and before each kit release. This is a maintenance plan, not an active scheduled automation.

1. Compare the pinned revision in `plugins/aataraxiaa/vendor/provenance.json` with releases and commits in `nicobailon/visual-explainer`. Review changes to the skill, renderer CLI, HTML conventions, dependencies and license.
2. Record either “no update needed” or the selected revision and rationale in the update PR. Do not follow upstream HEAD at runtime.
3. In an update branch, extend `scripts/sync-upstream.py` to accept the selected revision and derive its version from the upstream manifest. The current script reproduces the existing pin and hardcodes upstream version 0.14.0; changing only provenance is insufficient. Validate the selected tree contains the expected skill and renderer before replacing files.
4. Vendor only upstream tracked files and its license. Keep upstream files unchanged. Regenerate checksums and inspect the diff for removed files, new dependencies and license changes.
5. Run checksum verification and the full behavioral suite. Generate representative plan, result and review pages with the updated renderer; inspect them in a browser. Test a fresh native session in both hosts, including advisory non-blocking behavior and strict-mode exemptions.
6. Review compatibility with our wrapper, bump plugin and marketplace versions together, publish a tagged release, and update installation examples. Explain user-visible changes and any unverified host behavior in release notes.

If an upstream release breaks compatibility, keep the existing pin and open a compatibility issue. For a regression after release, publish a new patch release restoring the last known-good pin; do not rewrite old tags.

The first update should add the revision/version selection described above. That change needs its own tests for invalid revisions and missing upstream layout. The existing `--check` operation verifies integrity only; it does not check whether upstream is current.
