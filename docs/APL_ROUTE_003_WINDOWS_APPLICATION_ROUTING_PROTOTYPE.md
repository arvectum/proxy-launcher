# APL-ROUTE-003 — Windows application-routing prototype

Status: **CONTROL-PLANE / READ-ONLY WFP PROTOTYPE COMPLETE; LIVE ENFORCEMENT IS LOCAL/NATIVE TECHNICAL DEBT**.

## What is implemented

`windows_app_routing.py` uses the Windows Filtering Platform user-mode API `FwpmGetAppIdFromFileName0` to retrieve the same application identity primitive that WFP exposes as `FWPM_CONDITION_ALE_APP_ID`. The module then compiles APL-ROUTE-001 rules into a deterministic filter-plan representation for the ALE connect-redirect layers.

The prototype is deliberately non-mutating:

- it does not call `FwpmFilterAdd`, `FwpmCalloutAdd` or `FwpsCalloutRegister`;
- it does not install a driver, service, provider, sublayer or filter;
- it does not change the Windows firewall or system proxy;
- Windows CI calls the real read-only WFP application-id API for the active Python executable and proves that no live filter API was added.

CIDR/all destination plans can be represented directly. Domain plans are marked `enforcement_ready=false` until a DNS-aware address lifecycle is designed; a one-time DNS resolution is not silently treated as equivalent to a domain rule.

## Required native/local continuation

Microsoft's WFP connect-redirection architecture requires an ALE callout capable of redirecting selected application connections to a proxy service. Implementing that safely requires a native privileged component, installation/removal ownership, signing, crash/reboot recovery, loop prevention and real Windows networking acceptance.

That enforcement work is intentionally **not** fabricated in a Python/hosted-CI task. It is recorded as local/native debt after the control-plane proof.

## Acceptance

- [x] real WFP application-id retrieval wrapper;
- [x] Windows executable identity feeds rule compiler;
- [x] ALE connect-redirect layer/condition plan;
- [x] direct-vs-proxy operation represented;
- [x] CIDR/all vs DNS-domain readiness distinction;
- [x] Windows hosted read-only WFP smoke test;
- [x] CI asserts no live filter/callout registration API is present;
- [ ] native WFP callout/proxy service implementation;
- [ ] privileged installation/signing/removal;
- [ ] real browser/application redirect + recovery acceptance on Windows.
