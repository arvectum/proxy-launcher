# APL-LNX-009 — Debian/Ubuntu CI acceptance

Status: CI acceptance implemented. This is not a substitute for APL-LNX-010 real Astra Linux acceptance.

The acceptance matrix runs on clean Ubuntu 22.04 and 24.04 GitHub-hosted runners and exercises the governed Linux source/test suite plus both release-form package formats.

## Matrix

- all `test_linux*.py` contract/regression tests;
- canonical PyInstaller Linux build;
- `.deb` build, real dpkg install on the ephemeral runner, removal, and preservation of a synthetic per-user state marker;
- AppImage build using the pinned toolchain and extraction inspection without FUSE;
- version/commit evidence artifact.

The Debian lifecycle deliberately uses `--force-depends` because dependency resolution is not the subject of this isolated package lifecycle test; package metadata itself still declares `network-manager`. No package maintainer scripts exist, so install/remove cannot alter proxy state.

## Acceptance criteria

- [x] Ubuntu 22.04 CI lane.
- [x] Ubuntu 24.04 CI lane.
- [x] Linux unit/contract suite included.
- [x] `.deb` install/remove lifecycle included.
- [x] User-owned state preservation asserted.
- [x] AppImage structure/extraction acceptance included.
- [x] Evidence identifies OS, product version and commit.
- [ ] Astra Linux graphical/runtime acceptance — APL-LNX-010 local technical debt.
