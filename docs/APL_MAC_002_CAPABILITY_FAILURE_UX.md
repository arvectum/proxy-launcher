# APL-MAC-002 — macOS capability & failure UX

Status: implemented/tested as a deterministic UI contract.

The macOS UI contract maps preflight state to three explicit user states: ready, system authorization required, or unavailable. It never describes an unavailable host as supported merely because `sys.platform == darwin`.

Failure wording distinguishes authorization denial, missing/failing `networksetup`, and rollback/recovery failures. Messages avoid claiming that proxy settings were applied when the operation failed and keep recovery evidence visible.

- [x] ready/auth-required/unavailable UX model;
- [x] fail-closed enable semantics;
- [x] authorization is explicit and password ownership remains with macOS;
- [x] stable failure messages for authorization/system-tool/recovery errors;
- [x] deterministic tests;
- [ ] visual/manual UX acceptance on a real Mac — APL-MAC-008.
