#!/usr/bin/env python3
"""
AnsibleBlocks Pack Generator

Generates a declarative JSON block pack from an installed Ansible collection
by querying `ansible-doc --json` for each module.

Usage:
    python3 tools/generate_pack.py cisco.ios --color '#1BA0D8'
    python3 tools/generate_pack.py arista.eos --color '#4E8CC2' --out packs/arista-eos.json

Requirements:
    - Python 3.9+
    - ansible-core installed (ansible-doc available)
    - Target collection installed via `ansible-galaxy collection install`
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import re
from datetime import datetime, timezone
from typing import Any, Optional

# ── Ansible type → pack field type mapping ────────────────────────────

TYPE_MAP: dict[str, dict[str, Any]] = {
    "str": {"type": "text"},
    "string": {"type": "text"},
    "path": {"type": "text"},
    "raw": {"type": "text", "multiline": True},
    "jsonarg": {"type": "text", "multiline": True},
    "json": {"type": "text", "multiline": True},
    "list": {"type": "text", "yamlType": "list"},
    "dict": {"type": "text", "yamlType": "dict"},
    "bool": {"type": "boolean"},
    "boolean": {"type": "boolean"},
    "int": {"type": "number"},
    "integer": {"type": "number"},
    "float": {"type": "number"},
}

# Options that are Ansible connection/runtime params, not module params
SKIP_OPTIONS = {
    "provider", "transport", "auth_pass", "authorize",
    "host", "port", "username", "password", "ssh_keyfile",
    "timeout", "context",
}

# ── Helpers ───────────────────────────────────────────────────────────


def run_ansible_doc(module_fqcn: str) -> dict[str, Any]:
    """Run ansible-doc --json for a single module and return parsed JSON."""
    result = subprocess.run(
        [sys.executable, "-m", "ansible", "doc", module_fqcn, "--json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ansible-doc failed for {module_fqcn}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def list_collection_modules(collection: str) -> list[str]:
    """List all modules in a collection using ansible-doc --list."""
    result = subprocess.run(
        [sys.executable, "-m", "ansible", "doc", "--list", "--json", "-t", "module"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ansible-doc --list failed: {result.stderr.strip()}")
    all_modules = json.loads(result.stdout)
    prefix = collection + "."
    return sorted(k for k in all_modules if k.startswith(prefix))


def sanitize_block_type(fqcn: str) -> str:
    """Convert FQCN to a valid Blockly block type: cisco.ios.ios_config → cisco_ios_config."""
    parts = fqcn.split(".")
    if len(parts) >= 3:
        # e.g. cisco.ios.ios_config → cisco_ios_config
        # But avoid double prefix: cisco.ios.ios_config → just use last two
        namespace, coll_name, module_name = parts[0], parts[1], ".".join(parts[2:])
        # If module already starts with collection prefix, don't double it
        coll_prefix = coll_name + "_"
        if module_name.startswith(coll_prefix):
            return f"{namespace}_{module_name}".replace(".", "_").replace("-", "_")
        return f"{namespace}_{coll_name}_{module_name}".replace(".", "_").replace("-", "_")
    return fqcn.replace(".", "_").replace("-", "_")


def option_to_field(key: str, opt: dict[str, Any]) -> dict[str, Any] | None:
    """Convert an ansible-doc option to a pack field definition."""
    if key in SKIP_OPTIONS:
        return None

    ansible_type = str(opt.get("type", "str")).lower()
    mapping = TYPE_MAP.get(ansible_type, {"type": "text"})

    field: dict[str, Any] = {
        "key": key,
        "fieldId": key.upper(),
        "type": mapping["type"],
        "label": key.replace("_", " "),
    }

    # Add type extras
    if "yamlType" in mapping:
        field["yamlType"] = mapping["yamlType"]
    if mapping.get("multiline"):
        field["multiline"] = True

    # Default value
    default = opt.get("default")
    if default is not None and default != "":
        if mapping["type"] == "boolean":
            field["default"] = bool(default)
        elif mapping["type"] == "number":
            try:
                field["default"] = int(default) if isinstance(default, int) else float(default)
            except (ValueError, TypeError):
                pass
        elif isinstance(default, str):
            field["default"] = default

    # Description
    desc = opt.get("description")
    if isinstance(desc, list):
        field["description"] = " ".join(str(d) for d in desc)
    elif isinstance(desc, str):
        field["description"] = desc

    # Choices → dropdown
    choices = opt.get("choices")
    if choices and isinstance(choices, list) and len(choices) <= 20:
        field["type"] = "dropdown"
        field["options"] = [[str(c), str(c)] for c in choices]
        # Remove yamlType if it was set (dropdowns don't need it)
        field.pop("yamlType", None)
        field.pop("multiline", None)

    # Required
    if opt.get("required"):
        field["required"] = True

    # Deprecated
    if opt.get("removed_in") or opt.get("deprecated"):
        field["deprecated"] = True

    # Aliases
    aliases = opt.get("aliases")
    if aliases and isinstance(aliases, list):
        field["aliases"] = aliases

    return field


def detect_structure(options: dict[str, Any]) -> tuple[dict[str, Any], str | None, list[str]]:
    """
    Detect the module structure (flat, wrapped, deep).
    Returns (structure_dict, wrapper_key_or_none, unmapped_param_keys).
    """
    unmapped: list[str] = []

    # Look for a 'config' key with suboptions — common wrapped pattern
    for key in ["config", "configuration"]:
        if key in options:
            opt = options[key]
            if isinstance(opt, dict) and "suboptions" in opt:
                ansible_type = str(opt.get("type", "")).lower()
                if ansible_type == "list":
                    return (
                        {"type": "wrapped", "wrapper": key, "wrapperType": "list-of-one"},
                        key, unmapped,
                    )
                elif ansible_type == "dict":
                    return (
                        {"type": "wrapped", "wrapper": key, "wrapperType": "object"},
                        key, unmapped,
                    )

    # Check if any option has deeply nested suboptions (Level 2+)
    for key, opt in options.items():
        if key in SKIP_OPTIONS:
            continue
        if isinstance(opt, dict) and "suboptions" in opt:
            sub = opt["suboptions"]
            if isinstance(sub, dict):
                for _sk, sv in sub.items():
                    if isinstance(sv, dict) and "suboptions" in sv:
                        unmapped.append(f"{key}.{_sk} (deep nesting)")

    return {"type": "flat"}, None, unmapped


def generate_module(fqcn: str, doc_data: dict[str, Any]) -> dict[str, Any] | None:
    """Generate a single module definition from ansible-doc output."""
    doc = doc_data.get("doc", {})
    options = doc.get("options", {})

    if not options:
        return None

    block_type = sanitize_block_type(fqcn)
    short_desc = doc.get("short_description", fqcn.split(".")[-1])
    module_name = fqcn.split(".")[-1]

    structure, wrapper_key, unmapped = detect_structure(options)

    # Determine which options to convert to fields
    fields: list[dict[str, Any]] = []
    if wrapper_key and wrapper_key in options:
        # For wrapped structures, use suboptions as fields
        wrapper_opt = options[wrapper_key]
        suboptions = wrapper_opt.get("suboptions", {})

        # Also include top-level params that aren't the wrapper
        for key, opt in options.items():
            if key == wrapper_key or key in SKIP_OPTIONS:
                continue
            if isinstance(opt, dict):
                field = option_to_field(key, opt)
                if field:
                    field["topLevel"] = True
                    fields.append(field)

        # Then add wrapped suboptions
        for key, opt in suboptions.items():
            if key in SKIP_OPTIONS:
                continue
            if isinstance(opt, dict):
                # Skip deeply nested suboptions (Level 2+)
                if "suboptions" in opt:
                    unmapped.append(f"{wrapper_key}.{key} (has suboptions)")
                    continue
                field = option_to_field(key, opt)
                if field:
                    fields.append(field)
    else:
        # Flat structure — all options become fields
        for key, opt in options.items():
            if key in SKIP_OPTIONS:
                continue
            if isinstance(opt, dict):
                if "suboptions" in opt:
                    unmapped.append(f"{key} (has suboptions)")
                    continue
                field = option_to_field(key, opt)
                if field:
                    fields.append(field)

    if not fields:
        return None

    # Always add state field if it exists in options
    module_def: dict[str, Any] = {
        "fqcn": fqcn,
        "blockType": block_type,
        "label": module_name,
        "tooltip": str(short_desc),
        "helpUrl": f"https://docs.ansible.com/ansible/latest/collections/{fqcn.replace('.', '/')}_module.html",
        "structure": structure,
        "fields": fields,
    }

    if unmapped:
        module_def["unmappedParams"] = unmapped

    return module_def


# ── Main ──────────────────────────────────────────────────────────────


def generate_pack(
    collection: str,
    color: str,
    version_override: str | None = None,
) -> dict[str, Any]:
    """Generate a complete pack definition for an Ansible collection."""

    print(f"Listing modules in {collection}...")
    modules = list_collection_modules(collection)
    print(f"Found {len(modules)} modules")

    if not modules:
        print(f"ERROR: No modules found for collection '{collection}'", file=sys.stderr)
        sys.exit(1)

    # Derive pack metadata
    pack_id = collection.replace(".", "-")
    coll_parts = collection.split(".")
    pack_name = " ".join(p.upper() if len(p) <= 3 else p.title() for p in coll_parts)

    # Get collection version
    coll_version = version_override or "unknown"
    if not version_override:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ansible", "galaxy", "collection", "list", collection],
                capture_output=True, text=True, timeout=15,
            )
            for line in result.stdout.splitlines():
                if collection in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        coll_version = parts[1]
                        break
        except Exception:
            pass

    # Generate module definitions
    module_defs: list[dict[str, Any]] = []
    skipped: list[str] = []

    for fqcn in modules:
        short_name = fqcn.split(".")[-1]
        print(f"  Processing {short_name}...", end=" ")

        try:
            doc_data = run_ansible_doc(fqcn)
            if fqcn not in doc_data:
                print("SKIP (no doc)")
                skipped.append(fqcn)
                continue

            module_def = generate_module(fqcn, doc_data[fqcn])
            if module_def:
                module_defs.append(module_def)
                n_fields = len(module_def["fields"])
                unmapped = len(module_def.get("unmappedParams", []))
                status = f"OK ({n_fields} fields"
                if unmapped:
                    status += f", {unmapped} unmapped"
                status += ")"
                print(status)
            else:
                print("SKIP (no fields)")
                skipped.append(fqcn)
        except Exception as e:
            print(f"ERROR: {e}")
            skipped.append(fqcn)

    # Build block/category style names
    style_base = re.sub(r"[^a-z0-9]", "_", pack_id.replace("-", "_"))

    pack: dict[str, Any] = {
        "schemaVersion": 1,
        "packVersion": "1.0.0",
        "id": pack_id,
        "name": pack_name,
        "collection": collection,
        "collectionVersion": coll_version,
        "minAppVersion": "1.0.0",
        "testedWithAppVersion": "0.1.0",
        "publishedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "qualityLevel": "generated",
        "source": "generated",
        "categoryColor": color,
        "blockStyleName": f"{style_base}_blocks",
        "categoryStyleName": f"{style_base}_category",
        "modules": module_defs,
    }

    print(f"\n{'='*60}")
    print(f"Pack: {pack_name} ({pack_id})")
    print(f"Collection: {collection} v{coll_version}")
    print(f"Modules: {len(module_defs)} generated, {len(skipped)} skipped")
    if skipped:
        print(f"Skipped: {', '.join(s.split('.')[-1] for s in skipped)}")
    print(f"Quality: generated")
    print(f"{'='*60}")

    return pack


def main():
    parser = argparse.ArgumentParser(
        description="Generate an AnsibleBlocks pack from an Ansible collection",
    )
    parser.add_argument("collection", help="Collection FQCN, e.g. cisco.ios")
    parser.add_argument("--color", default="#6B7280", help="Hex color for the category (default: gray)")
    parser.add_argument("--out", help="Output file path (default: packs/{collection-id}.json)")
    parser.add_argument("--version", help="Override collection version string")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-print JSON (default)")

    args = parser.parse_args()

    pack = generate_pack(args.collection, args.color, args.version)

    out_path = args.out or f"packs/{args.collection.replace('.', '-')}.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
        f.write("\n")

    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
