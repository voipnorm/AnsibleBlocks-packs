#!/usr/bin/env python3
"""
AnsibleBlocks Curated Overlay Applicator

Merges a curated overlay JSON on top of a generated pack to improve UX:
  - reorder fields
  - rename labels / descriptions
  - hide advanced fields
  - add field groups
  - override structure hints
  - set quality level to 'curated'

Usage:
    python3 tools/apply_overlay.py packs/ansible-builtin.json overlays/ansible-builtin.json
    python3 tools/apply_overlay.py packs/ansible-builtin.json overlays/ansible-builtin.json --out packs/ansible-builtin.json

Overlay format:
    {
      "qualityLevel": "curated",
      "source": "generated+curated",
      "modules": {
        "ansible.builtin.copy": {
          "label": "copy",
          "tooltip": "Copy files to remote hosts",
          "fieldOrder": ["src", "dest", "mode", "owner", "group"],
          "fieldOverrides": {
            "src":  { "label": "source path", "required": true },
            "dest": { "label": "destination path", "required": true }
          },
          "hideFields": ["attributes", "unsafe_writes"],
          "advancedFields": ["backup", "checksum", "directory_mode"]
        }
      }
    }
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from typing import Any


def apply_overlay(pack: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Apply a curated overlay on top of a generated pack."""
    result = copy.deepcopy(pack)

    # Pack-level overrides
    for key in ["qualityLevel", "source", "name", "categoryColor"]:
        if key in overlay:
            result[key] = overlay[key]

    module_overlays = overlay.get("modules", {})
    if not module_overlays:
        return result

    for module_def in result.get("modules", []):
        fqcn = module_def["fqcn"]
        mod_overlay = module_overlays.get(fqcn)
        if not mod_overlay:
            continue

        # Simple scalar overrides
        for key in ["label", "tooltip", "helpUrl"]:
            if key in mod_overlay:
                module_def[key] = mod_overlay[key]

        # Structure override
        if "structure" in mod_overlay:
            module_def["structure"].update(mod_overlay["structure"])

        fields = module_def.get("fields", [])
        fields_by_key = {f["key"]: f for f in fields}

        # Apply field-level overrides
        field_overrides = mod_overlay.get("fieldOverrides", {})
        for field_key, overrides in field_overrides.items():
            if field_key in fields_by_key:
                fields_by_key[field_key].update(overrides)

        # Mark fields as hidden (remove from fields list)
        hide_fields = set(mod_overlay.get("hideFields", []))
        if hide_fields:
            fields = [f for f in fields if f["key"] not in hide_fields]

        # Mark fields as advanced
        advanced_fields = set(mod_overlay.get("advancedFields", []))
        for field in fields:
            if field["key"] in advanced_fields:
                field["advanced"] = True

        # Reorder fields
        field_order = mod_overlay.get("fieldOrder")
        if field_order:
            ordered: list[dict[str, Any]] = []
            remaining = {f["key"]: f for f in fields}
            for key in field_order:
                if key in remaining:
                    ordered.append(remaining.pop(key))
            # Append any fields not in the order list
            ordered.extend(remaining.values())
            fields = ordered

        module_def["fields"] = fields

    return result


def main():
    parser = argparse.ArgumentParser(description="Apply a curated overlay to a generated pack")
    parser.add_argument("pack", help="Path to the generated pack JSON")
    parser.add_argument("overlay", help="Path to the overlay JSON")
    parser.add_argument("--out", help="Output path (default: stdout)")

    args = parser.parse_args()

    with open(args.pack) as f:
        pack = json.load(f)
    with open(args.overlay) as f:
        overlay = json.load(f)

    result = apply_overlay(pack, overlay)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
        print(f"Wrote curated pack to {args.out}", file=sys.stderr)
    else:
        json.dump(result, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
