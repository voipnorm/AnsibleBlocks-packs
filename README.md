# AnsibleBlocks Packs

Block pack registry and JSON pack definitions for [AnsibleBlocks](https://github.com/voipnorm/AnsibleBlocks).

## Available Packs

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Catalyst Center | `cisco.dnac` | 14 | 1.0.0 |
| Cisco ACI | `cisco.aci` | 14 | 1.0.0 |
| Cisco ASA | `cisco.asa` | 4 | 1.0.0 |
| Cisco IOS | `cisco.ios` | 8 | 1.0.0 |
| Cisco IOS-XR | `cisco.iosxr` | 15 | 1.0.0 |
| Cisco NX-OS | `cisco.nxos` | 18 | 1.0.0 |
| Meraki | `cisco.meraki` | 8 | 1.0.0 |
| Netcommon | `ansible.netcommon` | 5 | 1.0.0 |

**Total: 86 modules across 8 packs**

## Structure

```
registry.json          # Pack catalog with SHA-256 checksums
schema/
  pack.schema.json     # JSON Schema for pack validation
packs/
  cisco-ios.json       # Individual pack files
  ...
```

## Installation

Packs are installed automatically through the AnsibleBlocks Pack Manager. You can also import packs manually:

1. Download a `.json` pack file from the [Releases](https://github.com/voipnorm/AnsibleBlocks-packs/releases) page
2. In AnsibleBlocks, open **Packs** > **Import**
3. Select the downloaded file

## Pack Schema

All packs conform to the JSON Schema at `schema/pack.schema.json`. See the [AnsibleBlocks documentation](https://github.com/voipnorm/AnsibleBlocks) for the full pack specification.

## License

MIT
