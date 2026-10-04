# Contributing to AnsibleBlocks Packs

## Pack Types

| Quality Level | Description |
|---------------|-------------|
| `official` | First-party maintained, hand-crafted, fully tested |
| `curated` | Generated + human-reviewed, improved labels and field ordering |
| `generated` | Machine-generated from `ansible-doc`, functional but raw |
| `community` | Third-party contributions, not first-party guaranteed |

## Generating a New Pack

### Prerequisites

- Python 3.9+
- `ansible-core` installed
- Target collection installed: `ansible-galaxy collection install <collection>`

### Steps

1. **Install the collection:**
   ```bash
   ansible-galaxy collection install arista.eos
   ```

2. **Generate the pack:**
   ```bash
   python3 tools/generate_pack.py arista.eos --color '#4E8CC2'
   ```

3. **Review the output** in `packs/arista-eos.json`:
   - Check module count and field types
   - Note any `unmappedParams` for deep-nested modules
   - Verify `structure` detection (flat vs wrapped)

4. **(Optional) Create a curated overlay** in `overlays/arista-eos.json` to improve UX:
   ```bash
   python3 tools/apply_overlay.py packs/arista-eos.json overlays/arista-eos.json --out packs/arista-eos.json
   ```

5. **Validate** the pack loads in AnsibleBlocks via Import.

## Creating a Curated Overlay

Overlays improve generated packs without re-running the generator. Create a JSON file in `overlays/`:

```json
{
  "qualityLevel": "curated",
  "source": "generated+curated",
  "modules": {
    "vendor.collection.module_name": {
      "tooltip": "Improved tooltip text",
      "fieldOrder": ["name", "state", "config"],
      "fieldOverrides": {
        "name": { "label": "device name", "required": true }
      },
      "hideFields": ["provider"],
      "advancedFields": ["timeout", "retries"]
    }
  }
}
```

### Overlay fields

| Field | Effect |
|-------|--------|
| `fieldOrder` | Reorders fields (unlisted fields appear after) |
| `fieldOverrides` | Merge overrides into matching fields by key |
| `hideFields` | Remove fields from the pack entirely |
| `advancedFields` | Mark fields as `advanced: true` (hidden in beginner mode) |

## Submitting a Pack

1. Fork this repo
2. Generate and/or curate your pack
3. Run the CI validation locally:
   ```bash
   python3 -m pip install -r tools/requirements.txt
   python3 -m unittest discover -s tests -v
   python3 tools/generate_registry.py --repo voipnorm/AnsibleBlocks-packs --tag v0.0.0 --out /tmp/candidate-registry.json
   python3 tools/validate_packs.py --registry /tmp/candidate-registry.json
   ```
4. Open a PR with:
   - The pack JSON in `packs/`
   - Any overlay in `overlays/`
   - Leave the published `registry.json` unchanged. CI validates a temporary
     candidate manifest; the release workflow updates discovery after publishing
     all assets. Use Python 3.10 or newer for these tools.

## Pack Schema

All packs must conform to `schema/pack.schema.json`. Key constraints:

- `schemaVersion: 1`
- `id`, `name`, `collection`, `modules` are required
- Max 1,000 modules per pack
- Max 8MB file size
- Each module needs `fqcn`, `blockType`, `label`, `structure`, `fields`

Semantic checks also reject escaping IDs, reserved object properties, unsafe
YAML paths, invalid collection names, and module/block collisions. Keep the
producer schema synchronized with `src/shared/packSchema.json` in AnsibleBlocks.

Release tags must be `vMAJOR.MINOR.PATCH` and point to a commit on main. Releases
are staged as drafts with every pack and its checksum manifest, published, then
advertised by updating `registry.json`. The registry push is a normal fast-forward
push; branch protection or concurrent main changes can reject it safely. In that
case, maintainers must reconcile the manifest from the published release before
advertising it. Never replace already published asset bytes under the same tag.

## File Structure

```
packs/              # Pack JSON files
overlays/           # Curated overlay files
schema/             # JSON Schema
tools/
  generate_pack.py  # Auto-generator from ansible-doc
  apply_overlay.py  # Overlay applicator
registry.json       # Pack catalog with SHA-256 checksums
```
