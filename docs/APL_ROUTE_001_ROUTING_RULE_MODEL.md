# APL-ROUTE-001 — routing rule model

Status: implemented/tested as a platform-neutral control-plane schema; it performs no traffic interception or privileged mutation.

The model separates:

- routing action: `proxy` or `direct`;
- application identity: Windows executable path, macOS bundle id/path, Linux executable/package id;
- destination selector: all traffic, normalized IDNA domain, or canonical IPv4/IPv6 CIDR;
- rule identity, priority, enable state and description;
- deterministic JSON serialization/versioning.

Rules with the broad `all` selector cannot mix narrower destinations. Application identities require a stable platform-specific identifier. Ordering is deterministic by priority then rule id.

This domain model intentionally does not promise that every selector/action combination is enforceable on every OS. APL-ROUTE-002 owns that feasibility decision and platform-specific adapters must reject unsupported plans rather than silently approximate them.

- [x] cross-platform application identity model;
- [x] domain/CIDR/all destination model;
- [x] direct/proxy action model;
- [x] deterministic ordering and schema-versioned serialization;
- [x] validation/canonicalization tests;
- [x] no OS mutation/enforcement dependency.
