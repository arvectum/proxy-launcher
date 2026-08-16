# APL-CORE-006 — Capability model & unsupported-feature UX

Status: implemented.

## Goal

Make platform/product capabilities explicit after APL-CORE-005 automatic backend selection. UI and runtime code must not guess support from `sys.platform`, widget presence, or concrete backend internals.

## Capability model

`capability_model.py` is the canonical declaration for the governed desktop backends:

- `windows` → Windows;
- `macos` → macOS;
- `linux` → Linux / Astra Linux.

Every declared feature has one state:

- `supported` — may be executed and shown enabled;
- `unsupported` — intentionally unavailable on the selected platform;
- `planned` — product backlog capability that must remain disabled until implementation lands.

Current features:

| Feature | Windows | macOS | Linux / Astra |
|---|---|---|---|
| System proxy | supported | supported | supported |
| Bypass/no_proxy rules | supported | supported | supported |
| Ownership-aware rollback | supported | supported | supported |
| Autostart | supported | unsupported | unsupported |
| Application routing | planned | planned | planned |

Application routing is intentionally represented now because it is a known product backlog item. Declaring it prevents a future UI from accidentally implying that application-level routing already works.

## Runtime binding

`backend_runtime.capabilities_for_platform()` resolves capabilities through the same backend id selected by `backend_id_for_platform()`.

`create_backend()` also verifies that the backend id has a capability declaration. This is a fail-closed invariant: a new governed backend cannot silently appear without reviewed product capability semantics.

## Unsupported-feature UX contract

`unsupported_feature_view()` returns stable presentation data for product controls.

Rules:

1. Unsupported and planned features remain **visible**.
2. Their controls are **disabled**.
3. The UX states why the feature is unavailable instead of silently hiding it.
4. Planned features use `Запланировано`; platform-unavailable features use `Недоступно`.
5. Supported features use `Доступно` and remain enabled.
6. Execution paths may call `require_feature()`; unavailable execution fails closed with `UnsupportedFeatureError` carrying backend and feature context.

This avoids three bad states:

- a missing control looking like a rendering bug;
- a disabled control with no explanation;
- a platform-specific feature accidentally executing because a caller only checked the operating system name.

## Windows baseline preservation

APL-CORE-006 does not change the customer-confirmed Windows 0.2.3 proxy mutation path. `WindowsBackend`, `proxy_core_legacy.py`, registry/PAC ownership logic and rollback mechanics are unchanged.

The capability model sits above backend implementation and describes availability; it does not alter how supported system-proxy operations execute.

## Tests and CI

`tests/test_capability_model.py` covers:

- complete governed backend declaration;
- runtime platform → backend → capability identity;
- common safety capabilities on Windows/macOS/Linux;
- Windows-only autostart support;
- application routing remaining planned everywhere;
- visible/explained/disabled unsupported UX;
- visible/explained/disabled planned UX;
- enabled supported-feature UX;
- fail-closed `require_feature()` behavior;
- rejection of unknown backends.

The `core-backends` workflow compiles and executes these tests on Linux and macOS runners together with the existing backend contract suite.

## Acceptance

- Capability support is explicit and queryable by stable backend id.
- Backend selection and capability selection cannot drift independently.
- Unsupported/planned features have a deterministic user-facing disabled state with an explanation.
- Attempts to require an unavailable feature fail closed.
- Linux/Astra is represented as one current backend capability target.
- Known future application routing cannot be mistaken for a shipped capability.
- Existing Windows proxy implementation remains untouched.

## Follow-up

APL-CORE-007 should consume this model in the unified backend/GUI regression matrix and assert that each platform exposes only the interactions allowed by its declared capabilities.
