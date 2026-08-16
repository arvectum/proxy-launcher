# APL-LNX-002 — Linux/Astra NetworkManager preflight & operational capability detection

Status: implemented

## Goal

Convert the Linux/Astra runtime fingerprint from APL-LNX-001 into a deterministic, read-only operational verdict for the NetworkManager backend before any proxy mutation is attempted.

## Public API

`linux_networkmanager_preflight.detect_networkmanager_preflight()` returns immutable `NetworkManagerPreflight` evidence with:

- APL-LNX-001 runtime facts;
- `nmcli` version;
- NetworkManager daemon state and connectivity state;
- all active connection UUIDs and the subset eligible for the proxy backend;
- explicit support for `proxy.method`, `proxy.browser-only`, `proxy.pac-url` and `proxy.pac-script` on an active managed profile;
- NetworkManager `modify.system` and `modify.own` permission values;
- governed status: `ready`, `auth_required`, or `unavailable`;
- stable human-readable reasons when the host is not immediately ready.

## Readiness semantics

### `ready`

Returned only when all of the following are true:

1. `nmcli` is present and executable;
2. the NetworkManager daemon is reachable through `nmcli general status`;
3. at least one active non-VPN, non-loopback profile has a real device;
4. all four NetworkManager WWW proxy properties used by `LinuxBackend` can be read on that profile;
5. `nmcli general permissions` reports `yes` for either system-profile or own-profile modification.

### `auth_required`

Returned when all technical checks pass, but NetworkManager reports `auth` instead of `yes`. This is deliberately distinct from `ready`: the product may later invoke an explicit PolicyKit-authorized flow, but the preflight itself never triggers an authorization prompt.

### `unavailable`

Returned for missing `nmcli`, unreachable NetworkManager, no eligible active managed connection, unavailable proxy setting surface, unreadable permissions, or explicit `no`/unknown mutation permission.

## Safety boundary

The preflight is strictly observational. It does **not**:

- install packages;
- start, stop, enable, reload, or restart NetworkManager;
- modify a connection profile;
- run `sudo`;
- invoke PolicyKit authorization;
- cycle a network interface;
- create rollback state.

This keeps capability discovery safe on customer and Astra Linux systems.

## Astra Linux basis

Astra Linux documentation states that `nmcli` is the NetworkManager command-line client and recommends `nmcli general permissions` to inspect the current user's permissions. It also documents that interfaces listed in legacy `/etc/network/interfaces` locations may be outside NetworkManager control, which is why APL-LNX-002 requires a real active NetworkManager profile instead of inferring support from distro identity alone.

Current Astra Linux Special Edition 1.8 documentation notes that, when NetworkManager is present, default interface configuration no longer lists ordinary interfaces in the legacy locations, improving the normal NetworkManager path while still requiring runtime verification.

## NetworkManager basis

Upstream NetworkManager defines the connection-profile WWW proxy setting with:

- `proxy.method`: `none` or `auto`;
- `proxy.browser-only`: boolean;
- `proxy.pac-url`: PAC URL;
- `proxy.pac-script`: PAC script.

These are exactly the properties already used by the Linux backend.

## Verification

`tests/test_linux_networkmanager_preflight.py` covers:

1. fully ready NetworkManager host;
2. PolicyKit authorization-required state;
3. missing `nmcli` with zero command execution;
4. unreachable NetworkManager daemon;
5. VPN/loopback-only active connections;
6. missing proxy property support;
7. explicit modification denial.

All command execution is injected in tests, so regression coverage is deterministic and does not mutate CI runner networking.

## Official references

- Astra Linux network configuration / NetworkManager: https://wiki.astralinux.ru/pages/viewpage.action?pageId=3277370
- NetworkManager `nm-settings-nmcli` proxy setting: https://www.networkmanager.dev/docs/api/latest/nm-settings-nmcli.html
- NetworkManager `NMSettingProxy`: https://www.networkmanager.dev/docs/libnm/latest/NMSettingProxy.html
