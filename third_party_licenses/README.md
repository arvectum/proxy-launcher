# Pinned third-party license fallback texts

This directory contains **license text only**. It contains no executable third-party code.

APL-IP-004 normally collects complete license/copyright material directly from the exact build/runtime environment. A repository-pinned fallback is permitted only when a supported packaging environment contains the governed runtime component but does not expose its license text beside the runtime.

## Tcl 8.6

- file: `tcl/8.6/license.terms`
- upstream repository: `tcltk/tcl`
- upstream path: `license.terms`
- upstream line: `core-8-6-branch`
- upstream blob SHA observed/pinned during APL-IP-004: `d8049cd9e7ca055f7e584a76f88861a294b30c9c`
- captured: 2026-08-22

## Tk 8.6

- file: `tk/8.6/license.terms`
- upstream repository: `tcltk/tk`
- upstream path: `license.terms`
- upstream line: `core-8-6-branch`
- upstream blob SHA observed/pinned during APL-IP-004: `01264352c87ca7e34771bd1ee18bed5201ef139f`
- captured: 2026-08-22

These files are not a substitute for dependency/version reconciliation. If the supported Tcl/Tk major-minor line changes, the collector and fallback provenance must be reviewed before promotion.
