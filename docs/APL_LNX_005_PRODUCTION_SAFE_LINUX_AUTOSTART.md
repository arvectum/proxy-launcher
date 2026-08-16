# APL-LNX-005 — Production-safe Linux autostart

Status: implemented (code/CI); native Astra graphical-session validation remains an environment acceptance gate.

## Goal

Provide production-safe per-user autostart for Linux and Astra Linux without root, `sudo`, `pkexec`, system services, credential collection, or destructive ownership assumptions.

The feature means **automatic proxy connection at graphical login**, not merely opening the GUI. The autostart command is the packaged Arvectum executable with `--start`.

## Canonical mechanism

APL-LNX-005 uses the freedesktop/XDG per-user autostart directory:

- `${XDG_CONFIG_HOME}/autostart/arvectum-proxy-launcher.desktop` when `XDG_CONFIG_HOME` is absolute;
- otherwise `~/.config/autostart/arvectum-proxy-launcher.desktop`.

No system-wide `/etc/xdg/autostart` entry is created or modified.

## Packaged-build boundary

Autostart may be registered only by a frozen production build whose resolved executable basename is exactly:

`Arvectum Proxy Launcher`

Source-checkout execution is refused. This prevents a development interpreter path from becoming a persistent login command.

The generated desktop entry launches exactly the resolved packaged executable followed by `--start` and contains the explicit ownership marker:

`X-Arvectum-Autostart=APL-LNX-005`

## Safety contract

1. **Per-user only.** No root privileges or system-wide startup files are used.
2. **Packaged executable only.** Development/source execution cannot register autostart.
3. **Exact ownership.** An entry is managed only when its entire UTF-8 content exactly matches the canonical APL-LNX-005 rendering for the current executable.
4. **No foreign overwrite.** Any same-named file with different content is a conflict and is left untouched.
5. **No foreign deletion.** Disable refuses to remove a same-named entry that does not exactly match the owned contract.
6. **No symlink target mutation.** A symlink at the managed file path is rejected and never followed for writes or deletion.
7. **Regular-file requirement.** FIFOs, directories, devices and other non-regular targets are rejected.
8. **Atomic creation.** The new entry is written to a same-directory temporary file with mode `0600`, flushed and fsynced before publication.
9. **Race re-check.** The target is checked again immediately before publication; a newly-created concurrent entry aborts the operation.
10. **Post-write verification.** The resulting file is read back and must exactly equal the intended owned entry.
11. **Post-delete verification.** Disable verifies that the owned entry is absent after unlink.
12. **Fail closed on read/path errors.** Ambiguous or unreadable state is never interpreted as safe ownership.

## PolicyKit behavior at login

APL-LNX-004 established that a NetworkManager mutation requiring PolicyKit interaction is permitted only after an explicit user action in the GUI. A background login autostart is not such an action.

Therefore APL-LNX-005 deliberately does **not** set `ARVECTUM_POLICYKIT_INTERACTIVE=1` and does not add `nmcli --ask`.

Consequences:

- if NetworkManager is already operationally `ready`, login autostart may connect the proxy normally;
- if the host is `auth_required`, the headless autostart attempt fails closed without prompting for credentials and without relaxing the APL-LNX-003/004 safety boundary;
- the user can then connect from the GUI, where the explicit PolicyKit UX is available;
- `unavailable` remains fail-closed.

## GUI behavior

The Linux/Astra checkbox is now active only when the current runtime can prove a canonical packaged executable and there is no ownership conflict.

Label:

`Автоподключение прокси при входе в Linux/Astra`

After every toggle the checkbox is refreshed from the actual filesystem state rather than from the requested state.

If a conflicting same-named file exists, the checkbox is disabled and the file remains unchanged. If an operation fails, the UI restores the real state and reports that unowned entries were not modified.

## Verification

`tests/test_linux_autostart.py` covers:

- source-checkout rejection;
- canonical executable-name enforcement;
- XDG config path rules;
- exact entry creation;
- executable paths containing spaces;
- file mode `0600`;
- idempotent enable;
- foreign-file overwrite refusal;
- foreign-file deletion refusal;
- symlink refusal without target modification;
- owned-entry disable and absence verification;
- post-write verification failure handling.

The core backend CI compiles `linux_autostart.py` and runs the full Linux/Astra backend contract matrix on Ubuntu and macOS runners to preserve cross-platform import safety.

## Native validation boundary

CI can prove file ownership logic, deterministic rendering and fail-closed state transitions. It cannot prove desktop-environment startup behavior on every Astra edition without a real graphical session.

Later native Astra acceptance must verify at least:

- Fly graphical login reads the per-user XDG autostart entry;
- packaged executable path with spaces launches correctly;
- `ready` host reconnects at login;
- `auth_required` host does not open an unexpected credential prompt and leaves the network safe;
- manual GUI connection after login still presents the APL-LNX-004 PolicyKit flow;
- disable prevents subsequent login launch;
- a foreign same-named `.desktop` file remains byte-for-byte unchanged.
