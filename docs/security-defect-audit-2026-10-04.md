# Pack producer security and delivery audit — 2026-10-04 UTC

Baseline: `afdaca2d5e774a98b4e29599259b626e88a61502`. All validated producer findings
below are fixed and tested. The companion AnsibleBlocks audit documents consumer
fixes, including path traversal, prototype pollution, template execution,
collection argument injection and enforced download provenance.

| Finding/defect | Correction | Evidence |
| --- | --- | --- |
| Release tag shell injection, medium with tag-push prerequisite | Remove expression interpolation from shell scripts; environment arguments are quoted, tags must be vMAJOR.MINOR.PATCH, source must be on main. | Malicious tag rejection and actionlint. |
| Registry advertised unavailable assets | Draft release stages all assets and manifest; publish before updating discovery. Normal fast-forward push rejects concurrent drift. | Workflow inspection and exact-byte manifest tests. |
| Source CI would require premature registry updates | Validate a temporary candidate manifest; keep main's published discovery unchanged until release. | Unpublished-source regression test. |
| Shallow validation and consumer schema drift | Shared bounded JSON Schema plus semantic checks for IDs, reserved keys, collection/FQCN identity, HTTPS docs, path grammar, size and inventory/checksum identity. | All 37 packs validate; schema matches the consumer exactly. |
| Generator default/field defects | Correct string false, unset invalid defaults, normalize/deduplicate wrapper field IDs, preserve raw parameters, validate outputs and collection names before external tools. | Generator unit tests. |
| Overlay mutation/data loss | Deep-copy input and preserve fields with duplicate YAML keys when reordering; select overrides by field ID or key. | Mutation and duplicate-key regression tests. |
| Mutable actions/unbounded validator dependency resolution | Pin official actions to immutable commits, use six exact Python dependency pins, read-only validation token and serialized write-token release job. | actionlint and pip-audit: zero known advisories at audit time. |

Ten producer tests pass. The companion app constructs/extracts/applies every
module from all 37 producer packs in real Blockly and exercises actual Electron
workflows with temporary mock files. Original pack asset and registry bytes remain
unchanged, preserving published checksums and URLs. Legacy pack normalization is
performed in consumer memory; it does not rewrite installed asset bytes.

Use Python 3.10+ and `tools/requirements.txt`; follow CONTRIBUTING.md for source
validation. `python tools/validate_packs.py` checks exact identity against the
checked-in published registry, appropriate when source equals that release.
For unreleased edits, generate and validate a temporary candidate as CI does.

No new release was published. GitHub branch/tag protection, release account access
and signing keys require owner-controlled service settings. Checksums authenticate
assets against the trusted registry, not against an independently compromised
publisher. The release workflow has been statically checked but not exercised
with a real publication token. Third-party Ansible collection implementation and
device behavior are outside the producer audit. These results are a bounded
review and cannot establish absence of all future security issues or defects.
