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
   python3 -c "import json; json.load(open('packs/your-pack.json'))"
   ```
4. Open a PR with:
   - The pack JSON in `packs/`
   - Any overlay in `overlays/`
   - Updated `registry.json` entry (maintainers will help with checksums)

## Pack Schema

All packs must conform to `schema/pack.schema.json`. Key constraints:

- `schemaVersion: 1`
- `id`, `name`, `collection`, `modules` are required
- Max 200 modules per pack
- Max 2MB file size
- Each module needs `fqcn`, `blockType`, `label`, `structure`, `fields`

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
