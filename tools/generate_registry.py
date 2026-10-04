#!/usr/bin/env python3
"""
Generate registry.json from all pack JSON files in packs/.

Computes SHA-256 checksums, file sizes, and generates download URLs
pointing to GitHub release assets.

Usage:
    python3 tools/generate_registry.py [--repo OWNER/REPO] [--tag TAG]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import re
from urllib.parse import quote
from validate_packs import validate_pack, MAX_PACK_BYTES
from datetime import datetime, timezone
from pathlib import Path


def generate_registry(
    packs_dir: Path,
    repo: str,
    tag: str,
    min_app_version: str = "0.1.0",
) -> dict:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or not re.fullmatch(r'v[0-9][a-zA-Z0-9._-]*', tag):
        raise ValueError('Invalid repository or release tag')
    packs = []

    for pack_path in sorted(packs_dir.glob("*.json")):
        raw = pack_path.read_bytes()
        sha256 = hashlib.sha256(raw).hexdigest()
        if len(raw) > MAX_PACK_BYTES: raise ValueError('Pack exceeds 8MB')
        data = json.loads(raw)
        validate_pack(data, pack_path.name)

        pack_id = data.get("id", pack_path.stem)
        download_url = (
            f"https://github.com/{repo}/releases/download/{quote(tag, safe='')}/{quote(pack_path.name, safe='')}"
        )

        packs.append(
            {
                "id": pack_id,
                "name": data.get("name", pack_id),
                "collection": data.get("collection", ""),
                "packVersion": data.get("packVersion", "0.0.0"),
                "collectionVersion": data.get("collectionVersion", ""),
                "moduleCount": len(data.get("modules", [])),
                "size": len(raw),
                "sha256": sha256,
                "downloadUrl": download_url,
                "qualityLevel": data.get("qualityLevel", "generated"),
                "minAppVersion": data.get("minAppVersion", min_app_version),
                "testedWithAppVersion": data.get(
                    "testedWithAppVersion",
                    data.get("minAppVersion", min_app_version),
                ),
                "publishedAt": data.get(
                    "publishedAt",
                    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
                "tags": data.get("tags", []),
            }
        )

    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "packs": packs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate registry.json from packs/")
    parser.add_argument(
        "--repo",
        default="voipnorm/AnsibleBlocks-packs",
        help="GitHub repo (owner/name)",
    )
    parser.add_argument(
        "--tag", default="v1.0.0", help="Release tag for download URLs"
    )
    parser.add_argument(
        "--min-app-version", default="0.1.0", help="Minimum app version"
    )
    parser.add_argument(
        "--out",
        default="registry.json",
        help="Output path (default: registry.json)",
    )
    args = parser.parse_args()

    packs_dir = Path("packs")
    if not packs_dir.exists():
        print("ERROR: packs/ directory not found", file=sys.stderr)
        sys.exit(1)

    registry = generate_registry(
        packs_dir,
        repo=args.repo,
        tag=args.tag,
        min_app_version=args.min_app_version,
    )

    out_path = Path(args.out)
    out_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {out_path} with {len(registry['packs'])} packs")
    for p in registry["packs"]:
        print(f"  {p['id']}: {p['moduleCount']} modules, {p['size']} bytes")


if __name__ == "__main__":
    main()
