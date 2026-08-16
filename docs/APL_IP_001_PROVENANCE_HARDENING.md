# APL-IP-001 — IP provenance & human-authorship hardening

Status: **AUTONOMOUS/CI PORTION COMPLETE; HUMAN/LEGAL SIGN-OFF REQUIRED**.

## Completed autonomously

- cross-platform dependency/sovereignty audits completed first;
- repository source/build/config inventory is generated from Git and SHA-256 hashed;
- common generated/third-party source markers are surfaced as review findings rather than ignored;
- `IP_PROVENANCE.md` defines owned-source and third-party boundaries;
- `THIRD_PARTY_NOTICES.txt` now covers Windows/Linux/macOS artifact classes and distinguishes build-only/host dependencies;
- provenance evidence is generated and uploaded on CI;
- tests prevent automation from claiming human/legal sign-off or clean-baseline completion.

## Required human/legal completion

The following cannot be established honestly by CI and remain technical/legal debt:

1. human review of significant application/backend/recovery/routing modules and any CI review findings;
2. review of commit/source history for imported fragments and any non-trivial AI-assisted contributions;
3. final SBOM-vs-notices reconciliation against the exact production artifacts;
4. confirmation of employee/contractor contribution agreements and transfer/ownership documents for ООО «Арвектум»;
5. authorized approval of the clean IP baseline and creation of the provenance tag only after that approval.

No Git-history deletion/rewrite is part of the remediation plan. Ambiguous or template-like code should be reviewed and, where necessary, deliberately rewritten by an authorized human contributor with the new reasoning/design recorded in normal Git history.

## Verdict

The repository now has a machine-verifiable provenance **baseline**, not a machine-issued authorship certificate. APL-IP-001 remains `HUMAN SIGN-OFF PENDING` until the legal/human steps above are completed; all autonomous engineering controls for this roadmap task are present.
