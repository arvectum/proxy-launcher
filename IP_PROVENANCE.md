# IP_PROVENANCE.md — Arvectum Proxy Launcher source provenance

Status: **AUTOMATED BASELINE COMPLETE / HUMAN-LEGAL SIGN-OFF PENDING**

This record defines the repository provenance boundary for APL-IP-001. It does not claim that an automated scan can establish copyright authorship or legal ownership by itself.

## Repository-authored source boundary

Arvectum-owned/product source is maintained in this repository and includes the top-level Python product modules, platform backends/runtime/preflight/diagnostics/autostart modules, PowerShell/shell build and release scripts, Inno Setup configuration, tests, GitHub/GitVerse CI definitions, product documentation and Arvectum-created visual assets.

No third-party source tree is intentionally vendored into the repository. Third-party components enter release artifacts through the controlled build/package toolchains or host operating-system interfaces and must be represented by the SBOM/third-party notices rather than being relabeled as Arvectum source.

## Automated provenance evidence

`tools/ip_provenance_check.py`:

1. obtains the version-controlled source inventory from `git ls-files`;
2. hashes each governed source/build/config file with SHA-256;
3. records size, path and source category in a deterministic JSON manifest;
4. identifies source files containing common third-party/generated-code markers for mandatory review rather than silently accepting them;
5. rejects an empty source inventory and writes evidence under `artifacts/ip-provenance/`.

The manifest is CI evidence, not a copyright certificate.

## Third-party boundary

- CPython / Python standard library — upstream Python Software Foundation ecosystem, frozen into desktop artifacts where applicable.
- Tcl/Tk — upstream Tcl/Tk ecosystem, used by Tkinter GUI builds.
- PyInstaller and its build dependency set — build/freezer dependencies, exact versions governed by `requirements-build.lock.txt`.
- AppImage type-2 runtime — Linux AppImage distribution only; separately hash pinned and licensed upstream; it includes additional statically linked OSS components documented in `THIRD_PARTY_NOTICES.txt`.
- Inno Setup — Windows installer build-time dependency; not part of portable runtime.
- Windows/macOS/Linux host system APIs and tools — platform dependencies, not Arvectum-authored code.

## Human-authorship / legal review boundary

Before declaring a clean IP baseline/tag, an authorized human reviewer for ООО «Арвектум» must:

- review all material product modules and confirm the intended source provenance/creative contribution;
- investigate any provenance-review findings produced by CI;
- review source history for imported/copied fragments that tooling cannot reliably classify;
- reconcile final shipped SBOM with `THIRD_PARTY_NOTICES.txt` and applicable license texts;
- verify that employee/contractor/AI-assisted contribution records support the chain of exclusive rights claimed by ООО «Арвектум»;
- approve any deliberate third-party code inclusion and its license obligations;
- sign the clean-baseline record and only then create the legal/provenance baseline tag.

Git history must not be rewritten or artificially removed to manufacture provenance. AI assistance, where used, is treated as a review/audit concern; meaningful modules require human review rather than a false claim that tooling proves human authorship.

## Baseline verdict

- Automated source inventory/hash manifest: **implemented**.
- Dependency/stack sovereignty audits: **implemented, conditional**.
- Third-party notices baseline: **implemented and cross-platform scoped**.
- Automated suspicious provenance marker surfacing: **implemented**.
- Human review of significant modules: **PENDING — HUMAN ACTION**.
- Legal chain-of-title review for ООО «Арвектум»: **PENDING — HUMAN/LEGAL ACTION**.
- Clean IP baseline/tag: **BLOCKED until the two preceding reviews are signed off**.
