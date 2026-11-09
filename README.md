<h1 align="center">AnsibleBlocks Packs</h1>

<p align="center"><strong>Downloadable Ansible module blocks for AnsibleBlocks</strong></p>

<p align="center">
  <a href="https://github.com/voipnorm/AnsibleBlocks-packs/releases/latest"><img src="https://img.shields.io/github/v/release/voipnorm/AnsibleBlocks-packs?style=flat-square" alt="Latest catalog release"></a>
  <a href="https://github.com/voipnorm/AnsibleBlocks-packs/releases"><img src="https://img.shields.io/github/downloads/voipnorm/AnsibleBlocks-packs/total?style=flat-square" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <a href="https://github.com/voipnorm/AnsibleBlocks-packs/releases/latest"><strong>Browse the latest pack release</strong></a>
  · <a href="https://github.com/voipnorm/AnsibleBlocks-releases/releases/latest">Download AnsibleBlocks</a>
</p>

## Official pack registry

This repository publishes the JSON block definitions and catalog used by AnsibleBlocks Pack Manager. Each pack maps modules from an Ansible collection to visual blocks. Install the corresponding Ansible collection on your controller to run playbooks you export from the app.

## Install or upgrade a pack

1. Open **Packs → Available** in AnsibleBlocks.
2. Choose **Install** for a new pack or **Upgrade** for a newer version of an installed pack. The app verifies registry downloads with SHA-256 checksums.
3. Restart AnsibleBlocks to load the blocks.

For manual installation, download the pack’s JSON asset from the latest release and select it under **Packs → Import**. [Latest pack release](https://github.com/voipnorm/AnsibleBlocks-packs/releases/latest)

## RoomOS compatibility

Cisco RoomOS pack `1.1.1` targets `voipnorm.roomos` collection `0.1.6` and requires AnsibleBlocks `1.0.0` or later. In-app pack upgrades are available in AnsibleBlocks `1.0.1`. New RoomOS blocks default to certificate verification. Explicit settings in existing playbooks are preserved. [RoomOS collection on Galaxy](https://galaxy.ansible.com/ui/repo/published/voipnorm/roomos/) · [Suite compatibility](suite-compatibility.json)

## Available packs

**3,804 module definitions across 37 packs.** [Machine-readable catalog](registry.json)

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
| RoomOS | `voipnorm.roomos` | 3 | 1.1.1 |

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
| Dell Enterprise SONiC | `dellemc.enterprise_sonic` | 89 | 1.0.0 |
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

## Contributing

Pack definitions live in [packs/](packs/) and are validated against the [pack schema](schema/pack.schema.json). The contribution guide covers generation, overlays, quality levels, and release validation. [Contribution guide](CONTRIBUTING.md) · [Security and delivery audit](docs/security-defect-audit-2026-10-04.md)

## Support and license

For a pack issue, include the pack version, collection version, and affected module name. [Pack issues](https://github.com/voipnorm/AnsibleBlocks-packs/issues)

The materials in this repository are available under the [MIT License](LICENSE).
