# APL-ROUTE-004 — routing recovery / security / ownership model

Status: implemented as a durable control-plane contract. Native WFP/nftables/NetworkExtension enforcement must consume this contract before it is allowed to mutate host routing state.

## Ownership rules

Every enforcement resource created by Arvectum must have an explicit resource id under the `Arvectum.ProxyLauncher.` namespace and be listed in the durable routing ownership journal. Foreign filters, firewall tables, drivers, services or policies are never implicitly owned and must never be deleted during recovery.

## Two-phase lifecycle

1. **prepared** — canonical plan digest + exact intended owned resources are persisted atomically *before* the first host mutation;
2. **applied** — entered only after the platform adapter confirms that intended resources were installed;
3. **restoring** — entered before cleanup/rollback starts;
4. journal deletion — allowed only after restoration/resource cleanup has been explicitly verified.

A pending journal blocks a new routing session. Corrupt/unreadable evidence fails closed and remains visible for support; it is not overwritten by a new enable attempt.

## Security boundary

- the Python GUI/control plane does not receive arbitrary “delete firewall rules” authority;
- a future native privileged component should accept only schema-validated Arvectum plans/resources and use a narrow authenticated local IPC boundary;
- WFP/nftables/other resources must use stable provider/table/sublayer/chain identities scoped to Arvectum;
- proxy-loop prevention must exclude the Arvectum local proxy service's own outbound sockets from re-redirection;
- driver/helper update and uninstall must refuse to destroy ownership evidence before owned resources are verified absent/restored;
- plan SHA-256 binds the session journal to the exact canonical control-plane plan.

## Crash/reboot contract

At startup, the product checks for the routing journal before allowing new enforcement. `prepared` means a mutation may have partially happened; `applied` means owned routing resources are expected to exist; `restoring` means cleanup was interrupted. All three states require reconciliation/restore, never blind recreation.

## Acceptance

- [x] durable versioned routing ownership schema;
- [x] atomic 0600 evidence write before mutation;
- [x] plan digest binding;
- [x] Arvectum-only resource namespace enforcement;
- [x] fail-closed second-session/corrupt-state behavior;
- [x] explicit prepared/applied/restoring transitions;
- [x] evidence cannot be deleted before verified restore;
- [x] deterministic tests;
- [ ] integrate with future native Windows WFP callout/service;
- [ ] live crash/reboot/kill recovery acceptance on Windows;
- [ ] equivalent real-host enforcement acceptance for later Linux/macOS implementations.
