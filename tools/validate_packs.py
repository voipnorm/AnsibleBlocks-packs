#!/usr/bin/env python3
"""Validate the producer schema, security invariants and registry byte identity."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MAX_PACK_BYTES = 8 * 1024 * 1024
FORBIDDEN = {"__proto__", "prototype", "constructor"}
SCHEMA = json.loads((ROOT / "schema/pack.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def safe_data(value, depth=0):
    if depth > 50:
        raise ValueError("Input too deeply nested")
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN:
                raise ValueError(f"Unsafe property {key}")
            safe_data(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            safe_data(child, depth + 1)


def validate_pack(data: dict, filename: str | None = None) -> None:
    VALIDATOR.validate(data)
    safe_data(data)
    if data["id"] == "index" or (filename and filename != f'{data["id"]}.json'):
        raise ValueError("Reserved ID or filename/ID mismatch")
    if data.get('blockStyleName') in FORBIDDEN or data.get('categoryStyleName') in FORBIDDEN:
        raise ValueError('Unsafe style name')
    blocks, modules = set(), set()
    for module in data["modules"]:
        block, fqcn = module["blockType"], module["fqcn"]
        if block in FORBIDDEN or block in {"ansible_play", "ansible_task", "ansible_vars", "ansible_when", "ansible_loop", "ansible_block_rescue", "generic_module"} or block in blocks or fqcn in modules:
            raise ValueError("Duplicate or reserved module/block type")
        blocks.add(block)
        modules.add(fqcn)
        if not fqcn.startswith(data["collection"] + "."):
            raise ValueError("Module does not belong to collection")
        url = urlparse(module["helpUrl"])
        if url.scheme != "https" or not url.netloc or url.username or url.password:
            raise ValueError("Unsafe documentation URL")
        if module["structure"].get("wrapper") in FORBIDDEN:
            raise ValueError("Unsafe wrapper")
        fields = set()
        for field in module["fields"]:
            if field["key"] in FORBIDDEN or (module.get("supportsRawParams") and field["fieldId"] == "RAW_PARAMS"):
                raise ValueError("Unsafe or duplicate field")
            fields.add(field["fieldId"])
            if field["type"] == "dropdown" and not field.get("options"):
                raise ValueError("Empty dropdown")
            path = field.get("yamlPath")
            if path:
                if len(path) > 500:
                    raise ValueError("YAML path too long")
                for part in path.split("."):
                    match = re.fullmatch(r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\[(\d+)\])?", part)
                    if not match or match[1] in FORBIDDEN or (match[2] and int(match[2]) > 999):
                        raise ValueError("Unsafe YAML path")


def validate_repository(root: Path, registry_path: Path | None = None) -> None:
    packs = {}
    for path in sorted((root / "packs").glob("*.json")):
        raw = path.read_bytes()
        if len(raw) > MAX_PACK_BYTES:
            raise ValueError(f"{path.name}: exceeds 8MB")
        data = json.loads(raw)
        validate_pack(data, path.name)
        packs[data["id"]] = (data, raw)
    registry = json.loads((registry_path or root / "registry.json").read_text(encoding="utf-8"))
    if registry["schemaVersion"] != 1 or len(registry["packs"]) != len(packs):
        raise ValueError("Registry inventory mismatch")
    seen = set()
    for entry in registry["packs"]:
        if entry["id"] not in packs or entry["id"] in seen:
            raise ValueError("Unknown or duplicate registry ID")
        seen.add(entry["id"])
        data, raw = packs[entry["id"]]
        if entry["sha256"] != hashlib.sha256(raw).hexdigest() or entry["size"] != len(raw) or entry["moduleCount"] != len(data["modules"]):
            raise ValueError(f'{entry["id"]}: byte identity mismatch')
        for key in ["name", "collection", "packVersion", "collectionVersion", "minAppVersion", "qualityLevel"]:
            if entry[key] != data[key]:
                raise ValueError(f'{entry["id"]}: {key} mismatch')
        url = urlparse(entry["downloadUrl"])
        if url.scheme != "https" or url.netloc != "github.com" or not re.fullmatch(r"/voipnorm/AnsibleBlocks-packs/releases/download/v[0-9][a-zA-Z0-9._-]*/[a-z][a-z0-9_-]*\.json", url.path) or url.query or url.fragment:
            raise ValueError("Unsafe registry URL")
    compatibility = json.loads((root / "suite-compatibility.json").read_text(encoding="utf-8"))
    components = compatibility["components"]
    roomos = packs["voipnorm-roomos"][0]
    for actual, expected in [
        (roomos["schemaVersion"], components["ansibleBlocks"]["packSchemaVersion"]),
        (roomos["packVersion"], components["ansibleBlocksPacks"]["roomosPackVersion"]),
        (roomos["collectionVersion"], components["roomosCollection"]["version"]),
        (roomos["collection"], components["roomosCollection"]["galaxyName"]),
    ]:
        if actual != expected:
            raise ValueError("Suite compatibility drift")
    print(f"Validated {len(packs)} packs, schema, registry identity and compatibility")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    validate_repository(ROOT, args.registry)
