# AnsibleBlocks Packs

Block pack registry and JSON pack definitions for [AnsibleBlocks](https://github.com/voipnorm/AnsibleBlocks).

## Available Packs

### Ansible Core

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Ansible Builtin | `ansible.builtin` | 71 | 1.0.0 |
| Ansible POSIX | `ansible.posix` | 13 | 1.0.0 |
| Ansible Windows | `ansible.windows` | 65 | 1.0.0 |
| Netcommon | `ansible.netcommon` | 5 | 1.0.0 |

### Networking — Cisco

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Catalyst Center | `cisco.dnac` | 14 | 1.0.0 |
| Cisco ACI | `cisco.aci` | 14 | 1.0.0 |
| Cisco ASA | `cisco.asa` | 4 | 1.0.0 |
| Cisco IOS | `cisco.ios` | 8 | 1.0.0 |
| Cisco IOS-XR | `cisco.iosxr` | 15 | 1.0.0 |
| Cisco NX-OS | `cisco.nxos` | 18 | 1.0.0 |
| Meraki | `cisco.meraki` | 8 | 1.0.0 |

### Networking — Multi-Vendor

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Arista EOS | `arista.eos` | 33 | 1.0.0 |
| Juniper Device | `juniper.device` | 54 | 1.0.0 |
| Palo Alto PAN-OS | `paloaltonetworks.panos` | 118 | 1.0.0 |
| F5 BIG-IP | `f5networks.f5_modules` | 177 | 1.0.0 |
| Fortinet FortiOS | `fortinet.fortios` | 709 | 1.0.0 |
| Check Point MGMT | `check_point.mgmt` | 408 | 1.0.0 |
| VyOS | `vyos.vyos` | 28 | 1.0.0 |
| Infoblox NIOS | `infoblox.nios_modules` | 35 | 1.0.0 |

### Cloud & Infrastructure

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Amazon AWS | `amazon.aws` | 141 | 1.0.0 |
| Azure | `azure.azcollection` | 442 | 1.0.0 |
| Google Cloud | `google.cloud` | 198 | 1.0.0 |
| VMware vSphere | `community.vmware` | 171 | 1.0.0 |
| Docker | `community.docker` | 37 | 1.0.0 |
| Kubernetes | `kubernetes.core` | 21 | 1.0.0 |
| Terraform | `cloud.terraform` | 3 | 1.0.0 |
| Hetzner Cloud | `hetzner.hcloud` | 40 | 1.0.0 |

### Security & Identity

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| HashiCorp Vault | `community.hashi_vault` | 25 | 1.0.0 |
| FreeIPA | `freeipa.ansible_freeipa` | 104 | 1.0.0 |
| Community Crypto | `community.crypto` | 37 | 1.0.0 |

### Monitoring & Observability

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Grafana | `grafana.grafana` | 9 | 1.0.0 |
| Zabbix | `community.zabbix` | 48 | 1.0.0 |
| Splunk ES | `splunk.es` | 17 | 1.0.0 |

### General & Windows

| Pack | Collection | Modules | Version |
|------|-----------|---------|---------|
| Community General | `community.general` | 568 | 1.0.0 |
| Community Windows | `community.windows` | 54 | 1.0.0 |

**Total: 3,821 modules across 35 packs**

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
