# APL-LNX-004 — Linux/Astra GUI capability state & PolicyKit authorization UX

Status: implemented (code/CI); native Astra validation remains a later environment gate.

## Goal

Turn the APL-LNX-003 backend readiness model into an explicit Linux/Astra desktop UX and close the `auth_required` gap without introducing `sudo`, `pkexec`, a custom password collector, a privileged daemon, or an implicit elevation path.

The product must distinguish:

- **ready** — NetworkManager can apply the system proxy without a new authorization challenge;
- **auth_required** — the host is technically supported, but NetworkManager/PolicyKit requires interactive authorization;
- **unavailable** — a new system-proxy mutation must not be attempted.

## Architecture

### Dedicated Linux GUI entry point

Linux packaging and launch scripts now use `linux_gui.py`. The proven Windows `proxy_gui.py` remains unchanged as the Windows product entry point.

`linux_gui.py` reuses the common branded controls and settings dialogs but owns Linux/Astra runtime semantics:

- Linux/Astra platform badge;
- capability-aware primary status;
- explicit PolicyKit confirmation;
- platform-neutral recovery copy;
- Linux autostart is visibly disabled until its own governed task is implemented.

### PolicyKit boundary

`linux_policykit_ux.py` owns the authorization boundary.

The environment marker `ARVECTUM_POLICYKIT_INTERACTIVE=1` is:

1. absent during ordinary GUI inspection and read-only preflight;
2. removed when child environments are constructed by default;
3. added only to the child created after an explicit user confirmation;
4. Linux-only;
5. not a privilege grant — it only permits the real NetworkManager mutation to request authorization.

The GUI never receives, reads or stores the PolicyKit password.

### NetworkManager interaction

For an explicitly interactive child, the Linux backend receives an injected nmcli runner. It adds the global `--ask` option only to governed mutation commands:

- `nmcli connection modify ...`;
- `nmcli device reapply ...`.

Read-only commands such as status, permissions and connection inspection remain non-interactive.

This preserves APL-LNX-002's read-only capability probe and prevents a status refresh from unexpectedly opening an authorization dialog.

## Runtime behavior

### `ready`

GUI state:

- badge: `ГОТОВО К ПОДКЛЮЧЕНИЮ`;
- enable button is available;
- no authorization explanation is shown;
- normal child process is launched without the PolicyKit marker.

### `auth_required`

GUI state:

- badge: `НУЖНО РАЗРЕШЕНИЕ`;
- this state is **not** displayed as ready;
- enable button remains actionable because it starts an authorization flow rather than pretending permission already exists;
- before any mutation, Arvectum shows its own explanatory yes/no confirmation;
- only after `Yes` is the marked child created;
- NetworkManager/PolicyKit, not Arvectum, owns the actual authentication UI.

If the user cancels Arvectum's confirmation, no marked child is created and no network mutation is attempted.

If PolicyKit denies/cancels authorization, the backend operation fails safely and the GUI returns to the capability state with a non-destructive explanation.

### `unavailable`

GUI state:

- badge: `СИСТЕМНЫЙ ПРОКСИ НЕДОСТУПЕН`;
- enable is disabled;
- read-only diagnostics remain available;
- the user is told that NetworkManager is not currently safe to modify and the network has been left unchanged.

## Existing safety invariants preserved

- no `sudo`;
- no `pkexec`;
- no custom credential dialog;
- no password storage;
- no automatic PolicyKit prompt from read-only preflight;
- no NetworkManager restart;
- no interface cycling;
- no package installation;
- no relaxation of `auth_required` for ordinary CLI/service execution;
- no relaxation of `unavailable`, even inside an interactive child;
- rollback remains outside the new-enable preflight gate;
- Windows customer-proven GUI entry point is not modified.

## Exceptions / no_proxy

If NetworkManager is already `ready`, live no-proxy synchronization keeps its existing behavior.

If the current host requires authorization, editing the exception list remains a local configuration operation and does not silently open PolicyKit. The GUI tells the user that the saved exceptions will be applied on the next explicit proxy connection, where the normal authorization UX is available.

## Linux packaging wiring

The following now target `linux_gui.py`:

- `build_linux.sh`;
- `run_gui.sh`;
- `arvectum-proxy.desktop` template.

This prevents Linux releases from entering Windows-only single-instance/autostart presentation logic.

## Verification

`tests/test_linux_policykit_ux.py` covers:

1. Linux-only explicit interaction marker;
2. parent marker stripping by default;
3. one-shot child marker creation;
4. `nmcli --ask` only on mutations;
5. no duplicate `--ask`;
6. subprocess runner contract preservation;
7. actionable-but-not-ready `auth_required` GUI state;
8. fail-closed `unavailable` GUI state;
9. ready state without authorization UX;
10. ordinary unmarked core path remains fail-closed;
11. marked `auth_required` path may reach NetworkManager authority;
12. interactive backend receives only the governed PolicyKit runner.

Existing APL-LNX-003 tests continue to own the non-interactive mutation gate, including rollback availability.

## Native validation boundary

This task can prove the state machine, process boundary and command construction in CI without an Astra Linux machine. It cannot truthfully prove the exact native authentication-agent appearance or Astra edition-specific policy rules without a real Astra graphical session.

That native evidence belongs to the later Astra acceptance task and must test at least:

- Fly graphical session with its authentication agent;
- a normal authorized user;
- a user requiring an administrator challenge;
- explicit cancel/deny;
- a policy rule that returns hard `no`;
- successful enable followed by rollback;
- GUI responsiveness while authorization is pending.
