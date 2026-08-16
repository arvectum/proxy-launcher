# APL-ROUTE-002 — per-application routing feasibility matrix

Status: COMPLETE. Research date: 2026-08-17. This task chooses platform architectures; it does not itself install privileged traffic interception.

## Executive decision

| Platform | User-selected installed applications | Per-app proxy/direct enforcement | Destination-aware rules | Product decision |
|---|---|---|---|---|
| Windows | **YES** | **FEASIBLE** through Windows Filtering Platform (WFP) application-layer enforcement | **YES** for IP/port conditions at ALE layers; domain identity needs DNS/hostname strategy | **P1 prototype target — APL-ROUTE-003** |
| Linux/Astra | **YES, with controlled process/cgroup identity** | **FEASIBLE** using cgroup/socket identity plus nftables marking/redirect/policy-routing architecture | IP/CIDR straightforward; domains require controlled DNS/name-resolution mapping | **P2 after Windows proof** |
| macOS | **ENTERPRISE/managed constrained** | Apple NetworkExtension supports per-app VPN/App Proxy, but official per-app configuration is tied to managed app rules/configuration profiles and entitlements | framework supports app rules/domain exclusions in managed per-app VPN scenarios | **Do not promise arbitrary consumer per-app routing in v2 without entitlement/deployment proof** |

## Windows

Microsoft's Windows Filtering Platform exposes `FWPM_CONDITION_ALE_APP_ID` at ALE connect/bind redirect layers together with remote address/port conditions. Microsoft's connect-redirection documentation states that WFP ALE callout drivers can redirect an application's connection request to a proxy service, with the proxy creating the outbound connection and maintaining redirect context.

### Architecture implication

A correct Windows implementation is not a registry/system-proxy trick and should not be approximated by changing proxy environment variables per process. The enforcement plane should be a minimal native WFP component/callout plus a local proxy/redirect service, while the existing Python desktop app remains the control plane.

The control plane compiles APL-ROUTE-001 rules into an explicit filter plan:

- application identity -> WFP application id derived from executable;
- destination CIDR/port -> ALE conditions;
- `DIRECT` -> permit/bypass Arvectum redirection;
- `PROXY` -> redirect eligible application connections to the local Arvectum proxy service;
- ownership/session id -> filter/provider/sublayer identity for deterministic cleanup.

### Boundaries

- Actual WFP redirect enforcement requires privileged/native installation and real Windows networking tests.
- Driver/service signing and secure update/removal are release/security concerns, not Python-only work.
- Domain rules cannot be treated as durable packet identities merely by resolving a domain once; DNS changes/CDNs must be modeled explicitly.

**Verdict:** best first platform; proceed with a non-mutating filter-plan prototype in APL-ROUTE-003 and keep live callout enforcement as local/native technical debt.

## Linux / Astra

The nftables project documents socket metadata matching including UID/GID and `socket cgroupv2`, allowing rules to identify traffic belonging to a cgroup v2 hierarchy. This makes per-application routing technically feasible if Arvectum owns or can reliably associate launched processes with a dedicated cgroup/systemd scope.

### Candidate architecture

1. assign opted-in applications to Arvectum-owned cgroup v2 scopes;
2. match their sockets with nftables `socket cgroupv2` (or an equivalent stable supported host mechanism);
3. mark/redirect eligible traffic to a local transparent proxy or policy-routing table;
4. keep all rules in an Arvectum-owned nftables table/chain for deterministic rollback;
5. preserve pre-existing firewall state and never flush/replace foreign tables.

### Constraints

- Selecting an already-running arbitrary application is harder than launching it into an owned scope; re-parenting processes is policy/permission sensitive.
- System services and sandboxed packages may have their own cgroup ownership constraints.
- nftables/cgroup operations are privileged and require a narrow authorization model comparable to the NetworkManager boundary already used by the product.
- domain selectors require a DNS-aware mapping/interception strategy rather than static one-time IP expansion.

**Verdict:** feasible but second after Windows; require real Astra kernel/nftables/cgroup capability acceptance before product commitment.

## macOS

Apple's NetworkExtension documentation supports source-application mode packet tunnels and App Proxy providers. Apple's per-app VPN routing documentation associates macOS app rules with MDM-managed apps, and `NEAppProxyProviderManager` configurations are created from managed `com.apple.vpn.managed.applayer` profiles. NetworkExtension providers also require the corresponding entitlement.

### Product implication

The enterprise/managed path is real, but it is not equivalent to “a normal standalone GUI lets any user pick arbitrary installed apps and transparently reroutes them” without additional Apple deployment/entitlement constraints. Therefore Arvectum should not market generic macOS per-app routing until a signed NetworkExtension prototype is accepted under the intended distribution model.

**Verdict:** keep system-proxy/domain routing in the normal macOS SKU; investigate per-app routing as an enterprise/managed capability only after Windows/Linux proof.

## Mobile note for later backlog

iOS per-app VPN is likewise MDM-managed per Apple's documentation; Android feasibility is a separate platform study and should use VPNService/per-app allow/deny capabilities rather than assumptions from desktop OSes.

## Primary references

- Microsoft Learn — Filtering conditions available at each filtering layer (`FWPM_LAYER_ALE_CONNECT_REDIRECT_*`, `FWPM_CONDITION_ALE_APP_ID`).
- Microsoft Learn — Using Bind or Connect Redirection (WFP ALE callout redirect architecture).
- Apple Developer Documentation — Routing your VPN network traffic / per-app VPN.
- Apple Developer Documentation — `NEAppProxyProviderManager`, App Proxy Provider, Packet Tunnel Provider.
- nftables official manpage — `meta skuid` and `socket cgroupv2` expressions.

## Acceptance

- [x] Windows enforcement mechanism and privilege/native boundary identified.
- [x] Linux/Astra cgroup/nftables mechanism and constraints identified.
- [x] macOS NetworkExtension/MDM entitlement constraint identified.
- [x] domain-vs-IP semantic gap recorded.
- [x] Windows chosen as first enforcement prototype.
- [x] unsupported consumer-macOS promise explicitly rejected.
