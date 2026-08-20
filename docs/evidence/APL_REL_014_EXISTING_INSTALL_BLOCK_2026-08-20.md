# APL-REL-014 owner-host first run

Date: 2026-08-20

Result: `BLOCK` before lifecycle mutation.

Reason: the owner Windows host already had Arvectum Proxy Launcher registered under the expected HKCU Inno Setup AppId. The first APL-REL-014 implementation intentionally refused to replace a registered installation.

The signed release preflight had already confirmed:

- release tag `v0.2.3-ru.2`;
- release-policy commit `47823585c42da54ab51dc2246583dc24d74d4ba6`;
- installer SHA-256 `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`.

No destructive lifecycle phase started. This block is retained as safety evidence, not as a product failure.
